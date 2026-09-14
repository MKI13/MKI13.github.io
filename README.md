# EF-Sinn Webseite

Öffentliche Webseite der Schreinerwerkstatt EF-Sinn in München und Unterhaching. Statisches HTML, CSS und lokales JavaScript; Veröffentlichung über GitHub Pages unter **www.ef-sinn.de**.

## Bei einem neuen Chat oder Arbeitsauftrag zuerst lesen

**`docs/WORK_STATUS.md`** enthält den aktuellen Abschlussstand, Prüfungen und offene Aufgaben. Ergänzend gelten `AGENTS.md` und die offenen GitHub-Issues. Nicht aus einem abgebrochenen Chat auf einen veröffentlichten Stand schließen.

## Veröffentlichung und Architektur

- Produktionszweig: **`main`**, GitHub Pages aus `/`, Domain `www.ef-sinn.de`, HTTPS aktiviert.
- HTML-Seiten im Stammverzeichnis und unter `leistungen/`; sieben Sprachdateien unter `i18n/`.
- `assets/js/i18n.js`: Sprachwahl mit optional gespeicherter Präferenz, Fehlerbehandlung und Schutz gegen verspätete Antworten.
- `assets/js/inquiry.js`: lokale Anfragevorbereitung mit Prüfung, Vorschau, E-Mail-Link, Kopieren und Textdatei. **Kein serverseitiger Direktversand und keine Foto-Uploads.** Fotos werden erst im E-Mail-Programm angehängt.
- `assets/optimized/`: responsive WebP-Kopien vorhandener eigener Bilder. Die Originale bleiben unverändert; `manifest.json` dokumentiert Herkunft, Prüfsummen und Größen.

Es werden keine zusätzlichen Analyse-, Werbe- oder Formularanbieter eingebunden. Die Sprachpräferenz kann im Browser gespeichert werden; Anfragetexte werden vom Assistenten nicht in Browser-Speichern abgelegt. Hosting und Kontaktbearbeitung sind in der Datenschutzerklärung beschrieben. Diese technische Beschreibung ist keine rechtliche Konformitätsbescheinigung.

## Entwicklung und Prüfung

```sh
python3 -m unittest discover -s tests -v
node --check assets/js/i18n.js
node --check assets/js/inquiry.js
npm ci --prefix qa
cd qa && npx playwright install chromium && npm test
```

Der Browser-Audit startet einen eigenen lokalen Server auf einem freien Port und beendet ihn anschließend. Ergebnisse und Screenshots liegen in `.qa-results/`. Er prüft tatsächliche Bilddateien bei verschiedenen Pixeldichten, explizite Rückfallgrößen und das Nachladen großer Dialogbilder. Er prüft alle 14 Seiten bei 360, 768 und 1440 Pixeln sowie Touch-Anfragen, sieben Sprachen, lange Texte, Downloads, blockierten Browser-Speicher und den Betrieb ohne JavaScript. Testeingaben sind künstlich; E-Mail-Links werden abgefangen und nicht versendet. Kopiererfolg und -ablehnung werden an der Browser-API simuliert. **Ein bestandener Browser-Audit beweist keine E-Mail-Zustellung.**

Für einen rein lesenden Vergleich der veröffentlichten Seite kann `EFSINN_BASE_URL=https://www.ef-sinn.de/` gesetzt werden. Auch dabei versendet der Test keine Anfragen.

## Bildpflege

Nach dem Hinzufügen eigener Originalbilder und ihrer HTML-Verweise: `python3 scripts/optimize_images.py` (Pillow erforderlich). Die Bildpflege wendet über `scripts/responsive_images.py` passende Layoutgrößen an; dieses Hilfsskript kann bei Layoutänderungen auch separat ohne Pillow ausgeführt werden. Anschließend Änderungen visuell prüfen, Tests ausführen und Originale nicht löschen. Keine erfundenen Referenzen, Bewertungen oder Materialangaben ergänzen.

## Freigabe

Änderungen über einen separaten Branch und Pull Request veröffentlichen. Erst mit bestandenen Prüfungen und erteilter Veröffentlichungsfreigabe nach `main` mergen; danach den tatsächlichen Pages-Build und die Live-Seite prüfen. Details: `DEPLOYMENT-GUIDE.md` und `GO-LIVE-CHECKLIST.md`.

## Direktversand – Issue #16

Implementierter Serverdienst, Browserintegration, Tests und Betriebsanleitung: `server/README.md`. Die öffentliche Konfiguration ist bis zur freigegebenen HTTPS-Bereitstellung und echten INBOX-Abnahme deaktiviert; die vorhandene E-Mail-Vorbereitung bleibt verwendbar. Keine Test-SMTP-Annahme als echte Zustellung ausgeben.
