---
tags:
  - bluetooth
  - ble
  - protocol
  - beaconline
  - technology
erstellt: 2026-05-10
---

# BLE Advertisement Format

Bluetooth Low Energy (BLE) uses **advertising packets** to make devices discoverable without establishing an active connection. This mechanism is the foundation for beacon systems such as [[Measure2Go]] and [[BEACON-LINE Advertisement in CSV Format]].

---

## 1. Packet Structure at the Physical Layer

Every BLE advertising packet consists of the following fields:

```
┌───────────┬──────────────────┬─────────────────────────────┬─────────┐
│ Preamble  │  Access Address  │           PDU               │   CRC   │
│  1 Byte   │    4 Bytes       │    2–39 Bytes               │ 3 Bytes │
└───────────┴──────────────────┴─────────────────────────────┴─────────┘
```

| Field | Size | Description |
|---|---|---|
| **Preamble** | 1 byte | Synchronization sequence `0xAA` |
| **Access Address** | 4 bytes | Fixed address for advertising: `0x8E89BED6` |
| **PDU** | 2–39 bytes | Protocol Data Unit (header + payload) |
| **CRC** | 3 bytes | Cyclic redundancy check for error detection |

---

## 2. PDU – Protocol Data Unit

### 2.1 PDU Header (2 Bytes)

```
Bit:  15  14  13  12  11  10   9   8   7   6   5   4   3   2   1   0
      ───────────────────────────────────────────────────────────────
      RFU TxAdd RxAdd RFU  ←── Length (6 bit) ───→  ←── PDU Type ──→
```

| Field | Bits | Description |
|---|---|---|
| **PDU Type** | 4 | Type of advertising packet |
| **Length** | 6 | Length of the payload (0–37 bytes) |
| **TxAdd** | 1 | Address type of the sender (0 = public, 1 = random) |
| **RxAdd** | 1 | Address type of the receiver |

### 2.2 PDU Types

| Type | Value | Name | Description |
|---|---|---|---|
| `ADV_IND` | `0x00` | Connectable Undirected | General advertising, connectable |
| `ADV_DIRECT_IND` | `0x01` | Connectable Directed | Directed advertising to a specific device |
| `ADV_NONCONN_IND` | `0x02` | Non-Connectable Undirected | Broadcast only, no connection |
| `ADV_SCAN_IND` | `0x06` | Scannable Undirected | Broadcast + scan response possible |
| `SCAN_REQ` | `0x03` | Scan Request | Request for additional data |
| `SCAN_RSP` | `0x04` | Scan Response | Response to a scan request |
| `CONNECT_IND` | `0x05` | Connect Request | Connection setup |

> 💡 Beacon systems typically use **`ADV_NONCONN_IND`** – no connection, broadcast only.

---

## 3. Advertising Data (AD) Structure

The payload consists of one or more **AD structures** arranged consecutively:

```
┌────────┬─────────┬──────────────────┐
│ Length │ AD Type │    AD Data       │
│ 1 Byte │  1 Byte │  Length-1 bytes  │
└────────┴─────────┴──────────────────┘
```

Multiple AD structures are concatenated directly (max. 31 bytes total):

```
[Len][Type][Data...][Len][Type][Data...][Len][Type][Data...]
```

### Important AD Types (GAP Types)

| AD Type | Name | Description |
|---|---|---|
| `0x01` | **Flags** | Advertising mode (general discoverable, BR/EDR not supported, etc.) |
| `0x02` | Incomplete 16-bit UUIDs | Incomplete UUID list |
| `0x03` | Complete 16-bit UUIDs | Complete list of 16-bit service UUIDs |
| `0x06` | Incomplete 128-bit UUIDs | Incomplete 128-bit UUID list |
| `0x07` | Complete 128-bit UUIDs | Complete 128-bit UUID list |
| `0x08` | Shortened Local Name | Shortened device name |
| `0x09` | Complete Local Name | Full device name |
| `0x0A` | TX Power Level | Transmit power in dBm (for distance estimation) |
| `0x16` | Service Data (16-bit UUID) | Service data with 16-bit UUID |
| `0xFF` | **Manufacturer Specific Data** | Manufacturer-specific payload |

#### Flags (0x01) – Breakdown

```
Bit 0: LE Limited Discoverable Mode
Bit 1: LE General Discoverable Mode   ← typical for beacons
Bit 2: BR/EDR Not Supported           ← always set for pure BLE
Bit 3: Simultaneous LE and BR/EDR (Controller)
Bit 4: Simultaneous LE and BR/EDR (Host)
```

---

## 4. Manufacturer Specific Data (0xFF)

The most flexible AD field – the first 2 bytes are always the **Company ID** (assigned by the Bluetooth SIG):

```
┌────────┬───────────┬──────────────────────────────────┐
│  0xFF  │ Company ID│        Custom Payload            │
│        │  2 Bytes  │        variable                  │
└────────┴───────────┴──────────────────────────────────┘
```

