import io
import json
import hashlib
import uuid
from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor
from email import policy
from email.parser import BytesParser
from pathlib import Path
import pytest
from PIL import Image
from werkzeug.datastructures import MultiDict
from inquiry_service.config import Settings
from inquiry_service.app import create_app
from inquiry_service.store import Store
from inquiry_service.worker import tick
from inquiry_service.mail import SMTPTransport
from inquiry_service.receipt import matches
from inquiry_service.validation import Invalid

ORIGIN='https://www.ef-sinn.de'
BASE='https://api.ef-sinn.test'

class Clock:
    value=1_800_000_000
    def __call__(self): return self.value

@pytest.fixture
def env(tmp_path):
    clock=Clock()
    cfg=Settings(data_dir=tmp_path/'private',secret=b'unit-test-only-secret-not-for-production',origins=(ORIGIN,),host='api.ef-sinn.test',
                 smtp_user='info@ef-sinn.de',smtp_password='synthetic-test-token',enabled=True)
    app=create_app(cfg,clock)
    app.testing=True
    store=app.extensions['inquiry_store'];store.heartbeat()
    return cfg,clock,app,app.test_client(),store


def request(env,path,method='GET',data=None,headers=None):
    return env[3].open(path,method=method,data=data,headers={'Origin':ORIGIN,**(headers or {})},base_url=BASE,
                       content_type='multipart/form-data' if method=='POST' else None)


def prepare(env):
    response=request(env,'/v1/challenge')
    assert response.status_code==200
    env[1].value+=3
    fields={'name':'Test Müller','email':'customer@example.org','phone':'','project':'Bett reparieren','message':'Die Verbindung am Bett ist locker.',
            'language':'de','challenge':response.json['challenge'],'website':''}
    headers={'Idempotency-Key':str(uuid.uuid4()),'X-Status-Token':uuid.uuid4().hex+uuid.uuid4().hex}
    return fields,headers


def image_bytes(fmt='PNG'):
    out=io.BytesIO();Image.new('RGB',(40,30),'white').save(out,format=fmt)
    return out.getvalue()


def submit(env,fields,headers):
    return request(env,'/v1/inquiries','POST',fields,headers)


def test_valid_request_with_photo_is_durable_and_not_claimed_delivered(env):
    fields,headers=prepare(env);fields['photos']=(io.BytesIO(image_bytes()),'../../my-photo.png')
    response=submit(env,fields,headers)
    assert response.status_code==202 and response.json['state']=='queued'
    row=env[4].get(headers['Idempotency-Key'])
    message=BytesParser(policy=policy.default).parsebytes(row['payload'])
    assert message['To']=='info@ef-sinn.de' and message['Reply-To']=='customer@example.org'
    attachments=list(message.iter_attachments())
    assert len(attachments)==1 and attachments[0].get_filename()=='foto-1.jpg'
    photo=Image.open(io.BytesIO(attachments[0].get_payload(decode=True)))
    assert photo.format=='JPEG' and not photo.getexif()
    assert 'Test Müller' not in json.dumps(response.json)
    restored=Store(env[0],env[1]).get(headers['Idempotency-Key'])
    assert restored['payload']==row['payload']

@pytest.mark.parametrize('language',['de','de-AT','en','fr','el','it','es'])
def test_seven_languages_accepted(env,language):
    fields,headers=prepare(env);fields['language']=language
    assert submit(env,fields,headers).status_code==202

@pytest.mark.parametrize('field,value,code',[
    ('name','','required_fields'),('message','short','required_fields'),('project','','required_fields'),
    ('email','x@invalid','invalid_email'),('email','a@b.com\r\nBcc: x@y.com','invalid_field'),
    ('name','x'*121,'invalid_field'),('message','x'*5001,'invalid_field'),
    ('phone','abc','invalid_phone'),('phone','1234','invalid_phone'),('language','ru','invalid_language'),
    ('message','hello\x00world','invalid_field'),('location','a\nb','invalid_field'),
])
def test_fields_rejected_before_queue(env,field,value,code):
    fields,headers=prepare(env);fields[field]=value
    response=submit(env,fields,headers)
    assert response.status_code==422 and response.json['error']==code
    assert env[4].counters()=={}


def test_at_least_one_valid_reply_channel_is_required(env):
    fields,headers=prepare(env);fields['email']=''
    assert submit(env,fields,headers).json['error']=='contact_required'
    fields['phone']='+49 176 1234567'
    assert submit(env,fields,headers).status_code==202

