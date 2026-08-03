# MOKOSmart S03D Door Sensor — BLE Advertising Data Format

## Scope

This document describes the BLE advertising format used by the MOKOSmart S03D Bluetooth Door Sensor.

The S03D uses a custom format consisting of:

1. **ADV_IND** advertising packet: door/hall status, battery voltage, timestamp, MAC, Major, Minor, RSSI@1m.
2. **SCAN_RSP** scan response packet: TX power and complete local name.

The important door state is encoded in **Device Status bit 3**.

## Product summary

| Item | Value |
|---|---|
| Product | MOKOSmart S03D Bluetooth Door Sensor |
| Sensor function | Door/window open-close via Hall sensor + magnet |
| Main ADV Type | `0xFF` Manufacturer Specific Data |
| Company ID in MOKO table/raw examples | `0A 62` / MOKO Technology |
| Packet family | Customized-PIR / Door Sensor packet |
| Door state bit | Device Status bit 3 |
| Battery unit | mV |
| Timestamp format | `YY/MM/DD/HH:MM:SS` |

## Door state logic

For parser implementation, use **Device Status bit 3** from the ADV packet.

| Device Status bit 3 | Door state | Magnet state |
|---:|---|---|
| `0` | Door closed | Magnet approaching |
| `1` | Door open | Magnet away |

Note: The manual also describes Hall sensor electrical status separately. For BLE parsing, the advertisement table and packet example indicate bit 3 as the door open/close status bit.

## ADV_IND packet format

Offsets below are offsets in the complete advertising payload.

| Offset | Field | Length | Example | Description |
|---:|---|---:|---|---|
| 0 | ADV Length | 1 | `0x02` | Flags AD length |
| 1 | ADV Type | 1 | `0x01` | Flags |
| 2 | Beacon Type / Flags | 1 | `0x04` | BR/EDR not supported |
| 3 | ADV Length | 1 | `0x1A` | Manufacturer data AD length |
| 4 | ADV Type | 1 | `0xFF` | Manufacturer data |
| 5-6 | Company ID | 2 | `0A 62` | MOKO Technology Ltd according to MOKO table |
| 7 | iBeacon Type | 1 | `0x02` | fixed |
| 8 | iBeacon Length | 1 | `0x15` | 21 bytes |
| 9 | Device Status | 1 | e.g. `0x09` | Bitfield, includes door open/close bit |
| 10 | RFU | 1 | `0x00` | Reserved |
| 11-16 | MAC address | 6 | device MAC | MAC address read from chipset |
| 17-22 | Timestamp | 6 | `16 03 1E 0D 3A 19` | `YY/MM/DD/HH:MM:SS` |
| 23-24 | Battery voltage | 2 | `0E 2A` | mV |
| 25-26 | Major | 2 | `00 00` | configurable group value |
| 27-28 | Minor | 2 | `00 00` | configurable device ID value |
| 29 | RSSI@1m | 1 | `0xB0` | calibrated RSSI at 1 m, signed int8 |

## Manufacturer-specific payload view

If the parser receives only payload bytes after AD Type `0xFF`, use this table:

| Payload offset | Field | Length | Decode |
|---:|---|---:|---|
| 0-1 | Company ID | 2 | `0A 62` according to MOKO raw example |
| 2 | iBeacon Type | 1 | `0x02` |
| 3 | iBeacon Length | 1 | `0x15` |
| 4 | Device Status | 1 | bitfield |
| 5 | RFU | 1 | reserved |
| 6-11 | MAC address | 6 | raw MAC bytes |
| 12-17 | Timestamp | 6 | `YY MM DD HH MM SS` |
| 18-19 | Battery voltage | 2 | `uint16_be`, mV |
| 20-21 | Major | 2 | `uint16_be` |
| 22-23 | Minor | 2 | `uint16_be` |
| 24 | RSSI@1m | 1 | `int8_t`, dBm |

## Device Status bitfield

| Bits | Name | Meaning |
|---:|---|---|
| 7-6 | RFU | reserved |
| 5-4 | PIR delay response status | `10` = high delay, `01` = medium delay, `00` = low delay |
| 3 | Door Open/Close status | `0` = closed, `1` = open |
| 2-1 | PIR sensor sensitivity | `10` = high, `01` = medium, `00` = low |
| 0 | PIR sensor detection status | `0` = no effective motion, `1` = effective motion detected |

For S03D door detection, normally only bit 3 is required.

## Decoder formulas

```c
uint8_t status = p[4];
bool door_open = (status & (1u << 3)) != 0;

uint16_t battery_mv = ((uint16_t)p[18] << 8) | p[19];
uint16_t major      = ((uint16_t)p[20] << 8) | p[21];
uint16_t minor      = ((uint16_t)p[22] << 8) | p[23];
int8_t rssi_1m      = (int8_t)p[24];
```

Timestamp conversion:

```c
uint8_t year   = p[12];  // YY
uint8_t month  = p[13];
uint8_t day    = p[14];
uint8_t hour   = p[15];
uint8_t minute = p[16];
uint8_t second = p[17];
```

## SCAN_RSP packet format

| Offset | Field | Length | Example | Description |
|---:|---|---:|---|---|
| 0 | ADV Length | 1 | `0x02` | TX Power AD length |
| 1 | ADV Type | 1 | `0x0A` | TX Power Level |
| 2 | TX Power | 1 | `0xF4` | signed int8, dBm; example `-12 dBm` |
| 3 | ADV Length | 1 | variable | Complete Local Name length |
| 4 | ADV Type | 1 | `0x09` | Complete Local Name |
| 5..n | Device name | 1-10 | ASCII | device name |
| after name | Serial ID | 1-5 | ASCII digits | serial ID, range 0-99999 |

## Parser identification

Recommended detection:

```text
Find AD Type 0xFF
AND raw payload starts with 0A 62 02 15
AND payload length is sufficient for Device Status + MAC + Timestamp + Battery + Major + Minor + RSSI@1m
```

For the door state:

```text
status = payload[4]
door_open = (status & 0x08) != 0
```

## Open validation points

Validate these points with real BLE captures from your S03D devices:

- Whether your firmware uses this older MK PIR / Customized-PIR format or the newer MK Sensor “Sensor info” format.
- Whether the Company ID is transmitted as raw `0A 62` exactly as in the MOKO examples.
- Whether timestamp is always valid or can be unset after battery change / reset.
- Whether the scan response is needed for your gateway or can be ignored.

## Example capture template

```text
Device: S03D Door Sensor
MAC:
RSSI:
ADV raw:
SCAN_RSP raw:
Decoded:
  door_open:
  battery_mv:
  timestamp:
  major:
  minor:
  rssi_1m:
```

## Sources

- MOKO Door Sensor User Manual V1.1, 2024-12-24: https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2025/03/S03D-Door-Sensor-User-Maunal_V1.1_20241224.pdf
- MOKOSmart S03D product page: https://www.mokosmart.com/bluetooth-door-sensor/
