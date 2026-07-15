---
tags:
  - bluetooth
  - ble
  - protokoll
  - taskit
  - spezifikation
erstellt: 2026-05-10
aktualisiert: 2026-05-18
quelle: BLE/BcastPacket-Tabelle 1.csv
status: referenz
---

# taskit BLE Manufacturer Advertisement Format

Spezifikation des herstellerspezifischen BLE Broadcast-Pakets für taskit-Produkte (BLE Sensor & Beacon).

- Grundlage: [[BLE/BLE Advertisement Format]]
- Quelle: [[BLE/BcastPacket-Tabelle 1.csv]]
- **Company Identifier taskit:** `0x017B` (Little Endian → `0x7B 0x01`)

---

## 1. Paketstruktur

Das Format nutzt das Standard-BLE-Advertising-Paket (31 Bytes) bestehend aus zwei AD-Strukturen:

1. **Flags AD** (3 Bytes) – immer `02 01 06`
2. **Manufacturer Specific Data AD** (variable Länge) mit taskit Company ID

```
┌──────────────┬───────────────────────────────────────────────────────────┐
│  Flags AD    │              Manufacturer Specific Data (0xFF)            │
│              │                                                           │
│  02 01 06    │  [Len] FF  7B 01  [Type] [Version]  [Payload ...]         │
│  3 Bytes     │  variable Länge (Len = 0x1A oder 0x1B, je nach Typ)       │
└──────────────┴───────────────────────────────────────────────────────────┘
```

| Byte | Wert | Bedeutung |
|---:|---|---|
| 1 | `0x02` | Length of Flags AD |
| 2 | `0x01` | AD Type: Flags |
| 3 | `0x06` | LE General Discoverable + BR/EDR Not Supported |
| 4 | `0x1A` / `0x1B` | Length of Manufacturer Specific AD (26 oder 27) |
| 5 | `0xFF` | AD Type: Manufacturer Specific Data |
| 6 | `0x7B` | Company ID Low (taskit) |
| 7 | `0x01` | Company ID High (taskit) |
| 8 | `0x20..0x50` | **Typ-Byte** (Frame-Kennung – siehe Kap. 2) |
| 9 | `0x15` / Version | iBeacon-Length bzw. Protokoll-Version |
| 10–31 | – | typabhängige Nutzdaten |

> Die Bytes 1–7 sind in allen taskit-Varianten identisch (bis auf Byte 4: `0x1A` ohne MAC, `0x1B` mit MAC).

---

## 2. Frame-Typen (Byte 8)

Das Byte 8 unterscheidet zwischen Anonymous (iBeacon-kompatibel) und Named (eigene taskit-Formate):

| Typ-Byte | Kategorie | Name | Byte 4 (Len) | Beschreibung |
|---|---|---|:---:|---|
| `0x02` | Anonymous | **Taskit iBeacon** | `0x1A` | iBeacon-kompatibel (Apple-Layout) mit taskit Company ID |
| `0x20` | Named | **Taskit Sensor mit MAC** | `0x1B` | Sensor-Frame, identifiziert über MAC-Adresse |
| `0x30` | Named | **Taskit Sensor mit RPI** | `0x1A` | Sensor-Frame, identifiziert über Rotating Proximity Identifier (RPI) |
| `0x40` | Named | **Anchor Beacon** | `0x1B` | Ortungs-Anker (z. B. Beaconline) |
| `0x50` | Named | **Text** | `0x1B` | ASCII-Textnachricht |

> **Vergleich Apple iBeacon:** Byte 6/7 = `0x4C 0x00` (Apple), Byte 8 = `0x02`, Byte 9 = `0x15`. Taskit iBeacon verwendet exakt dasselbe Layout, jedoch mit Company ID `0x7B 0x01`.

---

## 3. Komplette Byte-Tabelle

Die folgende Tabelle zeigt die vollständige Belegung aller 31 Bytes für alle Frame-Typen.

