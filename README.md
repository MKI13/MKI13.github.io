# Holzbau Karampas - Statische Webseite

Eine vollständig DSGVO-konforme, sichere und performante Webseite für eine Schreinerwerkstatt ohne externe Abhängigkeiten.

## 🔒 Sicherheits- & Datenschutz-Features

### Implementierte Sicherheitsmaßnahmen

✅ **Keine Cookies oder Client-Storage**
- Kein localStorage, sessionStorage oder IndexedDB
- Keine Session-Verwaltung im Browser
- Kein Tracking oder Analytics clientseitig

✅ **Keine externen Ressourcen**
- Keine Google Fonts oder andere CDN-Schriftarten
- Nur System-Fonts (DSGVO-konform)
- Keine externen JavaScript-Bibliotheken
- Alle Assets lokal gehostet

✅ **Kein JavaScript**
- Eliminiert XSS-Vektoren (Cross-Site Scripting)
- Keine clientseitige Datenverarbeitung
- Rein statische HTML/CSS-Implementierung
- CSS-only Animationen für Performance

✅ **WCAG AA Konformität**
- Kontrastverhältnis ≥ 4.5:1 für alle Texte
- Semantisches HTML5 mit ARIA-Attributen
- Tastaturnavigation mit sichtbaren Focus-States
- Screen Reader optimiert

✅ **Privacy by Design**
- Kontaktformular ohne direkte E-Mail-Anzeige
- Honeypot-Feld gegen Spam-Bots
- Keine IP-Logging im Frontend
- Keine Fingerprinting-Möglichkeiten

---

## 📁 Projektstruktur

```
holzbau-karampas/
├── index.html           # Startseite
├── about.html           # Über uns Seite
├── contact.html         # Kontaktseite mit Formular
├── styles.css           # Komplettes Stylesheet
├── README.md            # Diese Datei
├── impressum.html       # [TODO] Impressum (gesetzlich erforderlich)
├── datenschutz.html     # [TODO] Datenschutzerklärung
└── assets/              # [Optional] Ordner für Bilder
    ├── images/
    └── favicon.ico
```

---

## 🚀 Deployment-Anleitung

### Option 1: GitLab Pages (Empfohlen)

1. **Repository erstellen**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <GITLAB_URL>
   git push -u origin main
   ```

2. **GitLab CI/CD konfigurieren**
   
   Erstellen Sie eine `.gitlab-ci.yml` im Root-Verzeichnis:
   
   ```yaml
   pages:
     stage: deploy
     script:
       - mkdir .public
       - cp -r * .public
       - mv .public public
     artifacts:
       paths:
         - public
     only:
       - main
   ```

3. **Zugriff**
   - Die Seite ist nach dem Deployment unter `https://<username>.gitlab.io/<projectname>` erreichbar
   - Konfigurieren Sie eine Custom Domain in den Settings

### Option 2: Netlify

1. Netlify-Konto erstellen
2. Neues Projekt: "Import from Git" → GitLab auswählen
3. Build Settings:
   - Build command: (leer lassen)
   - Publish directory: `/`
4. Deploy!

**Formular-Konfiguration für Netlify:**
In `contact.html` das Formular anpassen:
```html
<form data-netlify="true" name="contact" method="POST">
```

### Option 3: Eigener Server (Apache/Nginx)

**Apache (.htaccess)**
```apache
# HTTPS erzwingen
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Security Headers
Header set X-Content-Type-Options "nosniff"
Header set X-Frame-Options "SAMEORIGIN"
Header set X-XSS-Protection "1; mode=block"
Header set Referrer-Policy "strict-origin-when-cross-origin"
Header set Permissions-Policy "geolocation=(), microphone=(), camera=()"

# Content Security Policy
Header set Content-Security-Policy "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
```

