# EF-Sinn Webseite – dauerhafter Arbeitsstand

Stand: 23. November 2026 · Asset-Version: `20261123`

## Zuerst lesen, wenn ein Chat endet

Repository: `MKI13/MKI13.github.io`. **GitHub Pages veröffentlicht `main` aus `/` unter `https://www.ef-sinn.de/`.** Der zu Beginn vorgefundene Repository-Standardzweig war ein alter Designzweig; deshalb Produktionsstand immer ausdrücklich gegen `main` prüfen. Keine anderen Projekte auf dem GEEKOM-PC verändern.

Die erneute Fertigstellung und Veröffentlichung nach bestandenen Tests wurden vom Inhaber freigegeben. Eine alte Chatnotiz zu Commit `e066bc7` ließ sich auf GitHub nicht verifizieren. Ausgangspunkt dieser tatsächlich implementierten Version ist `f39d5fff849e9bbcb2d03e4e26259a5c6cb5ef0d`; ältere behauptete Testergebnisse werden nicht übernommen.

## Website-Überarbeitung vom 23. November 2026

Grundlage ist `main` bei Commit `12e4c11`. Die öffentlich ausgelieferte Startseite und `index.html` dieses Commits waren beim Vergleich identisch. Die Überarbeitung liegt im separaten Zweig `website/ueberarbeitung-20261123`.

| Geprüfter Bereich | Ergebnis der Überarbeitung |
| --- | --- |
| Startseite und Kundenweg | Klarer Einstieg mit Projektanfrage und Referenzen. Doppelte Abschnitte und die zweite Galerie auf der Startseite entfallen. Die zentrale Referenzseite enthält weiterhin alle 30 Projekte samt Filter und Bildansicht. |
| Gestaltung und Bedienbarkeit | Durchgängige Farben, gut sichtbare Tastaturfokusse, lokalisierter Sprunglink und eine durchgehende Überschriftenhierarchie auf den geprüften Kernseiten. Die gemeinsame Linkfarbe erreicht auf Weiß 7,68:1, die bisherige 3,63:1. |
| Bilder und Ladeumfang | Eigenes Foto mit responsiven WebP-Varianten, priorisierter Abruf und festen Bildmaßen. Die Startseite enthält 38.927 statt 67.693 Byte HTML vor Komprimierung. Im Browser wurde bei 320 und 360 px die 480er-Variante gewählt. Die Originaldateien blieben erhalten. |
| Auffindbarkeit | Produktion behält ihre kanonischen Adressen. Die Sitemap nennt das Änderungsdatum der Startseite. Die strukturierten Betriebsdaten verwenden eine eindeutige Büroadresse. Die sichtbaren FAQ bleiben vorhanden. Google hat das separate FAQ-Suchergebnis 2026 eingestellt. [Google Search Central](https://developers.google.com/search/updates) |
| Technische Grundlagen | Gültiges Favicon, funktionierende Navigation von verschachtelten Fehlerseiten und lokale Einbindung von Bildern, Stilen und Skripten. Die öffentliche Domain hat weiterhin ihren eigenen Produktionszweig. |
| Datenschutz und Kontakt | Keine weiteren Drittanbieter und kein automatischer Versand. Die Anfrage wird im Tab vorbereitet. Die Testanfrage wurde angezeigt, kopiert und als Textdatei gespeichert. |
| KI-Auffindbarkeit | Live geprüft: `/llms.txt` und `/ki-anfrage.json` sind erreichbar. `/MLS` liefert 404. Die maschinenlesbaren Dateien bleiben unter ihren bisherigen URLs erreichbar. |

Prüfnachweis: 39 statische Python-Tests und JavaScript-Syntaxprüfung bestanden. Interaktiver Chromium-Browsertest für 14 Seiten bei 320, 360, 768 und 1.440 px ohne horizontalen Überlauf, fehlende Hauptüberschrift oder Fehler bei den im Test geladenen Bildern. Zusätzlich geprüft: alle sieben Sprachvarianten auf der Startseite, Parkett-Vorauswahl, Anfragevorschau, Kopieren, Textdownload, Kontakt bei deaktivierten Seitenskripten sowie Galerie-Filter und Öffnen/Schließen per Tastatur. Die GitHub-Prüfläufe verwendeten bislang das wechselnde Runner-Image `ubuntu-latest`. Nach dessen Wechsel auf Ubuntu 26.04 konnte Playwright 1.58.2 nicht starten. Beide Prüfläufe sind deshalb auf Ubuntu 24.04 festgelegt. Die vollständige bestehende lokale Playwright-Suite startete in dieser Umgebung wegen eines fehlenden Chromium-Programms und gesperrtem Download nicht. Es gab keine externe Testsendung, keinen Safari-Gerätetest und keine Messung echter Nutzerdaten aus Search Console oder Core Web Vitals.

Impressum und Datenschutzhinweise wurden technisch geprüft und inhaltlich übernommen. Vor Produktionsfreigabe ist die Entscheidung zur zusätzlich veröffentlichten Steuernummer separat zu treffen. § 5 DDG nennt die einschlägige Umsatzsteuer- beziehungsweise Wirtschafts-Identifikationsnummer. [§ 5 DDG](https://www.gesetze-im-internet.de/ddg/__5.html)

## Historischer Arbeitsstand zu Issue #16

Arbeitszweig: `website/issue-16-direct-delivery`, Basis `11c45e3`. Serverdienst und optionale siebensprachige Browseroberfläche sind implementiert. Einstieg: `server/README.md`. Der Dienst enthält HTTP-Verarbeitung, serverseitige Bildprüfung/Neucodierung, eine transaktionale Warteschlange, geschützte Wiederholungen, TLS-SMTP und getrennte INBOX-Verifikation. Dies ist eine ausführbare Codebasis, aber noch kein aktivierter öffentlicher Versand.

Im lokalen Integrationstest werden Browser, echte API und eine tatsächliche TLS-SMTP-Verbindung zum lokalen Testempfänger einschließlich Fotos und Antwortadresse geprüft. Keine externe Nachricht wurde versendet. Die vollständigen Prüfungen und die Produktionsgrenzen gehören in den zugehörigen Pull Request und unter `docs/qa/issue16-*`.

**Produktionsabschluss noch offen:** Kein freigegebener öffentlicher Backendserver oder Website-SMTP-Zugang ist nachgewiesen. Die Website-Umgebung enthält keine entsprechenden SMTP-/Hosting-Variablen; vorhandene SSH-Aliase benennen Hermes-Rechner. Deshalb bleibt `assets/js/inquiry-delivery-config.js` deaktiviert. Vor Aktivierung sind Hosting, eigener SMTP-Token, echter Eingang einer freigegebenen Testanfrage und betriebsspezifische Datenschutzhinweise zu verifizieren. Issue #16 wurde auf Wunsch des Inhabers ohne Aktivierung des öffentlichen Versands geschlossen. Keine anderen Projekte oder öffentlichen GEEKOM-Ports verändern.

## Abgeschlossene Fortsetzung: Issue #18

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

Vor einem Merge die private Vorschau prüfen und die Freigabe für ef-sinn.de einholen. Danach aktuellen Stand von `main`, PR-Prüfungen und den öffentlichen GitHub-Pages-Build kontrollieren. Direktversand bleibt gemäß Abschluss von Issue #16 deaktiviert.