| Byte | Apple iBeacon | Taskit iBeacon | Taskit Sensor RPI | Taskit Sensor MAC | Anchor Beacon | Text |
|---:|---|---|---|---|---|---|
| 1 | `0x02` | `0x02` | `0x02` | `0x02` | `0x02` | `0x02` |
| 2 | `0x01` | `0x01` | `0x01` | `0x01` | `0x01` | `0x01` |
| 3 | `0x06` | `0x06` | `0x06` | `0x06` | `0x06` | `0x06` |
| 4 | `0x1A` | `0x1A` | `0x1A` | `0x1B` | `0x1B` | `0x1B` |
| 5 | `0xFF` | `0xFF` | `0xFF` | `0xFF` | `0xFF` | `0xFF` |
| 6 | `0x4C` (Apple) | `0x7B` (taskit) | `0x7B` (taskit) | `0x7B` (taskit) | `0x7B` (taskit) | `0x7B` (taskit) |
| 7 | `0x00` | `0x01` | `0x01` | `0x01` | `0x01` | `0x01` |
| 8 | `0x02` (Type) | `0x02` (Type) | `0x30` (Type) | `0x20` (Type) | `0x40` (Type) | `0x50` (Version) |
| 9 | `0x15` (Len) | `0x15` (Len) | Version | Version | Version | Version |
| 10 | UUID with Type | RPI / UUID | **Hardware ID** | **Hardware ID** | Hardware ID | Hardware ID |
| 11 | UUID | UUID | **SenML Unit ID** | **SenML Unit ID** | SenML Unit ID | SenML Unit ID |
| 12 | UUID | UUID | **RPI / UUID** | **MAC** | MAC | ASCII Text |
| 13–17 | UUID | UUID | RPI / UUID | MAC | MAC | ASCII Text |
| 18–25 | UUID (bis B25) | UUID (bis B25) | – | **Name** (8 B) | Name | ASCII Text |
| 26–27 | Major ID | MajorValue | – | – | – | – |
| 28–31 | Minor (B28-29) + RSSI (B30) | Minor (B28-29) + RSSI (B30) | **Value als 32-Bit Float (IEEE 754)** | **Value als 32-Bit Float (IEEE 754)** | – | – |

> Die Spalten für Blue RTD / Blue Loop RX / Blue Loop TX / Blue pH-Meter sind Spezialisierungen von **Taskit Sensor mit MAC** (Byte 8 = `0x20`) und unterscheiden sich nur in Byte 10 (Hardware ID) und Byte 11 (SenML Unit ID).

---

## 4. Sensor-Payload (Typ `0x20` / `0x30`)

### 4.1 Hardware ID (Byte 10)

| Wert | Gerät |
|---:|---|
| `1` | Blue RTD (Temperatur, PT100/PT1000) |
| `3` | Blue Loop RX (4–20 mA Eingang) |
| `4` | Blue Loop TX (4–20 mA Ausgang) |
| `5` | Blue pH-Meter |

### 4.2 SenML Unit ID (Byte 11)