**Nginx (nginx.conf)**
```nginx
server {
    listen 443 ssl http2;
    server_name ihre-domain.de;
    
    root /var/www/holzbau-karampas;
    index index.html;
    
    # Security Headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;" always;
    
    # HTTPS Redirect
    if ($scheme != "https") {
        return 301 https://$server_name$request_uri;
    }
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

---

## 📧 Kontaktformular Backend

Das Formular in `contact.html` benötigt ein Backend zur Verarbeitung. 

### Option A: Formspree.io (Empfohlen für Einfachheit)

1. Konto erstellen auf https://formspree.io
2. Neues Formular anlegen
3. Form-ID kopieren
4. In `contact.html` anpassen:
   ```html
   <form action="https://formspree.io/f/IHRE_FORM_ID" method="POST">
   ```

**Vorteile:**
- DSGVO-konform (EU-Server verfügbar)
- Spam-Schutz integriert
- Einfache Einrichtung
- Kostenlos bis 50 Submissions/Monat

### Option B: Netlify Forms

Wenn auf Netlify gehostet:
```html
<form data-netlify="true" name="contact" method="POST">
```

### Option C: Eigener PHP-Endpoint

Erstellen Sie `contact-handler.php` auf Ihrem Server:

```php
<?php
// Sicherheitsheader
header('Content-Type: application/json');
header('X-Content-Type-Options: nosniff');

// Nur POST-Requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    exit('Method Not Allowed');
}

// Input validieren und sanitizen
$name = filter_input(INPUT_POST, 'name', FILTER_SANITIZE_STRING);
$email = filter_input(INPUT_POST, 'email', FILTER_SANITIZE_EMAIL);
$phone = filter_input(INPUT_POST, 'phone', FILTER_SANITIZE_STRING);
$subject = filter_input(INPUT_POST, 'subject', FILTER_SANITIZE_STRING);
$message = filter_input(INPUT_POST, 'message', FILTER_SANITIZE_STRING);

// Honeypot-Check (Spam-Schutz)
if (!empty($_POST['_gotcha'])) {
    http_response_code(400);
    exit('Spam detected');
}

// E-Mail validieren
if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    exit('Invalid email');
}

// E-Mail versenden
$to = 'ihre@email.de';
$email_subject = "Kontaktanfrage: $subject";
$email_body = "Name: $name\nE-Mail: $email\nTelefon: $phone\n\nNachricht:\n$message";
$headers = "From: noreply@ihre-domain.de\r\nReply-To: $email";

if (mail($to, $email_subject, $email_body, $headers)) {
    http_response_code(200);
    echo json_encode(['success' => true]);
} else {
    http_response_code(500);
    echo json_encode(['success' => false]);
}
?>
```

In `contact.html`:
```html
<form action="contact-handler.php" method="POST">
```

---

## 📝 Pflicht-Seiten erstellen

### 1. Impressum (impressum.html)

**Gesetzlich erforderliche Angaben (§ 5 TMG):**
- Vollständiger Name des Betreibers
- Anschrift der Werkstatt
- Kontaktdaten (Telefon, E-Mail)
- USt-IdNr. (falls vorhanden)
- Berufsgenossenschaft
- Zuständige Kammer (Handwerkskammer)

**Template:**
```html
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Impressum - Holzbau Karampas</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- Navigation einbinden -->
    
    <section class="page-header">
        <div class="container">
            <h1 class="page-title">Impressum</h1>
        </div>
    </section>
    
    <section style="padding: 4rem 0;">
        <div class="container">
            <h2>Angaben gemäß § 5 TMG</h2>
            <p>
                [Ihr vollständiger Name]<br>
                [Straße und Hausnummer]<br>
                [PLZ und Ort]
            </p>
            
            <h3>Kontakt</h3>
            <p>
                Telefon: [Telefonnummer]<br>
                E-Mail: [E-Mail-Adresse]
            </p>
            
            <h3>Berufsbezeichnung</h3>
            <p>Schreiner (Geselle)</p>
            
            <h3>Zuständige Kammer</h3>
            <p>Handwerkskammer [Ihre Region]</p>
            
            <h3>Berufsgenossenschaft</h3>
            <p>BG Holz und Metall</p>
            
            <!-- Weitere gesetzlich erforderliche Angaben -->
        </div>
    </section>
    
    <!-- Footer einbinden -->
