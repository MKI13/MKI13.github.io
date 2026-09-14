"""Distinguish pre-DATA failures, explicit rejection and a lost final reply."""
import re
import smtplib
import ssl
from .config import RECIPIENT

class SMTPTransport:
    def __init__(self,cfg,factory=smtplib.SMTP,context_factory=ssl.create_default_context):
        self.cfg,self.factory,self.context_factory=cfg,factory,context_factory

    def send(self,raw,before_data):
        smtp=None
        transmitting=False
        try:
            smtp=self.factory(self.cfg.smtp_host,self.cfg.smtp_port,timeout=self.cfg.smtp_timeout)
            smtp.ehlo()
            smtp.starttls(context=self.context_factory())
            smtp.ehlo()
            smtp.login(self.cfg.smtp_user,self.cfg.smtp_password)
            for action,value in ((smtp.mail,self.cfg.smtp_user),(smtp.rcpt,RECIPIENT)):
                code,_=action(value)
                if code not in (250,251): return ('retry' if 400<=code<500 else 'failed','smtp_envelope_rejected')
            code,_=smtp.docmd('DATA')
            if code!=354: return ('retry' if 400<=code<500 else 'failed','smtp_data_rejected')
            before_data()
            transmitting=True
            body=re.sub(br'(?m)^\.',b'..',raw)
            if not body.endswith(b'\r\n'): body+=b'\r\n'
            smtp.send(body+b'.\r\n')
            code,_=smtp.getreply()
            if code==250: return ('smtp_accepted','')
            if 400<=code<500: return ('retry','smtp_explicit_rejection')
            if 500<=code<600: return ('failed','smtp_explicit_rejection')
            return ('uncertain','smtp_unexpected_final_reply')
        except smtplib.SMTPAuthenticationError:
            return ('failed','smtp_authentication')
        except (OSError,smtplib.SMTPException,RuntimeError):
            return ('uncertain','smtp_reply_unknown') if transmitting else ('retry','smtp_connection')
        finally:
            if smtp:
                try: smtp.close()
                except OSError: pass

    def check_connection(self):
        # No MAIL/RCPT/DATA: this verifies authentication, not delivery.
        with self.factory(self.cfg.smtp_host,self.cfg.smtp_port,timeout=self.cfg.smtp_timeout) as smtp:
            smtp.ehlo();smtp.starttls(context=self.context_factory());smtp.ehlo()
            smtp.login(self.cfg.smtp_user,self.cfg.smtp_password)
            code,_=smtp.noop()
            return code==250
