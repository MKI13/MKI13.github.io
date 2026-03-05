#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N = ROOT / "i18n"
SOURCE_LANG = "de"
TARGETS = ["en", "fr", "el", "it", "es", "de-AT"]
MODEL = "glm-5:cloud"


def load(lang):
    p = I18N / f"{lang}.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8") or "{}")


def save(lang, data):
    p = I18N / f"{lang}.json"
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def translate_batch(lang, pairs):
    # pairs: {key: german_text}
    payload = json.dumps(pairs, ensure_ascii=False)
    prompt = (
        f"Translate this JSON values from German to {lang}. Keep keys unchanged. "
        "Return ONLY valid JSON object, no markdown, no comments.\n" + payload
    )
    cmd = ["ollama", "run", MODEL, prompt]
    out = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT, timeout=300)
    # find first { ... }
    start = out.find("{")
    end = out.rfind("}")
    if start == -1 or end == -1:
        raise RuntimeError(f"No JSON in model output for {lang}: {out[:300]}")
    return json.loads(out[start:end+1])


def main():
    src = load(SOURCE_LANG)
    if not src:
        print("No de.json content found")
        return 1

    for lang in TARGETS:
        cur = load(lang)
        missing = {k: v for k, v in src.items() if k not in cur or not cur.get(k)}
        if not missing:
            print(f"{lang}: up-to-date")
            continue

        print(f"{lang}: translating {len(missing)} keys...")
        try:
            translated = translate_batch(lang, missing)
        except Exception as e:
            print(f"{lang}: translation failed: {e}")
            continue

        for k, v in missing.items():
            cur[k] = translated.get(k, v)
        save(lang, cur)
        print(f"{lang}: updated")

    return 0


if __name__ == "__main__":
    sys.exit(main())
