import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LANGS = ['de', 'en', 'fr', 'el', 'it', 'es', 'de-AT']
NON_DE_LANGS = ['en', 'fr', 'el', 'it', 'es', 'de-AT']
TRANSLATED_NON_GERMAN = ['en', 'fr', 'el', 'it', 'es']
LEGAL_KEYS = [
    'legal.imprint.contact.title',
    'legal.imprint.professional.title',
    'legal.imprint.tax.title',
    'legal.imprint.liability_content.title',
    'legal.imprint.copyright.text',
    'legal.privacy.collection.title',
    'legal.privacy.hosting.title',
    'legal.privacy.controller.title',
    'legal.privacy.contact_assistant.title',
    'legal.privacy.cookies.title',
]
GERMAN_RESIDUE = re.compile(r'\b(Schreiner|Datenschutz|Impressum|Kontakt|Telefon|Berufsbezeichnung|Steuerliche|Haftung|Urheberrecht|Datenerfassung|Aufsichtsbehörde|Anfrage|Keine Cookies)\b')


def load(lang):
    return json.loads((ROOT / f'i18n/{lang}.json').read_text(encoding='utf-8'))


class GrowthPackageTest(unittest.TestCase):
    def test_legal_pages_are_part_of_i18n_completeness_audit(self):
        audit = (ROOT / 'tests/test_i18n_completeness.py').read_text(encoding='utf-8')
        self.assertIn("'impressum.html'", audit)
        self.assertIn("'datenschutz.html'", audit)

    def test_legal_imprint_and_privacy_keys_are_translated_for_every_language(self):
        de = load('de')
        for key in LEGAL_KEYS:
            self.assertIn(key, de)
            self.assertTrue(de[key].strip(), key)
        for lang in NON_DE_LANGS:
            data = load(lang)
            missing = [key for key in LEGAL_KEYS if not data.get(key)]
            unchanged = [key for key in LEGAL_KEYS if data.get(key) == de.get(key)]
            residue = [key for key in LEGAL_KEYS if lang in TRANSLATED_NON_GERMAN and GERMAN_RESIDUE.search(data.get(key, ''))]
            self.assertEqual([], missing, f'{lang} missing legal keys')
            self.assertEqual([], unchanged, f'{lang} unchanged legal keys')
            self.assertEqual([], residue, f'{lang} German residue in legal keys')

    def test_language_buttons_have_localized_accessible_names(self):
        script = (ROOT / 'assets/js/i18n.js').read_text(encoding='utf-8')
        self.assertIn('labelKey', script)
        self.assertIn('lang.de.label', script)
        self.assertNotIn("'Language '+l.code", script)
        for lang in LANGS:
            data = load(lang)
            for code in LANGS:
                key = f'lang.{code}.label'
                self.assertIn(key, data)
                self.assertNotRegex(data[key], r'^Language\s')

    def test_homepage_has_targeted_hero_small_jobs_trust_and_case_studies(self):
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        self.assertIn('home.smalljobs.title', html)
        self.assertIn('home.trust.title', html)
        self.assertIn('portfolio-case-study', html)
        de = load('de')
        self.assertIn('Schreiner in München & Unterhaching', de['home.hero.title'])
        self.assertIn('Maßmöbel', de['home.hero.title'])
        self.assertIn('Einbauschränke', de['home.hero.title'])
        self.assertIn('Küchen', de['home.hero.title'])
        self.assertIn('Parkett', de['home.hero.title'])
        self.assertIn('Kleine Schreinerarbeiten', de['home.smalljobs.title'])
        self.assertIn('Fotos', de['home.smalljobs.text'])


    def test_critic_blockers_are_fixed_for_legal_phone_and_a11y(self):
        files = [p for p in ROOT.rglob('*') if p.is_file() and p.suffix in {'.html', '.json', '.js'}]
        all_text = '\n'.join(p.read_text(encoding='utf-8') for p in files)
        self.assertNotIn('tel:+491****6451', all_text)
        self.assertNotIn('+491****6451', all_text)
        self.assertIn('tel:+4917687186451', all_text)
        script = (ROOT / 'assets/js/i18n.js').read_text(encoding='utf-8')
        self.assertIn('aria-pressed', script)
        self.assertIn('data-i18n-content', script)
        for page in ['impressum.html', 'datenschutz.html']:
            html = (ROOT / page).read_text(encoding='utf-8')
            self.assertIn('data-i18n-content', html)
            self.assertRegex(html, r'<title data-i18n="legal\.(imprint|privacy)\.pageTitle">')

    def test_legal_body_language_residue_removed_after_critic(self):
        english_phrases = ['This notice explains', 'The website operator is responsible', 'You provide data when', 'Consumer dispute resolution']
        for lang in ['de', 'de-AT', 'fr', 'it', 'es', 'el']:
            data = load(lang)
            body = data['legal.privacy.body'] + data['legal.imprint.body']
            for phrase in english_phrases:
                self.assertNotIn(phrase, body, f'{lang} still contains English legal residue: {phrase}')
        for lang in LANGS:
            data = load(lang)
            self.assertIn('legal.imprint.pageTitle', data)
            self.assertIn('legal.privacy.pageTitle', data)
            self.assertIn('legal.imprint.metaDescription', data)
            self.assertIn('legal.privacy.metaDescription', data)

    def test_design_styles_include_premium_sections(self):
        css = (ROOT / 'styles.css').read_text(encoding='utf-8')
        self.assertIn('.small-jobs-section', css)
        self.assertIn('.premium-trust-section', css)
        self.assertIn('.portfolio-case-study', css)
        self.assertIn('letter-spacing', css[css.index('.premium-trust-section'):])


if __name__ == '__main__':
    unittest.main()
