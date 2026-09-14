# EF-Sinn Direktversand – Issue #16

## Betriebsstatus

Die Implementierung enthält echten HTTP-Empfang, serverseitige Foto-/Feldprüfung, eine persistente Warteschlange und SMTP mit TLS. Sie ist **kein Demo-Endpoint**. Die lokale Integration verwendet jedoch ausschließlich einen lokalen Test-Mailserver; das ist **kein Nachweis einer Nachricht im Proton-Postfach**.

Die öffentliche Website bleibt bis zur vollständigen Produktionsabnahme beim bisherigen E-Mail-/Kopier-/Download-Verfahren. `assets/js/inquiry-delivery-config.js` steht absichtlich auf `enabled: false`. Fehlende Hosting- und SMTP-Zugänge werden nicht durch einen unsicheren öffentlichen GEEKOM-Endpunkt oder einen ungefragten neuen Anbieter ersetzt.

## Trennung der Zugangsdaten

Der öffentliche API-Container erhält ausschließlich den Anfrage-HMAC-Schlüssel. Der Proton-SMTP-Token wird nur in den getrennten Worker eingebunden. Die API-Konfiguration liest den SMTP-Token nicht. SMTP-Vorprüfung wird im Worker ausgeführt. Secret-Werte erscheinen nicht in der Darstellung des Konfigurationsobjekts.

## Aufbau

`inquiry_service/app.py` nimmt Formulardaten entgegen. `validation.py` prüft alle Felder, Rückkontakt, Bildanzahl, Dateigrößen und tatsächlich decodierbare JPEG-/PNG-/WebP-Dateien. Bilder werden maximal 2000 Pixel groß neu als JPEG codiert; ursprüngliche Dateinamen und EXIF-Daten werden nicht übernommen. SVG, GIF, defekte Dateien und übergroße Pixelbilder werden abgelehnt.

`store.py` führt eine SQLite-Warteschlange mit privaten Dateirechten. Eine eindeutige Kennung und ein zufälliges Status-Token verhindern doppelte Einreihung; parallele Anfragen werden atomar behandelt. Statusantworten enthalten keine Formulardaten. HMAC-geschützte, zeitlich begrenzte Herausforderungen, eine einmalige Challenge-Nutzung, Honeypot sowie IP-/Gesamtlimits begrenzen Missbrauch. Diese Maßnahmen sind kein Versprechen, sämtliche automatisierten Anfragen zu verhindern.

`worker.py` übergibt an `smtp.protonmail.ch:587`, ausschließlich mit überprüftem STARTTLS und SMTP-Token. Empfänger ist fest `info@ef-sinn.de`; Kundenadressen stehen nur in `Reply-To`. Es handelt sich nicht um ein offenes Mail-Relay. MIME ist für Unicode-Inhalte transportabel codiert.

## Zustände und Wiederholung

`queued` → `sending` → `transmitting` → `smtp_accepted`. Nur ein tatsächlicher, zusätzlich geprüfter INBOX-Eingang darf zu `receipt_verified` führen. Ein angenommenes HTTP-Formular ist keine E-Mail-Zustellbestätigung.

Fehler vor der Übertragung des Nachrichteninhalts und ausdrückliche temporäre SMTP-Ablehnungen dürfen begrenzt wiederholt werden. Ein Verbindungsabbruch während oder nach der Datenübertragung führt zu `uncertain` und **nicht** zu einem automatischen Neuversand. Worker-Leases verhindern, dass ein alter, wieder aufgewachter Worker nach einer Neuzuweisung noch senden kann. Wiederholung einer verlorenen HTTP-Antwort nutzt dieselbe Anfragekennung und denselben unveränderten Inhalt.

Idempotenz- und Statusdaten werden 14 Tage gehalten. Nach erfolgreicher SMTP-Annahme wird der vollständige Nachrichteninhalt aus der Warteschlange entfernt. Nicht abgeschlossene Inhalte bleiben höchstens 7 Tage; eine Anfrage ohne Versandfortschritt läuft nach 72 Stunden als fehlgeschlagen aus. Der Betreiber muss die Warteschlange und Fehler überwachen. Backups müssen die Löschfristen ebenfalls berücksichtigen; Dateilöschung allein ist keine Zusicherung physischer Löschung aus allen Datenträgerkopien.

## Tests

```sh
python -m venv .venv
.venv/bin/pip install --require-hashes -r server/requirements-test.txt
PYTHONPATH=server .venv/bin/python -m pytest server/tests -q
npm ci --prefix qa
(cd qa && npx playwright install chromium)
PYTHONPATH=server .venv/bin/python server/tests/run_browser_integration.py
```

Der Integrationslauf startet eigene Loopback-Server auf freien Ports, erzeugt nur künstliche Testdaten und beendet die eigenen Prozesse anschließend. Geprüft wird Browser → tatsächliche HTTP-API → tatsächliche TLS-SMTP-Verbindung zum lokalen Testempfänger, einschließlich Foto-Inhalt und Reply-To. Fehlerantworten und verlorene HTTP-Antworten werden kontrolliert erzeugt. Es wird keine externe E-Mail versendet. Belege und Screenshots stehen in `.qa-results/`.

## Bereitstellung auf einem freigegebenen EU-Server

Voraussetzungen: ein vom Inhaber freigegebener Server mit Docker/Compose, ein darauf gerichteter eigener API-Hostname und ein gesonderter Proton-SMTP-Token für die freigegebene Absenderadresse. Verträge, Verarbeitungsort, Auftragsverarbeitung und Kosten sind vorher zu klären. GitHub Pages führt diesen Python-Dienst nicht aus.