@pytest.mark.parametrize('kind',['SVG','TEXT','GIF','TRUNCATED'])
def test_disguised_or_unsupported_image_rejected(env,kind):
    raw={'SVG':b'<svg onload="alert(1)"></svg>','TEXT':b'not an image','GIF':image_bytes('GIF'),'TRUNCATED':image_bytes()[:15]}[kind]
    fields,headers=prepare(env);fields['photos']=(io.BytesIO(raw),'photo.jpg')
    assert submit(env,fields,headers).json['error']=='file_type'
    assert env[4].counters()=={}


def test_file_count_limit(env):
    fields,headers=prepare(env);fields['photos']=[(io.BytesIO(image_bytes()),f'{n}.png') for n in range(6)]
    assert submit(env,fields,headers).json['error']=='too_many_files'


def test_file_size_limit(env):
    fields,headers=prepare(env);fields['photos']=(io.BytesIO(b'x'*(env[0].max_file_bytes+1)),'x.jpg')
    assert submit(env,fields,headers).status_code==413


def test_pixel_limit(env):
    cfg=replace(env[0],max_pixels=10)
    from inquiry_service.validation import photos_from
    from werkzeug.datastructures import FileStorage
    with pytest.raises(Invalid,match='image_dimensions'):
        photos_from(MultiDict([('photos',FileStorage(io.BytesIO(image_bytes()),filename='a.png'))]),cfg)


def test_honeypot_challenge_timing_and_expiry(env):
    fields,headers=prepare(env);fields['website']='spam'
    assert submit(env,fields,headers).status_code==400
    fields['website']='';env[1].value-=3
    assert submit(env,fields,headers).json['error']=='challenge_too_soon'
    env[1].value+=1300;env[4].heartbeat()
    assert submit(env,fields,headers).json['error']=='challenge_expired'


def test_challenge_cannot_be_reused_for_second_request(env):
    fields,headers=prepare(env)
    assert submit(env,fields,headers).status_code==202
    headers={**headers,'Idempotency-Key':str(uuid.uuid4())}
    assert submit(env,fields,headers).json['error']=='challenge_used'


def test_duplicate_id_returns_same_job_but_changed_payload_conflicts(env):
    fields,headers=prepare(env)
    assert submit(env,fields,headers).status_code==202
    assert submit(env,fields,headers).status_code==200
    fields['message']+=' changed'
    assert submit(env,fields,headers).status_code==409
    assert env[4].counters()=={'queued':1}


def test_atomic_concurrent_deduplication(env):
    store=env[4];identifier=str(uuid.uuid4())
    def add(_): return store.enqueue(identifier,'a'*64,'fingerprint','one-nonce',b'mime','{}')[1]
    with ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(add,range(16)))
    assert results.count(True)==1 and store.counters()=={'queued':1}


def test_status_requires_private_capability(env):
    fields,headers=prepare(env);submit(env,fields,headers)
    path='/v1/inquiries/'+headers['Idempotency-Key']
    assert request(env,path,headers={'X-Status-Token':headers['X-Status-Token']}).json['state']=='queued'
    assert request(env,path,headers={'X-Status-Token':'f'*64}).status_code==404
    assert request(env,path).status_code==400


def test_explicit_origins_cors_and_no_cookie(env):
    result=env[3].get('/v1/challenge',headers={'Origin':'https://evil.example'},base_url=BASE)
    assert result.status_code==403 and 'Access-Control-Allow-Origin' not in result.headers
    result=request(env,'/v1/inquiries','OPTIONS')
    assert result.status_code==204 and result.headers['Access-Control-Allow-Origin']==ORIGIN
    assert 'Set-Cookie' not in result.headers
    assert result.headers['Cache-Control']=='no-store'


def test_rate_limits_and_stale_worker_fail_closed(env):
    env[4].rate('test','ip',1)
    with pytest.raises(Invalid,match='rate_limited'): env[4].rate('test','ip',1)
    env[1].value+=61
    assert request(env,'/v1/challenge').status_code==503


def test_queue_is_bounded(env):
    env[4].cfg=replace(env[0],max_queue_bytes=1)
    fields,headers=prepare(env)
    assert submit(env,fields,headers).status_code==503
    assert env[4].counters()=={}

