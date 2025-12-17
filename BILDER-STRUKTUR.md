# 📸 Bildstruktur und Speicheranleitung für ef-sin Webseite

## Ordnerstruktur

Erstellen Sie folgende Ordnerstruktur in Ihrem Projekt:

```
ef-sin/
├── index.html
├── about.html
├── contact.html
├── konfigurator.html
├── styles.css
├── konfigurator-styles.css
└── bilder/
    ├── hero/
    │   └── hero-hauptbild.jpg (1920x1080px)
    ├── portfolio/
    │   ├── kueche-01.jpg (800x600px)
    │   ├── kueche-02.jpg
    │   ├── tisch-01.jpg
    │   ├── schrank-01.jpg
    │   ├── kleiderschrank-01.jpg
    │   ├── treppe-01.jpg
    │   ├── treppe-02.jpg
    │   ├── terrasse-01.jpg
    │   ├── terrasse-02.jpg
    │   └── badmoebel-01.jpg
    ├── werkstatt/
    │   ├── werkstatt-aussen.jpg (1200x800px)
    │   ├── werkstatt-innen-01.jpg
    │   ├── werkstatt-innen-02.jpg
    │   └── maschinen.jpg
    ├── portrait/
    │   └── portrait-meister.jpg (800x600px)
    └── icons/
        └── favicon.ico (32x32px, 16x16px Multi-Size)
```

---

## Bildanforderungen & Optimierung

### Allgemeine Anforderungen

**Dateiformate:**
- JPEG (.jpg) für Fotos
- PNG (.png) nur für Logos/Icons mit Transparenz
- WebP (.webp) als Alternative (optional, bessere Kompression)

**Qualität:**
- JPEG Kompression: 80-85% (Balance zwischen Qualität und Dateigröße)
- Maximale Dateigröße: 500 KB pro Bild
- Farbraum: sRGB (für Web optimiert)

**Dateinamen:**
- Kleinbuchstaben
- Keine Leerzeichen (Bindestriche verwenden)
- Beschreibend und eindeutig
- Beispiel: `kueche-eiche-modern-01.jpg` statt `IMG_1234.jpg`

---

## Detaillierte Bildspezifikationen

### 1. Hero-Bild (Startseite)

**Speicherort:** `/bilder/hero/hero-hauptbild.jpg`

**Spezifikationen:**
- Größe: 1920x1080 Pixel (16:9 Format)
- Querformat
- Qualität: 85%
- Max. Dateigröße: 300 KB

**Inhalt:**
- Professionelles Foto Ihrer Werkstatt ODER
- Besonders schönes fertiges Projekt ODER
- Detailaufnahme von Holzbearbeitung

**Wichtig:**
- Kein Text im Bild (wird über CSS eingeblendet)
- Gute Beleuchtung
- Professionell aussehend

---

### 2. Portfolio-Bilder

**Speicherort:** `/bilder/portfolio/`

**Spezifikationen pro Bild:**
- Größe: 800x600 Pixel (4:3 Format)
- Qualität: 80-85%
- Max. Dateigröße: 200 KB

**Benötigte Bilder (Minimum 8-12 Stück):**

#### Küchen:
- `kueche-01.jpg` - Gesamtansicht Küche
- `kueche-02.jpg` - Detailaufnahme (z.B. Schubladen)
- `kueche-03.jpg` - Weitere Küche (optional)

#### Schränke:
- `schrank-01.jpg` - Einbauschrank
- `kleiderschrank-01.jpg` - Kleiderschrank
- `schrank-02.jpg` - Weitere Schränke (optional)

#### Treppen:
- `treppe-01.jpg` - Holztreppe Gesamtansicht
- `treppe-02.jpg` - Treppe Detail (Geländer, Stufen)

#### Holzterrassen:
- `terrasse-01.jpg` - Holzterrasse fertig
- `terrasse-02.jpg` - Terrasse mit Überdachung
- `terrasse-03.jpg` - Terrassendetail (optional)

