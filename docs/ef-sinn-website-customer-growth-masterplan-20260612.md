# EF-Sinn Website Masterplan: seriöse Kunden und größere Aufträge

Stand: 2026-06-12
Branch: `website/customer-growth-masterplan-20260612`
Basis: Live/aktuelles Repo unter `/home/marios/clawd/repos/MKI13.github.io`
Audit: `/home/marios/clawd/webseite/ef-sinn-website-kritiker-audit-20260612.md`

## Ziel

Die EF-Sinn-Webseite soll stärker zeigen, wofür Marios wirklich stehen soll: eine lokale Schreiner-Werkstatt für hochwertige Maßarbeit im Raum München und Unterhaching. Die Seite soll mehr passende Anfragen bringen, weniger unklare Kleinanfragen, und bessere Chancen auf größere Projekte wie Einbauschränke, Küchen, Innenausbau, Parkett/Bodenbeläge und hochwertige Terrassen.

Wichtig: Die aktuelle Live-Seite bleibt die Basis. Der lokale Service-Area-Entwurf ist nur Ideenquelle. Er wird nicht als Ganzes veröffentlicht.

## Feste Regeln

- Keine Veröffentlichung ohne ausdrückliches OK von Marios.
- Kein direkter Push auf `main`.
- Keine erfundenen Bewertungen, Sterne, Zahlen, Zertifikate oder Kundenstimmen.
- Keine 24 dünnen Ortsseiten. Das wäre Doorway-Risiko.
- Originalbilder bleiben erhalten. Für die Website werden nur optimierte Web-Derivate genutzt.
- Bei neuen Kundenbildern, Kundennamen oder Bewertungen vorher Freigabe prüfen.
- Jede Phase braucht Kritikerurteil und echte Verifikation.

## Kritiker-Gates

### Local-SEO-Kritiker

Prüft:

- Ist das echter lokaler Nutzen oder nur SEO-Fassade?
- Sind München, Unterhaching, Grünwald/Pullach und Umgebung natürlich eingebunden?
- Stimmen Sitemap, Canonical, interne Links und JSON-LD?

Blocker:

- Copy-Paste-Ortsseiten.
- Zu viele dünne Städte-Seiten.
- Sitemap listet unfertige Seiten.
- Ortsbehauptungen ohne echte Substanz.

### Schreiner-/Handwerk-Vertrauen-Kritiker

Prüft:

- Würde ein Eigentümer, Architekt oder eine Hausverwaltung EF-Sinn ein größeres Projekt zutrauen?
- Sieht man echte Person, Werkstatt, Arbeit, Material und Details?
- Sind die Referenzen konkret genug?

Blocker:

- Stockfoto-Gefühl.
- Generische Qualitätsfloskeln.
- Keine echte Person oder Werkstatt sichtbar.
- Referenzen ohne Problem, Lösung, Material und Ergebnis.

### Conversion-/UX-Kritiker

Prüft:

- Versteht ein Besucher sofort, ob EF-Sinn für sein Projekt passt?
- Ist der nächste Schritt klar?
- Macht die Anfrage genug Vorqualifizierung, ohne abzuschrecken?
- Ist die mobile Nutzung sauber?

Blocker:

- Kontakt versteckt.
- CTA zu allgemein oder zu billig wirkend.
- Anfrage-Assistent zu lang oder unklar.
- Wichtige Aktionen funktionieren mobil schlecht.

### Technik-/Performance-Kritiker

Prüft:

- Keine kaputten Links und Assets.
- JSON-LD parsebar.
- Genau ein H1 pro Seite.
- Canonicals absolut und korrekt.
- Bilder nicht unnötig groß.
- Browser-Konsole ohne Fehler.

Blocker:

- Kaputte interne Links.
- 5 MB Bilder direkt auf normalen Seiten.
- Console-Errors.
- Widerspruch zwischen Sitemap und Canonical.

### Legal-/Datenschutz-Kritiker

Prüft:

