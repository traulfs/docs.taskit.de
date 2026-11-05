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
description: "CSV-Ausgabe von BeaconLine: eine Zeile pro BLE-Advertisement eines Bline-Anchors über TCP-Port 4000, MQTT, NATS oder REST, mit Feldern und Beispiel."
---

# BeaconLine-Advertisement im CSV-Format

Vom Bline-Anchor empfangene BLE-Advertisements werden als **eine Zeile pro Empfang** über TCP-Port 4000 / MQTT / NATS / REST ausgegeben. Die Zeile ist eine flache, kommagetrennte Liste mit fester Feldreihenfolge – eines der Felder enthält die vollständigen BLE-Rohdaten als Hex-String, dekodiert gemäß [[BLE/taskit BLE Manufacturer Advertisement]].

---

## 1. Zeilenaufbau

```
<timestamp_ms>,<anchor>,<mac>,<rssi>,<conn>,<adv_hex>,<node_name>
```

| # | Feld | Typ | Einheit / Werte | Beschreibung |
|:-:|---|---|---|---|
| 1 | `timestamp_ms` | uint64 | Unix ms (UTC) | Zeitstempel des Empfangs am Anchor – Millisekunden seit Epoch. |
| 2 | `anchor` | string | `bline-<SN>-<port>` | Kennung des Bline-Anchors, der das Paket empfangen hat. `SN` = Seriennummer, `port` = HCI-Index. |
| 3 | `mac` | string | `aabbccddeeff` | BLE-Quelladresse des Senders (öffentlich oder zufällig, ggf. RPI) – **ohne Doppelpunkte**, 12 Hex-Zeichen am Stück. |
| 4 | `rssi` | int8 | dBm | Empfangene Signalstärke (typ. −30 … −100). |
| 5 | `conn` | char | `C` / `N` | `C` = verbindbares Advertisement (**C**onnectable), `N` = nicht verbindbar (**N**on-connectable). |
| 6 | `adv_hex` | Hex-String | 0…62 Hex-Zeichen (≤ 31 Bytes) | Vollständige Advertising-PDU als Hex in Kleinbuchstaben – siehe [[BLE/taskit BLE Manufacturer Advertisement]]. |
| 7 | `node_name` | string | UTF-8 | Knotenname (Complete Local Name aus der Scan Response oder per Konfiguration zugewiesen). |

> **Hinweise**
> - Trennzeichen ist `,` (Komma). Die Felder selbst enthalten keine Kommas; `adv_hex` besteht garantiert nur aus Hex-Zeichen, `node_name` ist taskit-intern und kommafrei.
> - Zeilenende ist `\n` (LF). Keine Kopfzeile, keine Anführungszeichen.
> - Empfangen mehrere Anchors dasselbe Paket → mehrere Zeilen mit identischem `mac` + `adv_hex`, aber unterschiedlichem `anchor`, `rssi` und ggf. `timestamp_ms`.

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
| `rssi` | `-80` | −80 dBm (mittlere Entfernung) |
| `conn` | `C` | Verbindbar |
| `adv_hex` | `0201061bff7b0120000c8e404cca5bbf1e335f676173330000000000208044` | 31-Byte-Advertising-Payload |
| `node_name` | `taskit_m2go.Mems` | M2Go-Knoten mit MEMS-Sensor |

---

## 3. Dekodierung von `adv_hex` (Beispiel)

Anwendung der Tabelle aus [[BLE/taskit BLE Manufacturer Advertisement]] auf die 31 Bytes:

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
| 12–17 | `40 4c ca 5b bf 1e` | MAC | `404cca5bbf1e` (identisch mit Feld 3) |
| 18–27 | `33 5f 67 61 73 33 00 00 00 00 00` | Name (ASCII, mit Nullen aufgefüllt) | `"3_gas3"` |
| 28–31 | `00 20 80 44` | **Wert** | IEEE-754-Float (LE) → **1024.25** |

> **Byte-Reihenfolge des Floats:** Die Bytes 28–31 = `00 20 80 44` werden als Little Endian gelesen → `0x44802000` → `1024.25`. Eine Big-Endian-Interpretation `0x00208044` ergäbe einen subnormalen Wert (~3·10⁻³⁹) und scheidet daher aus.

---

## 4. Parser-Skizze (Pseudocode)

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

`split(",", 6)` ist wichtig: So landen versehentliche Trennzeichen im letzten Feld und brechen das Parsen nicht, selbst wenn `node_name` jemals ein Komma enthalten sollte.

---

## 5. Sonderfälle

| Situation | Auswirkung in der CSV |
|---|---|
| Sender ohne Scan Response | `node_name` ist leer (Zeile endet mit `,`). |
| RPI-Frame (`Type = 0x30`) | `mac` enthält die *zufällige* Adresse des aktuellen Intervalls; die physische MAC lässt sich nicht ableiten. |
| Anchor Beacon (`Type = 0x40`) | `node_name` enthält den Anchor-Namen; das Feld `Value` trägt keinen Sensormesswert. |
| Text-Frame (`Type = 0x50`) | Die Bytes 12–31 enthalten ASCII; die Float-Interpretation entfällt. |
| Apple-iBeacon-kompatibel (`Type = 0x02`) | Die Bytes 26–31 folgen dem Apple-Layout (Major / Minor / RSSI-Kalibrierung). |

---

## 6. Verwandte Notizen

- [[BEACON-LINE Advertisement in JSON Format|BeaconLine-Advertisement im JSON-Format]] – alternative Darstellung derselben Felder als JSON/NDJSON
- [[BLE/taskit BLE Manufacturer Advertisement]] – vollständige Frame-Spezifikation
- [[SenML Units|SenML-Einheiten]] – Bedeutung der Unit IDs
- [[BEACON-LINE/API|API]] – HTTP-REST-API des BeaconLine Servers
