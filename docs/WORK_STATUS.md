# EF-Sinn Webseite – dauerhafter Arbeitsstand

Stand: 14. September 2026 · Asset-Version: `20260914-review`

## Zuerst lesen, wenn ein Chat endet

Repository: `MKI13/MKI13.github.io`. **GitHub Pages veröffentlicht `main` aus `/` unter `https://www.ef-sinn.de/`.** Der zu Beginn vorgefundene Repository-Standardzweig war ein alter Designzweig; deshalb Produktionsstand immer ausdrücklich gegen `main` prüfen. Keine anderen Projekte auf dem GEEKOM-PC verändern.

Die erneute Fertigstellung und Veröffentlichung nach bestandenen Tests wurden vom Inhaber freigegeben. Eine alte Chatnotiz zu Commit `e066bc7` ließ sich auf GitHub nicht verifizieren. Ausgangspunkt dieser tatsächlich implementierten Version ist `f39d5fff849e9bbcb2d03e4e26259a5c6cb5ef0d`; ältere behauptete Testergebnisse werden nicht übernommen.

## Aktuelle Fortsetzung: Issue #18

Die erhaltenen Änderungen auf `website/review-followup-20260914` wurden gegen den veröffentlichten Stand `9f60287` geprüft. Die zwei Review-Befunde aus PR #17 sind behoben: Bildgrößen nach tatsächlichem Layout und Pixeldichte, sowie die Beschreibung von Vorschau und ausdrücklicher E-Mail-Übergabe in allen sieben Sprachen.

Nachweise: **39/39 Python-Tests, 67/67 Chromium-Prüfungen**. Tatsächlich gewählte Bilddateien, erzwungene explizite Rückfallwerte und das Nachladen großer Dialogbilder sind mitgeprüft. Der gesamte Bildgenerator lief erneut durch: alle 14 HTML-Dateien blieben per Prüfsumme identisch; Originale und WebP-Dateien blieben unverändert. Berichte liegen unter `docs/qa/` und in den CI-Artefakten.

Issue #16: Infrastruktur-Vorprüfung und konkrete Empfehlung stehen in `docs/ISSUE-16-DELIVERY-DECISION.md`. Kein Backend wurde aktiviert und kein Vertrag geschlossen. Hosting- und SMTP-Freigabe sowie echter Zustelltest bleiben offen.

## In dieser Version umgesetzt

1. **Bilder:** 79 vorhandene Originalbilder in 228 Varianten-Zuordnungen aufbereitet. Eigene Referenzfotos unverändert erhalten, SHA-256-Herkunftsnachweise im Manifest. Originale insgesamt 63.345.576 Bytes; jeweils größte WebP-Ausführung insgesamt 12.224.534 Bytes, **80,7 % weniger**. Dies ist ein Dateigrößenvergleich, keine erfundene Ladezeitmessung.
2. **Anfrage-Assistent:** Name/Beschreibung prüfen, optionale Maße und Zeitraum, Vorschau, E-Mail-Übergabe, Kopieren, echte UTF-8-Textdatei, Bearbeiten. Lange Anfragen werden nicht abgeschnitten; klare Ausweichmöglichkeit für gesperrte Zwischenablage. Ohne JavaScript keine Formularübertragung und keine persönlichen Eingaben in der URL.
3. **Sprachen:** Alle neuen Oberflächentexte in sieben Sprachen. Ausfälle des Browser-Speichers und der Sprachdatei sowie überholte Antworten nach schnellem Umschalten abgefangen. Eingaben und Projektwahl bleiben beim Sprachwechsel erhalten.
4. **Darstellung und Bedienung:** Kontaktseite bei 360 Pixeln ohne Überlauf; Startbereich wächst mit seinem Inhalt statt Texte abzuschneiden. Bildansicht der Referenzen als echtes Dialogfenster mit Tastatur-/Touch-Bedienung, Escape und Fokusrückgabe. Kein leerer Bildverweis mehr.
5. **Prüfungen und Fortsetzung:** 39 Python-Regressionstests und 67 Browserprüfungen, reproduzierbarer Audit mit Screenshots, GitHub-Workflow, aktualisierte README/Deployment-Anleitung und `AGENTS.md`.

## Nachweise und Grenzen

Lokaler Prüflauf: `python3 -m unittest discover -s tests -v`; `qa/browser-audit.mjs` prüft 14 Seiten in drei Breiten und die realen Bedienwege in Chromium. `npm audit` meldete für die festgeschriebenen Testabhängigkeiten keine bekannten Schwachstellen. Berichte und Screenshots: `.qa-results/` bzw. das GitHub-Actions-Artefakt. Die endgültige GitHub-Prüfung, Merge-Revision und Live-Verifikation gehören in den Abschlusskommentar des zugehörigen Release-Pull-Requests; vor einer weiteren Bearbeitung diesen Kommentar und den tatsächlichen Pages-Status lesen.

Testnachrichten sind künstlich. E-Mail-Links werden abgefangen; keine Kundenanfrage wurde versendet. Zwischenablage-Erfolg/-Ablehnung werden an der Browser-API simuliert; der Textdatei-Download wird als echte Datei geprüft. Chromium-Desktop-/Touch-Prüfung ist kein Test auf einem echten iPhone/Safari. Es wird keine pauschale rechtliche oder vollständige Barrierefreiheitskonformität behauptet.

## Noch offen: genau abgegrenzt

**Issue #16 – echter Direktversand mit optionalen Foto-Anhängen.** Vor Aktivierung: vorhandene Backendmöglichkeiten prüfen, Anbieter/Kosten und Datenschutzgrundlage klären, Empfangsadresse aktivieren und einen echten Ende-zu-Ende-Zustelltest nachweisen. Der derzeitige Assistent öffnet das E-Mail-Programm; der Besucher versendet dort selbst. Kein unbestätigter Drittanbieter wurde eingeschaltet.

## Nächster Einstieg

Nicht die fertigen Bild-, Formular- oder Sprachkorrekturen neu bauen. Zuerst `main`, Release-PR, Pages-Veröffentlichung und Issue #16 lesen. Falls weiterentwickelt wird, #16 entlang seiner vollständigen Akzeptanzkriterien bearbeiten; bei fehlenden externen Freigaben nichts als einsatzbereiten Direktversand ausgeben. Änderungen auf einem eigenen Branch, Tests vollständig ausführen und nach Merge live prüfen.
