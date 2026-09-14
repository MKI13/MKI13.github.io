"""Real browser -> local API -> real TLS SMTP test sink. Never sends external mail."""
import functools
import http.server
import json
import os
import subprocess
import tempfile
import threading
from pathlib import Path
from urllib.parse import urlsplit
from email import policy
from email.parser import BytesParser
from PIL import Image
from werkzeug.serving import make_server,WSGIRequestHandler
from inquiry_service.config import Settings
from inquiry_service.app import create_app
from inquiry_service.mail import SMTPTransport
from inquiry_service.worker import tick
from inquiry_service.receipt import matches
from smtp_sink import Sink
ROOT=Path(__file__).resolve().parents[2]

class Quiet(WSGIRequestHandler):
    def log(self,*args,**kwargs): pass


def main():
    with tempfile.TemporaryDirectory(prefix='ef-sinn-issue16-') as temporary:
        path=Path(temporary)
        sink=Sink(path)
        api_address={}
        class Frontend(http.server.SimpleHTTPRequestHandler):
            def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
            def log_message(self,*args): pass
            def do_GET(self):
                if urlsplit(self.path).path=='/assets/js/inquiry-delivery-config.js':
                    value=('window.EFSINN_DELIVERY='+json.dumps({'enabled':True,'endpoint':api_address['url']})+';').encode()
                    self.send_response(200);self.send_header('Content-Type','text/javascript');self.send_header('Content-Length',str(len(value)));self.end_headers();self.wfile.write(value)
                else: super().do_GET()
        frontend=http.server.ThreadingHTTPServer(('127.0.0.1',0),Frontend)
        front_url=f'http://127.0.0.1:{frontend.server_port}/'
        cfg=Settings(data_dir=path/'private',secret=b'local-test-only-key-never-production',origins=(front_url.rstrip('/'),),host='127.0.0.1',
                     smtp_user='info@ef-sinn.de',smtp_password='synthetic-test-token',smtp_host='127.0.0.1',smtp_port=sink.server_address[1],enabled=True)
        app=create_app(cfg);store=app.extensions['inquiry_store'];store.heartbeat()
        api=make_server('127.0.0.1',0,app,threaded=True,request_handler=Quiet)
        api_address['url']=f'http://127.0.0.1:{api.server_port}/'
        transport=SMTPTransport(cfg,context_factory=lambda:sink.client_context)
        stop=threading.Event()
        def worker():
            while not stop.is_set():
                tick(store,transport);stop.wait(.1)
        servers=[frontend,api,sink]
        threads=[threading.Thread(target=s.serve_forever,daemon=True) for s in servers]
        threads.append(threading.Thread(target=worker,daemon=True))
        for thread in threads: thread.start()
        photo=path/'synthetic-photo.png';Image.new('RGB',(80,60),'white').save(photo)
        try:
            env={**os.environ,'ISSUE16_BASE_URL':front_url,'ISSUE16_PHOTO':str(photo)}
            subprocess.run(['node',str(ROOT/'qa/direct-delivery-audit.mjs')],env=env,check=True,timeout=180)
            assert len(sink.messages)==3,f'Expected exactly 3 distinct emails, got {len(sink.messages)}'
            for raw in sink.messages:
                message=BytesParser(policy=policy.default).parsebytes(raw)
                identifier=str(message['Message-ID']).strip('<>').split('@')[0]
                job=store.get(identifier)
                assert job and job['state']=='smtp_accepted'
                assert matches(raw,identifier,json.loads(job['expected']))
                assert len(list(message.iter_attachments()))==1
            report={'test':'Browser to real local HTTP API and TLS SMTP test sink','external_messages_sent':0,
                    'distinct_local_messages':3,'duplicate_messages':0,'message_body_reply_address_and_photos_verified':True,
                    'production_inbox_verified':False}
            output=ROOT/'.qa-results';output.mkdir(exist_ok=True)
            (output/'direct-delivery-integration.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(report))
        finally:
            stop.set()
            for server in servers: server.shutdown();server.server_close()
            for thread in threads: thread.join(timeout=5)

if __name__=='__main__': main()
