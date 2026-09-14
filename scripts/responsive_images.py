"""Emit responsive sizes from actual CSS layouts, preserving image assets and markup."""
from html.parser import HTMLParser
from pathlib import Path
import re

LAYOUT_SIZES = {
    'service-gallery': '(max-width: 768px) calc(100vw - 2rem), (max-width: 900px) calc((100vw - 6rem) / 2), (max-width: 1200px) calc((100vw - 8rem) / 3), 358px',
    'case-grid': '(max-width: 768px) calc(100vw - 2rem), (max-width: 900px) calc(100vw - 4rem), (max-width: 1200px) calc((100vw - 6rem) / 3), 368px',
    'half-content': '(max-width: 768px) calc(100vw - 2rem), (max-width: 1200px) calc((100vw - 8rem) / 2), 536px',
    'service-detail': '(max-width: 768px) calc(100vw - 2rem), (max-width: 1200px) calc(40vw - 3.2rem), 429px',
    'project-single': '(max-width: 768px) calc(100vw - 5rem), (max-width: 1200px) calc(100vw - 8rem), 1072px',
    'project-double': '(max-width: 768px) calc(100vw - 5rem), (max-width: 1200px) calc((100vw - 8.5rem) / 2), 532px',
    'project-triple': '(max-width: 768px) calc(100vw - 5rem), (max-width: 1200px) calc((100vw - 9rem) / 3), 352px',
    'full-content': '(max-width: 768px) calc(100vw - 2rem), (max-width: 1200px) calc(100vw - 4rem), 1136px',
}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

class ImageLayouts(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.stack = []
        self.replacements = []
        self.offsets = [0]
        for line in text.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.feed(text)

    def layout(self):
        contexts = [set(attrs.get('class', '').split()) for _, attrs in self.stack]
        for classes in reversed(contexts):
            if 'service-gallery-grid' in classes:
                return 'service-gallery'
            if 'portfolio-case-grid' in classes:
                return 'case-grid'
            if 'project-gallery-grid' in classes:
                if 'triple' in classes:
                    return 'project-triple'
                return 'project-double' if classes & {'double', 'quad'} else 'project-single'
            if classes & {'intro-grid', 'about-grid'}:
                return 'half-content'
            if 'service-detail-grid' in classes:
                return 'service-detail'
        return 'full-content'

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'img' and attrs.get('srcset') and not re.fullmatch(r'\d+(?:\.\d+)?px', attrs.get('sizes', '')):
            layout = self.layout()
            original = self.get_starttag_text()
            updated = re.sub(r'\s(?:sizes|data-image-layout)="[^"]*"', '', original)
            sizes = ('auto, ' if attrs.get('loading') == 'lazy' else '') + LAYOUT_SIZES[layout]
            updated = re.sub(r'\s*/?>$', ' sizes="' + sizes + '" data-image-layout="' + layout + '">', updated)
            line, column = self.getpos()
            start = self.offsets[line - 1] + column
            self.replacements.append((start, start + len(original), updated))
        if tag not in VOID:
            self.stack.append((tag, attrs))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


def rewrite_sizes(text):
    parser = ImageLayouts(text)
    for start, end, replacement in reversed(parser.replacements):
        text = text[:start] + replacement + text[end:]
    return text


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    pages = sorted(root.glob('*.html')) + sorted((root / 'leistungen').glob('*.html'))
    for page in pages:
        page.write_text(rewrite_sizes(page.read_text()))
    print('Layout-specific image sizes updated in', len(pages), 'pages.')
