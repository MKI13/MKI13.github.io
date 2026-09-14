import json
import re
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from responsive_images import LAYOUT_SIZES, rewrite_sizes

class Images(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.images=[]; self.duplicate_attributes=[]; self.feed(text)
    def handle_starttag(self, tag, attrs):
        names=[name for name, _ in attrs]
        if len(set(names)) != len(names): self.duplicate_attributes.append(tag)
        if tag=='img': self.images.append(dict(attrs))

class ReviewFollowupTests(unittest.TestCase):
    def test_gallery_uses_container_width_not_global_eighty_viewport(self):
        html='<div class="service-gallery-grid"><div class="gallery-item"><img src="a.webp" srcset="a.webp 480w, b.webp 960w" loading="lazy" sizes="80vw"></div></div>'
        image=Images(rewrite_sizes(html)).images[0]
        self.assertEqual('service-gallery',image['data-image-layout'])
        self.assertEqual('auto, '+LAYOUT_SIZES['service-gallery'],image['sizes'])
        self.assertNotIn('80vw',image['sizes'])
    def test_eager_image_uses_explicit_layout_without_invalid_auto(self):
        html='<div class="portfolio-case-grid"><img src="a.webp" srcset="a.webp 480w" sizes="80vw"></div>'
        image=Images(rewrite_sizes(html)).images[0]
        self.assertEqual(LAYOUT_SIZES['case-grid'],image['sizes'])
        self.assertFalse(image['sizes'].startswith('auto'))
    def test_fixed_icon_size_is_preserved(self):
        html='<img src="icon.webp" srcset="icon.webp 64w" sizes="48px" alt="Icon">'
        self.assertEqual(html,rewrite_sizes(html))
    def test_nearest_layout_wins_and_project_columns_are_distinguished(self):
        for css_class,layout in [('single','project-single'),('double','project-double'),('triple','project-triple'),('quad','project-double')]:
            html=f'<div class="service-gallery-grid"><div class="project-gallery-grid {css_class}"><img src="a.webp" srcset="a.webp 480w" sizes="80vw"></div></div>'
            self.assertEqual(layout,Images(rewrite_sizes(html)).images[0]['data-image-layout'])
    def test_repeated_updates_are_idempotent_with_unicode_and_multiline_markup(self):
        html='<p>Maßmöbel für München 🪵</p>\n<div class="service-gallery-grid">\n<img src="a.webp"\n srcset="a.webp 480w" sizes="80vw" alt="Größe &amp; Maße" loading="lazy">\n</div>'
        first=rewrite_sizes(html)
        self.assertEqual(first,rewrite_sizes(first))
        self.assertIn('Maßmöbel für München 🪵',first)
        self.assertIn('alt="Größe &amp; Maße"',first)
    def test_every_committed_page_already_has_current_sizes(self):
        for path in list(ROOT.glob('*.html'))+list((ROOT/'leistungen').glob('*.html')):
            text=path.read_text()
            self.assertEqual(text,rewrite_sizes(text),str(path))
            self.assertNotIn('80vw',text)
            self.assertEqual([],Images(text).duplicate_attributes,str(path))
    def test_all_locales_describe_preview_and_explicit_handoff(self):
        words={
            'de':['Vorschau','Zwischenablage','Textdatei','E-Mail selbst versenden'],
            'de-AT':['Vorschau','Zwischenablage','Textdatei','E-Mail selbst versenden'],
            'en':['preview','clipboard','text file','send the email yourself'],
            'fr':['aperçu','presse-papiers','fichier texte','envoyez vous-même'],
            'el':['προεπισκόπηση','πρόχειρο','αρχείο κειμένου','στείλετε οι ίδιοι'],
            'it':['anteprima','appunti','file di testo','invia personalmente'],
            'es':['vista previa','portapapeles','archivo de texto','envía personalmente'],
        }
        for lang,terms in words.items():
            body=json.loads((ROOT/f'i18n/{lang}.json').read_text())['legal.privacy.body']
            for term in terms: self.assertIn(term,body,lang+': '+term)
            self.assertNotIn('Beim Absenden öffnet sich',body)
    def test_static_privacy_fallback_matches_german_dictionary(self):
        html=(ROOT/'datenschutz.html').read_text()
        match=re.search(r'<div class="legal-copy" data-i18n="legal.privacy.body">(.*?)</div>',html,re.S)
        self.assertIsNotNone(match)
        data=json.loads((ROOT/'i18n/de.json').read_text())
        self.assertEqual(data['legal.privacy.body'],match[1])
    def test_image_pipeline_applies_layout_sizes_on_every_run(self):
        source=(ROOT/'scripts/optimize_images.py').read_text()
        self.assertIn('from responsive_images import rewrite_sizes',source)
        self.assertIn('page.write_text(rewrite_sizes(',source)
        self.assertNotIn('80vw',source)

if __name__=='__main__': unittest.main()
