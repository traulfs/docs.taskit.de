# MOKOSmart H4-P5202DH2 / H4 Pro — BLE Advertising Data Format

## Scope

This document describes the BLE advertising formats relevant for the MOKOSmart H4-P5202DH2 / H4 Pro Temperature & Humidity Sensor.

The device can advertise several frame types. For environmental sensor decoding, the important custom frame is the **MOKO T&H frame**, transported as **Service Data** (`AD Type = 0x16`) with MOKO-defined Service UUID `0xABFE` and Frame Type `0x70`.

## Product summary

| Item | Value |
|---|---|
| Product | MOKOSmart H4-P5202DH2 / H4 Pro |
| Sensor function | Temperature and relative humidity |
| Main sensor frame | MOKO custom T&H frame |
| Main AD Type | `0x16` Service Data |
| Service UUID | `0xABFE` |
| Frame Type | `0x70` |
| Temperature unit | 0.1 °C / digit, signed int16 |
| Humidity unit | 0.1 %RH / digit, unsigned int16 |
| Battery unit | mV |
| Byte order | Multi-byte values shown in the MOKO examples are MSB first / big endian |

## Supported advertisement frame types

The H4 series supports standard and custom beacon frames. Depending on slot configuration, the device may advertise one or more of these formats:

| Frame | Purpose |
|---|---|
| iBeacon | Apple-compatible beacon UUID / Major / Minor |
| Eddystone UID | Google Eddystone UID |
| Eddystone URL | Google Eddystone URL |
| Eddystone TLM | Battery / telemetry |
| Device Info | MOKO custom device information |
| T&H | MOKO custom temperature and humidity frame |
| No data | Empty slot |

For gateway sensor decoding, prioritize the **T&H frame**.

## T&H ADV packet format

Offsets below are offsets in the complete advertising payload.

| Offset | Field | Length | Example | Description |
|---:|---|---:|---|---|
| 0 | Data length | 1 | `0x02` | Flags AD length |
| 1 | Data type | 1 | `0x01` | Flags |
| 2 | Advertising type | 1 | `0x06` | LE General Discoverable, BR/EDR not supported |
| 3 | Data length | 1 | `0x02` | TX Power AD length |
| 4 | Data type | 1 | `0x0A` | TX Power Level |
| 5 | TX power | 1 | `0x00` | signed int8, dBm |
| 6 | Data length | 1 | `0x13` | Service Data AD length |
| 7 | Data type | 1 | `0x16` | Service Data |
| 8-9 | Service UUID | 2 | `AB FE` | MOKO-defined Service UUID |
| 10 | Frame Type | 1 | `0x70` | T&H frame |
| 11 | Ranging data | 1 | `0x00` | Calibrated ranging data / power reference |
| 12 | Advertising interval | 1 | `0x0A` | Unit: 100 ms; example 1000 ms |
| 13-14 | Temperature | 2 | `00 C8` | signed int16, 0.1 °C / digit |
| 15-16 | Humidity | 2 | `01 37` | unsigned int16, 0.1 %RH / digit |
| 17-18 | Battery voltage | 2 | `0C 2B` | unsigned int16, mV |
| 19 | Device type / RFU | 1 | `0x03` | reserved / device type field |
| 20-25 | MAC address | 6 | `D9 16 E3 A6 20 95` | Beacon MAC address |

## Service Data payload view

If the parser receives only Service Data after AD type `0x16`, use this table:

| Payload offset | Field | Length | Decode |
|---:|---|---:|---|
| 0-1 | Service UUID | 2 | must be `AB FE` |
| 2 | Frame Type | 1 | must be `0x70` |
| 3 | Ranging data | 1 | signed or raw calibration byte |
| 4 | Advertising interval | 1 | value × 100 ms |
| 5-6 | Temperature | 2 | `int16_be / 10.0` °C |
| 7-8 | Humidity | 2 | `uint16_be / 10.0` %RH |
| 9-10 | Battery voltage | 2 | `uint16_be` mV |
| 11 | Device type / RFU | 1 | reserved |
| 12-17 | MAC address | 6 | raw MAC bytes |

## Decoder formulas

```c
int16_t temp_raw = (int16_t)((p[5] << 8) | p[6]);
uint16_t hum_raw = (uint16_t)((p[7] << 8) | p[8]);
uint16_t batt_mv = (uint16_t)((p[9] << 8) | p[10]);

float temperature_c = temp_raw / 10.0f;
float humidity_rh   = hum_raw / 10.0f;
```

Examples from MOKO documentation:

| Raw value | Decoded value |
|---|---|
| `00 C8` | 200 → 20.0 °C |
| `01 37` | 311 → 31.1 %RH |
| `0C 2B` | 3115 mV |

## Parser identification

Recommended detection:

```text
Find AD Type 0x16
AND Service UUID == AB FE
AND Frame Type == 0x70
```

Do not parse all `0xABFE` frames as temperature/humidity. MOKO also defines other frame types, for example:

| Frame Type | Meaning |
|---|---|
| `0x40` | Device Info |
| `0x50` | MOKO custom iBeacon response frame |
| `0x60` | 3-axis accelerometer frame |
| `0x70` | Temperature & Humidity frame |

## Open validation points

Validate these points with real BLE captures from your H4-P5202DH2/H4 Pro devices:

- Which advertisement slots are enabled in your configuration.
- Whether T&H frame `0x70` is active by default.
- Whether the device also emits iBeacon or Eddystone frames in alternating slots.
- Whether MAC byte order should be displayed exactly as transmitted or normalized to your project convention.

## Example capture template

```text
Device: H4-P5202DH2 / H4 Pro
MAC:
RSSI:
ADV raw:
SCAN_RSP raw:
Decoded:
  temperature_c:
  humidity_rh:
  battery_mv:
  adv_interval_ms:
```

## Sources

- MOKO BeaconX Pro APP User Manual V1.1, Customized T&H advertisement: https://devzone.nordicsemi.com/cfs-file/__key/communityserver-discussions-components-files/4/8255.MOKO-Standard-APP-User-Maunal_5F00_V1.1_5F00_20220301.pdf
- H4 Series Beacon Datasheet: https://fcc.report/FCC-ID/2AO94-H4/5130724.pdf
- MOKOSmart H4 Pro product page: https://www.mokosmart.com/mokosmart-h4-p5202dh2-beacon-ip66-waterproof-with-external-sensor/