#### Weitere Möbel:
- `tisch-01.jpg` - Esstisch
- `badmoebel-01.jpg` - Badezimmermöbel
- `regal-01.jpg` - Regale (optional)
- `bett-01.jpg` - Betten (optional)

**Foto-Tipps:**
- Tageslicht bevorzugen
- Keine ablenkenden Gegenstände im Hintergrund
- Parallele Linien (keine schrägen Winkel)
- Zeigen Sie die Qualität der Arbeit
- Vor/Nach-Bilder sind beeindruckend

---

### 3. Werkstatt-Bilder

**Speicherort:** `/bilder/werkstatt/`

**Spezifikationen:**
- Größe: 1200x800 Pixel
- Qualität: 85%
- Max. Dateigröße: 250 KB

**Benötigte Bilder:**

#### werkstatt-aussen.jpg
- Außenansicht Ihrer Werkstatt
- Eingang sichtbar
- Bei gutem Wetter fotografieren

#### werkstatt-innen-01.jpg & -02.jpg
- Innenraum der Werkstatt
- Ordentlich aufgeräumt
- Zeigen Sie Ihre Maschinen/Werkzeuge
- Professionelle Arbeitsumgebung

#### maschinen.jpg (optional)
- Detailaufnahme wichtiger Maschinen
- Zeigt Ihre professionelle Ausstattung

---

### 4. Portrait-Foto

**Speicherort:** `/bilder/portrait/portrait-meister.jpg`

**Spezifikationen:**
- Größe: 800x600 Pixel
- Qualität: 85%
- Max. Dateigröße: 150 KB

**Inhalt:**
- Professionelles Portrait-Foto von Ihnen
- Vor neutralem/werkstatt Hintergrund
- Freundlich und professionell
- Arbeitskleidung oder Business-Casual

**Alternativ:**
- Foto bei der Arbeit
- In der Werkstatt
- Mit fertigen Projekten

---

### 5. Favicon

**Speicherort:** `/bilder/icons/favicon.ico`

**Spezifikationen:**
- Multi-Size ICO-Datei: 16x16px und 32x32px
- Alternativ: PNG (32x32px)
- Einfaches, erkennbares Design

**Vorschläge:**
- Stilisiertes Holz-Icon
- Ihre Initialen "ef"
- Säge oder Werkzeug-Symbol
- Firmenlogo vereinfacht

**Online-Tools zum Erstellen:**
- https://favicon.io/
- https://realfavicongenerator.net/

---

## Bilder in HTML einbinden

### Ersetzen der Platzhalter

**Vorher (Platzhalter):**
```html
<div class="image-placeholder" role="img" aria-label="Projekt 1">
    <span class="placeholder-text">Projekt 1<br>800x600px</span>
</div>
```

**Nachher (Echtes Bild):**
```html
<img src="bilder/portfolio/kueche-01.jpg" 
     alt="Maßgefertigte Küche aus Eiche mit Soft-Close"
     loading="lazy"
     width="800"
     height="600">
```

### Wichtige Attribute:

- **src**: Pfad zum Bild
- **alt**: Beschreibender Text (SEO & Accessibility!)
- **loading="lazy"**: Lazy Loading für Performance
- **width/height**: Verhindert Layout-Shift

---

## Bild-Optimierung Tools

### Online-Tools (kostenlos):

1. **TinyPNG** - https://tinypng.com
   - JPEG & PNG Kompression
   - Behält Qualität bei
   - Einfach Drag & Drop

2. **Squoosh** - https://squoosh.app
   - Von Google entwickelt
   - Verschiedene Formate (WebP, AVIF)
   - Vorschau-Vergleich

3. **ImageOptim** - https://imageoptim.com (Mac)
   - Desktop-App
   - Batch-Verarbeitung
   - Verlustfreie Kompression

### Desktop-Programme:

