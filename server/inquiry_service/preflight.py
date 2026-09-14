"""Check deployment configuration and optional SMTP AUTH without sending a message."""
import argparse
import json
import shutil
from .config import Settings
from .store import Store
from .mail import SMTPTransport


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smtp',action='store_true',help='Perform STARTTLS and AUTH only; no email is sent')
    args=parser.parse_args()
    try:
        cfg=Settings.from_env();store=Store(cfg)
        report={'configuration':True,'worker_recent':store.healthy(),'free_disk_ok':shutil.disk_usage(cfg.data_dir).free>=256*1024*1024,
                'queue_states':store.counters(),'smtp_auth_checked':False,'production_receipt_verified':False}
        if args.smtp:
            report['smtp_auth_checked']=SMTPTransport(cfg).check_connection()
        print(json.dumps(report,indent=2))
        if not report['free_disk_ok'] or (args.smtp and not report['smtp_auth_checked']): raise SystemExit(1)
    except (OSError,ValueError,KeyError):
        print(json.dumps({'configuration':False,'error':'Required deployment settings or mounted secret files are missing/invalid; values are not printed'}))
        raise SystemExit(1)

if __name__=='__main__': main()
