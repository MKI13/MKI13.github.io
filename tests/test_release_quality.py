import hashlib
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
ROOT = Path(__file__).resolve().parents[1]
PAGES = list(ROOT.glob('*.html')) + list((ROOT / 'leistungen').glob('*.html'))
class Elements(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.items=[]; self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.items.append((tag,dict(attrs)))
class ReleaseQualityTests(unittest.TestCase):
    def test_no_javascript_form_is_fail_closed(self):
        elements=Elements((ROOT/'contact.html').read_text()).items
        form=next(a for tag,a in elements if tag=='form' and a.get('id')=='inquiry-form')
        button=next(a for tag,a in elements if tag=='button' and a.get('id')=='inq-review')
        self.assertEqual('post',form['method']); self.assertIn('disabled',button)
        self.assertIn('<noscript>',(ROOT/'contact.html').read_text())
    def test_form_has_bounded_validated_fields(self):
        elements=Elements((ROOT/'contact.html').read_text()).items
        fields={a.get('id'):a for tag,a in elements if tag in {'input','textarea'}}
        self.assertIn('required',fields['inq-name']); self.assertIn('required',fields['inq-message'])
        self.assertEqual('10',fields['inq-message']['minlength']); self.assertEqual('5000',fields['inq-message']['maxlength'])
        self.assertEqual('email',fields['inq-email']['type'])
        self.assertIn('inq-measurements',fields); self.assertIn('inq-timeframe',fields)
    def test_inquiry_never_stores_uploads_or_injects_user_html(self):
        js=(ROOT/'assets/js/inquiry.js').read_text()
        for forbidden in ['localStorage','sessionStorage','indexedDB','fetch(','XMLHttpRequest','innerHTML']:
            self.assertNotIn(forbidden,js)
        self.assertIn('mailto:info@ef-sinn.de',js); self.assertIn('encodeURIComponent',js)
        self.assertIn('MAX_MAILTO_LENGTH',js); self.assertIn('reviewText.value',js)
    def test_inquiry_has_one_external_controller_and_all_fallbacks(self):
        html=(ROOT/'contact.html').read_text()
        self.assertEqual(1,html.count('src="assets/js/inquiry.js'))
        for identifier in ['inquiry-preview','inquiry-preview-text','inq-open-email','inq-copy','inq-download','inq-edit','inquiry-status']:
            self.assertEqual(1,html.count('id="'+identifier+'"'),identifier)
        self.assertIn('role="status"',html); self.assertIn('aria-live="polite"',html)
    def test_dynamic_inquiry_strings_exist_in_every_language(self):
        keys=['openEmail','openEmpty','longNote','copied','manualCopy','downloaded','emailOpened','emptyOpened','noScript','measurements.label','timeframe.label']
        for lang in ['de','de-AT','en','fr','el','it','es']:
            data=json.loads((ROOT/f'i18n/{lang}.json').read_text())
            for key in keys:
                self.assertTrue(data.get('contact.inquiry.'+key),lang+': '+key)
    def test_responsive_image_files_and_metadata_exist(self):
        for page in PAGES:
            for tag,attributes in Elements(page.read_text()).items:
                if tag!='img' or 'optimized/' not in attributes.get('src',''):
                    continue
                for key in ['width','height','srcset','sizes','decoding']:
                    self.assertIn(key,attributes,str(page)+': '+key)
                self.assertEqual('async',attributes['decoding'])
                for candidate in attributes['srcset'].split(','):
                    value,descriptor=candidate.strip().rsplit(' ',1)
                    self.assertTrue((page.parent/urlparse(value).path).is_file(),value)
                    self.assertRegex(descriptor,r'^\d+w$')
    def test_image_originals_are_unchanged_and_derivatives_are_bounded(self):
        manifest=json.loads((ROOT/'assets/optimized/manifest.json').read_text())
        self.assertTrue(manifest['originals_retained']); self.assertGreater(len(manifest['images']),50)
        for relative,info in manifest['images'].items():
            source=ROOT/relative
            self.assertEqual(info['sha256'],hashlib.sha256(source.read_bytes()).hexdigest(),relative)
            self.assertEqual(info['original_bytes'],source.stat().st_size)
            for variant in info['variants']:
                file=ROOT/variant['path']; content=file.read_bytes()
                self.assertEqual(b'RIFF',content[:4]); self.assertEqual(b'WEBP',content[8:12])
                self.assertEqual(variant['bytes'],len(content))
                self.assertLessEqual(variant['width'],min(info['width'],256 if info['icon'] else 1600))
    def test_image_budget_improves_without_replacing_reference_content(self):
        images=json.loads((ROOT/'assets/optimized/manifest.json').read_text())['images'].values()
        original=sum(i['original_bytes'] for i in images)
        optimized=sum(i['variants'][-1]['bytes'] for i in images)
        self.assertLess(optimized,original*0.3)
    def test_release_asset_versions_are_consistent(self):
        for page in PAGES:
            html=page.read_text()
            self.assertNotRegex(html,r'(?:styles\.css|assets/js/i18n\.js)\?v=(?!20260913-release)[^"\s]+')
if __name__=='__main__':
    unittest.main()