</body>
</html>
```

### 2. Datenschutzerklärung (datenschutz.html)

**Wichtige Punkte:**
- Verantwortlicher für Datenverarbeitung
- Kontaktformular: Welche Daten werden erhoben und wie lange gespeichert
- Server-Logs (falls vorhanden)
- Rechte der Betroffenen (Auskunft, Löschung, etc.)
- Datenschutzbeauftragter (bei Bedarf)

**Empfehlung:** Nutzen Sie einen Generator wie:
- https://www.datenschutz-generator.de/
- https://www.e-recht24.de/muster-datenschutzerklaerung.html

**WICHTIG:** Passen Sie die Datenschutzerklärung an Ihre tatsächliche Datenverarbeitung an!

---

## 🖼️ Bilder hinzufügen

### Bildoptimierung vor Upload

1. **Komprimierung:**
   - Online-Tools: TinyPNG, Squoosh.app
   - CLI: ImageMagick, jpegoptim

2. **Responsive Bilder:**
   ```html
   <picture>
       <source media="(max-width: 600px)" srcset="bild-small.jpg">
       <source media="(max-width: 1200px)" srcset="bild-medium.jpg">
       <img src="bild-large.jpg" alt="Beschreibung">
   </picture>
   ```

3. **Lazy Loading:**
   ```html
   <img src="bild.jpg" alt="Beschreibung" loading="lazy">
   ```

### Platzhalter ersetzen

Suchen Sie nach `.image-placeholder` in allen HTML-Dateien und ersetzen Sie mit:

```html
<!-- Vorher: -->
<div class="image-placeholder" role="img" aria-label="Projekt 1">
    <span class="placeholder-text">Projekt 1<br>600x400px</span>
</div>

<!-- Nachher: -->
<img src="assets/images/projekt-1.jpg" 
     alt="Maßgefertigte Küche aus Massivholz"
     loading="lazy">
