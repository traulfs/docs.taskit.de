---
tags:
  - bluetooth
  - ble
  - protocol
  - beaconline
  - technology
  - json
erstellt: 2026-07-15
aktualisiert: 2026-07-15
quelle: BLE/BcastPacket-Tabelle 1.csv
status: reference
description: "JSON-Format von BeaconLine: BLE-Advertisements eines Bline-Anchors als NDJSON, ein Objekt pro Empfang mit nativen JSON-Typen; Zuordnung zum CSV-Format."
---

# BeaconLine-Advertisement im JSON-Format

Alternative Darstellung zum [[BEACON-LINE Advertisement in CSV Format|BeaconLine-Advertisement im CSV-Format]]: Vom Bline-Anchor empfangene BLE-Advertisements werden als **ein JSON-Objekt pro Empfang** ausgegeben – **NDJSON / JSON Lines** (ein vollständiges JSON-Objekt pro Zeile, getrennt durch `\n`), nicht als ein großes JSON-Array. Es sind dieselben Felder wie im CSV-Format, aber mit **nativen JSON-Typen** statt einer flachen Kommaliste. Eines der Felder enthält weiterhin die vollständigen BLE-Rohdaten als Hex-String, dekodiert gemäß [[BLE/taskit BLE Manufacturer Advertisement]].

---

## 1. Objektaufbau

```json
{"ts_ms": <uint64>, "anchor": "<string>", "mac": "<string>", "rssi": <int8>, "connectable": <bool>, "adv_hex": "<hex-string>", "node_name": "<string|null>"}
```

| Feld | Typ | Einheit / Werte | Beschreibung | Entspricht CSV-Feld |
|---|---|---|---|---|
| `ts_ms` | number (uint64) | Unix ms (UTC) | Zeitstempel des Empfangs am Anchor – Millisekunden seit Epoch. | `timestamp_ms` |
| `anchor` | string | `bline-<SN>-<port>` | Kennung des Bline-Anchors, der das Paket empfangen hat. `SN` = Seriennummer, `port` = HCI-Index. | `anchor` |
| `mac` | string | `aabbccddeeff` | BLE-Quelladresse des Senders (öffentlich oder zufällig, ggf. RPI) – **ohne Doppelpunkte**, 12 Hex-Zeichen am Stück. | `mac` |
| `rssi` | number (int) | dBm | Empfangene Signalstärke (typ. −30 … −100). | `rssi` |
| `connectable` | boolean | `true` / `false` | `true` = verbindbares Advertisement, `false` = nicht verbindbar. | `conn` (`C`/`N`) |
| `adv_hex` | string | 0…62 Hex-Zeichen (≤ 31 Bytes) | Vollständige Advertising-PDU als Hex in Kleinbuchstaben – siehe [[BLE/taskit BLE Manufacturer Advertisement]]. | `adv_hex` |
| `node_name` | string \| `null` | UTF-8 | Knotenname (Complete Local Name aus der Scan Response oder per Konfiguration zugewiesen). `null`, wenn unbekannt. | `node_name` |

> **Hinweise**
> - **Ein JSON-Objekt pro Zeile** (NDJSON), Zeilenende `\n`. Kein umschließendes Array, kein Komma zwischen den Zeilen.
> - Die Feldreihenfolge in den JSON-Objekten ist **nicht garantiert** – Parser müssen über den Feldnamen zugreifen, nicht über die Position (anders als beim CSV-Format).
> - `rssi` und `ts_ms` sind **native JSON-Zahlen**, keine Strings – beim Parsen ist keine Umwandlung nötig.
> - `connectable` ist ein **Boolean**, kein einzelnes Zeichen wie `conn` in der CSV.
> - Empfangen mehrere Anchors dasselbe Paket → mehrere Objekte mit identischem `mac` + `adv_hex`, aber unterschiedlichem `anchor`, `rssi` und ggf. `ts_ms`.

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
| `rssi` | `-80` | −80 dBm (mittlere Entfernung) |
| `connectable` | `true` | Verbindbar |
| `adv_hex` | `"0201061bff7b0120000c8e404cca5bbf1e335f676173330000000000208044"` | 31-Byte-Advertising-Payload |
| `node_name` | `"taskit_m2go.Mems"` | M2Go-Knoten mit MEMS-Sensor |

---

## 3. Dekodierung von `adv_hex` (Beispiel)