- Bewertungen, Bilder und Kundenstimmen sind echt und erlaubt.
- Datenschutz passt zur tatsächlichen Technik.
- Keine irreführenden Standort-, Leistungs- oder Qualifikationsaussagen.

Blocker:

- Fake-Bewertungen.
- Private Kundendaten oder genaue Privatadressen.
- Tracking ohne passende Erklärung.
- Veröffentlichung ohne Marios' OK.

## Phasenplan

### Phase 1: Startseite seriöser und projektorientierter machen

Status: begonnen.

Ziel:

Der obere Bereich soll nicht nach billigem Schnellkontakt klingen. Er soll sagen: Fotos, Maße und ein grober Rahmen reichen für eine erste Einschätzung. Das zieht bessere Anfragen an und bleibt ehrlich.

Dateien:

- `index.html`
- eventuell später `styles.css`
- eventuell später i18n-Dateien, falls mehrsprachige Texte angepasst werden

Kleinster Slice:

- Navigation-CTA von `Kostenlose Erstberatung` zu `Projekt anfragen` schärfen.
- Hero-CTA von `Kostenlose Erstberatung anfragen` zu `Projekt mit Fotos anfragen` ändern.
- Hero-Microcopy um Fotos, Maße, Zeitraum und groben Rahmen ergänzen.
- Unsichere 24-Stunden-Aussage durch `Realistische erste Einschätzung` ersetzen.
- Hero-Kicker um `Maßmöbel` und `Parkett & Bodenbeläge` schärfen.

Prüfung:

- Seite lokal öffnen.
- Mobil prüfen.
- Eine H1 bleibt erhalten.
- CTA führt weiter zum Anfrage-Assistenten.
- Keine Console-Errors.
- Keine neuen Fake-Claims.

### Phase 2: Trust-Block direkt nach Hero

Ziel:

Die Seite soll früher zeigen, wer EF-Sinn ist und warum man Marios für ein größeres Projekt vertrauen kann.

Mögliche Inhalte:

- echtes Foto von Marios, Werkstatt oder Montage.
- Werkstatt München / Büro Unterhaching.
- Persönliche Beratung durch Marios.
- Maßanfertigung statt Standardlösung.
- Planung, Fertigung und Montage aus einer Hand, nur wenn es so stimmt.
- Echte Referenzen aus München und Umgebung.

Offen von Marios:

- bestes Foto von Marios/Werkstatt/Team.
- echte Bewertungen oder Kundenstimmen.
- welche großen Zielgruppen aktiv gewünscht sind: Privatkunden, Architekten, Hausverwaltungen, Eigentümer.

Nicht tun:

- keine erfundenen Sterne.
- keine erfundene Jahreszahl oder Projektanzahl.
- keine Kundenlogos ohne Freigabe.

### Phase 3: Lokale SEO sauber aufbauen

Ziel:

Mehr Sichtbarkeit für München, Unterhaching und Umgebung, ohne Doorway-Seiten.

Umsetzung:

- Eine starke Hub-Seite, zum Beispiel `einsatzgebiet.html`.
- Danach nur wenige echte lokale Seiten, wenn sie genug Substanz haben:
  - München,
  - Unterhaching,
  - Grünwald/Pullach,
  - eventuell München Süd.

Jede lokale Seite braucht:

- eigene Einleitung,
- lokale Begründung,
- passende Leistungen,
- echte Referenz oder zumindest echte regionale Bezüge,
- FAQ,
- interne Links,
- Self-Canonical,
- Sitemap-Eintrag nur, wenn freigegeben.

### Phase 4: Referenzen zu Case Studies ausbauen

Ziel:

Das Portfolio soll größere Aufträge verkaufen. Bilder allein reichen nicht.

Pro gute Referenz:

- Ausgangslage,
- Lösung,
- Material,
- Besonderheit,
- Ergebnis,
- Ort/Region ohne genaue Privatadresse,
- CTA `Ähnliches Projekt besprechen`.

Priorität:

