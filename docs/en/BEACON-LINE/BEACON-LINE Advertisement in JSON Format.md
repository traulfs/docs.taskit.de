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
---

# BeaconLine Advertisement in JSON Format

Alternative representation to [[BEACON-LINE Advertisement in CSV Format]]: BLE advertisements observed by the Bline anchor are output as **one JSON object per reception** — **NDJSON / JSON Lines** (one complete JSON object per line, separated by `\n`), not as one large JSON array. Same fields as in the CSV format, but with **native JSON types** instead of a flat comma list. One of the fields still contains the complete raw BLE data as a hex string, decoded according to [[BLE/taskit BLE Manufacturer Advertisement]].

---

## 1. Object Structure

```json
{"ts_ms": <uint64>, "anchor": "<string>", "mac": "<string>", "rssi": <int8>, "connectable": <bool>, "adv_hex": "<hex-string>", "node_name": "<string|null>"}
```

| Field | Type | Unit / Values | Description | Corresponds to CSV field |
|---|---|---|---|---|
| `ts_ms` | number (uint64) | Unix ms (UTC) | Reception timestamp at the anchor — milliseconds since epoch. | `timestamp_ms` |
| `anchor` | string | `bline-<SN>-<port>` | Identifier of the Bline anchor that observed the packet. `SN` = serial number, `port` = HCI index. | `anchor` |
| `mac` | string | `aabbccddeeff` | BLE source address of the sender (public or random, possibly RPI) — **without colons**, 12 hex characters in a row. | `mac` |
| `rssi` | number (int) | dBm | Received signal strength (typ. −30 … −100). | `rssi` |
| `connectable` | boolean | `true` / `false` | `true` = connectable advertisement, `false` = non-connectable. | `conn` (`C`/`N`) |
| `adv_hex` | string | 0…62 hex characters (≤ 31 bytes) | Complete advertising PDU as lowercase hex — see [[BLE/taskit BLE Manufacturer Advertisement]]. | `adv_hex` |
| `node_name` | string \| `null` | UTF-8 | Node name (complete local name from scan response, or assigned via configuration). `null` if unknown. | `node_name` |

> **Notes**
> - **One JSON object per line** (NDJSON), line ending `\n`. No enclosing array, no comma between lines.
> - Field order in JSON objects is **not guaranteed** — parsers must access fields by name, not by position (unlike the CSV format).
> - `rssi` and `ts_ms` are **native JSON numbers**, not strings – no cast needed when parsing.
> - `connectable` is a **boolean**, not a single character like `conn` in the CSV.
> - Multiple anchors seeing the same packet → multiple objects with identical `mac` + `adv_hex`, but different `anchor`, `rssi`, and possibly `ts_ms`.

---

## 2. Example Object

```json
{"ts_ms": 1779364221617, "anchor": "bline-80346594359-01", "mac": "404cca5bbf1e", "rssi": -80, "connectable": true, "adv_hex": "0201061bff7b0120000c8e404cca5bbf1e335f676173330000000000208044", "node_name": "taskit_m2go.Mems"}
```

| Field | Value | Meaning |
|---|---|---|
| `ts_ms` | `1779364221617` | 2026-05-22 11:50:21.617 UTC |
| `anchor` | `"bline-80346594359-01"` | Bline anchor SN `80346594359`, HCI index `01` |
| `mac` | `"404cca5bbf1e"` | BLE address of the sensor |
| `rssi` | `-80` | −80 dBm (medium distance) |
| `connectable` | `true` | Connectable |
| `adv_hex` | `"0201061bff7b0120000c8e404cca5bbf1e335f676173330000000000208044"` | 31-byte advertising payload |
| `node_name` | `"taskit_m2go.Mems"` | M2Go node with MEMS sensor |

---

## 3. Decoding `adv_hex` (Example)

Identical to the CSV format — `adv_hex` is the same hex string in both formats. Applying the table from [[BLE/taskit BLE Manufacturer Advertisement]] to the 31 bytes:

| Byte | Hex | Section | Meaning |
|---:|:---:|---|---|
| 1–3 | `02 01 06` | **Flags AD** | Length 2, type `0x01` (flags), value `0x06` = LE General Discoverable + BR/EDR Not Supported |
| 4 | `1b` | MSD AD | Length = 27 bytes (sensor *with MAC*) |
| 5 | `ff` | MSD AD | AD type Manufacturer Specific Data |
| 6–7 | `7b 01` | MSD AD | Company ID `0x017B` (taskit, little endian) |
| 8 | `20` | **Type byte** | `0x20` = **Taskit Sensor with MAC** |
| 9 | `00` | Version | Protocol version 0 |
| 10 | `0c` | Hardware ID | `12` — taskit hardware (here, the M2Go's MEMS sensor) |
| 11 | `8e` | SenML Unit ID | `142` — manufacturer-specific unit |
| 12–17 | `40 4c ca 5b bf 1e` | MAC | `404cca5bbf1e` (identical to the `mac` field) |
| 18–27 | `33 5f 67 61 73 33 00 00 00 00 00` | Name (ASCII, zero-padded) | `"3_gas3"` |
| 28–31 | `00 20 80 44` | **Value** | IEEE 754 float (LE) → **1024.25** |

> **Float endianness:** bytes 28–31 = `00 20 80 44` are read as little endian → `0x44802000` → `1024.25`. A big-endian interpretation `0x00208044` would produce a subnormal value (~3·10⁻³⁹) and is therefore ruled out.

---

## 4. Parser Sketch (Pseudo)

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

No manual split handling needed — `json.loads` handles type conversion (number, bool, string, `null`) automatically. `obj.get("node_name")` returns `None` if the field is missing or `null`.

---

## 5. Special Cases

| Situation | Effect in JSON |
|---|---|
| Sender without scan response | `node_name` is `null` (instead of an empty field with a trailing comma in the CSV). |
| RPI frame (`Type = 0x30`) | `mac` contains the *random* address of the current interval; the physical MAC cannot be derived. |
| Anchor beacon (`Type = 0x40`) | `node_name` contains the anchor name; the `Value` field carries no sensor measurement. |
| Text frame (`Type = 0x50`) | Bytes 12–31 contain ASCII; the float interpretation does not apply. |
| Apple iBeacon-compatible (`Type = 0x02`) | Bytes 26–31 follow the Apple layout (major / minor / RSSI calibration). |

---

## 6. CSV vs. JSON Comparison

| Aspect | CSV format | JSON format |
|---|---|---|
| Framing | 1 line = 1 comma list | 1 line = 1 JSON object (NDJSON) |
| Field access | by fixed position | by field name |
| `connectable` | single character `C`/`N` | boolean `true`/`false` |
| Numbers | as string in text | native JSON number |
| Missing name | empty field, line ends with `,` | `node_name: null` |
| Payload size | more compact | somewhat larger (field names repeat per line) |
| Robustness with additional fields | requires format change | new fields can be ignored, backward-compatible |

---

## 7. Related Notes

- [[BEACON-LINE Advertisement in CSV Format]] — original/reference format
- [[BLE/taskit BLE Manufacturer Advertisement]] — complete frame specification
- [[SenML Units]] — meaning of the unit IDs
