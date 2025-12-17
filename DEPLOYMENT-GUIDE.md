# 🚀 Deployment-Guide für GitLab

## Schritt-für-Schritt Anleitung zum Hochladen und Deployment

### Voraussetzungen

- [ ] GitLab-Account (https://gitlab.com)
- [ ] Git installiert auf Ihrem Computer
- [ ] Alle Dateien aus diesem Projekt

---

## Option 1: GitLab Web-Interface (Einfach)

### 1. Neues Projekt erstellen

1. Gehen Sie zu https://gitlab.com
2. Klicken Sie auf "New project" → "Create blank project"
3. Projekt-Name: `holzbau-karampas` (oder beliebig)
4. Visibility: "Public" (damit die Website öffentlich ist)
5. ✅ "Initialize repository with a README" NICHT ankreuzen
6. Klicken Sie auf "Create project"

### 2. Dateien hochladen

1. Im neuen Projekt: Klicken Sie auf "+" → "Upload file"
2. Laden Sie ALLE Dateien aus dem Ordner hoch:
   - index.html
   - about.html
   - contact.html
   - styles.css
   - impressum.html
   - datenschutz.html
   - .gitlab-ci.yml
   - robots.txt
   - sitemap.xml
   - README.md
   - .gitignore
3. Commit message: "Initial commit - Webseite Upload"
4. Klicken Sie auf "Upload file"

### 3. GitLab Pages aktivieren

1. Warten Sie ca. 2-5 Minuten
2. Gehen Sie zu: Settings → Pages
3. Ihre Webseite ist nun verfügbar unter:
   ```
   https://[ihr-username].gitlab.io/holzbau-karampas
   ```

### 4. Deployment prüfen

1. Gehen Sie zu: CI/CD → Pipelines
2. Sie sollten einen grünen Haken sehen (Deployment erfolgreich)
3. Bei Problemen: Klicken Sie auf die Pipeline und sehen Sie sich die Logs an

---

## Option 2: Git Command Line (Fortgeschritten)

### 1. Repository lokal einrichten

```bash
# In den Projekt-Ordner wechseln
cd /pfad/zu/holzbau-karampas

# Git initialisieren
git init

# Alle Dateien hinzufügen
git add .

# Ersten Commit erstellen
git commit -m "Initial commit - Holzbau Karampas Webseite"
```

### 2. Mit GitLab verbinden

```bash
# Remote hinzufügen (URL von GitLab kopieren)
git remote add origin https://gitlab.com/[ihr-username]/holzbau-karampas.git

# Branch umbenennen (falls nötig)
git branch -M main

# Hochladen
git push -u origin main
```

### 3. Bei Problemen mit Authentifizierung

**SSH-Key einrichten (empfohlen):**

```bash
# SSH-Key generieren
ssh-keygen -t ed25519 -C "ihre@email.de"

# Public Key anzeigen
cat ~/.ssh/id_ed25519.pub
```

Dann in GitLab:
1. Settings → SSH Keys
2. Key einfügen und speichern
3. Remote URL ändern:
   ```bash
   git remote set-url origin git@gitlab.com:[ihr-username]/holzbau-karampas.git
   ```

**Oder Personal Access Token:**

1. GitLab: Settings → Access Tokens
2. Token erstellen mit "write_repository" Berechtigung
3. Bei `git push` Username = Ihr GitLab-Username, Passwort = Token

---

## Custom Domain einrichten

### 1. Domain kaufen

Empfohlene Anbieter:
- IONOS (https://ionos.de)
- Strato (https://strato.de)
- All-Inkl (https://all-inkl.com)

### 2. Domain mit GitLab verbinden

**Bei Ihrem Domain-Provider:**

Fügen Sie folgende DNS-Records hinzu:

```
Type: A
Name: @
Value: 35.185.44.232

Type: CNAME
Name: www
Value: [ihr-username].gitlab.io
```

**In GitLab:**

1. Settings → Pages → New Domain
2. Domain eingeben: `ihre-domain.de`
3. Optional: SSL/TLS-Zertifikat (Let's Encrypt) aktivieren
4. Speichern

**Wichtig:** DNS-Änderungen können 24-48 Stunden dauern!

### 3. SSL-Zertifikat (HTTPS)

GitLab Pages bietet automatisch Let's Encrypt SSL an:

1. Settings → Pages → Ihre Domain
2. ✅ "Automatic certificate management using Let's Encrypt" aktivieren
3. Warten Sie 10-30 Minuten auf Zertifikat

---

## Dateien aktualisieren

### Web-Interface

1. Gehen Sie zur betreffenden Datei
2. Klicken Sie auf "Edit" (Stift-Symbol)
3. Änderungen vornehmen
4. "Commit changes"
5. Automatisches Re-Deployment startet

### Command Line

```bash
# Änderungen vornehmen in den Dateien

# Status prüfen
git status

# Geänderte Dateien hinzufügen
git add .

# Commit erstellen
git commit -m "Beschreibung der Änderung"

# Hochladen
git push
```

Automatisches Deployment startet nach jedem Push!

---

## Troubleshooting

### Pipeline schlägt fehl

**Problem:** Rote "X" bei Pipeline

**Lösung:**
1. CI/CD → Pipelines → Fehlgeschlagene Pipeline anklicken
2. Job-Log lesen
3. Häufige Fehler:
   - `.gitlab-ci.yml` Syntax-Fehler
   - Dateien fehlen
   - Branch-Name ist nicht `main` oder `master`

### Seite zeigt 404

**Problem:** URL führt zu 404-Fehler

**Lösung:**
1. Pipeline erfolgreich? (Grüner Haken)
2. Settings → Pages → Domain korrekt?
3. index.html im Root-Verzeichnis?
4. Cache leeren (Strg + F5)

### CSS/Bilder laden nicht

**Problem:** Seite wird ohne Styling angezeigt

**Lösung:**
1. Dateipfade prüfen (relativ, nicht absolut!)
2. styles.css im Root-Verzeichnis?
3. Browser-Konsole auf Fehler prüfen (F12)
4. Ggf. Hard-Refresh (Strg + Shift + R)

### Domain funktioniert nicht

**Problem:** Custom Domain erreichbar nicht

**Lösung:**
1. DNS-Records korrekt? (Bei Domain-Provider prüfen)
2. 24-48h warten (DNS-Propagierung)
3. Mit `dig ihre-domain.de` oder `nslookup ihre-domain.de` testen
4. SSL-Zertifikat aktiviert?

---

## Performance-Optimierung

### 1. Bilder komprimieren

```bash
# ImageMagick installieren
sudo apt install imagemagick

# Bild komprimieren
convert input.jpg -quality 85 -strip output.jpg

# Mehrere Bilder auf einmal
for img in *.jpg; do convert "$img" -quality 85 -strip "optimized_$img"; done
```

**Oder Online-Tools:**
- https://tinypng.com
- https://squoosh.app

### 2. Browser-Caching aktivieren

Fügen Sie `.htaccess` hinzu (wenn Server Apache nutzt):

```apache
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType text/html "access plus 1 hour"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
</IfModule>
```

### 3. Gzip-Kompression

In `.gitlab-ci.yml` hinzufügen:

```yaml
pages:
  script:
    - mkdir -p public
    - cp -r *.html public/
    - cp -r *.css public/
    # Gzip alle Text-Dateien
    - find public -type f \( -name '*.html' -o -name '*.css' \) -exec gzip -k {} \;
```

---

## Monitoring & Analytics

### 1. Uptime-Monitoring

**UptimeRobot (kostenlos):**
1. https://uptimerobot.com
2. Monitor hinzufügen
3. URL: https://ihre-domain.de
4. Intervall: 5 Minuten
5. Alert per E-Mail bei Ausfall

### 2. Google Search Console

1. https://search.google.com/search-console
2. Property hinzufügen: `https://ihre-domain.de`
3. Ownership verifizieren (HTML-Tag oder DNS)
4. Sitemap einreichen: `https://ihre-domain.de/sitemap.xml`

### 3. Plausible Analytics (DSGVO-konform)

Falls Sie später Analytics benötigen:
1. https://plausible.io (kostenpflichtig, aber DSGVO-konform)
2. Oder selbst hosten: https://github.com/plausible/analytics

**WICHTIG:** Keine Google Analytics ohne Cookie-Banner!

---

## Backup-Strategie

### Automatisches Git-Backup

Git ist bereits Ihr Backup! Alle Versionen sind gespeichert.

### Zusätzliches lokales Backup

```bash
# Repository klonen
git clone https://gitlab.com/[ihr-username]/holzbau-karampas.git backup-holzbau

# Zip-Archiv erstellen
zip -r holzbau-backup-$(date +%Y%m%d).zip backup-holzbau
```

### Cloud-Backup

Repository zusätzlich auf GitHub spiegeln:

```bash
# GitHub-Remote hinzufügen
git remote add github https://github.com/[ihr-username]/holzbau-karampas.git

# Auf GitHub pushen
git push github main
```

---

## Nächste Schritte nach Deployment

- [ ] Alle Links testen
- [ ] Mobile Ansicht testen
- [ ] Kontaktformular testen
- [ ] Google Search Console einrichten
- [ ] Google My Business Profil erstellen
- [ ] Lokale Verzeichnisse eintragen
- [ ] Social Media Profile verlinken

---

## Nützliche GitLab-Commands

```bash
# Status prüfen
git status

# Änderungen ansehen
git diff

# Letzte Commits ansehen
git log --oneline

# Zu älterem Commit zurückkehren
git checkout [commit-hash]

# Branch erstellen (für Tests)
git checkout -b test-branch

# Zurück zu main
git checkout main

# Remote-URL anzeigen
git remote -v
```

---

## Support & Hilfe

**GitLab-Dokumentation:**
- Pages: https://docs.gitlab.com/ee/user/project/pages/
- CI/CD: https://docs.gitlab.com/ee/ci/

**Git-Basics:**
- https://git-scm.com/book/de/v2

**Community-Support:**
- GitLab Forum: https://forum.gitlab.com
- Stack Overflow: https://stackoverflow.com/questions/tagged/gitlab

---

**Viel Erfolg mit dem Deployment! 🎉**

Bei Fragen: Siehe README.md für weitere Details.
