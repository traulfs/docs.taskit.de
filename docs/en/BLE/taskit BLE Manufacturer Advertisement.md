---
tags:
  - bluetooth
  - ble
  - protocol
  - taskit
  - specification
erstellt: 2026-05-10
aktualisiert: 2026-05-18
quelle: BLE/BcastPacket-Tabelle 1.csv
status: reference
---

# taskit BLE Manufacturer Advertisement Format

Specification of the manufacturer-specific BLE broadcast packet for taskit products (BLE sensor & beacon).

- Based on: [[BLE/BLE Advertisement Format]]
- Source: `BLE/BcastPacket-Tabelle 1.csv`
- **taskit Company Identifier:** `0x017B` (little endian → `0x7B 0x01`)

---

## 1. Packet Structure

The format uses the standard BLE advertising packet (31 bytes) consisting of two AD structures:

1. **Flags AD** (3 bytes) – always `02 01 06`
2. **Manufacturer Specific Data AD** (variable length) with the taskit company ID

```
┌──────────────┬───────────────────────────────────────────────────────────┐
│  Flags AD    │              Manufacturer Specific Data (0xFF)            │
│              │                                                           │
│  02 01 06    │  [Len] FF  7B 01  [Type] [Version]  [Payload ...]         │
│  3 Bytes     │  variable length (Len = 0x1A or 0x1B, depending on type)  │
└──────────────┴───────────────────────────────────────────────────────────┘
```

| Byte | Value | Meaning |
|---:|---|---|
| 1 | `0x02` | Length of Flags AD |
| 2 | `0x01` | AD Type: Flags |
| 3 | `0x06` | LE General Discoverable + BR/EDR Not Supported |
| 4 | `0x1A` / `0x1B` | Length of Manufacturer Specific AD (26 or 27) |
| 5 | `0xFF` | AD Type: Manufacturer Specific Data |
| 6 | `0x7B` | Company ID Low (taskit) |
| 7 | `0x01` | Company ID High (taskit) |
| 8 | `0x20..0x50` | **Type byte** (frame identifier – see section 2) |
| 9 | `0x15` / Version | iBeacon length or protocol version |
| 10–31 | – | Type-dependent payload |

> Bytes 1–7 are identical across all taskit variants (except byte 4: `0x1A` without MAC, `0x1B` with MAC).

---

## 2. Frame Types (Byte 8)

