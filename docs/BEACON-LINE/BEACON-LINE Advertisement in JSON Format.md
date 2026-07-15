---
tags:
  - bluetooth
  - ble
  - protokoll
  - beaconline
  - technik
  - json
erstellt: 2026-07-15
aktualisiert: 2026-07-15
quelle: BLE/BcastPacket-Tabelle 1.csv
status: referenz
---

# BeaconLine Advertisement im JSON-Format

Alternative Darstellung zu [[BEACON-LINE Advertisement in CSV Format]]: Beobachtete BLE-Advertisements werden vom [[BeaconLine Scanning|Bline-Anchor]] (siehe [[BeaconLine Scanning 2026-05-22 13.33.13.excalidraw]]) als **ein JSON-Objekt pro Empfang** ausgegeben — **NDJSON / JSON Lines** (ein vollständiges JSON-Objekt je Zeile, `\n`-getrennt), nicht als ein großes JSON-Array. Dieselben Felder wie im CSV-Format, aber mit **nativen JSON-Typen** statt flacher Komma-Liste. Eines der Felder enthält weiterhin die komplette BLE-Rohdaten als Hex-String, der nach [[BLE/taskit BLE Manufacturer Advertisement]] dekodiert wird.

---

## 1. Objektaufbau

```json
{"ts_ms": <uint64>, "anchor": "<string>", "mac": "<string>", "rssi": <int8>, "connectable": <bool>, "adv_hex": "<hex-string>", "node_name": "<string|null>"}
```

| Feld | Typ | Einheit / Werte | Beschreibung | Entspricht CSV-Feld |
|---|---|---|---|---|
| `ts_ms` | number (uint64) | Unix-ms (UTC) | Empfangszeitstempel am Anchor — Millisekunden seit Epoch. | `timestamp_ms` |
| `anchor` | string | `bline-<SN>-<port>` | Identifier des Bline-Anchors, der das Paket gesehen hat. `SN` = Seriennummer, `port` = HCI-Index. | `anchor` |
| `mac` | string | `aabbccddeeff` | BLE-Quelladresse des Senders (Public oder Random, ggf. RPI) — **ohne Doppelpunkte**, 12 Hex-Zeichen am Stück. | `mac` |
| `rssi` | number (int) | dBm | Empfangsfeldstärke (typ. −30 … −100). | `rssi` |
| `connectable` | boolean | `true` / `false` | `true` = Connectable Advertisement, `false` = Non-Connectable. | `conn` (`C`/`N`) |
| `adv_hex` | string | 0…62 Hex-Zeichen (≤ 31 Bytes) | Vollständige Advertising-PDU als Lowercase-Hex — siehe [[BLE/taskit BLE Manufacturer Advertisement]]. | `adv_hex` |
| `node_name` | string \| `null` | UTF-8 | Knoten-Name (Complete Local Name aus Scan-Response oder per Konfiguration zugewiesen). `null`, wenn unbekannt. | `node_name` |

> **Hinweise**
> - Ein **JSON-Objekt pro Zeile** (NDJSON), Zeilenende `\n`. Kein umschließendes Array, kein Komma zwischen den Zeilen.
> - Feld-Reihenfolge ist bei JSON-Objekten **nicht garantiert** — Parser müssen über die Feldnamen zugreifen, nicht über die Position (Unterschied zum CSV-Format).
> - `rssi` und `ts_ms` sind **echte JSON-Zahlen**, keine Strings — kein Cast beim Parsen nötig.
> - `connectable` ist ein **Boolean**, kein Einzelzeichen wie `conn` im CSV.
> - Mehrere Anchor sehen dasselbe Paket → mehrere Objekte mit identischem `mac` + `adv_hex`, aber unterschiedlichem `anchor`, `rssi` und ggf. `ts_ms`.

---

## 2. Beispielobjekt

```json
{"ts_ms": 1779364221617, "anchor": "bline-80346594359-01", "mac": "404cca5bbf1e", "rssi": -80, "connectable": true, "adv_hex": "0201061bff7b0120000c8e404cca5bbf1e335f676173330000000000208044", "node_name": "taskit_m2go.Mems"}
```

| Feld | Wert | Bedeutung |
|---|---|---|
| `ts_ms` | `1779364221617` | 2026-05-22 11:50:21.617 UTC |
| `anchor` | `"bline-80346594359-01"` | Bline-Anchor SN `80346594359`, HCI-Index `01` |
| `mac` | `"404cca5bbf1e"` | BLE-Adresse des Sensors |
| `rssi` | `-80` | −80 dBm (mittlere Distanz) |
| `connectable` | `true` | Connectable |
| `adv_hex` | `"0201061bff7b0120000c8e404cca5bbf1e335f676173330000000000208044"` | 31 Byte Advertising-Payload |
| `node_name` | `"taskit_m2go.Mems"` | M2Go-Knoten mit MEMS-Sensor |

---

## 3. Dekodierung von `adv_hex` (Beispiel)

