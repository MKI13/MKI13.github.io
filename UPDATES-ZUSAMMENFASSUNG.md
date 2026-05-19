# EF-Sinn Website – Updates Zusammenfassung

Stand: 2026-05-19

## Ziel der aktuellen Überarbeitung

Die Website wurde für den Livegang auf GitHub Pages vorbereitet und stärker auf lokale Suche, Vertrauen und Kundenanfragen ausgerichtet.

## Wichtige umgesetzte Punkte

### SEO und Conversion
- Startseite-H1 auf lokale Suchintention gestärkt: Schreiner in München für Maßmöbel, Küchen, Parkett und Innenausbau.
- Header-Schnellkontakt ergänzt: Telefon und „Kostenlose Erstberatung“.
- Mobile feste Kontaktleiste ergänzt: „Anrufen“ und „Projekt anfragen“.
- Ablauf-/Prozess-Sektion auf der Startseite ergänzt.
- Neue lokale SEO-Landingpage erstellt: `schreiner-muenchen.html`.
- Portfolio-H1 auf „Referenzen für Schreinerarbeiten in München“ geändert.
- Portfolio-Suche mit Suchfeld und Chips ergänzt.
- Projektkarten mit direkter Anfrage-CTA ergänzt.
- Neues Parkett-Projekt ergänzt.

### Kontakt und Anfrage
- Kontaktseite um statischen Anfrage-Assistenten ergänzt.
- Kein Backend, keine automatische Speicherung, keine automatische Übermittlung.
- Beim Absenden öffnet sich nur das E-Mail-Programm mit vorbereiteter Nachricht an `info@ef-sinn.de`.
- Projektart-Auswahl als 10 sichtbare Buttons umgesetzt, nicht als Dropdown.
- Feld „Eigene Projektart“ ergänzt; eigener Text überschreibt die gewählte Vorlage.

### Adressen und Google Maps
- Werkstatt-Adresse überall korrigiert auf: `Germeringer Weg 3C, 81245 München`.
- Büro-Adresse: `Schmorellstraße 6, 82008 Unterhaching`.
- Google-Maps-Link für das Büro zeigt auf das vorhandene Unternehmensprofil: `Karampas Marios Schreiner`.
- Startseite und Kontaktseite enthalten Maps-Links für Werkstatt und Büro.
- Keine eingebettete Google-Maps-Karte; nur externe Links auf Klick.

### Strukturierte Daten / technische SEO
- LocalBusiness JSON-LD erweitert mit:
  - `ContactPoint`
  - `hasMap`
  - `sameAs`
  - `alternateName: Karampas Marios Schreiner`
  - `legalName: Marios Karampas`
  - Büro-/Werkstattadresse
  - Büro-Koordinaten `48.0614877, 11.6225611`
- `sitemap.xml` aktualisiert.
- `robots.txt` vorhanden und auf Sitemap verweisend.
- `llms.txt` aktualisiert.

### Rechtliches / Datenschutz
- Impressum aktualisiert mit Name, Adresse, Telefon, E-Mail, Handwerkskammer für München und Oberbayern, BGHM, Steuernummer und USt-IdNr.
- Datenschutzerklärung aktualisiert für GitHub Pages, statischen Anfrage-Assistenten, keine Cookies, kein Tracking und Google-Maps-Textlinks.
- 404-Seite ergänzt.

## Geänderte Dateien

- `index.html`
- `about.html`
- `contact.html`
- `portfolio.html`
- `schreiner-muenchen.html`
- `impressum.html`
- `datenschutz.html`
- `404.html`
- `styles.css`
- `sitemap.xml`
- `robots.txt`
- `llms.txt`
- `GO-LIVE-CHECKLIST.md`
- mehrere Service-Seiten unter `leistungen/`

## Verifikation

Lokal geprüft:

- JSON-LD parsebar.
- Keine doppelten IDs.
- Lokale Links und lokale Assets geprüft.
- Kernseiten liefern HTTP 200.
- Kontaktseite im Browser geprüft: keine JavaScript-Fehler.
- Anfrage-Assistent generiert eine vorbereitete E-Mail.
- Portfolio-Suche zeigt bei „Parkett“ ein passendes Projekt.
- Google-Maps-Büro-Link zeigt auf das Unternehmensprofil `Karampas Marios Schreiner`.
- Werkstatt-Adresse bleibt exakt `Germeringer Weg 3C, 81245 München`.

## Noch offen nach Livegang

- GitHub Pages Deployment nach Merge prüfen.
- Live-Domain testen: `https://www.ef-sinn.de/`.
- Google Search Console prüfen oder einrichten.
- Sitemap bei Google einreichen.
- Google-Unternehmensprofil weiter pflegen: Fotos, Leistungen, Beschreibung, Öffnungszeiten, Website-Link.
- Lighthouse/PageSpeed auf der Live-Domain prüfen.
- Mobile Ansicht auf echtem Handy prüfen.
- Optional weitere lokale Landingpages erstellen, wenn sie echten Nutzwert haben.

## Hinweis

`assets/js/page-flip.browser.js` war bereits untracked sichtbar und wurde nicht als Teil dieser Website-Änderung bewertet. Nicht blind löschen oder committen, bevor klar ist, ob die Datei gebraucht wird.
