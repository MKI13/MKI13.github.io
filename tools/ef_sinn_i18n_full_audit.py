#!/usr/bin/env python3
"""Browser-level EF-Sinn i18n audit for visible text and common UI attributes.

Checks that when a non-German language is selected, visible text/labels/alt/aria/title/
placeholder/value do not remain as German source strings that have translations.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    "index.html",
    "about.html",
    "contact.html",
    "portfolio.html",
    "schreiner-muenchen.html",
    "404.html",
    "leistungen/innenausbau.html",
    "leistungen/kuechen.html",
    "leistungen/moebelbau.html",
    "leistungen/restaurierung.html",
    "leistungen/terrassen.html",
    "leistungen/treppen.html",
]
LANGS = ["en", "fr", "el", "it", "es"]
ATTRS = ["aria-label", "title", "placeholder", "alt", "value"]
GERMAN_SIGNAL = re.compile(
    r"[äöüÄÖÜß]|\b(und|oder|für|mit|Ihre|Ihr|Sie|Unsere|Leistungen|Kontakt|Anfrage|Beratung|"
    r"Schreiner|Schreinerarbeiten|Holz|Küche|Küchen|Möbel|Maß|Parkett|Treppen|Werkstatt|Telefon|"
    r"Direkt|anrufen|Jetzt|Mehr erfahren|Vorherige|Nächste|Projekt|Fotos|Kostenlose|Erstberatung|"
    r"Schnellkontakt|Start|Über uns|Aufmaß|Fertigung|Montage|Referenzen|ansehen|Seite|gefunden|"
    r"verschoben|Zurück|Persönliche|Maßgefertigt|Saubere|Planung|Antwort|Stunden|Beschreibung|"
    r"Einschätzung|reichen|reicht|mehr|Beratung|Erst|anschauen|gemeinsam|planen|Räume|bleiben|"
    r"Sichtbare|Referenzbilder|Startseite|Standorte|erreichbar|Projekt|besprechen|Schließen)\b",
    re.IGNORECASE,
)
ALLOWED_LITERAL = re.compile(
    r"^(\+|\d+$|ef-sinn|Marios|Karampas|München|Munich|Múnich|Monaco|Μόναχο|München & Unterhaching|"
    r"Schmorellstraße.*|Germeringer Weg.*|81245 München|82008 Unterhaching|DE\d+|https?://|info@|"
    r"[·•✓✦\s]+)$",
    re.IGNORECASE,
)

JS_COLLECT = r"""
const attrs = arguments[0];
function norm(s){return String(s||'').replace(/\s+/g,' ').trim();}
function pathFor(el){
  if(!el || !el.tagName) return '';
  let out=[];
  while(el && el.nodeType===1 && out.length<5){
    let part=el.tagName.toLowerCase();
    if(el.id) part += '#'+el.id;
    else if(el.className && typeof el.className === 'string') part += '.'+el.className.trim().split(/\s+/).slice(0,2).join('.');
    out.unshift(part);
    el=el.parentElement;
  }
  return out.join(' > ');
}
const items=[];
const walker=document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {acceptNode(node){
  const p=node.parentElement;
  if(!p) return NodeFilter.FILTER_REJECT;
  const tag=p.tagName;
  if(['SCRIPT','STYLE','NOSCRIPT','SVG'].includes(tag)) return NodeFilter.FILTER_REJECT;
  const v=norm(node.nodeValue);
  if(!v) return NodeFilter.FILTER_REJECT;
  return NodeFilter.FILTER_ACCEPT;
}});
while(walker.nextNode()){
  const n=walker.currentNode;
  items.push({kind:'text', tag:n.parentElement.tagName.toLowerCase(), path:pathFor(n.parentElement), value:norm(n.nodeValue)});
}
for(const el of Array.from(document.querySelectorAll('*'))){
  for(const attr of attrs){
    if(!el.hasAttribute(attr)) continue;
    const value=norm(el.getAttribute(attr));
    if(value) items.push({kind:'attr', attr, tag:el.tagName.toLowerCase(), path:pathFor(el), value});
  }
}
return {url: location.href, lang: document.documentElement.lang, title: document.title, fallback: document.documentElement.getAttribute('data-i18n-fallback-done'), items};
"""


def norm(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def load_dicts() -> dict[str, dict[str, str]]:
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "i18n").glob("*.json")}


def should_flag_signal(value: str) -> bool:
    if not value or is_allowed_literal(value):
        return False
    return bool(GERMAN_SIGNAL.search(value))


def is_allowed_literal(value: str) -> bool:
    value = norm(value)
    if not value:
        return True
    if value.startswith('+') or '@' in value or value.startswith('http://') or value.startswith('https://'):
        return True
    if value in {'Marios Karampas', 'Weßling / Starnberg', 'Portfolio', 'Breadcrumb', 'Navigation',
                 'Schreiner', 'Tischler', 'Unterhaching', 'Garapa', 'Cumaru', 'Greenwood',
                 'Material', 'Optional'} or value.startswith('Language '):
        return True
    return bool(ALLOWED_LITERAL.match(value))


def audit(base_url: str, pages: list[str], langs: list[str], timeout: float) -> dict:
    dictionaries = load_dicts()
    de = dictionaries["de"]
    de_values: dict[str, str] = {}
    for key, value in de.items():
        if isinstance(value, str):
            de_values[norm(value)] = key

    options = Options()
    firefox_binary = Path("/snap/firefox/current/usr/lib/firefox/firefox")
    if firefox_binary.exists():
        options.binary_location = str(firefox_binary)
    options.add_argument("-headless")
    options.set_preference("intl.accept_languages", "en-US,en")
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(393, 873)
    try:
        all_results = []
        german_page_values = {}
        for page in pages:
            url = urljoin(base_url.rstrip("/") + "/", page) + f"?i18n_audit_de={int(time.time()*1000)}"
            driver.get(url)
            driver.execute_script("localStorage.setItem('site_lang', 'de');")
            driver.get(url)
            try:
                WebDriverWait(driver, timeout).until(
                    lambda d: d.execute_script("return document.documentElement.getAttribute('data-i18n-fallback-done')") == 'de'
                )
            except Exception:
                pass
            data_de = driver.execute_script(JS_COLLECT, ATTRS)
            german_page_values[page] = {norm(item.get("value")) for item in data_de["items"] if norm(item.get("value"))}

        for lang in langs:
            for page in pages:
                url = urljoin(base_url.rstrip("/") + "/", page) + f"?i18n_audit={int(time.time()*1000)}"
                driver.get(url)
                driver.execute_script("localStorage.setItem('site_lang', arguments[0]);", lang)
                driver.get(url)
                try:
                    WebDriverWait(driver, timeout).until(
                        lambda d: d.execute_script("return document.documentElement.getAttribute('data-i18n-fallback-done')") == lang
                    )
                except Exception:
                    pass
                data = driver.execute_script(JS_COLLECT, ATTRS)
                issues = []
                seen = set()
                for item in data["items"]:
                    value = norm(item.get("value"))
                    key = de_values.get(value)
                    if key:
                        translated = norm(dictionaries.get(lang, {}).get(key, ""))
                        if translated and translated != value:
                            sig = ("unchanged-source", page, lang, item.get("kind"), item.get("attr", ""), value, item.get("path", ""))
                            if sig not in seen:
                                seen.add(sig)
                                issues.append({**item, "issue": "unchanged-source", "key": key, "expected": translated})
                            continue
                    if lang != "de" and value in german_page_values.get(page, set()) and len(value) >= 6 and not is_allowed_literal(value):
                        sig = ("unchanged-page-text", page, lang, item.get("kind"), item.get("attr", ""), value, item.get("path", ""))
                        if sig not in seen:
                            seen.add(sig)
                            issues.append({**item, "issue": "unchanged-page-text"})
                        continue
                    if lang != "de" and should_flag_signal(value):
                        sig = ("german-signal", page, lang, item.get("kind"), item.get("attr", ""), value, item.get("path", ""))
                        if sig not in seen:
                            seen.add(sig)
                            issues.append({**item, "issue": "german-signal"})
                all_results.append({
                    "page": page,
                    "lang": lang,
                    "documentLang": data["lang"],
                    "fallback": data["fallback"],
                    "title": data["title"],
                    "issueCount": len(issues),
                    "issues": issues,
                })
        return {"baseUrl": base_url, "pages": pages, "langs": langs, "results": all_results}
    finally:
        driver.quit()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--output", default="/tmp/ef_sinn_i18n_full_audit.json")
    ap.add_argument("--pages", nargs="*", default=PAGES)
    ap.add_argument("--langs", nargs="*", default=LANGS)
    ap.add_argument("--timeout", type=float, default=5.0)
    args = ap.parse_args()
    result = audit(args.base_url, args.pages, args.langs, args.timeout)
    out = Path(args.output)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    total = sum(r["issueCount"] for r in result["results"])
    print(f"AUDIT base={args.base_url} pages={len(args.pages)} langs={len(args.langs)} issues={total} output={out}")
    for r in result["results"]:
        if r["issueCount"]:
            print(f"{r['lang']:>5} {r['page']:<34} issues={r['issueCount']} fallback={r['fallback']!r} title={r['title']}")
            for issue in r["issues"][:8]:
                loc = f"{issue.get('kind')} {issue.get('attr','')} {issue.get('path','')}".strip()
                print(f"      - {issue['issue']}: {issue['value']!r} ({loc})")
            if r["issueCount"] > 8:
                print(f"      ... {r['issueCount']-8} more")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
