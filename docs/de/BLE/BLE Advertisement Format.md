---
tags:
  - bluetooth
  - ble
  - protokoll
  - beaconline
  - technik
erstellt: 2026-05-10
---

# BLE Advertisement Format

Bluetooth Low Energy (BLE) verwendet **Advertising Packets**, um Geräte auffindbar zu machen, ohne eine aktive Verbindung aufzubauen. Dieses Verfahren ist die Grundlage für Beacon-Systeme wie [[Measure2Go]] und [[BEACON-LINE Advertisement in CSV Format]].

---

## 1. Paketstruktur auf Physical Layer

Jedes BLE-Advertising-Paket besteht aus folgenden Feldern:

```
┌───────────┬──────────────────┬─────────────────────────────┬─────────┐
│ Preamble  │  Access Address  │           PDU               │   CRC   │
│  1 Byte   │    4 Bytes       │    2–39 Bytes               │ 3 Bytes │
└───────────┴──────────────────┴─────────────────────────────┴─────────┘
```

| Feld | Größe | Beschreibung |
|---|---|---|
| **Preamble** | 1 Byte | Synchronisationssequenz `0xAA` |
| **Access Address** | 4 Bytes | Feste Adresse für Advertising: `0x8E89BED6` |
| **PDU** | 2–39 Bytes | Protocol Data Unit (Header + Payload) |
| **CRC** | 3 Bytes | Cyclic Redundancy Check zur Fehlerprüfung |

---

## 2. PDU – Protocol Data Unit

### 2.1 PDU Header (2 Bytes)

```
Bit:  15  14  13  12  11  10   9   8   7   6   5   4   3   2   1   0
      ───────────────────────────────────────────────────────────────
      RFU TxAdd RxAdd RFU  ←── Length (6 Bit) ───→  ←── PDU Type ──→
```

| Feld | Bits | Beschreibung |
|---|---|---|
| **PDU Type** | 4 | Art des Advertising-Pakets |
| **Length** | 6 | Länge des Payloads (0–37 Bytes) |
| **TxAdd** | 1 | Adresstyp des Senders (0 = public, 1 = random) |
| **RxAdd** | 1 | Adresstyp des Empfängers |

### 2.2 PDU-Typen

| Typ | Wert | Name | Beschreibung |
|---|---|---|---|
| `ADV_IND` | `0x00` | Connectable Undirected | Generelles Advertising, verbindbar |
| `ADV_DIRECT_IND` | `0x01` | Connectable Directed | Gerichtetes Advertising an ein Gerät |
| `ADV_NONCONN_IND` | `0x02` | Non-Connectable Undirected | Nur Broadcast, keine Verbindung |
| `ADV_SCAN_IND` | `0x06` | Scannable Undirected | Broadcast + Scan Response möglich |
| `SCAN_REQ` | `0x03` | Scan Request | Anfrage nach zusätzlichen Daten |
| `SCAN_RSP` | `0x04` | Scan Response | Antwort auf Scan Request |
| `CONNECT_IND` | `0x05` | Connect Request | Verbindungsaufbau |

> 💡 Für Beacon-Systeme wird typischerweise **`ADV_NONCONN_IND`** verwendet – keine Verbindung, nur Broadcast.

---

## 3. Advertising Data (AD) Struktur

Der Payload besteht aus einer oder mehreren **AD Structures**, die hintereinander angeordnet sind:

```
┌────────┬─────────┬──────────────────┐
│ Length │ AD Type │    AD Data       │
│ 1 Byte │  1 Byte │  Length-1 Bytes  │
└────────┴─────────┴──────────────────┘
```

Mehrere AD Structures werden direkt aneinandergereiht (max. 31 Bytes gesamt):

```
[Len][Type][Data...][Len][Type][Data...][Len][Type][Data...]
```

### Wichtige AD Types (GAP Types)

| AD Type | Name | Beschreibung |
|---|---|---|
| `0x01` | **Flags** | Advertising-Modus (General Discoverable, BR/EDR nicht unterstützt etc.) |
| `0x02` | Incomplete 16-bit UUIDs | Unvollständige UUID-Liste |
| `0x03` | Complete 16-bit UUIDs | Vollständige Liste der 16-bit Service-UUIDs |
| `0x06` | Incomplete 128-bit UUIDs | Unvollständige 128-bit UUID-Liste |
| `0x07` | Complete 128-bit UUIDs | Vollständige 128-bit UUID-Liste |
| `0x08` | Shortened Local Name | Verkürzter Gerätename |
| `0x09` | Complete Local Name | Vollständiger Gerätename |
| `0x0A` | TX Power Level | Sendeleistung in dBm (für Distanzschätzung) |
| `0x16` | Service Data (16-bit UUID) | Dienstdaten mit 16-bit UUID |
| `0xFF` | **Manufacturer Specific Data** | Herstellerspezifische Nutzdaten |

#### Flags (0x01) – Aufschlüsselung

```
Bit 0: LE Limited Discoverable Mode
Bit 1: LE General Discoverable Mode   ← typisch für Beacons
Bit 2: BR/EDR Not Supported           ← immer gesetzt bei reinem BLE
Bit 3: Simultaneous LE and BR/EDR (Controller)
Bit 4: Simultaneous LE and BR/EDR (Host)
```

---

## 4. Manufacturer Specific Data (0xFF)

Das flexibelste AD-Feld – die ersten 2 Bytes sind immer die **Company ID** (vergeben von der Bluetooth SIG):

