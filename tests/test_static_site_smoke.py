import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urlparse

ROOT = Path(__file__).resolve().parents[1]
MASKED_TEL = 'tel:+491' + '****' + '6451'
MASKED_PHONE = '+491' + '****' + '6451'
DIALABLE_TEL = 'tel:+' + '49' + '176' + '8718' + '6451'

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


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title_text = []
        self.in_title = False
        self.h1_texts = []
        self.in_h1 = False
        self.meta_descriptions = []
        self.links = []
        self.images = []
        self.ids = set()
        self.legal_copy_depth = None
        self.legal_copy_text = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == 'title':
            self.in_title = True
        if tag == 'h1':
            self.in_h1 = True
        if 'id' in attr:
            self.ids.add(attr['id'])
        name = str(attr.get('name') or '')
        if tag == 'meta' and name.lower() == 'description':
            self.meta_descriptions.append(str(attr.get('content') or '').strip())
        if tag == 'a' and attr.get('href'):
            self.links.append(str(attr['href']))
        if tag == 'img' and attr.get('src'):
            self.images.append(str(attr['src']))
        classes = set(str(attr.get('class') or '').split())
        if tag == 'div' and 'legal-copy' in classes and self.legal_copy_depth is None:
            self.legal_copy_depth = 1
        elif self.legal_copy_depth is not None:
            self.legal_copy_depth += 1

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        if tag == 'h1':
            self.in_h1 = False
        if self.legal_copy_depth is not None:
            self.legal_copy_depth -= 1
            if self.legal_copy_depth <= 0:
                self.legal_copy_depth = None

    def handle_data(self, data):
        text = data.strip()
        if self.in_title and text:
            self.title_text.append(text)
        if self.in_h1 and text:
            self.h1_texts.append(text)
        if self.legal_copy_depth is not None and text:
            self.legal_copy_text.append(text)


def parse_page(page):
    parser = PageParser()
    parser.feed((ROOT / page).read_text(encoding='utf-8', errors='ignore'))
    return parser


def is_local_asset(url):
    parsed = urlparse(url)
    return not parsed.scheme and not parsed.netloc and not url.startswith(('mailto:', 'tel:', '#'))


class StaticSiteSmokeTest(unittest.TestCase):
    def test_main_pages_have_title_description_and_single_h1(self):
        for page in MAIN_PAGES:
            with self.subTest(page=page):
                parser = parse_page(page)
                self.assertTrue(' '.join(parser.title_text).strip(), page)
                self.assertTrue(any(parser.meta_descriptions), page)
                self.assertEqual(1, len([h for h in parser.h1_texts if h.strip()]), page)

    def test_internal_links_anchors_and_images_resolve(self):
        for page in MAIN_PAGES:
            parser = parse_page(page)
            page_dir = (ROOT / page).parent
            for href in parser.links:
                href_without_fragment, fragment = urldefrag(href)
                if not is_local_asset(href):
                    continue
                parsed_href = urlparse(href_without_fragment)
                href_path = parsed_href.path or page
                target_path = (page_dir / href_path).resolve()
                if target_path.is_dir():
                    target_path = target_path / 'index.html'
                self.assertTrue(target_path.exists(), f'{page} links missing target {href}')
                if fragment and target_path.suffix == '.html':
                    target_parser = parse_page(str(target_path.relative_to(ROOT)))
                    self.assertIn(fragment, target_parser.ids, f'{page} links missing anchor {href}')
            for src in parser.images:
                if not is_local_asset(src):
                    continue
                target_path = (page_dir / urldefrag(src)[0]).resolve()
                self.assertTrue(target_path.exists(), f'{page} references missing image {src}')

    def test_legal_pages_have_static_no_javascript_fallback_text(self):
        required = {
            'impressum.html': ['Marios Karampas', 'Schmorellstraße', 'info@ef-sinn.de'],
            'datenschutz.html': ['Datenschutz auf einen Blick', 'Verantwortlich', 'Keine Cookies'],
        }
        for page, snippets in required.items():
            with self.subTest(page=page):
                parser = parse_page(page)
                legal_text = ' '.join(parser.legal_copy_text)
                self.assertGreater(len(legal_text), 300, page)
                for snippet in snippets:
                    self.assertIn(snippet, legal_text)

    def test_navigation_exposes_services_and_references_language(self):
        page_expectations = {
            page: ('../index.html#leistungen' if page.startswith('leistungen/') else 'index.html#leistungen')
            for page in MAIN_PAGES
        }
        for page, services_href in page_expectations.items():
            html = (ROOT / page).read_text(encoding='utf-8', errors='ignore')
            with self.subTest(page=page):
                self.assertIn('data-i18n="nav.services"', html)
                self.assertIn(f'href="{services_href}"', html)
                self.assertIn('data-i18n="nav.portfolio">Referenzen</a>', html)
        de = (ROOT / 'i18n/de.json').read_text(encoding='utf-8')
        self.assertIn('"nav.portfolio": "Referenzen"', de)

    def test_customer_facing_phone_links_are_dialable_and_not_masked(self):
        files = [p for p in ROOT.rglob('*') if p.is_file() and p.suffix in {'.html', '.json', '.js'} and '.git' not in p.parts]
        all_text = '\n'.join(p.read_text(encoding='utf-8', errors='ignore') for p in files)
        self.assertNotIn(MASKED_TEL, all_text)
        self.assertNotIn(MASKED_PHONE, all_text)
        self.assertIn(DIALABLE_TEL, all_text)
        self.assertNotRegex(all_text, r'tel:[^"\s<>]*\*')

    def test_accessibility_skip_links_and_single_main_target(self):
        for page in MAIN_PAGES:
            html = (ROOT / page).read_text(encoding='utf-8', errors='ignore')
            with self.subTest(page=page):
                self.assertIn('class="skip-link"', html)
                self.assertIn('href="#main-content"', html)
                self.assertEqual(1, html.count('id="main-content"'))

    def test_no_keyword_stuffing_or_outdated_legal_references(self):
        files = [p for p in ROOT.rglob('*') if p.is_file() and p.suffix in {'.html', '.json'} and '.git' not in p.parts]
        all_text = '\n'.join(p.read_text(encoding='utf-8', errors='ignore') for p in files)
        self.assertNotIn('<meta name="keywords"', all_text)
        self.assertNotIn('§ 5 TMG', all_text)
        self.assertNotIn('§ 7 Abs. 1 TMG', all_text)
        self.assertIn('Angaben nach § 5 DDG', all_text)


if __name__ == '__main__':
    unittest.main()