Nach [RFC 8428 SenML Units](https://www.iana.org/assignments/senml/senml.xhtml):

| Wert | Einheit | Verwendung |
|---:|---|---|
| `55` | `Cel` (°C) | Blue RTD |
| `75` | `pH` | Blue pH-Meter |
| `143` | `mA` (Milliampere) | Blue Loop RX / TX |

### 4.3 ID-Feld (Bytes 12–17, ggf. bis 25)

- **Typ `0x20` (Sensor mit MAC):** 6 Byte BLE-MAC-Adresse in Bytes 12–17, danach 8 Byte **Name** (Bytes 18–25, ASCII)
- **Typ `0x30` (Sensor mit RPI):** Rotating Proximity Identifier in Bytes 12–17 (kein zusätzlicher Name)

### 4.4 Messwert (Bytes 28–31)

Der Messwert ist als **32-Bit IEEE-754-Float** kodiert (Bytes 28–31). Die Einheit ergibt sich aus der SenML Unit ID (Byte 11).

```
Beispiel Blue RTD bei 24,7 °C:
  Wert = 24.7 (IEEE 754 single)
       = 0x41 C5 99 9A
  → Bytes 28..31 = 41 C5 99 9A   (Byte-Order gemäß BLE-Spec, Little Endian)
```

---

## 5. iBeacon-Payload (Typ `0x02`)

Identisch zum Apple-iBeacon-Layout, lediglich mit taskit Company ID:

| Byte | Feld | Größe |
|---|---|---|
| 8 | iBeacon Type | `0x02` |
| 9 | iBeacon Length | `0x15` (= 21) |
| 10–25 | **UUID** (bzw. RPI) | 16 Bytes |
| 26–27 | **Major / MajorValue** | 2 Bytes |
| 28–29 | **Minor / MinorValue** | 2 Bytes |
| 30 | **RSSI** (TX Power @ 1 m) | 1 Byte (signed) |

Siehe auch: [[BLE/BLE Advertisement Format#5.1 iBeacon (Apple)]]

---

## 6. Ergänzende Definitionen (aus CSV)

Diese Felder sind in der CSV separat dokumentiert und beziehen sich auf taskit-eigene Frame-Erweiterungen:

### 6.1 MsgType

> Datenformat der Nutzdatenbytes 20 bis 31 — Details siehe Tabelle **„MsgType"**.

→ Das Byte legt das Format der nachfolgenden Nutzdaten fest.

### 6.2 BroadcastTime

```
Bit 7-4: BroadcastInterval   (Details siehe Tabelle "BcastIDs")
Bit 3-0: BroadcastNumber     (kontinuierlich hochgezählter Zähler)
```

→ Erlaubt dem Empfänger Paketverluste zu erkennen und das Sendeintervall zu bestimmen.

### 6.3 Serialnr

Taskit-eindeutige Seriennummer in **Little Endian**.

### 6.4 Daten

Format gemäß **MsgType** (siehe 6.1).

> Diese Felder ergänzen die Tabelle in Kap. 3; ihre genaue Byte-Position innerhalb des MsgType-Frames ist in den Tabellen **„MsgType"** und **„BcastIDs"** dokumentiert.

---

## 7. Vollständiges Beispielpaket – Blue RTD (24,7 °C)

```
Advertising Data (31 Bytes):

  02 01 06                              Flags: General Discoverable, BLE only
  1B FF                                 Length=27, Manufacturer Specific Data
       7B 01                            Company ID: taskit GmbH (0x017B, LE)
       20                               Type: Taskit Sensor mit MAC
       01                               Version
       01                               Hardware ID: 1 = Blue RTD
       37                               SenML Unit ID: 55 = Cel (°C)
       AA BB CC DD EE FF                MAC-Adresse (6 B)
       'B' 'R' 'T' 'D' '0' '0' '0' '1'  Name (8 B, ASCII)
       -- --                            (Bytes 26-27 unbelegt)
       41 C5 99 9A                      Value = 24.7 (IEEE 754 single)
```

---

## 8. Vollständiges Beispielpaket – Taskit iBeacon

```
Advertising Data (31 Bytes):

  02 01 06                              Flags
  1A FF                                 Length=26, Manufacturer Specific Data
       7B 01                            Company ID: taskit GmbH
       02 15                            iBeacon Type / Length
       F7 82 6D A6 4F A2 4E 98          UUID (16 Bytes)
       80 24 BC 5B 71 E0 89 3E
       00 01                            Major  = 1
       00 2A                            Minor  = 42
       C5                               RSSI   = −59 dBm @ 1 m
```

---

## 9. Versionshistorie

| Version | Datum | Änderung |
|---|---|---|
| v1.0 | 2026-05-10 | Initiale Spezifikation (Entwurf, abweichend von Implementierung) |
| **v2.0** | **2026-05-18** | **Vollständige Überarbeitung nach `BLE/BcastPacket-Tabelle 1.csv`** |

---

## Verwandte Dokumente

- [[BLE/BLE Advertisement Format]] – Allgemeines BLE-Advertising-Protokoll
- [[BLE/BcastPacket-Tabelle 1.csv]] – Originalquelle (taskit Broadcast Packetformat)
- [[Measure2Go]] – Produktbeschreibung
- [[BEACON-LINE Advertisement in CSV Format]] – Anchor-Beacon-System
