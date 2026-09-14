"""Bounded field validation and decode/re-encode of image uploads before persistence."""
import hashlib
import io
import json
import re
import warnings
from dataclasses import dataclass
from email.message import EmailMessage
from email.policy import SMTP
from email.utils import formatdate
from PIL import Image, ImageOps, UnidentifiedImageError
from .config import MAILBOX, RECIPIENT

LANGS = {'de', 'de-AT', 'en', 'fr', 'el', 'it', 'es'}
LIMITS = {'name':120, 'phone':50, 'email':254, 'project':160, 'location':160,
          'measurements':300, 'timeframe':160, 'appointment1':160, 'appointment2':160,
          'message':5000, 'language':5}

class Invalid(Exception):
    def __init__(self, code, status=422, field=None):
        self.code, self.status, self.field = code, status, field
        super().__init__(code)

@dataclass(frozen=True)
class Photo:
    content: bytes
    source_hash: str


def fields_from(form):
    unknown = set(form) - set(LIMITS) - {'challenge', 'website'}
    if unknown or any(len(form.getlist(k)) != 1 for k in form):
        raise Invalid('invalid_fields')
    data = {}
    for key, limit in LIMITS.items():
        value = str(form.get(key, '')).strip()
        if len(value) > limit or '\x00' in value:
            raise Invalid('invalid_field', field=key)
        if key != 'message' and re.search(r'[\x00-\x1f\x7f]', value):
            raise Invalid('invalid_field', field=key)
        if key == 'message' and re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', value):
            raise Invalid('invalid_field', field=key)
        data[key] = value
    if not data['name'] or len(data['message']) < 10 or not data['project']:
        raise Invalid('required_fields')
    email=data['email']
    malformed=False
    if email and MAILBOX.fullmatch(email):
        local,domain=email.rsplit('@',1)
        malformed=(len(local)>64 or local.startswith('.') or local.endswith('.') or '..' in local or
                   any(not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?',label) for label in domain.split('.')))
    if email and (not MAILBOX.fullmatch(email) or malformed):
        raise Invalid('invalid_email', field='email')
    if data['phone'] and (not re.fullmatch(r'[+()0-9 ./-]+', data['phone']) or len(re.sub(r'\D', '', data['phone'])) < 5):
        raise Invalid('invalid_phone', field='phone')
    if not data['email'] and not data['phone']:
        raise Invalid('contact_required')
    if data['language'] not in LANGS:
        raise Invalid('invalid_language')
    return data


def photos_from(files, cfg):
    if set(files) - {'photos'}:
        raise Invalid('invalid_files')
    uploads = files.getlist('photos')
    if len(uploads) > cfg.max_files:
        raise Invalid('too_many_files')
    photos, total = [], 0
    for upload in uploads:
        raw = upload.stream.read(cfg.max_file_bytes + 1)
        total += len(raw)
        if not raw or len(raw) > cfg.max_file_bytes or total > cfg.max_total_bytes:
            raise Invalid('file_size', 413)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error', Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(raw)) as image:
                    if image.format not in {'JPEG', 'PNG', 'WEBP'} or getattr(image, 'n_frames', 1) != 1:
                        raise Invalid('file_type')
                    if image.width * image.height > cfg.max_pixels or image.width < 1 or image.height < 1:
                        raise Invalid('image_dimensions')
                    image.load()
                    image = ImageOps.exif_transpose(image)
                    if image.mode in ('RGBA', 'LA') or 'transparency' in image.info:
                        rgba = image.convert('RGBA')
                        clean = Image.new('RGB', rgba.size, 'white')
                        clean.paste(rgba, mask=rgba.getchannel('A'))
                    else:
                        clean = image.convert('RGB')
                    clean.thumbnail((2000, 2000), Image.Resampling.LANCZOS)
                    out = io.BytesIO()
                    # No EXIF, embedded originals, filenames or active content survive this re-encoding.
                    clean.save(out, format='JPEG', quality=85, optimize=True)
                    if out.tell() > 3 * 1024 * 1024:
                        raise Invalid('file_size', 413)
                    photos.append(Photo(out.getvalue(), hashlib.sha256(raw).hexdigest()))
        except Invalid:
            raise
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
            raise Invalid('file_type') from None
    return photos


def canonical(data, photos):
    return json.dumps({'fields':data, 'photos':[p.source_hash for p in photos]}, sort_keys=True, ensure_ascii=False).encode()


def make_message(data, photos, request_id, cfg):
    msg = EmailMessage(policy=SMTP)
    msg['From'] = cfg.smtp_user
    msg['To'] = RECIPIENT
    if data['email']:
        msg['Reply-To'] = data['email']
    msg['Subject'] = f"EF-Sinn Projektanfrage [{request_id}]: {data['project']}"
    msg['Date'] = formatdate(localtime=False)
    msg['Message-ID'] = f'<{request_id}@ef-sinn.de>'
    labels = [('name','Name'),('phone','Telefon'),('email','E-Mail'),('project','Projektart'),
              ('location','Ort'),('measurements','Maße'),('timeframe','Zeitraum'),
              ('appointment1','Besichtigung 1'),('appointment2','Besichtigung 2'),('language','Sprache')]
    body = f'Website-Anfrage {request_id}\n\n' + '\n'.join(f'{label}: {data[key]}' for key,label in labels)
    body += '\n\nBeschreibung:\n' + data['message'] + '\n'
    msg.set_content(body, cte="quoted-printable")
    for number, photo in enumerate(photos, 1):
        msg.add_attachment(photo.content, maintype='image', subtype='jpeg', filename=f'foto-{number}.jpg')
    raw = msg.as_bytes()
    if len(raw) > 16 * 1024 * 1024:
        raise Invalid('file_size', 413)
    expected = {'body_sha256':hashlib.sha256(body.strip().encode()).hexdigest(),
                'reply_sha256':hashlib.sha256(data['email'].lower().encode()).hexdigest(),
                'photos':[hashlib.sha256(p.content).hexdigest() for p in photos]}
    return raw, json.dumps(expected, sort_keys=True)