```

**Empfohlene Bildgrößen:**
- Hero-Bild: 1920x1080px
- Portfolio: 800x600px
- Werkstatt/Portrait: 1200x800px

---

## ✅ Security Checklist vor Go-Live

### Pre-Deployment
- [ ] Kontaktformular Backend konfiguriert
- [ ] Impressum mit korrekten Daten erstellt
- [ ] Datenschutzerklärung angepasst
- [ ] Alle Platzhalter-Texte ersetzt
- [ ] Bilder optimiert und hochgeladen
- [ ] Telefonnummer und Adresse aktualisiert
- [ ] Alle Links getestet (interne und externe)

### Server-Konfiguration
- [ ] HTTPS erzwungen (SSL-Zertifikat installiert)
- [ ] Security Headers gesetzt (siehe Beispiele oben)
- [ ] Content Security Policy (CSP) konfiguriert
- [ ] robots.txt erstellt
- [ ] sitemap.xml generiert

### DSGVO-Compliance
- [ ] Kein Google Analytics oder Tracking ohne Consent
- [ ] Keine Social Media Embeds ohne Consent
- [ ] Kontaktformular mit Datenschutz-Checkbox
- [ ] Impressum verlinkt im Footer
- [ ] Datenschutzerklärung verlinkt im Footer
- [ ] Server in EU gehostet (empfohlen)

### Testing
- [ ] Mobile Responsiveness getestet (verschiedene Geräte)
- [ ] Browser-Kompatibilität geprüft (Chrome, Firefox, Safari, Edge)
- [ ] Accessibility getestet (Lighthouse, WAVE)
- [ ] Performance optimiert (PageSpeed Insights)
- [ ] Formular-Submission getestet
- [ ] 404-Seite erstellt

---

## 🛠️ Wartung & Updates

### Regelmäßige Aufgaben

**Monatlich:**
- Formular-Submissions prüfen
- Spam-Filter kontrollieren
- Backup erstellen

**Vierteljährlich:**
- SSL-Zertifikat Ablaufdatum prüfen
- Datenschutzerklärung auf Aktualität prüfen
- Portfolio-Bilder aktualisieren

**Jährlich:**
- Rechtliche Anforderungen prüfen (TMG, DSGVO)
- Inhalte aktualisieren
- Security-Audit durchführen

### Backup-Strategie

```bash
# Einfaches Backup-Script
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backup-holzbau-$DATE.tar.gz /var/www/holzbau-karampas/
# Auf externe Festplatte oder Cloud speichern
```

---

## 📊 Performance-Optimierung

### Bereits implementiert
✅ CSS-only Animationen (keine JavaScript-Overhead)
✅ System-Fonts (keine Font-Downloads)
✅ Minimale HTTP-Requests
✅ Semantic HTML (besseres Caching)

### Weitere Optimierungen

1. **HTTP/2 aktivieren** (auf Server-Ebene)
2. **Gzip/Brotli Kompression** aktivieren
3. **Browser-Caching** konfigurieren:
   ```apache
   <IfModule mod_expires.c>
       ExpiresActive On
       ExpiresByType text/css "access plus 1 year"
       ExpiresByType text/html "access plus 1 hour"
       ExpiresByType image/jpeg "access plus 1 year"
   </IfModule>
   ```

---

## 🆘 Troubleshooting

### Problem: Formular sendet nicht

**Lösung:**
1. Überprüfen Sie die `action` URL in `contact.html`
2. Testen Sie das Backend separat
3. Browser-Konsole auf Fehler prüfen
4. Spam-Filter des E-Mail-Providers prüfen

### Problem: Bilder werden nicht angezeigt

**Lösung:**
1. Pfade überprüfen (relativ vs. absolut)
2. Dateiberechtigungen prüfen (chmod 644)
3. Browser-Cache leeren
4. Developer Tools → Network Tab prüfen

### Problem: CSS wird nicht geladen

**Lösung:**
1. Pfad zu `styles.css` in allen HTML-Dateien prüfen
2. Server-Konfiguration für MIME-Types prüfen
3. Browser-Cache leeren (Strg + F5)

---

## 📞 Support & Kontakt

### Entwickler-Informationen
- Erstellt mit: HTML5, CSS3
- Keine Frameworks oder Libraries
- 100% statische Seite

### Nützliche Ressourcen
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [DSGVO Checkliste](https://www.datenschutz.org/)
- [HTML Validator](https://validator.w3.org/)
- [CSS Validator](https://jigsaw.w3.org/css-validator/)

---

## 📄 Lizenz

Dieses Projekt ist für Holzbau Karampas erstellt.
Alle Rechte vorbehalten.

---

## 🎯 Nächste Schritte

1. **Inhalte personalisieren**
   - Texte anpassen
   - Bilder hochladen
   - Kontaktdaten einfügen

2. **Rechtliche Seiten erstellen**
   - Impressum
   - Datenschutzerklärung

3. **Backend konfigurieren**
   - Formular-Handler einrichten
   - Spam-Schutz aktivieren

4. **Deployment**
   - GitLab Pages konfigurieren
   - Domain verbinden
   - SSL einrichten

5. **Testing & Go-Live**
   - Alle Funktionen testen
   - SEO optimieren
   - Launch! 🚀

---

**Viel Erfolg mit Ihrer neuen Webseite!**

---

## 🌍 Mehrsprachigkeit (i18n) – Auto-Sync Setup

Neue i18n-Struktur ist vorbereitet:
- `i18n/de.json` (Master)
- `i18n/en.json`, `fr.json`, `el.json`, `it.json`, `es.json`, `de-AT.json`
- `scripts/i18n_sync.py` (automatische Key-Erkennung + Übersetzung fehlender Werte)
- `.github/workflows/i18n-sync.yml` (manueller Workflow)
- `I18N-ROADMAP.md` (Rollout-Plan)

### Ziel-Workflow
1. Nur `de.json` bearbeiten
2. `python3 scripts/i18n_sync.py` ausführen
3. Übersetzungen werden automatisch ergänzt
4. Review + Deploy