Byte 8 distinguishes between Anonymous (iBeacon-compatible) and Named (taskit's own formats):

| Type Byte | Category | Name | Byte 4 (Len) | Description |
|---|---|---|:---:|---|
| `0x02` | Anonymous | **Taskit iBeacon** | `0x1A` | iBeacon-compatible (Apple layout) with taskit company ID |
| `0x20` | Named | **Taskit Sensor with MAC** | `0x1B` | Sensor frame, identified via MAC address |
| `0x30` | Named | **Taskit Sensor with RPI** | `0x1A` | Sensor frame, identified via Rotating Proximity Identifier (RPI) |
| `0x40` | Named | **Anchor Beacon** | `0x1B` | Positioning anchor (e.g. Beaconline) |
| `0x50` | Named | **Text** | `0x1B` | ASCII text message |

> **Comparison with Apple iBeacon:** bytes 6/7 = `0x4C 0x00` (Apple), byte 8 = `0x02`, byte 9 = `0x15`. Taskit iBeacon uses exactly the same layout, but with company ID `0x7B 0x01`.

---

## 3. Complete Byte Table

The following table shows the complete layout of all 31 bytes for every frame type.

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
| 18–25 | UUID (up to B25) | UUID (up to B25) | – | **Name** (8 B) | Name | ASCII Text |
| 26–27 | Major ID | MajorValue | – | – | – | – |
| 28–31 | Minor (B28-29) + RSSI (B30) | Minor (B28-29) + RSSI (B30) | **Value as 32-bit float (IEEE 754)** | **Value as 32-bit float (IEEE 754)** | – | – |

> The columns for Blue RTD / Blue Loop RX / Blue Loop TX / Blue pH-Meter are specializations of **Taskit Sensor with MAC** (byte 8 = `0x20`) and differ only in byte 10 (hardware ID) and byte 11 (SenML unit ID).

---

## 4. Sensor Payload (Type `0x20` / `0x30`)

### 4.1 Hardware ID (Byte 10)

| Value | Device |
|---:|---|
| `1` | Blue RTD (temperature, PT100/PT1000) |
| `3` | Blue Loop RX (4–20 mA input) |
| `4` | Blue Loop TX (4–20 mA output) |
| `5` | Blue pH-Meter |

### 4.2 SenML Unit ID (Byte 11)

Per [RFC 8428 SenML Units](https://www.iana.org/assignments/senml/senml.xhtml):

| Value | Unit | Used by |
|---:|---|---|
| `55` | `Cel` (°C) | Blue RTD |
| `75` | `pH` | Blue pH-Meter |
| `143` | `mA` (milliampere) | Blue Loop RX / TX |

### 4.3 ID Field (Bytes 12–17, up to 25 where applicable)

- **Type `0x20` (sensor with MAC):** 6-byte BLE MAC address in bytes 12–17, followed by an 8-byte **name** (bytes 18–25, ASCII)
- **Type `0x30` (sensor with RPI):** Rotating Proximity Identifier in bytes 12–17 (no additional name)

### 4.4 Measured Value (Bytes 28–31)

The measured value is encoded as a **32-bit IEEE 754 float** (bytes 28–31). The unit is determined by the SenML Unit ID (byte 11).

```
Example, Blue RTD at 24.7 °C:
  Value = 24.7 (IEEE 754 single)
       = 0x41 C5 99 9A
  → Bytes 28..31 = 41 C5 99 9A   (byte order per BLE spec, little endian)
```

---

## 5. iBeacon Payload (Type `0x02`)

Identical to the Apple iBeacon layout, only with the taskit company ID:

| Byte | Field | Size |
|---|---|---|
| 8 | iBeacon Type | `0x02` |
| 9 | iBeacon Length | `0x15` (= 21) |
| 10–25 | **UUID** (or RPI) | 16 bytes |
| 26–27 | **Major / MajorValue** | 2 bytes |
| 28–29 | **Minor / MinorValue** | 2 bytes |
| 30 | **RSSI** (TX power @ 1 m) | 1 byte (signed) |

See also: [[BLE/BLE Advertisement Format#5.1 iBeacon (Apple)]]

---

## 6. Supplementary Definitions (from CSV)

These fields are documented separately in the CSV and relate to taskit's own frame extensions:

### 6.1 MsgType

> Data format of payload bytes 20 to 31 — see the **"MsgType"** table for details.

→ This byte defines the format of the following payload data.

### 6.2 BroadcastTime

```
Bit 7-4: BroadcastInterval   (see "BcastIDs" table for details)
Bit 3-0: BroadcastNumber     (continuously incrementing counter)
```

→ Allows the receiver to detect packet loss and determine the transmit interval.

### 6.3 Serialnr

taskit-unique serial number in **little endian**.

### 6.4 Daten (Data)

Format per **MsgType** (see 6.1).

> These fields supplement the table in section 3; their exact byte position within the MsgType frame is documented in the **"MsgType"** and **"BcastIDs"** tables.

---

## 7. Complete Example Packet – Blue RTD (24.7 °C)

```
Advertising Data (31 bytes):

  02 01 06                              Flags: General Discoverable, BLE only
  1B FF                                 Length=27, Manufacturer Specific Data
       7B 01                            Company ID: taskit GmbH (0x017B, LE)
       20                               Type: Taskit Sensor with MAC
       01                               Version
       01                               Hardware ID: 1 = Blue RTD
       37                               SenML Unit ID: 55 = Cel (°C)
       AA BB CC DD EE FF                MAC address (6 B)
       'B' 'R' 'T' 'D' '0' '0' '0' '1'  Name (8 B, ASCII)
       -- --                            (bytes 26-27 unused)
       41 C5 99 9A                      Value = 24.7 (IEEE 754 single)
```

---

## 8. Complete Example Packet – Taskit iBeacon

```
Advertising Data (31 bytes):

  02 01 06                              Flags
  1A FF                                 Length=26, Manufacturer Specific Data
       7B 01                            Company ID: taskit GmbH
       02 15                            iBeacon Type / Length
       F7 82 6D A6 4F A2 4E 98          UUID (16 bytes)
       80 24 BC 5B 71 E0 89 3E
       00 01                            Major  = 1
       00 2A                            Minor  = 42
       C5                               RSSI   = −59 dBm @ 1 m
```

---

## 9. Version History

| Version | Date | Change |
|---|---|---|
| v1.0 | 2026-05-10 | Initial specification (draft, differs from implementation) |
| **v2.0** | **2026-05-18** | **Complete revision based on `BLE/BcastPacket-Tabelle 1.csv`** |

---

## Related Documents

- [[BLE/BLE Advertisement Format]] – General BLE advertising protocol
- [[Measure2Go]] – Product description
- [[BEACON-LINE Advertisement in CSV Format]] – Anchor beacon system