### Known Company IDs

| Company ID | Manufacturer |
|---|---|
| `0x004C` | Apple Inc. |
| `0x0059` | Nordic Semiconductor |
| `0x017B` | **taskit GmbH** |
| `0x0499` | Ruuvi Innovations |
| `0x02E5` | Espressif Inc. |

---

## 5. Known Beacon Formats

### 5.1 iBeacon (Apple)

Uses **Manufacturer Specific Data** with the Apple company ID:

```
┌────────┬─────────────┬──────┬────────┬──────────┬───────┬───────┬──────────┐
│AD Type │ Company ID  │Type  │Length  │   UUID   │ Major │ Minor │TX Power  │
│  0xFF  │ 0x4C 0x00   │ 0x02 │  0x15  │  16 B    │  2 B  │  2 B  │   1 B    │
│  1 B   │ (Apple) 2 B │  1 B │   1 B  │          │       │       │ (signed) │
└────────┴─────────────┴──────┴────────┴──────────┴───────┴───────┴──────────┘
```

| Field | Value / Size | Description |
|---|---|---|
| AD Type | `0xFF` – 1 byte | Marks manufacturer specific data |
| Company ID | `0x004C` (Apple) – 2 bytes | Little endian: `0x4C 0x00` |
| iBeacon Type | `0x02` – 1 byte | Marks the iBeacon format |
| iBeacon Length | `0x15` (= 21) – 1 byte | Length of the following payload |
| UUID | 16 bytes | Identifies the beacon group/application |
| Major | 2 bytes | Coarse subdivision (e.g. building, floor) |
| Minor | 2 bytes | Fine subdivision (e.g. room, position) |
| TX Power | 1 byte (signed) | Calibrated RSSI at 1 m (for distance estimation) |

### 5.2 Eddystone (Google)

Uses **Service Data** with the Eddystone UUID `0xFEAA`:

#### Eddystone-UID
```
[0x16][0xAA 0xFE][0x00][TX Power][Namespace 10B][Instance 6B]
```

#### Eddystone-URL
```
[0x16][0xAA 0xFE][0x10][TX Power][URL Scheme][Encoded URL]
```

URL schemes: `0x00` = `http://www.` | `0x01` = `https://www.` | `0x02` = `http://` | `0x03` = `https://`

#### Eddystone-TLM (Telemetry)
```
[0x16][0xAA 0xFE][0x20][Version][Battery mV][Temp][Adv Count][Uptime]
```
Contains battery status, temperature, and packet count – useful for maintenance monitoring.

---

## 6. Advertising Channels

BLE uses 3 dedicated advertising channels (chosen to avoid Wi-Fi channels 1, 6, 11):

| Channel | Frequency | Position in the 2.4 GHz band |
|---|---|---|
| **37** | 2402 MHz | Below Wi-Fi channel 1 |
| **38** | 2426 MHz | Between Wi-Fi channels 1 and 6 |
| **39** | 2480 MHz | Above Wi-Fi channel 11 |

Devices typically transmit on **all three channels** in sequence.

---

## 7. Advertising Interval & Power Consumption

| Interval | Responsiveness | Power consumption | Typical use |
|---|---|---|---|
| 20 ms | Very fast | High | Short-term tracking |
| 100 ms | Fast | Medium | General advertising |
| 1,000 ms | Normal | Low | Beacons, IoT sensors |
| 10,240 ms | Slow | Very low | Battery-optimized beacons |

> 💡 Measure2Go sensors: battery life of up to **2 years** through an optimized advertising interval.

---

## 8. Example: Complete Advertising Packet

```
Preamble:       AA
Access Addr:    D6 BE 89 8E
PDU Header:     02 04          (ADV_NONCONN_IND, Length=4+Payload)
AdvA (MAC):     XX XX XX XX XX XX

Advertising Data:
  [02][01][06]                  → Flags: General Discoverable, BLE only
  [1A][FF][4C 00]               → Manufacturer Specific, Apple
        [02][15]                → iBeacon Type + Length
        [UUID 16 Bytes]         → e.g. F7826DA6-4FA2-4E98-8024-BC5B71E0893E
        [00 01]                 → Major = 1
        [00 2A]                 → Minor = 42
        [C5]                    → TX Power = -59 dBm

CRC:            XX XX XX
```

---

## Sources & Further Reading

- [Bluetooth Core Specification 5.4](https://www.bluetooth.com/specifications/specs/core-specification-5-4/)
- [Bluetooth SIG Assigned Numbers – Company Identifiers](https://www.bluetooth.com/specifications/assigned-numbers/)
- [Eddystone Protocol Specification (GitHub)](https://github.com/google/eddystone)
- Related: [[Measure2Go]] | [[projekte/taskit.de]]
