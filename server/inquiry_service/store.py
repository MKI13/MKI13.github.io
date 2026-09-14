"""Bounded durable queue. Lost final SMTP replies never trigger blind retries."""
import hashlib
import hmac
import os
import sqlite3
import secrets
import time
from contextlib import contextmanager
from .validation import Invalid

class Store:
    def __init__(self,cfg,clock=time.time):
        self.cfg,self.clock=cfg,clock
        cfg.data_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
        os.chmod(cfg.data_dir,0o700)
        self.path=cfg.data_dir/'queue.sqlite3'
        with self.db() as db:
            db.executescript("""CREATE TABLE IF NOT EXISTS jobs (
              id TEXT PRIMARY KEY, token_hash TEXT NOT NULL, fingerprint TEXT NOT NULL,
              nonce TEXT UNIQUE NOT NULL, state TEXT NOT NULL, created REAL NOT NULL,
              updated REAL NOT NULL, retry_at REAL NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
              payload BLOB, expected TEXT NOT NULL, error TEXT NOT NULL DEFAULT '', lease TEXT NOT NULL DEFAULT '');
              CREATE TABLE IF NOT EXISTS rates (bucket TEXT PRIMARY KEY, window INTEGER, hits INTEGER);
              CREATE TABLE IF NOT EXISTS meta (name TEXT PRIMARY KEY, value REAL);
              CREATE INDEX IF NOT EXISTS jobs_claim ON jobs(state,retry_at,created);""")
        os.chmod(self.path,0o600)

    @contextmanager
    def db(self):
        db=sqlite3.connect(self.path,timeout=10)
        db.row_factory=sqlite3.Row
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA synchronous=FULL')
        db.execute('PRAGMA secure_delete=ON')
        try:
            with db: yield db
        finally: db.close()

    def digest(self,value):
        if isinstance(value,str): value=value.encode()
        return hmac.new(self.cfg.secret,value,hashlib.sha256).hexdigest()

    def heartbeat(self):
        with self.db() as db:
            db.execute("INSERT INTO meta VALUES('worker',?) ON CONFLICT(name) DO UPDATE SET value=excluded.value",(self.clock(),))

    def healthy(self):
        with self.db() as db:
            row=db.execute("SELECT value FROM meta WHERE name='worker'").fetchone()
        return bool(row and self.clock()-row['value']<=60)

    def get(self,identifier,token=None):
        with self.db() as db:
            row=db.execute('SELECT * FROM jobs WHERE id=?',(identifier,)).fetchone()
        if token is not None and (not row or not hmac.compare_digest(row['token_hash'],self.digest(token))): return None
        return dict(row) if row else None

    def rate(self,category,identity,limit):
        window=int(self.clock()//3600)
        key=self.digest(f'{category}:{window}:{identity}')
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute('DELETE FROM rates WHERE window<?',(window-1,))
            row=db.execute('SELECT hits FROM rates WHERE bucket=?',(key,)).fetchone()
            if row and row['hits']>=limit: raise Invalid('rate_limited',429)
            if not row and db.execute('SELECT COUNT(*) FROM rates').fetchone()[0]>=10000:
                raise Invalid('rate_limited',429)
            db.execute('INSERT INTO rates VALUES(?,?,1) ON CONFLICT(bucket) DO UPDATE SET hits=hits+1',(key,window))

    def enqueue(self,identifier,token,fingerprint,nonce,raw,expected):
        now=self.clock()
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT * FROM jobs WHERE id=?',(identifier,)).fetchone()
            if row:
                if not hmac.compare_digest(row['token_hash'],self.digest(token)) or not hmac.compare_digest(row['fingerprint'],fingerprint):
                    raise Invalid('request_conflict',409)
                return dict(row),False
            if db.execute('SELECT 1 FROM jobs WHERE nonce=?',(nonce,)).fetchone(): raise Invalid('challenge_used',409)
            count,size=db.execute('SELECT COUNT(*),COALESCE(SUM(length(payload)),0) FROM jobs WHERE payload IS NOT NULL').fetchone()
            if count>=self.cfg.max_queue_count or size+len(raw)>self.cfg.max_queue_bytes: raise Invalid('temporarily_unavailable',503)
            db.execute('INSERT INTO jobs(id,token_hash,fingerprint,nonce,state,created,updated,retry_at,payload,expected) VALUES(?,?,?,?,?,?,?,?,?,?)',
                (identifier,self.digest(token),fingerprint,nonce,'queued',now,now,now,raw,expected))
            return dict(db.execute('SELECT * FROM jobs WHERE id=?',(identifier,)).fetchone()),True

    def maintenance(self):
        now=self.clock()
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            db.execute("UPDATE jobs SET state='queued',retry_at=?,updated=? WHERE state='sending' AND updated<?",(now,now,now-600))
            db.execute("UPDATE jobs SET state='uncertain',error='interrupted_during_data',updated=? WHERE state='transmitting' AND updated<?",(now,now-600))
            db.execute("UPDATE jobs SET state='failed',error='queue_expired',updated=? WHERE state='queued' AND created<?",(now,now-72*3600))
            db.execute('UPDATE jobs SET payload=NULL WHERE created<?',(now-7*86400,))
            db.execute('DELETE FROM jobs WHERE created<?',(now-14*86400,))
            db.execute('DELETE FROM rates WHERE window<?',(int(now//3600)-1,))
        with self.db() as db: db.execute('PRAGMA wal_checkpoint(PASSIVE)')

    def claim(self):
        now=self.clock()
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute("SELECT * FROM jobs WHERE state='queued' AND retry_at<=? AND payload IS NOT NULL ORDER BY created LIMIT 1",(now,)).fetchone()
            if not row: return None
            lease=secrets.token_hex(16)
            db.execute("UPDATE jobs SET state='sending',updated=?,attempts=attempts+1,lease=? WHERE id=?",(now,lease,row['id']))
            result=dict(row);result['attempts']+=1;result['state']='sending';result['lease']=lease
            return result

    def begin_data(self,identifier,lease):
        with self.db() as db:
            cursor=db.execute("UPDATE jobs SET state='transmitting',updated=? WHERE id=? AND state='sending' AND lease=?",(self.clock(),identifier,lease))
            if cursor.rowcount!=1: raise RuntimeError('Queue lease lost; no DATA will be transmitted')

    def finish(self,identifier,outcome,code,lease):
        now=self.clock()
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT state,attempts,lease FROM jobs WHERE id=?',(identifier,)).fetchone()
            if not row or row['lease']!=lease or row['state'] not in ('sending','transmitting'): return
            state=('queued' if row['attempts']<4 else 'failed') if outcome=='retry' else outcome
            if state not in ('queued','failed','uncertain','smtp_accepted'): raise ValueError('Invalid outcome')
            retry_at=now+60*(2**min(row['attempts'],6))
            db.execute("UPDATE jobs SET state=?,error=?,updated=?,retry_at=?,payload=CASE WHEN ?='smtp_accepted' THEN NULL ELSE payload END WHERE id=?",
                       (state,code,now,retry_at,state,identifier))

    def receipt_verified(self,identifier):
        with self.db() as db:
            changed=db.execute("UPDATE jobs SET state='receipt_verified',payload=NULL,error='',updated=? WHERE id=? AND state IN ('smtp_accepted','uncertain')",(self.clock(),identifier))
            if changed.rowcount!=1: raise ValueError('Only a previously submitted message can be verified')

    def counters(self):
        with self.db() as db: return dict(db.execute('SELECT state,COUNT(*) FROM jobs GROUP BY state').fetchall())
