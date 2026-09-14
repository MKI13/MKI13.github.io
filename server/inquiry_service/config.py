"""Explicit, fail-closed deployment configuration. Secrets are read from mounted files."""
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit
import os
import re

RECIPIENT = 'info@ef-sinn.de'
MAILBOX = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,63}$")


def secret_file(name: str, minimum: int) -> bytes:
    path = os.environ.get(name, '')
    if not path:
        raise ValueError(f'{name} is required (a mounted file, never a browser secret)')
    data = Path(path).read_bytes().strip()
    if len(data) < minimum:
        raise ValueError(f'{name} is missing or too short')
    return data


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    secret: bytes
    origins: tuple[str, ...]
    host: str
    smtp_user: str
    smtp_password: str
    smtp_host: str = 'smtp.protonmail.ch'
    smtp_port: int = 587
    enabled: bool = False
    trust_proxy: bool = False
    max_file_bytes: int = 4 * 1024 * 1024
    max_total_bytes: int = 10 * 1024 * 1024
    max_files: int = 5
    max_pixels: int = 16_000_000
    max_queue_bytes: int = 128 * 1024 * 1024
    max_queue_count: int = 100
    submit_limit: int = 8
    global_limit: int = 40
    challenge_limit: int = 60
    smtp_timeout: int = 15
    min_challenge_age: int = 2

    @classmethod
    def from_env(cls):
        public = urlsplit(os.environ.get('INQUIRY_PUBLIC_URL', ''))
        if public.scheme != 'https' or not public.hostname or public.username or public.path not in ('', '/') or public.query or public.fragment:
            raise ValueError('INQUIRY_PUBLIC_URL must be the dedicated HTTPS backend origin')
        origins = tuple(x.strip() for x in os.environ.get('INQUIRY_ALLOWED_ORIGINS', 'https://www.ef-sinn.de,https://ef-sinn.de').split(','))
        for value in origins:
            parsed = urlsplit(value)
            if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.path or parsed.query or parsed.fragment:
                raise ValueError('Allowed origins must be explicit HTTPS origins')
        username = os.environ.get('SMTP_USERNAME', '')
        if not MAILBOX.fullmatch(username) or not username.lower().endswith('@ef-sinn.de'):
            raise ValueError('SMTP_USERNAME must be an EF-Sinn custom-domain mailbox')
        enabled = os.environ.get('INQUIRY_ENABLED', '0') == '1'
        cfg = cls(
            data_dir=Path(os.environ.get('INQUIRY_DATA_DIR', '/var/lib/ef-sinn-inquiry')).resolve(),
            secret=secret_file('INQUIRY_SECRET_FILE', 32), origins=origins,
            host=public.netloc, smtp_user=username,
            smtp_password=secret_file('SMTP_PASSWORD_FILE', 12).decode(),
            enabled=enabled, trust_proxy=os.environ.get('INQUIRY_TRUST_PROXY', '0') == '1',
        )
        return cfg