class FakeSMTP:
    final=250;failure=None
    def __init__(self,*args,**kwargs): self.sent=b'';self.tls=False
    def ehlo(self): return (250,b'OK')
    def starttls(self,context): self.tls=True
    def login(self,user,password):
        assert self.tls
        if self.failure=='login': raise OSError('synthetic failure')
    def mail(self,address): return (250,b'OK')
    def rcpt(self,address):
        assert address=='info@ef-sinn.de';return (250,b'OK')
    def docmd(self,command): assert command=='DATA';return (354,b'continue')
    def send(self,body):
        self.sent=body
        if self.failure=='send': raise OSError('synthetic failure')
    def getreply(self):
        if self.failure=='reply': raise OSError('synthetic failure')
        return self.final,b'controlled response'
    def close(self): pass

@pytest.mark.parametrize('failure,final,state',[('login',250,'queued'),('send',250,'uncertain'),('reply',250,'uncertain'),(None,250,'smtp_accepted'),(None,451,'queued'),(None,550,'failed')])
def test_smtp_phase_state_machine(env,failure,final,state):
    fields,headers=prepare(env);submit(env,fields,headers)
    factory=type('ConfiguredSMTP',(FakeSMTP,),{'failure':failure,'final':final})
    assert tick(env[4],SMTPTransport(env[0],factory))
    row=env[4].get(headers['Idempotency-Key'])
    assert row['state']==state
    if state=='smtp_accepted': assert row['payload'] is None
    if state=='uncertain':
        env[1].value+=3600
        assert not tick(env[4],SMTPTransport(env[0],factory))

@pytest.mark.parametrize('during_data,state',[ (False,'queued'),(True,'uncertain') ])
def test_crashed_worker_recovery(env,during_data,state):
    fields,headers=prepare(env);submit(env,fields,headers);job=env[4].claim()
    if during_data: env[4].begin_data(job['id'],job['lease'])
    env[1].value+=601;env[4].maintenance()
    assert env[4].get(job['id'])['state']==state


def test_receipt_requires_exact_body_reply_and_photos(env):
    fields,headers=prepare(env);fields['photos']=(io.BytesIO(image_bytes()),'a.png')
    submit(env,fields,headers);row=env[4].get(headers['Idempotency-Key'])
    expected=json.loads(row['expected'])
    assert matches(row['payload'],row['id'],expected)
    assert not matches(row['payload'],str(uuid.uuid4()),expected)
    assert not matches(row['payload'],row['id'],{**expected,'photos':[]})
    assert not matches(row['payload'],row['id'],{**expected,'reply_sha256':'bad'})
    tick(env[4],SMTPTransport(env[0],FakeSMTP))
    env[4].receipt_verified(row['id'])
    assert env[4].get(row['id'])['state']=='receipt_verified'


def test_retention_removes_payload_and_expires_status(env):
    fields,headers=prepare(env);submit(env,fields,headers)
    env[1].value+=8*86400;env[4].maintenance()
    row=env[4].get(headers['Idempotency-Key'])
    assert row['payload'] is None and row['state']=='failed'
    env[1].value+=7*86400;env[4].maintenance()
    assert env[4].get(headers['Idempotency-Key']) is None

@pytest.mark.parametrize('email',['a@bad..example','a@-bad.example','a@bad-.example','.a@example.org','a..b@example.org'])
def test_invalid_mailbox_structure(env,email):
    fields,headers=prepare(env);fields['email']=email
    assert submit(env,fields,headers).json['error']=='invalid_email'


def test_unicode_body_uses_portable_ascii_smtp_mime(env):
    fields,headers=prepare(env);fields['message']='Μια πραγματική περιγραφή. Grüße aus München.'
    submit(env,fields,headers);row=env[4].get(headers['Idempotency-Key'])
    assert row['payload'].isascii()
    assert matches(row['payload'],row['id'],json.loads(row['expected']))


def test_expired_worker_cannot_send_after_another_worker_reclaims(env):
    fields,headers=prepare(env);submit(env,fields,headers)
    old=env[4].claim();env[1].value+=601;env[4].maintenance();new=env[4].claim()
    assert old['lease']!=new['lease']
    with pytest.raises(RuntimeError): env[4].begin_data(old['id'],old['lease'])
    env[4].begin_data(new['id'],new['lease'])
    env[4].finish(old['id'],'smtp_accepted','',old['lease'])
    assert env[4].get(new['id'])['state']=='transmitting'
    env[4].finish(new['id'],'smtp_accepted','',new['lease'])
    assert env[4].get(new['id'])['state']=='smtp_accepted'
