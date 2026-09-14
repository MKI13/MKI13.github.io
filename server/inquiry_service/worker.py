"""Dedicated worker with durable crash recovery and no message-content logging."""
import json
import logging
import time
from .config import Settings
from .mail import SMTPTransport
from .store import Store


def tick(store,transport):
    store.heartbeat()
    store.maintenance()
    job=store.claim()
    if not job: return False
    try:
        outcome,code=transport.send(job['payload'],lambda:store.begin_data(job['id'],job['lease']))
    except Exception:
        state=store.get(job['id'])['state']
        outcome,code=('uncertain','worker_exception') if state=='transmitting' else ('retry','worker_exception')
    store.finish(job['id'],outcome,code,job['lease'])
    logging.getLogger('inquiry.worker').info(json.dumps({'id':job['id'],'outcome':outcome,'code':code}))
    return True


def main():
    cfg=Settings.from_env()
    if not cfg.enabled: raise SystemExit('INQUIRY_ENABLED must be explicitly enabled for the worker')
    logging.basicConfig(level=logging.INFO,format='%(message)s')
    store=Store(cfg);transport=SMTPTransport(cfg)
    while True:
        try: active=tick(store,transport)
        except Exception:
            logging.error('worker_storage_error')
            active=False
        time.sleep(0.2 if active else 2)

if __name__=='__main__': main()
