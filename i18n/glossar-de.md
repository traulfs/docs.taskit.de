# Glossar EN → DE (docs.taskit.de)

Verbindliche Begriffe für die deutsche Übersetzung unter `docs/de/`. Diese Datei liegt außerhalb von `docs/` und wird nicht veröffentlicht.

## Bleibt unverändert

- Produktnamen: Measure2Go, BeaconLine, Bline, BlineServer, P4-IO-Jacks, gpio.net, IO-Nuts, IO-Cards, Port-8, TSB, BlueRTD, RuuviTag, MOKOSmart, flespi
- BLE-Typ- und Frame-Namen: ADV_IND, SCAN_RSP, Flags, Manufacturer Specific Data, Service Data, iBeacon, Eddystone, RAWv2
- Feldnamen, Konstanten, Code (inkl. Kommentare in Codeblöcken), JSON/YAML, OpenAPI-Dateien, API-Pfade, MQTT-Topics und NATS-Subjects, Einheiten, CLI-Befehle
- Befehlsnamen in Tabellen (Write, Read, Set Bit, Return Code …)
- Dateinamen (deutsche Seiten haben denselben Pfad und Dateinamen wie die englischen)

## Begriffe

| EN | DE |
|---|---|
| advertisement / advertising packet | Advertisement / Advertising-Paket |
| scan response | Scan Response |
| reception (of a packet) | Empfang |
| anchor (Bline) | Anchor |
| gateway / edge device | Gateway / Edge-Gerät |
| payload | Payload (im Fließtext auch „Nutzdaten“) |
| field / frame / frame type | Feld / Frame / Frame-Typ |
| lead byte / continuation byte | Lead-Byte / Folgebyte |
| command byte / bit mask | Befehlsbyte / Bitmaske |
| byte order, endianness | Byte-Reihenfolge (little/big endian unverändert) |
| manufacturer-specific data (Fließtext) | herstellerspezifische Daten |
| company identifier | Company Identifier |
| signal strength / timestamp | Signalstärke / Zeitstempel |
| connectable / non-connectable | verbindbar / nicht verbindbar |
| battery voltage | Batteriespannung |
| operating mode / IO jack / pin | Betriebsmodus / IO-Jack / Pin |
| read / write (Fließtext) | lesen / schreiben |
| return code (Fließtext) | Rückgabecode |
| byte stream / input / output byte stream | Bytestrom / Eingangs- / Ausgangsbytestrom |
| publish / subscribe | veröffentlichen (Publish) / abonnieren (Subscribe) |
| baud rate / data bits / parity / stop bits | Baudrate / Datenbits / Parität / Stoppbits |
| floating point / single precision | Gleitkomma / einfache Genauigkeit |
| sign / exponent / mantissa | Vorzeichen / Exponent / Mantisse |
| code point / character encoding | Codepunkt / Zeichenkodierung |
| unit / measurement / measured value | Einheit / Messung / Messwert |
| probe (PT100) | Fühler |
| cloud connectivity | Cloud-Anbindung |
| callback | Callback |
| scope (Abschnitt) / product summary | Geltungsbereich / Produktübersicht |
| overview / example / notes | Übersicht / Beispiel / Hinweise |
| related notes / cross references | Verwandte Notizen / Querverweise |
| draft | Entwurf |
| article number / product page | Artikelnummer / Produktseite |

## Stil

- Sachliches technisches Deutsch; „Sie“, wo der Text die Leserin oder den Leser anspricht.
- Dezimalkomma im Fließtext und in Tabellen mit Messwerten (2,4 GHz, ±0,5 °C); in Code, Hex- und Binärbeispielen bleibt der Punkt.
- Wikilinks ohne eigenen Text bekommen einen deutschen Alias: `[[PORT Mode|PORT-Modus]]`. Produkt- und Spezifikationsnamen (z. B. `[[TSB]]`, `[[taskit BLE Manufacturer Advertisement]]`) bleiben ohne Alias.
- Jede Seite bekommt eine deutsche `description:` (120–155 Zeichen).