```
┌────────┬───────────┬──────────────────────────────────┐
│  0xFF  │ Company ID│        Custom Payload            │
│        │  2 Bytes  │        variable                  │
└────────┴───────────┴──────────────────────────────────┘
```

### Bekannte Company IDs

| Company ID | Hersteller |
|---|---|
| `0x004C` | Apple Inc. |
| `0x0059` | Nordic Semiconductor |
| `0x017B` | **taskit GmbH** |
| `0x0499` | Ruuvi Innovations |
| `0x02E5` | Espressif Inc. |

---

## 5. Bekannte Beacon-Formate

### 5.1 iBeacon (Apple)

Nutzt **Manufacturer Specific Data** mit Apple Company ID:

```
┌────────┬─────────────┬──────┬────────┬──────────┬───────┬───────┬──────────┐
│AD Type │ Company ID  │Type  │Length  │   UUID   │ Major │ Minor │TX Power  │
│  0xFF  │ 0x4C 0x00   │ 0x02 │  0x15  │  16 B    │  2 B  │  2 B  │   1 B    │
│  1 B   │ (Apple) 2 B │  1 B │   1 B  │          │       │       │ (signed) │
└────────┴─────────────┴──────┴────────┴──────────┴───────┴───────┴──────────┘
```

| Feld | Wert / Größe | Beschreibung |
|---|---|---|
| AD Type | `0xFF` – 1 Byte | Kennzeichnet Manufacturer Specific Data |
| Company ID | `0x004C` (Apple) – 2 Bytes | Little Endian: `0x4C 0x00` |
| iBeacon Type | `0x02` – 1 Byte | Kennzeichnet das iBeacon-Format |
| iBeacon Length | `0x15` (= 21) – 1 Byte | Länge der folgenden Nutzdaten |
| UUID | 16 Bytes | Identifiziert die Beacon-Gruppe/Anwendung |
| Major | 2 Bytes | Grobe Unterteilung (z.B. Gebäude, Etage) |
| Minor | 2 Bytes | Feine Unterteilung (z.B. Raum, Position) |
| TX Power | 1 Byte (signed) | Kalibrierte RSSI bei 1 m (für Distanzschätzung) |

### 5.2 Eddystone (Google)

Nutzt **Service Data** mit Eddystone UUID `0xFEAA`:

#### Eddystone-UID
```
[0x16][0xAA 0xFE][0x00][TX Power][Namespace 10B][Instance 6B]
```

#### Eddystone-URL
```
[0x16][0xAA 0xFE][0x10][TX Power][URL Scheme][Encoded URL]
```

URL Schemes: `0x00` = `http://www.` | `0x01` = `https://www.` | `0x02` = `http://` | `0x03` = `https://`

#### Eddystone-TLM (Telemetry)
```
[0x16][0xAA 0xFE][0x20][Version][Battery mV][Temp][Adv Count][Uptime]
```
Enthält Batteriezustand, Temperatur, Anzahl gesendeter Pakete – nützlich für Wartungsüberwachung.

---

## 6. Advertising Channels

BLE nutzt 3 dedizierte Advertising-Kanäle (so gewählt, dass WLAN-Kanäle 1, 6, 11 vermieden werden):

| Kanal | Frequenz | Position im 2,4-GHz-Band |
|---|---|---|
| **37** | 2402 MHz | Unterhalb WLAN-Kanal 1 |
| **38** | 2426 MHz | Zwischen WLAN-Kanal 1 und 6 |
| **39** | 2480 MHz | Oberhalb WLAN-Kanal 11 |

Geräte senden typischerweise auf **allen drei Kanälen** nacheinander.

---

## 7. Advertising Interval & Stromverbrauch

| Interval | Erreichbarkeit | Stromverbrauch | Typischer Einsatz |
|---|---|---|---|
| 20 ms | Sehr schnell | Hoch | Kurzzeitiges Tracking |
| 100 ms | Schnell | Mittel | Allgemeines Advertising |
| 1.000 ms | Normal | Gering | Beacons, IoT-Sensoren |
| 10.240 ms | Langsam | Sehr gering | Batterie-optimierte Beacons |

> 💡 Measure2Go-Sensoren: Batterielebensdauer bis zu **2 Jahre** durch optimiertes Advertising-Interval.

---

## 8. Beispiel: Vollständiges Advertising-Paket

```
Preamble:       AA
Access Addr:    D6 BE 89 8E
PDU Header:     02 04          (ADV_NONCONN_IND, Length=4+Payload)
AdvA (MAC):     XX XX XX XX XX XX

Advertising Data:
  [02][01][06]                  → Flags: General Discoverable, BLE only
  [1A][FF][4C 00]               → Manufacturer Specific, Apple
        [02][15]                → iBeacon Type + Length
        [UUID 16 Bytes]         → z.B. F7826DA6-4FA2-4E98-8024-BC5B71E0893E
        [00 01]                 → Major = 1
        [00 2A]                 → Minor = 42
        [C5]                    → TX Power = -59 dBm

CRC:            XX XX XX
```

---

## Quellen & Weiterführendes

- [Bluetooth Core Specification 5.4](https://www.bluetooth.com/specifications/specs/core-specification-5-4/)
- [Bluetooth SIG Assigned Numbers – Company Identifiers](https://www.bluetooth.com/specifications/assigned-numbers/)
- [Eddystone Protocol Specification (GitHub)](https://github.com/google/eddystone)
- Verwandt: [[Measure2Go]] | [[projekte/taskit.de]]
