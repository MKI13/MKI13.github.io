import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN_PAGES = [
    'index.html',
    'about.html',
    'contact.html',
    'portfolio.html',
    'schreiner-muenchen.html',
    '404.html',
    'impressum.html',
    'datenschutz.html',
    'leistungen/innenausbau.html',
    'leistungen/kuechen.html',
    'leistungen/moebelbau.html',
    'leistungen/restaurierung.html',
    'leistungen/terrassen.html',
    'leistungen/treppen.html',
]
TRANSLATED_LANGS = ['en', 'fr', 'el', 'it', 'es']
GERMAN_SIGNAL = re.compile(
    r'[äöüÄÖÜß]|\b(und|oder|für|mit|Ihre|Ihr|Sie|Unsere|Leistungen|Kontakt|Anfrage|Beratung|München|Schreiner|Holz|Küche|Küchen|Möbel|Maß|Parkett|Treppen|Werkstatt|Telefon|Direkt|anrufen|Jetzt|Mehr erfahren|Vorherige|Nächste|Projekt|Fotos|Kostenlose|Erstberatung|Schnellkontakt|Start|Über uns|Aufmaß|Fertigung|Montage|Referenzen|ansehen|Seite|gefunden|verschoben|Zurück|Erst|anschauen|gemeinsam|planen|Räume|bleiben|Sichtbare|Referenzbilder|Startseite|Standorte|erreichbar|besprechen|Schließen)\b',
    re.IGNORECASE,
)
NON_TRANSLATED_LITERAL = re.compile(
    r'^(\+|\d+$|ef-sinn|Marios|Karampas|München & Unterhaching|Schmorellstraße.*|Germeringer Weg.*|81245 München|82008 Unterhaching|DE\d+|https?://|info@|[·•✓✦\s]+)$',
    re.IGNORECASE,
)


class VisibleGermanParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.items = []

    def handle_starttag(self, tag, attrs):
        attr_map = dict(attrs)
        has_i18n = any(parent_i18n for _, parent_i18n in self.stack) or 'data-i18n' in attr_map
        self.stack.append((tag, has_i18n))
        for attr in ['aria-label', 'title', 'placeholder', 'alt', 'value']:
            if attr not in attr_map:
                continue
            i18n_attr = 'data-i18n-aria-label' if attr == 'aria-label' else f'data-i18n-{attr}'
            if 'data-i18n' in attr_map or i18n_attr in attr_map:
                continue
            value = normalize(attr_map[attr])
            if should_translate(value):
                self.items.append((tag, attr, value))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                self.stack = self.stack[:index]
                break

    def handle_data(self, data):
        if not self.stack:
            return
        tag, has_i18n = self.stack[-1]
        if tag in {'script', 'style', 'noscript', 'svg', 'path'} or has_i18n:
            return
        value = normalize(data)
        if should_translate(value):
            self.items.append((tag, '', value))


def normalize(value: object) -> str:
    return re.sub(r'\s+', ' ', str(value or '')).strip()


def should_translate(value: str) -> bool:
    return bool(value and GERMAN_SIGNAL.search(value) and not NON_TRANSLATED_LITERAL.match(value))


def hardcoded_german_literals():
    seen = set()
    literals = []
    for page in MAIN_PAGES:
        parser = VisibleGermanParser()
        parser.feed((ROOT / page).read_text(encoding='utf-8', errors='ignore'))
        for tag, attr, value in parser.items:
            if value not in seen:
                seen.add(value)
                literals.append((page, tag, attr, value))
    return literals


class I18nCompletenessTest(unittest.TestCase):
    def test_hardcoded_main_page_german_has_runtime_translation_source(self):
        de = json.loads((ROOT / 'i18n/de.json').read_text(encoding='utf-8'))
        reverse = {normalize(value): key for key, value in de.items() if isinstance(value, str)}
        missing = [f'{page} <{tag}> {attr or "text"}: {value}' for page, tag, attr, value in hardcoded_german_literals() if value not in reverse]
        self.assertEqual([], missing)

    def test_runtime_fallback_translates_untagged_text_and_attributes(self):
        script = (ROOT / 'assets/js/i18n.js').read_text(encoding='utf-8')
        self.assertIn('loadBaseGerman', script)
        self.assertIn('applyFallbackTranslations', script)
        self.assertIn('data-i18n-fallback-done', script)

    def test_each_non_german_language_has_main_page_fallback_values(self):
        de = json.loads((ROOT / 'i18n/de.json').read_text(encoding='utf-8'))
        reverse = {normalize(value): key for key, value in de.items() if isinstance(value, str)}
        source_literals = [value for _, _, _, value in hardcoded_german_literals()]
        for lang in TRANSLATED_LANGS:
            data = json.loads((ROOT / f'i18n/{lang}.json').read_text(encoding='utf-8'))
            missing = []
            unchanged = []
            for source in source_literals:
                key = reverse.get(source)
                if not key or key not in data:
                    missing.append(source)
                    continue
                if should_translate(source) and normalize(data[key]) == source:
                    unchanged.append(source)
            self.assertEqual([], missing, lang)
            self.assertEqual([], unchanged, lang)


if __name__ == '__main__':
    unittest.main()
