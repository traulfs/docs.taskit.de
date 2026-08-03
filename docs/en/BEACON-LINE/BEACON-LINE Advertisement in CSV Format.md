---
tags:
  - bluetooth
  - ble
  - protocol
  - beaconline
  - technology
  - csv
erstellt: 2026-05-24
aktualisiert: 2026-05-24
quelle: BLE/BcastPacket-Tabelle 1.csv
status: reference
---

# BeaconLine Advertisement in CSV Format

BLE advertisements observed by the [[BeaconLine Scanning|Bline anchor]] (see [[BeaconLine Scanning 2026-05-22 13.33.13.excalidraw]]) are output as **one line per reception** over TCP port 4000 / MQTT / NATS / REST. The line is a flat comma-separated list with a fixed field order — one of the fields contains the complete raw BLE data as a hex string, decoded according to [[BLE/taskit BLE Manufacturer Advertisement]].

---

## 1. Line Structure

```
<timestamp_ms>,<anchor>,<mac>,<rssi>,<conn>,<adv_hex>,<node_name>
```

| # | Field | Type | Unit / Values | Description |
|:-:|---|---|---|---|
| 1 | `timestamp_ms` | uint64 | Unix ms (UTC) | Reception timestamp at the anchor — milliseconds since epoch. |
| 2 | `anchor` | string | `bline-<SN>-<port>` | Identifier of the Bline anchor that observed the packet. `SN` = serial number, `port` = HCI index. |
| 3 | `mac` | string | `aabbccddeeff` | BLE source address of the sender (public or random, possibly RPI) — **without colons**, 12 hex characters in a row. |
| 4 | `rssi` | int8 | dBm | Received signal strength (typ. −30 … −100). |
| 5 | `conn` | char | `C` / `N` | `C` = **C**onnectable advertisement, `N` = **N**on-connectable. |
| 6 | `adv_hex` | hex string | 0…62 hex characters (≤ 31 bytes) | Complete advertising PDU as lowercase hex — see [[BLE/taskit BLE Manufacturer Advertisement]]. |
| 7 | `node_name` | string | UTF-8 | Node name (complete local name from scan response, or assigned via configuration). |

> **Notes**
> - Separator is `,` (comma). Fields themselves contain no commas; `adv_hex` is guaranteed hex-only, `node_name` is taskit-internal and comma-free.
> - Line ending is `\n` (LF). No header line, no quoting.
> - Multiple anchors seeing the same packet → multiple lines with identical `mac` + `adv_hex`, but different `anchor`, `rssi`, and possibly `timestamp_ms`.

---

## 2. Example Line

```
1779364221617,bline-80346594359-01,404cca5bbf1e,-80,C,0201061bff7b0120000c8e404cca5bbf1e335f676173330000000000208044,taskit_m2go.Mems
```

| Field | Value | Meaning |
|---|---|---|
| `timestamp_ms` | `1779364221617` | 2026-05-22 11:50:21.617 UTC |
| `anchor` | `bline-80346594359-01` | Bline anchor SN `80346594359`, HCI index `01` |
| `mac` | `404cca5bbf1e` | BLE address of the sensor |
| `rssi` | `-80` | −80 dBm (medium distance) |
| `conn` | `C` | Connectable |
| `adv_hex` | `0201061bff7b0120000c8e404cca5bbf1e335f676173330000000000208044` | 31-byte advertising payload |
| `node_name` | `taskit_m2go.Mems` | M2Go node with MEMS sensor |

---

## 3. Decoding `adv_hex` (Example)

Applying the table from [[BLE/taskit BLE Manufacturer Advertisement]] to the 31 bytes:

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
| 12–17 | `40 4c ca 5b bf 1e` | MAC | `404cca5bbf1e` (identical to field 3) |
| 18–27 | `33 5f 67 61 73 33 00 00 00 00 00` | Name (ASCII, zero-padded) | `"3_gas3"` |
| 28–31 | `00 20 80 44` | **Value** | IEEE 754 float (LE) → **1024.25** |

> **Float endianness:** bytes 28–31 = `00 20 80 44` are read as little endian → `0x44802000` → `1024.25`. A big-endian interpretation `0x00208044` would produce a subnormal value (~3·10⁻³⁹) and is therefore ruled out.

---

## 4. Parser Sketch (Pseudo)

```python
def parse_line(line: str) -> dict:
    ts, anchor, mac, rssi, conn, adv, name = line.rstrip("\n").split(",", 6)
    raw = bytes.fromhex(adv)
    return {
        "ts_ms":   int(ts),
        "anchor":  anchor,
        "mac":     mac,
        "rssi":    int(rssi),
        "conn":    conn == "C",
        "type":    raw[7],          # 0x02 / 0x20 / 0x30 / 0x40 / 0x50
        "version": raw[8],
        "hw_id":   raw[9],
        "unit_id": raw[10],
        "value":   struct.unpack("<f", raw[27:31])[0],   # LE float
        "name":    name,
    }
```

`split(",", 6)` is important: it ensures any stray delimiter characters end up in the last field and don't break parsing, even if `node_name` should ever contain a comma.

---

## 5. Special Cases

| Situation | Effect in CSV |
|---|---|
| Sender without scan response | `node_name` is empty (line ends with `,`). |
| RPI frame (`Type = 0x30`) | `mac` contains the *random* address of the current interval; the physical MAC cannot be derived. |
| Anchor beacon (`Type = 0x40`) | `node_name` contains the anchor name; the `Value` field carries no sensor measurement. |
| Text frame (`Type = 0x50`) | Bytes 12–31 contain ASCII; the float interpretation does not apply. |
| Apple iBeacon-compatible (`Type = 0x02`) | Bytes 26–31 follow the Apple layout (major / minor / RSSI calibration). |

---

## 6. Related Notes

- [[BEACON-LINE Advertisement in JSON Format]] — Alternative representation of the same fields as JSON/NDJSON
- [[BLE/taskit BLE Manufacturer Advertisement]] — Complete frame specification
- [[BLE/BcastPacket-Tabelle 1.csv]] — Original table
- [[BeaconLine Scanning 2026-05-22 13.33.13.excalidraw]] — Data path anchor → server → app
- [[SenML Units]] — Meaning of the unit IDs
- [[API]] — BeaconLine Server HTTP REST API