1. **GIMP** (kostenlos)
   - Bildbearbeitung
   - Größe ändern
   - Export mit Qualitätseinstellung

2. **IrfanView** (Windows, kostenlos)
   - Batch-Konvertierung
   - Resize-Funktion
   - Schnell und einfach

### Command Line (Fortgeschritten):

```bash
# ImageMagick installieren
sudo apt install imagemagick

# Bild verkleinern auf 800x600
convert input.jpg -resize 800x600 output.jpg

# Bild komprimieren (85% Qualität)
convert input.jpg -quality 85 output.jpg

# Batch: Alle JPG-Bilder im Ordner
for img in *.jpg; do 
    convert "$img" -resize 800x600 -quality 85 "optimiert_$img"; 
done
```

---

## Workflow für neue Bilder

### Schritt-für-Schritt:

1. **Fotos machen**
   - Gute Beleuchtung
   - Ruhige Hand / Stativ
   - Mehrere Blickwinkel

2. **Auswahl treffen**
   - Beste Fotos auswählen
   - Qualität vor Quantität

3. **Bilder bearbeiten**
   - Zuschneiden auf richtiges Format
   - Helligkeit/Kontrast anpassen
   - Störende Elemente entfernen (optional)

4. **Bilder optimieren**
   - Größe anpassen (siehe Spezifikationen oben)
   - Komprimieren mit Tool
   - Qualität prüfen

5. **Richtig benennen**
   - Beschreibender Name
   - Kleinbuchstaben, Bindestriche
   - Nummerierung bei Serie

6. **Hochladen**
   - In richtigen Ordner (/bilder/...)
   - Via FTP, GitLab oder Hosting-Panel

7. **In HTML einbinden**
   - Platzhalter ersetzen
   - Alt-Text hinzufügen
   - Testen!

---

## Checkliste vor Go-Live

- [ ] Hero-Bild hochgeladen und eingebunden
- [ ] Mindestens 8 Portfolio-Bilder hochgeladen
- [ ] Werkstatt-Außenansicht vorhanden
- [ ] Werkstatt-Innenansicht vorhanden
- [ ] Portrait-Foto eingebunden (optional)
- [ ] Favicon erstellt und verlinkt
- [ ] Alle Bilder optimiert (<500 KB)
- [ ] Alle Alt-Texte vergeben
- [ ] Alle Platzhalter ersetzt
- [ ] Mobile Ansicht getestet
- [ ] Ladezeit geprüft (PageSpeed Insights)

---

## Favicon einbinden

Fügen Sie im `<head>`-Bereich aller HTML-Dateien hinzu:

```html
<link rel="icon" type="image/x-icon" href="bilder/icons/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="bilder/icons/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="bilder/icons/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="bilder/icons/apple-touch-icon.png">
```

---

## Weitere Tipps

### Copyright beachten:
- Nur eigene Fotos verwenden
- Oder Fotos mit kommerzieller Lizenz
- Keine Google-Bilder ohne Lizenz!

### Professionelle Fotos:
- Überlegen Sie, einen Fotografen zu engagieren
- Investition lohnt sich für Hauptbilder
- Alternative: Handy-Fotos bei gutem Tageslicht

### Regelmäßig aktualisieren:
- Neue Projekte hinzufügen
- Veraltete Bilder ersetzen
- Saisonal anpassen (z.B. Weihnachtsdeko-Projekte)

### SEO-Optimierung:
- Aussagekräftige Dateinamen
- Gute Alt-Texte
- Sitemap aktualisieren

---

## Support & Fragen

Bei Problemen mit Bildern:
1. Überprüfen Sie Dateipfade (Case-Sensitive!)
2. Prüfen Sie Dateiberechtigungen (chmod 644)
3. Browser-Cache leeren (Strg + F5)
4. Developer-Tools öffnen (F12) → Network Tab

---

**Stand:** November 2024  
**Version:** 1.0
