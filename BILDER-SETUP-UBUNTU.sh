#!/bin/bash
#
# Bildstruktur für ef-sin Webseite erstellen
# Für Ubuntu Linux
#
# Verwendung:
#   chmod +x BILDER-SETUP-UBUNTU.sh
#   ./BILDER-SETUP-UBUNTU.sh
#

echo "=========================================="
echo "ef-sin - Bildstruktur erstellen"
echo "=========================================="
echo ""

# Prüfen ob wir im richtigen Verzeichnis sind
if [ ! -f "index.html" ]; then
    echo "❌ FEHLER: index.html nicht gefunden!"
    echo "Bitte führen Sie dieses Script im Projekt-Ordner aus."
    exit 1
fi

echo "✅ index.html gefunden. Starte Setup..."
echo ""

# Hauptordner erstellen
echo "📁 Erstelle Ordner 'bilder'..."
mkdir -p bilder

# Unterordner erstellen
echo "📁 Erstelle Unterordner..."
mkdir -p bilder/hero
mkdir -p bilder/portfolio
mkdir -p bilder/werkstatt
mkdir -p bilder/portrait
mkdir -p bilder/icons

echo ""
echo "✅ Ordnerstruktur erstellt!"
echo ""

# Struktur anzeigen
echo "📂 Erstellt wurde:"
tree bilder 2>/dev/null || find bilder -type d | sed 's|[^/]*/|  |g'

echo ""
echo "=========================================="
echo "📋 Nächste Schritte:"
echo "=========================================="
echo ""
echo "1. BILDER VORBEREITEN:"
echo "   - Optimieren Sie Ihre Bilder (siehe unten)"
echo "   - Benennen Sie sie korrekt"
echo ""
echo "2. BILDER KOPIEREN:"
echo "   Verwenden Sie die Befehle unten, um Ihre Bilder"
echo "   in die richtigen Ordner zu kopieren."
echo ""
echo "3. DATEINAMEN PRÜFEN:"
echo "   Die HTML-Dateien erwarten diese Dateinamen:"
echo ""
echo "   bilder/hero/"
echo "     └─ hero-hauptbild.jpg (1920x1080px)"
echo ""
echo "   bilder/portfolio/"
echo "     ├─ kueche-01.jpg (800x600px)"
echo "     ├─ tisch-01.jpg"
echo "     ├─ schrank-01.jpg"
echo "     ├─ kleiderschrank-01.jpg"
echo "     ├─ treppe-01.jpg"
echo "     ├─ terrasse-01.jpg"
echo "     ├─ terrasse-02.jpg"
echo "     └─ badmoebel-01.jpg"
echo ""
echo "   bilder/werkstatt/"
echo "     ├─ werkstatt-aussen.jpg (1200x800px)"
echo "     └─ werkstatt-innen.jpg"
echo ""
echo "   bilder/portrait/"
echo "     └─ portrait.jpg (800x600px) [optional]"
echo ""
echo "   bilder/icons/"
echo "     └─ favicon.ico (32x32px)"
echo ""
echo "=========================================="
echo "🖼️  BILDER OPTIMIEREN (ImageMagick):"
echo "=========================================="
echo ""
echo "ImageMagick installieren:"
echo "  sudo apt update"
echo "  sudo apt install imagemagick"
echo ""
echo "Bild optimieren und verkleinern:"
echo "  convert ORIGINAL.jpg -resize 800x600 -quality 85 bilder/portfolio/NAME.jpg"
echo ""
echo "Mehrere Bilder auf einmal:"
echo "  for img in *.jpg; do convert \"\$img\" -resize 800x600 -quality 85 \"bilder/portfolio/\$img\"; done"
echo ""
echo "Hero-Bild erstellen (1920x1080):"
echo "  convert ORIGINAL.jpg -resize 1920x1080^ -gravity center -extent 1920x1080 -quality 85 bilder/hero/hero-hauptbild.jpg"
echo ""
echo "=========================================="
echo "📋 BEISPIEL - Bilder kopieren:"
echo "=========================================="
echo ""
echo "# Wenn Ihre Bilder in ~/Bilder/ liegen:"
echo ""
echo "# Hero-Bild"
echo "cp ~/Bilder/werkstatt-schoen.jpg bilder/hero/hero-hauptbild.jpg"
echo ""
echo "# Portfolio"
echo "cp ~/Bilder/kueche1.jpg bilder/portfolio/kueche-01.jpg"
echo "cp ~/Bilder/tisch1.jpg bilder/portfolio/tisch-01.jpg"
echo "cp ~/Bilder/schrank1.jpg bilder/portfolio/schrank-01.jpg"
echo "cp ~/Bilder/kleiderschrank1.jpg bilder/portfolio/kleiderschrank-01.jpg"
echo "cp ~/Bilder/treppe1.jpg bilder/portfolio/treppe-01.jpg"
echo "cp ~/Bilder/terrasse1.jpg bilder/portfolio/terrasse-01.jpg"
echo "cp ~/Bilder/terrasse2.jpg bilder/portfolio/terrasse-02.jpg"
echo "cp ~/Bilder/bad1.jpg bilder/portfolio/badmoebel-01.jpg"
echo ""
echo "# Werkstatt"
echo "cp ~/Bilder/werkstatt-front.jpg bilder/werkstatt/werkstatt-aussen.jpg"
echo "cp ~/Bilder/werkstatt-innen.jpg bilder/werkstatt/werkstatt-innen.jpg"
echo ""
echo "# Portrait (optional)"
echo "cp ~/Bilder/portrait.jpg bilder/portrait/portrait.jpg"
echo ""
echo "=========================================="
echo "🔍 BILDER PRÜFEN:"
echo "=========================================="
echo ""
echo "Alle Bilder auflisten:"
echo "  find bilder -type f -name '*.jpg' -o -name '*.png'"
echo ""
echo "Bildgrößen prüfen:"
echo "  identify bilder/portfolio/*.jpg"
echo ""
echo "Dateigröße prüfen (sollte < 500 KB sein):"
echo "  du -h bilder/portfolio/*.jpg"
echo ""
echo "=========================================="
echo "✅ Setup abgeschlossen!"
echo "=========================================="
echo ""
echo "Nächster Schritt:"
echo "  1. Kopieren Sie Ihre Bilder in die Ordner"
echo "  2. Prüfen Sie die Dateinamen"
echo "  3. Testen Sie die Webseite: firefox index.html"
echo ""
