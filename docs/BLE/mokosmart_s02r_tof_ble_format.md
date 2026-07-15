# MOKOSmart S02R ToF Sensor Beacon — BLE Advertising Data Format

## Scope

This document describes the BLE advertising data format used by the MOKOSmart S02R / TOF Ranging Sensor Beacon.

The device advertises a custom sensor packet with ToF ranging distance, battery voltage, user data and a short MAC suffix. The relevant BLE data is inside the **Manufacturer Specific Data** AD structure (`AD Type = 0xFF`).

## Product summary

| Item | Value |
|---|---|
| Product | MOKOSmart S02R / TOF Ranging Sensor Beacon |
| Sensor function | Time-of-Flight distance / range measurement |
| Distance unit | millimetres |
| Main BLE format | Custom Manufacturer Specific Data |
| Main AD Type | `0xFF` |
| Default manufacturer code | logical `0x0059` / Nordic Semiconductor in the MOKO guide |
| Optional manufacturer code | logical `0x0A62` / MOKO Technology, configurable |
| Default beacon code | logical `0x6C07` |
| Sub type | `0x01` = ToF Sensor |
| Endianness | Little endian according to the MOKO guide |

## BLE advertisement overview

A typical legacy BLE advertising payload contains:

```text
02 01 06
12 FF <manufacturer-specific-payload>
07 09 4D 4B 20 54 4F 46
```

Meaning:

| Part | Meaning |
|---|---|
| `02 01 06` | Flags |
| `12 FF ...` | Manufacturer Specific Data |
| `07 09 4D 4B 20 54 4F 46` | Complete Local Name: `MK TOF` |

Note: The AD length for Manufacturer Specific Data is normally `0x12` for the 17-byte manufacturer-specific payload plus the AD type byte. Some text extraction of the PDF table may show `0x1A`; use real raw packets and the field count for parser validation.

## ADV packet format

Offsets below are offsets in the complete advertising payload, including AD length and AD type bytes.

| Offset | Field | Length | Example | Description |
|---:|---|---:|---|---|
| 0 | AD1 Length | 1 | `0x02` | Flags AD length |
| 1 | AD1 Type | 1 | `0x01` | Flags |
| 2 | AD1 Flags | 1 | `0x06` | LE General Discoverable, BR/EDR not supported |
| 3 | AD2 Length | 1 | `0x12` | Manufacturer data AD length |
| 4 | AD2 Type | 1 | `0xFF` | Manufacturer Specific Data |
| 5-6 | MFG Code | 2 | raw `59 00` | Logical `0x0059`, little endian |
| 7-8 | Beacon Code | 2 | raw `07 6C` | Logical `0x6C07`, little endian |
| 9-10 | Tag Battery | 2 | raw e.g. `EA 0B` | Battery voltage in mV, little endian |
| 11 | Event Status | 1 | `0xFF` | Reserved, default `0xFF` |
| 12-13 | Temperature | 2 | `FF FF` | Reserved, default `0xFFFF` |
| 14-15 | Ranging Distance | 2 | raw e.g. `78 00` | Distance in mm, little endian |
| 16-17 | User Data | 2 | `FF FF` | User-configurable ID / tag data |
| 18 | Sub Type | 1 | `0x01` | `0x01` = ToF Sensor |
| 19-20 | MAC Suffix | 2 | device-specific | Last 4 hex digits of MAC address |
| 21 | Reserved | 1 | `0xFF` | Reserved |

## Manufacturer-specific payload view

If the parser receives only the `0xFF` payload, excluding AD length and AD type, use this offset table:

| Payload offset | Field | Length | Decode |
|---:|---|---:|---|
| 0-1 | MFG Code | 2 | `uint16_le` |
| 2-3 | Beacon Code | 2 | `uint16_le` |
| 4-5 | Battery voltage | 2 | `uint16_le`, mV |
| 6 | Event Status | 1 | reserved |
| 7-8 | Temperature | 2 | reserved / currently `0xFFFF` |
| 9-10 | Ranging Distance | 2 | `uint16_le`, mm |
| 11-12 | User Data | 2 | `uint16_le` |
| 13 | Sub Type | 1 | `0x01` = ToF Sensor |
| 14-15 | MAC Suffix | 2 | last 2 bytes of MAC |
| 16 | Reserved | 1 | reserved |

## Decoder formulas

```c
uint16_t mfg_code      = p[0]  | (p[1]  << 8);
uint16_t beacon_code   = p[2]  | (p[3]  << 8);
uint16_t battery_mv    = p[4]  | (p[5]  << 8);
uint16_t distance_mm   = p[9]  | (p[10] << 8);
uint16_t user_data     = p[11] | (p[12] << 8);
uint8_t  subtype       = p[13];
```

## Parser identification

Recommended detection:

```text
AD Type == 0xFF
AND MFG Code == 0x0059 or 0x0A62
AND Beacon Code == 0x6C07
AND Sub Type == 0x01
```

Do not identify this product only by payload length. Firmware revisions or configured manufacturer/beacon codes can change.

## Scan response

The scan response normally contains the device name.

| Offset | Field | Length | Example | Description |
|---:|---|---:|---|---|
| 0 | AD Length | 1 | `0x07` | Name AD length |
| 1 | AD Type | 1 | `0x09` | Complete Local Name |
| 2..n | Device Name | 1-20 | ASCII `MK TOF` | Device name |

## Open validation points

Validate these points with real BLE captures from your devices:

- Whether your ordered S02R uses manufacturer code `0x0059` or `0x0A62`.
- Whether the beacon code remains `0x6C07`.
- Whether the AD2 length is always `0x12` in raw captures.
- Whether distance is updated at every advertising interval or only at the configured ToF sampling interval.

## Example capture template

```text
Device: S02R ToF Sensor Beacon
MAC:
RSSI:
ADV raw:
SCAN_RSP raw:
Decoded:
  battery_mv:
  distance_mm:
  user_data:
  subtype:
```

## Sources

- MOKO TOF Ranging Sensor User Guide V1.1, 2024-08-21: https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2025/03/TOF-Sensor-User-Guide_V1.1_20240821-Standard-Version.pdf
- MOKOSmart S02R product page: https://www.mokosmart.com/tof-sensor-beacon/
