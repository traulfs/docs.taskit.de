# Ruuvi RuuviTag — BLE Advertising Data Format

## Scope

This document describes the BLE advertising data format used by the RuuviTag wireless environmental sensor.

RuuviTag broadcasts sensor data in BLE advertising packets using **Manufacturer Specific Data** (`AD Type = 0xFF`). The current main format for RuuviTag is **Data Format 5 / RAWv2**.

## Product summary

| Item | Value |
|---|---|
| Product | RuuviTag |
| Sensor functions | Temperature, humidity, air pressure, motion / acceleration, battery |
| Main BLE transport | BLE advertising broadcast |
| Main AD Type | `0xFF` Manufacturer Specific Data |
| Ruuvi Manufacturer ID | logical `0x0499` |
| Raw manufacturer bytes | `99 04` |
| Current main data format | Format `0x05` / RAWv2 |
| RAWv2 payload length | 24 bytes after manufacturer ID |
| Multi-byte byte order | MSB first / big endian |

## Supported Ruuvi advertisement formats

Ruuvi documentation lists several data formats. For RuuviTag integration, the relevant ones are:

| Format | Name | Lifecycle | Notes |
|---:|---|---|---|
| `0x03` | RAWv1 | Deprecated | Older RuuviTag firmware; no MAC address in payload |
| `0x04` | URL | Obsolete | Eddystone URL based format, older hardware/firmware |
| `0x05` | RAWv2 | In production | Current primary RuuviTag sensor format |
| `0xC5` | Cut-RAWv2 | Beta | Similar to RAWv2, acceleration removed |

For a new gateway/parser, implement **Format 5 / RAWv2** first.

## BLE advertisement overview

A typical RuuviTag RAWv2 advertisement has this structure:

```text
02 01 06
1B FF 99 04 <24-byte RAWv2 payload>
```

Meaning:

| Part | Meaning |
|---|---|
| `02 01 06` | Flags |
| `1B` | AD length = 27 bytes following: AD type + manufacturer ID + payload |
| `FF` | Manufacturer Specific Data |
| `99 04` | Ruuvi manufacturer ID `0x0499`, transmitted little-endian in the BLE AD structure |
| `<payload>` | Ruuvi payload; first payload byte is data format, e.g. `0x05` |

## RAWv2 manufacturer-specific payload

If the parser receives only the payload after Ruuvi manufacturer bytes `99 04`, use this table.

| Payload offset | Field | Length | Decode | Unit / description |
|---:|---|---:|---|---|
| 0 | Data Format | 1 | `0x05` | RAWv2 |
| 1-2 | Temperature | 2 | `int16_be * 0.005` | °C |
| 3-4 | Humidity | 2 | `uint16_be * 0.0025` | %RH |
| 5-6 | Pressure | 2 | `uint16_be + 50000` | Pa |
| 7-8 | Acceleration X | 2 | `int16_be` | mg |
| 9-10 | Acceleration Y | 2 | `int16_be` | mg |
| 11-12 | Acceleration Z | 2 | `int16_be` | mg |
| 13-14 | Power Info | 2 | bitfield | battery + TX power |
| 15 | Movement Counter | 1 | `uint8_t` | incremented on motion interrupt |
| 16-17 | Measurement Sequence | 2 | `uint16_be` | measurement sequence number |
| 18-23 | MAC Address | 6 | raw MAC bytes | 48-bit MAC address |

## Power Info bitfield

Power Info is a 16-bit unsigned big-endian field.

| Bits | Field | Decode |
|---:|---|---|
| 15-5 | Battery voltage above 1.6 V | `battery_mv = ((power_info >> 5) & 0x07FF) + 1600` |
| 4-0 | TX power above -40 dBm in 2 dBm steps | `tx_power_dbm = (power_info & 0x1F) * 2 - 40` |

Supported ranges:

| Field | Range |
|---|---|
| Battery voltage | 1600 mV to 3646 mV |
| TX power | -40 dBm to +20 dBm |

## Decoder formulas

```c
static int16_t be_i16(const uint8_t *p)
{
    return (int16_t)(((uint16_t)p[0] << 8) | p[1]);
}

static uint16_t be_u16(const uint8_t *p)
{
    return ((uint16_t)p[0] << 8) | p[1];
}

uint8_t format = p[0]; // must be 0x05

float temperature_c = be_i16(&p[1]) * 0.005f;
float humidity_rh   = be_u16(&p[3]) * 0.0025f;
uint32_t pressure_pa = (uint32_t)be_u16(&p[5]) + 50000u;

int16_t acc_x_mg = be_i16(&p[7]);
int16_t acc_y_mg = be_i16(&p[9]);
int16_t acc_z_mg = be_i16(&p[11]);

uint16_t power_info = be_u16(&p[13]);
uint16_t battery_mv = ((power_info >> 5) & 0x07FFu) + 1600u;
int8_t tx_power_dbm = (int8_t)((power_info & 0x1Fu) * 2 - 40);

uint8_t movement_counter = p[15];
uint16_t measurement_sequence = be_u16(&p[16]);
```

## Invalid / not available values

Ruuvi uses special values for missing data:

| Field type | Invalid value |
|---|---|
| Signed integer field | smallest representable value, e.g. `0x8000` for int16 |
| Unsigned integer field | largest representable value, e.g. `0xFFFF` for uint16 |
| MAC address | all bits set, `FF:FF:FF:FF:FF:FF` |

## Parser identification

Recommended detection:

```text
Find AD Type 0xFF
AND manufacturer bytes == 99 04
AND first Ruuvi payload byte == 0x05
AND payload has at least 24 bytes
```

Then parse with RAWv2 offsets.

Do not identify Ruuvi data only by BLE address or device name. RuuviTag data is designed to be parsed from Manufacturer Specific Data.

## Notes on older formats

### Format 3 / RAWv1

RAWv1 is deprecated but may still appear in older deployed RuuviTags. It contains humidity, temperature, pressure, acceleration and battery voltage, but not the MAC address in the payload.

### Format 4 / URL

Format 4 is obsolete and was packed inside Eddystone URL. It is not recommended for new parser work.

### Format C5 / Cut-RAWv2

Format C5 is a beta format related to RuuviTag/Ruuvi Gateway. It resembles RAWv2 but omits acceleration to make space for other information.

## Example capture template

```text
Device: RuuviTag
MAC:
RSSI:
ADV raw:
SCAN_RSP raw:
Decoded:
  temperature_c:
  humidity_rh:
  pressure_pa:
  acc_x_mg:
  acc_y_mg:
  acc_z_mg:
  battery_mv:
  tx_power_dbm:
  movement_counter:
  measurement_sequence:
  mac_payload:
```

## Sources

- Ruuvi Bluetooth Advertisements documentation: https://docs.ruuvi.com/communication/bluetooth-advertisements
- Ruuvi Data Format 5 / RAWv2: https://docs.ruuvi.com/communication/bluetooth-advertisements/data-format-5-rawv2
- Ruuvi Data Format 3 / RAWv1: https://docs.ruuvi.com/communication/bluetooth-advertisements/data-format-3-rawv1
- Ruuvi Data Format 4 / URL: https://docs.ruuvi.com/communication/bluetooth-advertisements/data-format-4-url
- RuuviTag product page: https://ruuvi.com/ruuvitag/
