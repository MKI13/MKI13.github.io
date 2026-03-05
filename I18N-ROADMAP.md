# I18N Roadmap (Auto-Übersetzung)

## Ziel
Wenn `i18n/de.json` geändert wird, sollen neue/aktualisierte Texte automatisch in andere Sprachen übernommen werden.

## Sprachcodes
- de (Master)
- en
- fr
- el (Griechisch)
- it
- es
- de-AT (Österreich)

## Architektur
1. **Source of truth:** `i18n/de.json`
2. **Targets:** `i18n/*.json`
3. **Sync-Script:** `scripts/i18n_sync.py`
   - erkennt fehlende Keys
   - übersetzt nur fehlende Werte
   - schreibt Übersetzungen zurück
4. **Workflow:** `.github/workflows/i18n-sync.yml` (manuell startbar)

## Wichtige Hinweise
- Für produktive Auto-Läufe braucht es einen Runner mit gültigem Ollama Cloud Login.
- Empfehlung: Self-hosted Runner auf Leonidas, weil dort Ollama bereits eingerichtet ist.
- Vor Main-Merge: sprachliche QA auf Startseite + Kontaktseite.

## Rollout-Plan
1. Nur Branch-Test: `feat/i18n-auto-translate-pipeline`
2. 20-30 wichtige UI-Keys in `de.json` ergänzen
3. Sync laufen lassen
4. Sichtprüfung pro Sprache
5. Dann PR auf `claude/...` (aktuelle Live-Basis) oder direkt auf main nach Freigabe
