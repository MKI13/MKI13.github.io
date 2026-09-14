"""Loopback-only TLS SMTP test sink. Not a production mail relay."""
import socketserver
import ssl
import threading
import subprocess
from pathlib import Path

class Sink(socketserver.ThreadingTCPServer):
    allow_reuse_address=True
    daemon_threads=True
    def __init__(self,directory):
        cert=Path(directory)/'test-cert.pem';key=Path(directory)/'test-key.pem'
        subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(key),'-out',str(cert),
                        '-days','1','-subj','/CN=localhost','-addext','subjectAltName=DNS:localhost,IP:127.0.0.1'],
                       check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        self.context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);self.context.load_cert_chain(cert,key)
        self.client_context=ssl.create_default_context(cafile=str(cert))
        self.messages=[];self.lock=threading.Lock()
        super().__init__(('127.0.0.1',0),Handler)

class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        connection=self.request;connection.settimeout(20)
        stream=connection.makefile('rb')
        def reply(value): connection.sendall(value+b'\r\n')
        reply(b'220 localhost test SMTP')
        authenticated=False
        try:
            while True:
                line=stream.readline(65536)
                if not line: break
                verb=line.split(b' ',1)[0].strip().upper()
                if verb in (b'EHLO',b'HELO'):
                    reply(b'250-localhost\r\n250-STARTTLS\r\n250 AUTH PLAIN')
                elif verb==b'STARTTLS':
                    reply(b'220 begin TLS');stream.close()
                    connection=self.server.context.wrap_socket(connection,server_side=True)
                    stream=connection.makefile('rb')
                elif verb==b'AUTH':
                    if not isinstance(connection,ssl.SSLSocket): reply(b'530 TLS required')
                    else: authenticated=True;reply(b'235 authenticated test client')
                elif verb in (b'MAIL',b'RCPT'):
                    reply(b'250 OK' if authenticated else b'530 authentication required')
                elif verb==b'DATA' and authenticated:
                    reply(b'354 message follows');parts=[];size=0
                    while True:
                        chunk=stream.readline(65536)
                        if not chunk: return
                        if chunk==b'.\r\n': break
                        if chunk.startswith(b'..'): chunk=chunk[1:]
                        parts.append(chunk);size+=len(chunk)
                        if size>17*1024*1024: return
                    with self.server.lock: self.server.messages.append(b''.join(parts))
                    reply(b'250 accepted by local TEST SINK, not a real inbox')
                elif verb==b'QUIT': reply(b'221 goodbye');break
                elif verb in (b'NOOP',b'RSET'): reply(b'250 OK')
                else: reply(b'500 unsupported')
        except (OSError,ssl.SSLError): pass
        finally:
            try: stream.close();connection.close()
            except OSError: pass
