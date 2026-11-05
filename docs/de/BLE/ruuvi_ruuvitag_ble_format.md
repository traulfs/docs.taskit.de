---
description: "BLE-Advertising-Format des Umweltsensors RuuviTag: Data Format 5 (RAWv2) mit Temperatur, Luftfeuchte, Luftdruck, Beschleunigung und Batteriedaten."
---

# Ruuvi RuuviTag – BLE-Advertising-Datenformat

## Geltungsbereich

Dieses Dokument beschreibt das BLE-Advertising-Datenformat des drahtlosen Umweltsensors RuuviTag.

RuuviTag sendet Sensordaten in BLE-Advertising-Paketen als **Manufacturer Specific Data** (`AD Type = 0xFF`). Das aktuelle Hauptformat des RuuviTag ist **Data Format 5 / RAWv2**.

## Produktübersicht

| Merkmal | Wert |
|---|---|
| Produkt | RuuviTag |
| Sensorfunktionen | Temperatur, Luftfeuchte, Luftdruck, Bewegung / Beschleunigung, Batterie |
| Haupt-BLE-Transport | BLE-Advertising-Broadcast |
| Haupt-AD-Typ | `0xFF` Manufacturer Specific Data |
| Ruuvi Manufacturer ID | logisch `0x0499` |
| Roh-Herstellerbytes | `99 04` |
| Aktuelles Hauptdatenformat | Format `0x05` / RAWv2 |
| Länge der RAWv2-Payload | 24 Bytes nach der Manufacturer ID |
| Byte-Reihenfolge bei Mehrbytewerten | MSB zuerst / Big Endian |

## Unterstützte Ruuvi-Advertisement-Formate

Die Ruuvi-Dokumentation führt mehrere Datenformate auf. Für die Integration des RuuviTag sind diese relevant:

| Format | Name | Lebenszyklus | Hinweise |
|---:|---|---|---|
| `0x03` | RAWv1 | Veraltet (deprecated) | Ältere RuuviTag-Firmware; keine MAC-Adresse in der Payload |
| `0x04` | URL | Obsolet | Auf Eddystone-URL basierendes Format, ältere Hardware/Firmware |
| `0x05` | RAWv2 | In Produktion | Aktuelles primäres RuuviTag-Sensorformat |
| `0xC5` | Cut-RAWv2 | Beta | Ähnlich wie RAWv2, ohne Beschleunigung |

Implementieren Sie für ein neues Gateway oder einen neuen Parser zuerst **Format 5 / RAWv2**.

## Übersicht des BLE-Advertisements

Ein typisches RuuviTag-RAWv2-Advertisement hat diesen Aufbau:

```text
02 01 06
1B FF 99 04 <24-byte RAWv2 payload>
```

Bedeutung:

| Teil | Bedeutung |
|---|---|
| `02 01 06` | Flags |
| `1B` | AD-Länge = 27 folgende Bytes: AD-Typ + Manufacturer ID + Payload |
| `FF` | Manufacturer Specific Data |
| `99 04` | Ruuvi Manufacturer ID `0x0499`, in der BLE-AD-Struktur little-endian übertragen |
| `<payload>` | Ruuvi-Payload; das erste Payload-Byte ist das Datenformat, z. B. `0x05` |

## Herstellerspezifische RAWv2-Payload

Wenn der Parser nur die Payload nach den Ruuvi-Herstellerbytes `99 04` erhält, verwenden Sie diese Tabelle.

