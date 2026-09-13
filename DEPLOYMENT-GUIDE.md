# Veröffentlichung

## Produktionskonfiguration

GitHub Pages veröffentlicht den Zweig `main` aus `/` unter `www.ef-sinn.de`. HTTPS ist aktiviert. Diese Konfiguration vor einer Veröffentlichung erneut prüfen. Die Webseite benötigt keinen Produktions-Build und kein PHP-/Node-Backend.

## Ablauf

1. Arbeitszweig aus dem aktuellen `main` erstellen. Keine fremden Arbeitsverzeichnisse oder laufenden Entwicklungsprozesse verändern.
2. Python-Tests, JavaScript-Syntaxprüfung und `qa/browser-audit.mjs` erfolgreich ausführen; Screenshots tatsächlich ansehen.
3. Pull Request gegen `main` erstellen. Testergebnisse, Grenzen und offene Issues dokumentieren.
4. Nur nach Freigabe und grünen Prüfungen mergen. Weder Prüfungen umgehen noch einen fehlgeschlagenen Test als unbedeutend übergehen.
5. Pages-Build bis zu seinem echten Ergebnis prüfen. Anschließend Version der Live-Assets, wichtige Links, Darstellung und Anfrageablauf auf der veröffentlichten Domain verifizieren.
6. `docs/WORK_STATUS.md` aktualisieren. Bei einem Fehler den fehlerhaften Commit über einen Revert-PR zurücknehmen; kein Hard Reset oder Force Push.

## Direktversand

Der aktuelle Assistent bereitet E-Mails lokal vor. Ein `mailto:`-Link und ein Download sind keine Zustellbestätigung. Ein echter Webversand benötigt ein gesondert freigegebenes Backend und einen nachgewiesenen End-to-End-Zustelltest. Bis dahin keinen externen Formularanbieter aktivieren und keinen Versandknopf mit falschem Erfolgsversprechen veröffentlichen.
