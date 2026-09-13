#!/usr/bin/env python3
"""Generate responsive WebP assets from existing local photographs; retain originals."""
from pathlib import Path
import hashlib, json, os, re
from PIL import Image, ImageOps
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/optimized'
PAGES = sorted(ROOT.glob('*.html')) + sorted((ROOT / 'leistungen').glob('*.html'))
IMAGE = re.compile(r'<img\b[^>]*>', re.I | re.S)
SOURCE = re.compile(r'\bsrc="([^"]+)"')
BACKGROUND = re.compile(r"background-image:\s*url\(['\"]?([^)'\"]+)['\"]?\)")
def source_path(page, value):
    if ':' in value or value.startswith('//'):
        return None
    path = (page.parent / value).resolve()
    if ROOT not in path.parents or path.suffix.lower() not in {'.jpg', '.jpeg', '.png'}:
        return None
    if not path.is_file():
        raise FileNotFoundError(path)
    return path

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / 'manifest.json'
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    sources = {ROOT / key for key in previous.get('images', {})}
    for page in PAGES:
        text = page.read_text()
        for tag in IMAGE.findall(text):
            match = SOURCE.search(tag)
            if match:
                source = source_path(page, match[1])
                if source:
                    sources.add(source)
        for match in BACKGROUND.finditer(text):
            source = source_path(page, match[1])
            if source:
                sources.add(source)
    images = {}
    for source in sorted(sources):
        relative = source.relative_to(ROOT).as_posix()
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        icon = '/icons/' in relative or 'logo-ef-sinn' in relative
        with Image.open(source) as original:
            image = ImageOps.exif_transpose(original)
            image = image.convert('RGBA' if 'A' in image.getbands() else 'RGB')
            width, height = image.size
            targets = sorted({min(width, n) for n in ([64, 128, 256] if icon else [480, 960, 1600])})
            variants = []
            stem = re.sub(r'[^a-z0-9-]', '-', source.stem.lower()) + '-' + digest[:8]
            for target in targets:
                resized = image.resize((target, max(1, round(height * target / width))), Image.Resampling.LANCZOS)
                output = OUT / (stem + '-' + str(target) + '.webp')
                resized.save(output, 'WEBP', quality=85, method=6, icc_profile=original.info.get('icc_profile', b''))
                variants.append({'width': target, 'height': resized.height, 'path': output.relative_to(ROOT).as_posix(), 'bytes': output.stat().st_size})
        images[relative] = {'sha256': digest, 'original_bytes': source.stat().st_size, 'width': width, 'height': height, 'icon': icon, 'variants': variants}
    for page in PAGES:
        def replace_image(match):
            tag = match[0]
            source_match = SOURCE.search(tag)
            source = source_path(page, source_match[1]) if source_match else None
            if not source:
                return tag
            info = images[source.relative_to(ROOT).as_posix()]
            variants = info['variants']
            selected = next((v for v in variants if v['width'] >= (128 if info['icon'] else 960)), variants[-1])
            url = lambda variant: Path(os.path.relpath(ROOT / variant['path'], page.parent)).as_posix()
            tag = tag[:source_match.start(1)] + url(selected) + tag[source_match.end(1):]
            attributes = ['srcset="' + ', '.join(url(v) + ' ' + str(v['width']) + 'w' for v in variants) + '"']
            if info['icon']:
                fixed = re.search(r'\bwidth="(\d+)"', tag)
                size = int(fixed[1]) if fixed else round(50 * info['width'] / info['height'])
                attributes.append('sizes="' + str(size) + 'px"')
            else:
                attributes.append('sizes="(max-width: 760px) 100vw, 80vw"')
            for name, value in [('width', info['width']), ('height', info['height']), ('decoding', 'async')]:
                if not re.search(r'\b' + name + '=', tag):
                    attributes.append(name + '="' + str(value) + '"')
            if not info['icon'] and not re.search(r'\bloading=', tag):
                attributes.append('loading="lazy"')
            return re.sub(r'\s*/?>$', ' ' + ' '.join(attributes) + '>', tag)
        def replace_background(match):
            source = source_path(page, match[1])
            if not source:
                return match[0]
            variant = images[source.relative_to(ROOT).as_posix()]['variants'][-1]
            url = Path(os.path.relpath(ROOT / variant['path'], page.parent)).as_posix()
            return "background-image: url('" + url + "')"
        text = IMAGE.sub(replace_image, page.read_text())
        page.write_text(BACKGROUND.sub(replace_background, text))
    manifest_path.write_text(json.dumps({'generator': 'scripts/optimize_images.py', 'quality': 85, 'originals_retained': True, 'images': images}, ensure_ascii=False, indent=2) + '\n')
    original_bytes = sum(i['original_bytes'] for i in images.values())
    webp_bytes = sum(i['variants'][-1]['bytes'] for i in images.values())
    print(json.dumps({'images': len(images), 'variants': sum(len(i['variants']) for i in images.values()), 'original_bytes': original_bytes, 'largest_webp_bytes': webp_bytes, 'reduction_percent': round((1-webp_bytes/original_bytes)*100, 1)}, indent=2))
if __name__ == '__main__':
    main()