| Payload-Offset | Feld | Länge | Dekodierung | Einheit / Beschreibung |
|---:|---|---:|---|---|
| 0 | Data Format | 1 | `0x05` | RAWv2 |
| 1-2 | Temperature | 2 | `int16_be * 0.005` | °C |
| 3-4 | Humidity | 2 | `uint16_be * 0.0025` | %RH |
| 5-6 | Pressure | 2 | `uint16_be + 50000` | Pa |
| 7-8 | Acceleration X | 2 | `int16_be` | mg |
| 9-10 | Acceleration Y | 2 | `int16_be` | mg |
| 11-12 | Acceleration Z | 2 | `int16_be` | mg |
| 13-14 | Power Info | 2 | Bitfeld | Batterie + Sendeleistung |
| 15 | Movement Counter | 1 | `uint8_t` | wird bei einem Bewegungs-Interrupt erhöht |
| 16-17 | Measurement Sequence | 2 | `uint16_be` | Laufnummer der Messung |
| 18-23 | MAC Address | 6 | rohe MAC-Bytes | 48-Bit-MAC-Adresse |

## Bitfeld Power Info

Power Info ist ein vorzeichenloses 16-Bit-Feld in Big Endian.

| Bits | Feld | Dekodierung |
|---:|---|---|
| 15-5 | Batteriespannung über 1,6 V | `battery_mv = ((power_info >> 5) & 0x07FF) + 1600` |
| 4-0 | Sendeleistung über -40 dBm in 2-dBm-Schritten | `tx_power_dbm = (power_info & 0x1F) * 2 - 40` |

Unterstützte Bereiche:

| Feld | Bereich |
|---|---|
| Batteriespannung | 1600 mV bis 3646 mV |
| Sendeleistung | -40 dBm bis +20 dBm |

## Dekodierformeln

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

## Ungültige / nicht verfügbare Werte

Ruuvi verwendet Sonderwerte für fehlende Daten:

| Feldtyp | Ungültiger Wert |
|---|---|
| Vorzeichenbehaftetes Ganzzahlfeld | kleinster darstellbarer Wert, z. B. `0x8000` für int16 |
| Vorzeichenloses Ganzzahlfeld | größter darstellbarer Wert, z. B. `0xFFFF` für uint16 |
| MAC-Adresse | alle Bits gesetzt, `FF:FF:FF:FF:FF:FF` |

## Erkennung im Parser

Empfohlene Erkennung:

```text
Find AD Type 0xFF
AND manufacturer bytes == 99 04
AND first Ruuvi payload byte == 0x05
AND payload has at least 24 bytes
```

Anschließend mit den RAWv2-Offsets parsen.

Identifizieren Sie Ruuvi-Daten nicht allein anhand der BLE-Adresse oder des Gerätenamens. RuuviTag-Daten sind dafür ausgelegt, aus den Manufacturer Specific Data geparst zu werden.

## Hinweise zu älteren Formaten

### Format 3 / RAWv1

RAWv1 ist veraltet, kann aber in älteren, bereits eingesetzten RuuviTags noch vorkommen. Es enthält Luftfeuchte, Temperatur, Luftdruck, Beschleunigung und Batteriespannung, jedoch nicht die MAC-Adresse in der Payload.

### Format 4 / URL

Format 4 ist obsolet und wurde in Eddystone-URL verpackt. Für neue Parser wird es nicht empfohlen.

### Format C5 / Cut-RAWv2

Format C5 ist ein Beta-Format im Zusammenhang mit RuuviTag/Ruuvi Gateway. Es ähnelt RAWv2, lässt aber die Beschleunigung weg, um Platz für andere Informationen zu schaffen.

## Vorlage für Mitschnitte

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

## Quellen

- Ruuvi-Dokumentation zu Bluetooth-Advertisements: https://docs.ruuvi.com/communication/bluetooth-advertisements
- Ruuvi Data Format 5 / RAWv2: https://docs.ruuvi.com/communication/bluetooth-advertisements/data-format-5-rawv2
- Ruuvi Data Format 3 / RAWv1: https://docs.ruuvi.com/communication/bluetooth-advertisements/data-format-3-rawv1
- Ruuvi Data Format 4 / URL: https://docs.ruuvi.com/communication/bluetooth-advertisements/data-format-4-url
- RuuviTag-Produktseite: https://ruuvi.com/ruuvitag/
