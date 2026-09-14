# Issue #16 – Entscheidung zum Direktversand

Stand: 14. September 2026. **Servercode und Browserintegration implementiert; öffentlicher Direktversand noch nicht aktiviert.**

## Umsetzung dieser Fortsetzung

Die zuvor vorgeschlagene Architektur liegt unter `server/` als ausführbarer Dienst mit Operator-Anleitung, gepinnten Abhängigkeiten und eigenem CI-Workflow vor. Die Browserintegration befindet sich in `assets/js/inquiry-delivery.js` und ist über eine getrennte Konfiguration abschaltbar. Lokale SMTP-Testempfänger und simulierte Netzfehler sind ausdrücklich keine Nachweise des tatsächlichen Proton-Eingangs. Produktionsaktivierung und Empfangsprüfung sind weiter offen.

## Verifizierter Ausgangspunkt

Die Webseite wird über GitHub Pages veröffentlicht. Der öffentliche DNS-Eintrag für `www.ef-sinn.de` verweist auf `mki13.github.io`; die MX-Einträge der Domain verweisen auf Proton. Im Website-Repository wurde keine vorhandene Backend-/Hosting-Konfiguration gefunden. Die gezielte Suche nach zugehörigen Hostingunterlagen im verbundenen Postfach ergab keinen Treffer. Das ist kein Nachweis, dass der Inhaber nirgendwo weiteres Hosting besitzt.

GitHub Pages stellt statische Dateien bereit und ist kein Laufzeitserver für den Formularversand. Ein Proton-Postfach ist ebenfalls noch kein öffentliches Formular-Backend. Auf dem GEEKOM-PC werden für diese Aufgabe weder Ports ins Internet geöffnet noch bestehende Hermes- oder andere Projektprozesse als öffentlichen Empfangsserver umfunktioniert.

## Implementierte Architektur, öffentliche Bereitstellung noch offen

Die Webseite bleibt auf GitHub Pages. Ein getrenntes, kleines HTTPS-Backend in der EU prüft Anfragen und Fotos serverseitig. Es führt eine begrenzte, dauerhafte Versandwarteschlange mit eindeutiger Anfragekennung; E-Mails werden über einen eigenen, nur für die Webseite erteilten SMTP-Zugang versendet. Das vorhandene Proton-Konto ist dafür zuerst zu prüfen, bevor ein weiterer Versanddienst beauftragt wird.

Proton dokumentiert SMTP-Submission für bezahlte Mailtarife mit eigener Domain. Dafür ist ein gesonderter SMTP-Token nötig; das normale Kontopasswort darf nicht verwendet werden. Ob der konkrete Zugang bereitsteht, wurde nicht bestätigt. Ein gesunder DNS-Eintrag beweist weder SMTP-Freigabe noch Zustellung.

## Nicht ungeprüft durch einen Formularanbieter ersetzen

Form.taxi wurde als wartungsarme Alternative anhand der offiziellen Dokumentation geprüft. Dateiübertragungen erfordern dort einen bezahlten Tarif. Die Dokumentation verweist für individuelle Inhaltsregeln auf Prüfungen im Browser; ein Nachweis der in Issue #16 verlangten serverseitigen Regeln und Duplikatkontrolle liegt damit nicht vor. Außerdem entstehen zusätzliche Datenverarbeiter und Aufbewahrungspflichten. Deshalb keine Registrierung, keine Aktivierung und keine Kostenfreigabe als erteilt behandeln.

## Abnahme nach Freigabe der Infrastruktur

Das Backend muss Pflichtfelder, Rückkontakt, Feldlängen, Bildanzahl, tatsächliche Dateitypen und Gesamtgröße prüfen. Fotos dürfen nicht ausführbar gespeichert oder öffentlich abrufbar werden. Missbrauchsschutz, begrenzte Aufbewahrung, sichere Protokollierung ohne Nachrichteninhalte und eine dokumentierte Löschung gehören zur Abnahme. Browser-Prüfungen ersetzen die serverseitigen Prüfungen nicht.

Die Oberfläche bleibt siebensprachig. Sie unterscheidet klar zwischen Übertragung, Annahme durch den Server, Übergabe an SMTP und tatsächlich verifiziertem Testeingang. Bei unklarer SMTP-Antwort oder Timeout erfolgt kein automatischer Neuversand mit Duplikatrisiko. Eingaben und Ausweichwege bleiben erhalten; Doppelklick und wiederholte Anfragekennung dürfen nicht mehrere Nachrichten auslösen.

Für den Ende-zu-Ende-Test ist eine ausdrücklich freigegebene synthetische Nachricht mit Foto nötig. Der tatsächliche Empfang bei `info@ef-sinn.de`, korrekte Antwortadresse und lesbarer Anhang werden nachgewiesen. Erst danach darf die Produktionskonfiguration auf Direktversand umgeschaltet und Issue #16 geschlossen werden. Bis dahin bleibt der bestehende E-Mail-/Kopier-/Textdatei-Weg vollständig funktionsfähig.

## Noch erforderliche Entscheidung des Inhabers

Entweder vorhandenes, geeignetes EU-Hosting für das getrennte Backend benennen und freigeben, oder die Auswahl eines neuen Hostingangebots samt Kostenrahmen freigeben. Danach den gesonderten SMTP-Zugang am gewählten Backend sicher hinterlegen; keine Geheimnisse in Chat, Repository, Frontend oder öffentliche Protokolle übernehmen. Ohne diese Grundlage wäre eine Aktivierung keine abgeschlossene, überprüfbare Lösung.

## Offizielle Quellen, geprüft am 14. September 2026

- GitHub Pages: https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages
- Proton SMTP-Submission: https://proton.me/support/smtp-submission
- Form.taxi Dateiübertragung: https://docs.form.taxi/en/file-uploads
- Form.taxi Validierung: https://docs.form.taxi/en/form-validation
- Form.taxi Verarbeitung/Unterauftragnehmer: https://form.taxi/en/privacy

Die Empfehlung ist eine technische Architekturentscheidung, keine Zusicherung vollständiger rechtlicher Konformität. Anbieterbedingungen und Datenverarbeitung sind vor einer Beauftragung zu prüfen.