Identisch mit dem CSV-Format – `adv_hex` ist in beiden Formaten derselbe Hex-String. Anwendung der Tabelle aus [[BLE/taskit BLE Manufacturer Advertisement]] auf die 31 Bytes:

| Byte | Hex | Abschnitt | Bedeutung |
|---:|:---:|---|---|
| 1–3 | `02 01 06` | **Flags AD** | Länge 2, Typ `0x01` (Flags), Wert `0x06` = LE General Discoverable + BR/EDR Not Supported |
| 4 | `1b` | MSD AD | Länge = 27 Bytes (Sensor *mit MAC*) |
| 5 | `ff` | MSD AD | AD-Typ Manufacturer Specific Data |
| 6–7 | `7b 01` | MSD AD | Company ID `0x017B` (taskit, little endian) |
| 8 | `20` | **Typ-Byte** | `0x20` = **Taskit Sensor with MAC** |
| 9 | `00` | Version | Protokollversion 0 |
| 10 | `0c` | Hardware ID | `12` – taskit-Hardware (hier der MEMS-Sensor des M2Go) |
| 11 | `8e` | SenML Unit ID | `142` – herstellerspezifische Einheit |
| 12–17 | `40 4c ca 5b bf 1e` | MAC | `404cca5bbf1e` (identisch mit dem Feld `mac`) |
| 18–27 | `33 5f 67 61 73 33 00 00 00 00 00` | Name (ASCII, mit Nullen aufgefüllt) | `"3_gas3"` |
| 28–31 | `00 20 80 44` | **Wert** | IEEE-754-Float (LE) → **1024.25** |

> **Byte-Reihenfolge des Floats:** Die Bytes 28–31 = `00 20 80 44` werden als Little Endian gelesen → `0x44802000` → `1024.25`. Eine Big-Endian-Interpretation `0x00208044` ergäbe einen subnormalen Wert (~3·10⁻³⁹) und scheidet daher aus.

---

## 4. Parser-Skizze (Pseudocode)

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

Eine manuelle Behandlung des Trennens ist nicht nötig – `json.loads` übernimmt die Typumwandlung (Zahl, Boolean, String, `null`) automatisch. `obj.get("node_name")` liefert `None`, wenn das Feld fehlt oder `null` ist.

---

## 5. Sonderfälle

| Situation | Auswirkung im JSON |
|---|---|
| Sender ohne Scan Response | `node_name` ist `null` (statt eines leeren Felds mit abschließendem Komma in der CSV). |
| RPI-Frame (`Type = 0x30`) | `mac` enthält die *zufällige* Adresse des aktuellen Intervalls; die physische MAC lässt sich nicht ableiten. |
| Anchor Beacon (`Type = 0x40`) | `node_name` enthält den Anchor-Namen; das Feld `Value` trägt keinen Sensormesswert. |
| Text-Frame (`Type = 0x50`) | Die Bytes 12–31 enthalten ASCII; die Float-Interpretation entfällt. |
| Apple-iBeacon-kompatibel (`Type = 0x02`) | Die Bytes 26–31 folgen dem Apple-Layout (Major / Minor / RSSI-Kalibrierung). |

---

## 6. Vergleich CSV vs. JSON

| Aspekt | CSV-Format | JSON-Format |
|---|---|---|
| Rahmung | 1 Zeile = 1 Kommaliste | 1 Zeile = 1 JSON-Objekt (NDJSON) |
| Feldzugriff | über feste Position | über Feldnamen |
| `connectable` | einzelnes Zeichen `C`/`N` | Boolean `true`/`false` |
| Zahlen | als String im Text | native JSON-Zahl |
| Fehlender Name | leeres Feld, Zeile endet mit `,` | `node_name: null` |
| Payload-Größe | kompakter | etwas größer (Feldnamen wiederholen sich pro Zeile) |
| Robustheit bei zusätzlichen Feldern | erfordert Formatänderung | neue Felder können ignoriert werden, abwärtskompatibel |

---

## 7. Verwandte Notizen

- [[BEACON-LINE Advertisement in CSV Format|BeaconLine-Advertisement im CSV-Format]] – ursprüngliches Format / Referenzformat
- [[BLE/taskit BLE Manufacturer Advertisement]] – vollständige Frame-Spezifikation
- [[SenML Units|SenML-Einheiten]] – Bedeutung der Unit IDs