1. Küche / Küchenumbau.
2. Einbauschrank / Garderobe / Stauraum.
3. Innenausbau.
4. Parkett / Bodenbeläge / Bodenverlegung.
5. Hochwertige Terrasse.

### Phase 5: Anfrage-Assistent qualifizieren

Ziel:

Mehr brauchbare Anfragen. Nicht nur Name und Nachricht, sondern bessere Projektinfos.

Sinnvolle Felder:

- Projektart,
- Ort/Stadtteil,
- grobe Maße/Raumgröße,
- gewünschter Zeitraum,
- Projektstatus,
- optional grober Budgetrahmen,
- Hinweis: Fotos und Maße bitte in der E-Mail anhängen.

Wichtig:

Budget bleibt optional. Die Anfrage soll nicht abschrecken.

### Phase 6: Leistungseiten stärken

Ziel:

Leistungsseiten müssen zeigen, welche hochwertigen Arbeiten EF-Sinn wirklich übernehmen soll.

Fokus:

- `leistungen/moebelbau.html`: Einbauschränke, Garderoben, Badmöbel, Stauraum.
- `leistungen/kuechen.html`: Küche nach Maß, Umbau, Fronten, Stauraum.
- `leistungen/innenausbau.html`: Parkett, Bodenbeläge, Bodenverlegung, Wand/Decke/Holzdetails.
- `leistungen/terrassen.html`: Material, Unterkonstruktion, Langlebigkeit, gute Referenzen.

### Phase 7: Performance und Bilder

Ziel:

Schneller laden, besonders mobil.

Priorität:

- Logo von ca. 752 KB auf deutlich kleiner bringen.
- Große Terrassenbilder nicht direkt als normale Seitenbilder laden.
- WebP/AVIF oder optimierte JPG-Derivate nutzen.
- Thumbnails für Karten, größere Bilder nur in Detailansicht.

Prüfung:

- Bildgrößen messen.
- Link-/Asset-Crawl.
- Browser-Konsole.
- Mobile Ansicht.

### Phase 8: Freigabe und Livegang

Ziel:

Nur geprüfte Version veröffentlichen.

Vor Livegang:

- Marios sieht lokale Review-Version.
- Marios gibt ausdrücklich OK.
- Branch/PR statt direkter Main-Push.
- Link-/Asset-Crawl: 0 Fehler.
- JSON-LD parsebar.
- Sitemap/robots/canonical stimmen.
- Impressum/Datenschutz passen.
- Live nach Deployment prüfen.

## TTS-Kritiker für menschlichere Sprachnachrichten

Marios hat gesagt, die Stimme klingt zu künstlich. Deshalb bekommt jede wichtige Sprachnachricht ab jetzt einen kleinen Audio-Kritiker.

Regel:

Der gesprochene Text wird wie eine ruhige Sprachnachricht geschrieben, nicht wie ein Markdown-Bericht.

Checkliste:

- kurze Sätze, meistens 6 bis 14 Wörter.
- ein Gedanke pro Satz.
- natürliche Pausen durch Punkte und kurze Absätze.
- keine Markdown-Listen im TTS-Text.
- keine Überschriften, Pfadlisten oder technischen Rohlogs.
- kein Roboteranfang wie `Hier ist ein Update`.
- warm und direkt, aber nicht künstlich begeistert.
- erst sagen, was passiert ist, dann was offen ist, dann was als Nächstes kommt.

Beispielton:

`Marios, ich habe die Website weiter sortiert. Die Live-Seite bleibt die richtige Basis. Ich habe jetzt einen Masterplan mit Kritikern angelegt und den ersten kleinen Schritt lokal vorbereitet. Noch ist nichts online gegangen. Als Nächstes prüfe ich die Startseite im Browser und feile weiter an der Anfrage, damit sie seriöser wirkt.`

## Aktueller nächster Schritt

Phase 1 lokal abschließen:

- Microcopy im Hero prüfen.
- Browser und Console prüfen.
- Dann erst entscheiden, ob als nächster Slice ein kleiner Trust-Block folgt.