1. Auf dem Zielserver zwei Dateien **außerhalb** des Repositorys bereitstellen: einen zufälligen HMAC-Schlüssel mit mindestens 32 Bytes und den gesonderten SMTP-Token. Kein Kontopasswort verwenden. Die Dateien müssen für UID/GID 10001 lesbar, für andere Nutzer unlesbar sein; z. B. Eigentümer 10001:10001, Modus 0400. Dateirechte sind besonders wichtig, weil Compose dateibasierte Secrets einbindet.
2. `deployment.env.example` als private Umgebungsdatei auf dem Zielserver ausfüllen. Sie enthält nur Hostnamen, Mailadresse und Pfade, keine Tokenwerte. Den persistenten Datenbereich nicht in einen Webroot legen. Keine Hostports für API oder SQLite veröffentlichen; nach außen geht nur der HTTPS-Proxy.
3. Aus `server/` prüfen und starten: `docker compose --env-file /sicherer/pfad/deployment.env config --quiet`, dann `docker compose --env-file /sicherer/pfad/deployment.env up -d --build`. Diese Befehle sind für den freigegebenen Server, **nicht** für den GEEKOM-Arbeitsrechner gedacht.
4. Mit `docker compose ... exec worker python -m inquiry_service.preflight --smtp` Konfiguration, Datenträger und SMTP-Authentifizierung prüfen. Das sendet noch keine Nachricht. `/healthz` muss erreichbar sein; ein fehlender Worker verhindert die Annahme neuer Anfragen.
5. Erst die nachfolgende echte Abnahme durchführen und den betriebsspezifischen Datenschutzhinweis fertigstellen. Dann die Website-Konfiguration auf den geprüften HTTPS-Origin setzen, die entsprechenden Cache-Versionen aktualisieren und den veröffentlichten Browserablauf erneut testen.

## Echte Abnahme und Empfangsnachweis

Für die Abnahme eine freigegebene synthetische Anfrage mit Foto über die Browseroberfläche an das echte Backend senden. Dabei muss die normale erlaubte Website-Origin verwendet werden; keine Produktions-CORS-Regel zu `*` aufweiten. Den tatsächlichen Eingang in **INBOX** unter `info@ef-sinn.de` prüfen, nicht den Ordner Gesendet.

`python -m inquiry_service.receipt REQUEST_ID --output /privater/pfad/receipt.json` verbindet sich mit einem ausdrücklich konfigurierten IMAP-Zugang, sucht genau diese Message-ID und prüft Nachrichtentext, Antwortadresse und die Hashes der tatsächlich empfangenen Foto-Anhänge. Erforderlich sind `IMAP_HOST`, `IMAP_PORT`, `IMAP_USERNAME` und die Secret-Datei `IMAP_PASSWORD_FILE`; bei einer Bridge mit STARTTLS zusätzlich `IMAP_TLS_MODE=starttls` und gegebenenfalls die vertrauenswürdige CA über `IMAP_CA_FILE`. Zertifikatsprüfung bleibt aktiviert. Die Verifikation wird dort ausgeführt, wo sowohl Warteschlange als auch autorisierter Postfachzugang sicher verfügbar sind; keine Bridge ins Internet öffnen.

Die derzeitige IMAP-Funktion ist ein Betreiber-Abnahmewerkzeug, kein automatisch für jede Kundenanfrage laufender Lesedienst. Eine normale SMTP-Annahme wird deshalb in der Oberfläche ausdrücklich nicht als bestätigter Postfacheingang bezeichnet.

## Vor dem Einschalten der Website zwingend

Der Datenschutzhinweis muss in allen sieben Sprachen den tatsächlichen Backendanbieter, dessen Adresse und Verarbeitungsort, SMTP-Verarbeitung über Proton, Foto-Neucodierung, temporäre Speicherung und Löschfristen beschreiben. Die bisherigen Aussagen zur rein lokalen Vorbereitung dürfen im aktivierten Modus nicht als Beschreibung des Direktversands stehen bleiben. Solange der tatsächliche Betreiber nicht feststeht und kein echter Empfangsnachweis vorliegt, wird die öffentliche Konfiguration nicht aktiviert und Issue #16 nicht geschlossen.

## Betrieb und Rücknahme

Queue-Status über `inquiry_service.preflight` regelmäßig kontrollieren; `failed` oder `uncertain` mit der Anfragekennung bearbeiten, ohne Nachrichteninhalte in öffentliche Logs zu kopieren. Vor Änderungen private Volumes sichern und deren Aufbewahrung begrenzen. Zur Rücknahme zuerst die Website-Konfiguration deaktivieren. Den Worker für bereits angenommene Anfragen weiterlaufen lassen, den Status-Endpunkt erreichbar halten und die vorhandene Queue nicht löschen oder durch einen neuen Schlüssel unlesbar machen. Keine automatischen erneuten Sendungen für unklare Zustände erzwingen.

## Primärquellen

- https://proton.me/support/smtp-submission
- https://flask.palletsprojects.com/en/stable/web-security/
- https://flask.palletsprojects.com/en/stable/config/
- https://docs.python.org/3/library/smtplib.html
- https://docs.docker.com/compose/how-tos/use-secrets/
- https://caddyserver.com/docs/caddyfile/directives/request_body

Die technische Implementierung ist keine pauschale rechtliche Konformitätsbescheinigung.
