"""Small public API. No arbitrary recipients, public attachments or cookie sessions."""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time
import uuid
import re
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix
from .config import Settings
from .store import Store
from .validation import Invalid, fields_from, photos_from, canonical, make_message


def create_app(cfg=None,clock=time.time):
    cfg=cfg or Settings.from_env()
    os.umask(0o077)
    app=Flask(__name__,static_folder=None)
    app.config.update(MAX_CONTENT_LENGTH=cfg.max_total_bytes+128*1024,
                      MAX_FORM_MEMORY_SIZE=128*1024,MAX_FORM_PARTS=24,TRUSTED_HOSTS=[cfg.host])
    if cfg.trust_proxy: app.wsgi_app=ProxyFix(app.wsgi_app,x_for=1,x_proto=1)
    store=Store(cfg,clock)
    app.extensions['inquiry_store']=store
    app.extensions['inquiry_settings']=cfg

    def require_ready():
        if not cfg.enabled or not store.healthy(): raise Invalid('temporarily_unavailable',503)

    def response_job(row):
        state='processing' if row['state'] in ('sending','transmitting') else row['state']
        return {'request_id':row['id'],'state':state}

    def identifier(value):
        try:
            parsed=uuid.UUID(value)
            if parsed.version!=4 or str(parsed)!=value: raise ValueError()
        except (ValueError,AttributeError): raise Invalid('invalid_request_id',400) from None
        return value

    def capability():
        token=request.headers.get('X-Status-Token','')
        if not re.fullmatch(r'[0-9a-f]{64}',token): raise Invalid('invalid_status_token',400)
        return token

    def signature(value):
        return hmac.new(cfg.secret,value.encode(),hashlib.sha256).hexdigest()

    def verify_challenge(token):
        try:
            if len(token)>1024: raise ValueError()
            payload,sig=token.split('.')
            if not hmac.compare_digest(signature(payload),sig): raise ValueError()
            data=json.loads(base64.urlsafe_b64decode(payload+'='*(-len(payload)%4)))
            elapsed=clock()-data['iat']
            if data['origin']!=request.headers['Origin'] or not 0<=elapsed<=1200: raise ValueError()
            if not re.fullmatch(r'[0-9a-f]{32}',data['nonce']): raise ValueError()
            if elapsed<cfg.min_challenge_age: raise Invalid('challenge_too_soon',400)
            return data['nonce']
        except Invalid: raise
        except (ValueError,KeyError,TypeError): raise Invalid('challenge_expired',400) from None

    @app.before_request
    def guard():
        if request.path=='/healthz': return None
        if request.headers.get('Origin') not in cfg.origins: raise Invalid('origin_denied',403)
        if request.method=='OPTIONS': return '',204
        if request.path.startswith('/v1/'):
            store.rate('request',request.remote_addr or '-',180)

    @app.after_request
    def headers(response):
        origin=request.headers.get('Origin')
        if origin in cfg.origins:
            response.headers['Access-Control-Allow-Origin']=origin
            response.headers['Access-Control-Allow-Methods']='GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers']='Content-Type, Idempotency-Key, X-Status-Token'
            response.headers['Vary']='Origin'
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['Content-Security-Policy']="default-src 'none'; frame-ancestors 'none'"
        if response.status_code==429: response.headers['Retry-After']='3600'
        return response

    @app.errorhandler(Invalid)
    def invalid(error):
        body={'error':error.code}
        if error.field: body['field']=error.field
        return jsonify(body),error.status

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(error='request_too_large' if error.code==413 else 'invalid_request'),error.code

    @app.errorhandler(Exception)
    def unexpected(error):
        app.logger.error('inquiry_request_failed')
        return jsonify(error='temporarily_unavailable'),503

    @app.get('/healthz')
    def health():
        healthy=cfg.enabled and store.healthy()
        return jsonify(ready=healthy),200 if healthy else 503

    @app.get('/v1/challenge')
    def challenge():
        require_ready()
        store.rate('challenge',request.remote_addr or '-',cfg.challenge_limit)
        data={'iat':int(clock()),'nonce':secrets.token_hex(16),'origin':request.headers['Origin']}
        payload=base64.urlsafe_b64encode(json.dumps(data,separators=(',',':')).encode()).decode().rstrip('=')
        return jsonify(challenge=payload+'.'+signature(payload),min_age=cfg.min_challenge_age,
                       limits={'max_files':cfg.max_files,'file_bytes':cfg.max_file_bytes,'total_bytes':cfg.max_total_bytes})

    @app.post('/v1/inquiries')
    def submit():
        request_id=identifier(request.headers.get('Idempotency-Key',''))
        token=capability()
        existing=store.get(request_id,token)
        if not existing: require_ready()
        if request.mimetype!='multipart/form-data': raise Invalid('invalid_request',415)
        if request.form.get('website',''): raise Invalid('invalid_request',400)
        nonce=existing['nonce'] if existing else verify_challenge(request.form.get('challenge',''))
        if not existing:
            store.rate('submit',request.remote_addr or '-',cfg.submit_limit)
            store.rate('submit','global',cfg.global_limit)
        data=fields_from(request.form)
        photos=photos_from(request.files,cfg)
        raw,expected=make_message(data,photos,request_id,cfg)
        row,created=store.enqueue(request_id,token,store.digest(canonical(data,photos)),nonce,raw,expected)
        return jsonify(response_job(row)),202 if created else 200

    @app.get('/v1/inquiries/<request_id>')
    def status(request_id):
        row=store.get(identifier(request_id),capability())
        if not row: raise Invalid('not_found',404)
        return jsonify(response_job(row))

    return app
