# EF-Sinn Website Go-Live Checklist

Stand: 2026-05-19
Hosting: GitHub Pages mit Custom Domain `www.ef-sinn.de`

## Erledigt vor Livegang

### Inhalte und Kontakt
- [x] Firmenname auf `ef-sinn` aktualisiert
- [x] Inhaber / Verantwortlicher: Marios Karampas
- [x] Büro-Adresse: Schmorellstraße 6, 82008 Unterhaching
- [x] Werkstatt-Adresse: Germeringer Weg 3C, 81245 München
- [x] Telefonnummer und E-Mail auf den sichtbaren Seiten eingetragen
- [x] Öffnungszeiten eingetragen
- [x] Google-Unternehmensprofil für Büro verlinkt: Karampas Marios Schreiner
- [x] Impressum mit Kontaktdaten, Kammer, BGHM, Steuernummer und USt-IdNr. aktualisiert
- [x] Datenschutzerklärung an GitHub Pages, mailto-Anfrage-Assistent, Google-Maps-Links und Stand 19.05.2026 angepasst

### Anfrage / Datenschutz
- [x] Kein echtes Formular-Backend eingebaut
- [x] Anfrage-Assistent arbeitet statisch und öffnet nur eine vorbereitete E-Mail
- [x] Projektart-Auswahl als sichtbare Buttons statt Dropdown
- [x] Feld „Eigene Projektart“ ergänzt
- [x] Datenschutztext erklärt: keine Speicherung auf der Webseite, Versand erst über E-Mail-Programm des Besuchers
- [x] Keine automatisch eingebettete Google Maps Karte, nur externe Links auf Klick
- [x] Kein Analytics / Tracking / Cookie-Banner nötig

### SEO und Technik
- [x] Lokale SEO auf München / Unterhaching gestärkt
- [x] `schreiner-muenchen.html` als neue SEO-Landingpage erstellt
- [x] `sitemap.xml` aktualisiert
- [x] `robots.txt` vorhanden und auf Sitemap verweisend
- [x] `CNAME` vorhanden: `www.ef-sinn.de`
- [x] LocalBusiness JSON-LD mit `ContactPoint`, `hasMap`, `sameAs`, Büro-/Werkstattadresse und Google-Profilname ergänzt
- [x] Portfolio-Suche und Projekt-CTAs ergänzt
- [x] 404-Seite erstellt

### Medien
- [x] Bilderordner vorhanden
- [x] Hero-Bild vorhanden
- [x] Portfolio-Bilder vorhanden
- [x] Werkstatt-/Portfolio-Bilder vorhanden
- [x] Favicon und Apple Touch Icon vorhanden
- [x] Alt-Texte auf den geprüften Seiten vorhanden

### Getestet lokal
- [x] JSON-LD parsebar
- [x] Keine doppelten IDs
- [x] Lokale Links und lokale Assets geprüft
- [x] HTTP 200 für Kernseiten: Start, Kontakt, Portfolio, Leistungen, Impressum, Datenschutz, 404, neue SEO-Seite
- [x] Kontaktseite im Browser geprüft: keine JavaScript-Fehler
- [x] Google-Maps-Büro-Link zeigt auf das vorhandene Unternehmensprofil
- [x] Werkstatt-Adresse bleibt exakt: Germeringer Weg 3C, 81245 München

## Beim Livegang

- [x] Auf Feature-Branch arbeiten, nicht direkt auf `main`/`master`
- [ ] Änderungen committen
- [ ] Branch nach GitHub pushen
- [ ] Pull Request gegen `main` erstellen oder mergen lassen
- [ ] Nach Merge GitHub-Pages-Deployment abwarten
- [ ] Live-Seiten prüfen:
  - [ ] https://www.ef-sinn.de/
  - [ ] https://www.ef-sinn.de/contact.html
  - [ ] https://www.ef-sinn.de/portfolio.html
  - [ ] https://www.ef-sinn.de/schreiner-muenchen.html
  - [ ] https://www.ef-sinn.de/impressum.html
  - [ ] https://www.ef-sinn.de/datenschutz.html

## Nach Livegang offen / optional

- [ ] Google Search Console einrichten oder prüfen
- [ ] Sitemap in Google Search Console einreichen
- [ ] Google-Unternehmensprofil weiter pflegen: Leistungen, Fotos, Beschreibung, Öffnungszeiten, Website-Link
- [ ] Kundenbewertungen aktiv einholen
- [ ] Weitere lokale Landingpages prüfen, aber nur mit echtem Nutzwert:
  - [ ] Einbauschrank München
  - [ ] Parkett schleifen München
  - [ ] Küche nach Maß München
- [ ] Lighthouse/PageSpeed auf Live-Domain prüfen
- [ ] Mobile Ansicht auf echtem Handy prüfen
- [ ] Optional: lokale Branchenverzeichnisse aktualisieren
- [ ] Optional: Uptime-Monitoring einrichten

## Rechtlicher Hinweis

Impressum und Datenschutz wurden technisch und inhaltlich plausibilisiert, ersetzen aber keine Rechtsberatung. Bei Unsicherheit sollte ein Anwalt oder ein aktueller Datenschutz-/Impressums-Generator geprüft werden.
