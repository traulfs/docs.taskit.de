---
tags:
  - bluetooth
  - ble
  - protokoll
  - beaconline
  - technik
  - csv
erstellt: 2026-05-24
aktualisiert: 2026-05-24
quelle: BLE/BcastPacket-Tabelle 1.csv
status: referenz
---

# BeaconLine Advertisement im CSV-Format

Beobachtete BLE-Advertisements werden vom [[BeaconLine Scanning|Bline-Anchor]] (siehe [[BeaconLine Scanning 2026-05-22 13.33.13.excalidraw]]) als **eine Zeile pro Empfang** über TCP-Port 4000 / MQTT / NATS / REST ausgegeben. Die Zeile ist eine flache Komma-getrennte Liste mit fester Feldreihenfolge — eines der Felder enthält die komplette BLE-Rohdaten als Hex-String, der nach [[BLE/taskit BLE Manufacturer Advertisement]] dekodiert wird.

---

## 1. Zeilenaufbau

```
<timestamp_ms>,<anchor>,<mac>,<rssi>,<conn>,<adv_hex>,<node_name>
```

| # | Feld | Typ | Einheit / Werte | Beschreibung |
|:-:|---|---|---|---|
| 1 | `timestamp_ms` | uint64 | Unix-ms (UTC) | Empfangszeitstempel am Anchor — Millisekunden seit Epoch. |
| 2 | `anchor` | string | `bline-<SN>-<port>` | Identifier des Bline-Anchors, der das Paket gesehen hat. `SN` = Seriennummer, `port` = HCI-Index. |
| 3 | `mac` | string | `aabbccddeeff` | BLE-Quelladresse des Senders (Public oder Random, ggf. RPI) — **ohne Doppelpunkte**, 12 Hex-Zeichen am Stück. |
| 4 | `rssi` | int8 | dBm | Empfangsfeldstärke (typ. −30 … −100). |
| 5 | `conn` | char | `C` / `N` | `C` = **C**onnectable Advertisement, `N` = **N**on-Connectable. |
| 6 | `adv_hex` | hex-string | 0…62 Hex-Zeichen (≤ 31 Bytes) | Vollständige Advertising-PDU als Lowercase-Hex — siehe [[BLE/taskit BLE Manufacturer Advertisement]]. |
| 7 | `node_name` | string | UTF-8 | Knoten-Name (Complete Local Name aus Scan-Response oder per Konfiguration zugewiesen). |

> **Hinweise**
> - Trennzeichen ist `,` (Komma). Felder enthalten selbst keine Kommas; `adv_hex` ist garantiert hex-only, `node_name` taskit-intern ohne Komma.
> - Zeilenende ist `\n` (LF). Keine Header-Zeile, kein Quoting.
> - Mehrere Anchor sehen dasselbe Paket → mehrere Zeilen mit identischem `mac` + `adv_hex`, aber unterschiedlichem `anchor`, `rssi` und ggf. `timestamp_ms`.

---

## 2. Beispielzeile

```
1779364221617,bline-80346594359-01,404cca5bbf1e,-80,C,0201061bff7b0120000c8e404cca5bbf1e335f676173330000000000208044,taskit_m2go.Mems
```

| Feld | Wert | Bedeutung |
|---|---|---|
| `timestamp_ms` | `1779364221617` | 2026-05-22 11:50:21.617 UTC |
| `anchor` | `bline-80346594359-01` | Bline-Anchor SN `80346594359`, HCI-Index `01` |
| `mac` | `404cca5bbf1e` | BLE-Adresse des Sensors |
| `rssi` | `-80` | −80 dBm (mittlere Distanz) |
| `conn` | `C` | Connectable |
| `adv_hex` | `0201061bff7b0120000c8e404cca5bbf1e335f676173330000000000208044` | 31 Byte Advertising-Payload |
| `node_name` | `taskit_m2go.Mems` | M2Go-Knoten mit MEMS-Sensor |

---

## 3. Dekodierung von `adv_hex` (Beispiel)

Anwendung der Tabelle aus [[BLE/taskit BLE Manufacturer Advertisement]] auf die 31 Bytes:

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
| 12–17 | `40 4c ca 5b bf 1e` | MAC | `404cca5bbf1e` (identisch zu Feld 3) |
| 18–27 | `33 5f 67 61 73 33 00 00 00 00 00` | Name (ASCII, 0-gepaddet) | `"3_gas3"` |
| 28–31 | `00 20 80 44` | **Value** | IEEE 754 Float (LE) → **1024.25** |

> **Float-Endianness:** Bytes 28–31 = `00 20 80 44` werden als Little-Endian gelesen → `0x44802000` → `1024.25`. Big-Endian-Interpretation `0x00208044` ergäbe einen subnormalen Wert (~3·10⁻³⁹) und ist somit ausgeschlossen.

---

## 4. Parser-Skizze (Pseudo)

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

`split(",", 6)` ist wichtig: dadurch landen evtl. exotische Trennzeichen-Reste im letzten Feld und zerstören das Parsing nicht, selbst falls `node_name` einmal ein Komma enthält.

---

## 5. Sonderfälle

| Situation | Auswirkung im CSV |
|---|---|
| Sender ohne Scan-Response | `node_name` ist leer (Zeile endet mit `,`). |
| RPI-Frame (`Type = 0x30`) | `mac` enthält die *zufällige* Random-Address des aktuellen Intervalls; physische MAC ist nicht ableitbar. |
| Anchor-Beacon (`Type = 0x40`) | `node_name` enthält den Anchor-Namen, `Value`-Feld trägt keine Sensormessung. |
| Text-Frame (`Type = 0x50`) | Bytes 12–31 enthalten ASCII; die Float-Auswertung ist nicht anzuwenden. |
| Apple-iBeacon-kompatibel (`Type = 0x02`) | Bytes 26–31 nach Apple-Layout (Major / Minor / RSSI-Calibration). |

---

## 6. Verwandte Notizen

- [[BEACON-LINE Advertisement in JSON Format]] — Alternative Darstellung derselben Felder als JSON/NDJSON
- [[BLE/taskit BLE Manufacturer Advertisement]] — Vollständige Frame-Spezifikation
- [[BLE/BcastPacket-Tabelle 1.csv]] — Originaltabelle
- [[BeaconLine Scanning 2026-05-22 13.33.13.excalidraw]] — Datenpfad Anchor → Server → App
- [[SenML Units]] — Bedeutung der Unit-IDs
