"""Verify the real INBOX copy, not SMTP acceptance or a fabricated success flag."""
import argparse
import hashlib
import imaplib
import json
import os
import ssl
import uuid
from datetime import datetime,timezone
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses
from pathlib import Path
from .config import Settings,RECIPIENT,secret_file
from .store import Store


def matches(raw,identifier,expected):
    message=BytesParser(policy=policy.default).parsebytes(raw)
    if str(message.get('Message-ID','')).strip()!=f'<{identifier}@ef-sinn.de>': return False
    recipients=[address.lower() for _,address in getaddresses(message.get_all('To',[]))]
    if RECIPIENT not in recipients: return False
    replies=getaddresses(message.get_all('Reply-To',[]))
    reply=replies[0][1].lower() if len(replies)==1 else ''
    if hashlib.sha256(reply.encode()).hexdigest()!=expected['reply_sha256']: return False
    body=message.get_body(preferencelist=('plain',))
    if body is None: return False
    text=body.get_content().replace('\r\n','\n').strip()
    if hashlib.sha256(text.encode()).hexdigest()!=expected['body_sha256']: return False
    photos=[hashlib.sha256(part.get_payload(decode=True)).hexdigest() for part in message.iter_attachments()]
    return photos==expected['photos']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request_id',type=lambda value:str(uuid.UUID(value)))
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    cfg=Settings.from_env();store=Store(cfg)
    job=store.get(args.request_id)
    if not job or job['state'] not in ('smtp_accepted','uncertain'):
        raise SystemExit('No SMTP submission awaiting inbox verification')
    ca=os.environ.get('IMAP_CA_FILE')
    context=ssl.create_default_context(cafile=ca or None)
    host=os.environ['IMAP_HOST'];port=int(os.environ.get('IMAP_PORT','993'))
    mode=os.environ.get('IMAP_TLS_MODE','implicit')
    if mode not in ('implicit','starttls'): raise SystemExit('IMAP_TLS_MODE must be implicit or starttls')
    connection=(imaplib.IMAP4(host,port,timeout=20) if mode=='starttls' else imaplib.IMAP4_SSL(host,port,ssl_context=context,timeout=20))
    with connection as client:
        if mode=='starttls': client.starttls(ssl_context=context)
        client.login(os.environ['IMAP_USERNAME'],secret_file('IMAP_PASSWORD_FILE',1).decode())
        status,_=client.select('INBOX',readonly=True)
        if status!='OK': raise SystemExit('Cannot inspect INBOX')
        status,data=client.uid('search',None,'HEADER','Message-ID',f'"<{args.request_id}@ef-sinn.de>"')
        if status!='OK': raise SystemExit('INBOX search failed')
        found=False
        for uid in data[0].split()[-10:]:
            status,parts=client.uid('fetch',uid,'(BODY.PEEK[])')
            if status!='OK': continue
            for part in parts:
                if isinstance(part,tuple) and matches(part[1],args.request_id,json.loads(job['expected'])): found=True
        if not found: raise SystemExit('No matching INBOX message including body, reply address and photos; no delivery claim made')
    store.receipt_verified(args.request_id)
    proof={'request_id':args.request_id,'state':'receipt_verified','mailbox':'INBOX','recipient':RECIPIENT,
           'verified_at':datetime.now(timezone.utc).isoformat(),'attachment_count':len(json.loads(job['expected'])['photos'])}
    args.output.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    args.output.write_text(json.dumps(proof,indent=2)+'\n')
    os.chmod(args.output,0o600)
    print(json.dumps(proof))

if __name__=='__main__': main()