Identisch zum CSV-Format — `adv_hex` ist in beiden Formaten derselbe Hex-String. Anwendung der Tabelle aus [[BLE/taskit BLE Manufacturer Advertisement]] auf die 31 Bytes:

| Byte | Hex | Bereich | Bedeutung |
|---:|:---:|---|---|
| 1–3 | `02 01 06` | **Flags AD** | Länge 2, Type `0x01` (Flags), Wert `0x06` = LE General Discoverable + BR/EDR Not Supported |
| 4 | `1b` | MSD-AD | Länge = 27 Bytes (Sensor *mit MAC*) |
| 5 | `ff` | MSD-AD | AD-Type Manufacturer Specific Data |
| 6–7 | `7b 01` | MSD-AD | Company ID `0x017B` (taskit, Little Endian) |
| 8 | `20` | **Typ-Byte** | `0x20` = **Taskit Sensor mit MAC** |
| 9 | `00` | Version | Protokoll-Version 0 |
| 10 | `0c` | Hardware ID | `12` — taskit-Hardware (hier MEMS-Sensor des M2Go) |
| 11 | `8e` | SenML Unit ID | `142` — herstellerspezifische Einheit |
| 12–17 | `40 4c ca 5b bf 1e` | MAC | `404cca5bbf1e` (identisch zu Feld `mac`) |
| 18–27 | `33 5f 67 61 73 33 00 00 00 00 00` | Name (ASCII, 0-gepaddet) | `"3_gas3"` |
| 28–31 | `00 20 80 44` | **Value** | IEEE 754 Float (LE) → **1024.25** |

> **Float-Endianness:** Bytes 28–31 = `00 20 80 44` werden als Little-Endian gelesen → `0x44802000` → `1024.25`. Big-Endian-Interpretation `0x00208044` ergäbe einen subnormalen Wert (~3·10⁻³⁹) und ist somit ausgeschlossen.

---

## 4. Parser-Skizze (Pseudo)

```python
import json, struct

def parse_line(line: str) -> dict:
    obj = json.loads(line.rstrip("\n"))
    raw = bytes.fromhex(obj["adv_hex"])
    return {
        "ts_ms":   obj["ts_ms"],
        "anchor":  obj["anchor"],
        "mac":     obj["mac"],
        "rssi":    obj["rssi"],
        "conn":    obj["connectable"],
        "type":    raw[7],          # 0x02 / 0x20 / 0x30 / 0x40 / 0x50
        "version": raw[8],
        "hw_id":   raw[9],
        "unit_id": raw[10],
        "value":   struct.unpack("<f", raw[27:31])[0],   # LE float
        "name":    obj.get("node_name"),
    }
```

Kein manuelles Split-Handling nötig — `json.loads` übernimmt Typkonvertierung (Zahl, Bool, String, `null`) automatisch. `obj.get("node_name")` liefert `None`, falls das Feld fehlt oder `null` ist.

---

## 5. Sonderfälle

| Situation | Auswirkung im JSON |
|---|---|
| Sender ohne Scan-Response | `node_name` ist `null` (statt leerem Feld mit Trailing-Komma im CSV). |
| RPI-Frame (`Type = 0x30`) | `mac` enthält die *zufällige* Random-Address des aktuellen Intervalls; physische MAC ist nicht ableitbar. |
| Anchor-Beacon (`Type = 0x40`) | `node_name` enthält den Anchor-Namen, `Value`-Feld trägt keine Sensormessung. |
| Text-Frame (`Type = 0x50`) | Bytes 12–31 enthalten ASCII; die Float-Auswertung ist nicht anzuwenden. |
| Apple-iBeacon-kompatibel (`Type = 0x02`) | Bytes 26–31 nach Apple-Layout (Major / Minor / RSSI-Calibration). |

---

## 6. CSV vs. JSON im Vergleich

| Aspekt | CSV-Format | JSON-Format |
|---|---|---|
| Rahmung | 1 Zeile = 1 Komma-Liste | 1 Zeile = 1 JSON-Objekt (NDJSON) |
| Feldzugriff | über feste Position | über Feldnamen |
| `connectable` | Einzelzeichen `C`/`N` | Boolean `true`/`false` |
| Zahlen | als String im Text | native JSON-Zahl |
| Fehlender Name | leeres Feld, Zeile endet mit `,` | `node_name: null` |
| Payload-Größe | kompakter | etwas größer (Feldnamen wiederholen sich je Zeile) |
| Robustheit bei Zusatzfeldern | erfordert Formatänderung | neue Felder sind rückwärtskompatibel ignorierbar |

---

## 7. Verwandte Notizen

- [[BEACON-LINE Advertisement in CSV Format]] — Original-/Referenzformat
- [[BLE/taskit BLE Manufacturer Advertisement]] — Vollständige Frame-Spezifikation
- [[BLE/BcastPacket-Tabelle 1.csv]] — Originaltabelle
- [[BeaconLine Scanning 2026-05-22 13.33.13.excalidraw]] — Datenpfad Anchor → Server → App
- [[SenML Units]] — Bedeutung der Unit-IDs
