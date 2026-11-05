---
description: "BLE-Advertising-Format des MOKOSmart H4-P5202DH2 / H4 Pro (Temperatur und Luftfeuchte): MOKO-T&H-Frame, Service UUID 0xABFE, Frame-Typ 0x70."
---

# MOKOSmart H4-P5202DH2 / H4 Pro – BLE-Advertising-Datenformat

## Geltungsbereich

Dieses Dokument beschreibt die relevanten BLE-Advertising-Formate des Temperatur- und Luftfeuchtesensors MOKOSmart H4-P5202DH2 / H4 Pro.

Das Gerät kann mehrere Frame-Typen senden. Für die Dekodierung der Umweltsensordaten ist der eigene **MOKO-T&H-Frame** maßgeblich, der als **Service Data** (`AD Type = 0x16`) mit der von MOKO definierten Service UUID `0xABFE` und dem Frame-Typ `0x70` übertragen wird.

## Produktübersicht

| Merkmal | Wert |
|---|---|
| Produkt | MOKOSmart H4-P5202DH2 / H4 Pro |
| Sensorfunktion | Temperatur und relative Luftfeuchte |
| Haupt-Sensor-Frame | MOKO-eigener T&H-Frame |
| Haupt-AD-Typ | `0x16` Service Data |
| Service UUID | `0xABFE` |
| Frame-Typ | `0x70` |
| Einheit Temperatur | 0,1 °C / Digit, int16 vorzeichenbehaftet |
| Einheit Luftfeuchte | 0,1 %RH / Digit, uint16 vorzeichenlos |
| Einheit Batterie | mV |
| Byte-Reihenfolge | Mehrbytewerte in den MOKO-Beispielen: MSB zuerst / Big Endian |

## Unterstützte Advertisement-Frame-Typen

Die H4-Serie unterstützt Standard- und eigene Beacon-Frames. Je nach Slot-Konfiguration sendet das Gerät eines oder mehrere dieser Formate:

| Frame | Zweck |
|---|---|
| iBeacon | Apple-kompatible Beacon-UUID / Major / Minor |
| Eddystone UID | Google Eddystone UID |
| Eddystone URL | Google Eddystone URL |
| Eddystone TLM | Batterie / Telemetrie |
| Device Info | MOKO-eigene Geräteinformationen |
| T&H | MOKO-eigener Temperatur- und Luftfeuchte-Frame |
| No data | Leerer Slot |

Für die Dekodierung der Sensordaten im Gateway hat der **T&H-Frame** Vorrang.

## Paketformat des T&H-ADV

Die folgenden Offsets beziehen sich auf die vollständige Advertising-Payload.

| Offset | Feld | Länge | Beispiel | Beschreibung |
|---:|---|---:|---|---|
| 0 | Data length | 1 | `0x02` | Länge der Flags AD |
| 1 | Data type | 1 | `0x01` | Flags |
| 2 | Advertising type | 1 | `0x06` | LE General Discoverable, BR/EDR nicht unterstützt |
| 3 | Data length | 1 | `0x02` | Länge der TX Power AD |
| 4 | Data type | 1 | `0x0A` | TX Power Level |
| 5 | TX power | 1 | `0x00` | int8 vorzeichenbehaftet, dBm |
| 6 | Data length | 1 | `0x13` | Länge der Service Data AD |
| 7 | Data type | 1 | `0x16` | Service Data |
| 8-9 | Service UUID | 2 | `AB FE` | Von MOKO definierte Service UUID |
| 10 | Frame Type | 1 | `0x70` | T&H-Frame |
| 11 | Ranging data | 1 | `0x00` | Kalibrierte Ranging-Daten / Leistungsreferenz |
| 12 | Advertising interval | 1 | `0x0A` | Einheit: 100 ms; Beispiel 1000 ms |
| 13-14 | Temperature | 2 | `00 C8` | int16 vorzeichenbehaftet, 0,1 °C / Digit |
| 15-16 | Humidity | 2 | `01 37` | uint16 vorzeichenlos, 0,1 %RH / Digit |
| 17-18 | Battery voltage | 2 | `0C 2B` | uint16 vorzeichenlos, mV |
| 19 | Device type / RFU | 1 | `0x03` | Reserviert / Gerätetyp-Feld |
| 20-25 | MAC address | 6 | `D9 16 E3 A6 20 95` | MAC-Adresse des Beacons |

## Sicht auf die Service-Data-Payload

Wenn der Parser nur die Service Data nach dem AD-Typ `0x16` erhält, verwenden Sie diese Tabelle:

| Payload-Offset | Feld | Länge | Dekodierung |
|---:|---|---:|---|
| 0-1 | Service UUID | 2 | muss `AB FE` sein |
| 2 | Frame Type | 1 | muss `0x70` sein |
| 3 | Ranging data | 1 | vorzeichenbehaftetes oder rohes Kalibrierbyte |
| 4 | Advertising interval | 1 | Wert × 100 ms |
| 5-6 | Temperature | 2 | `int16_be / 10.0` °C |
| 7-8 | Humidity | 2 | `uint16_be / 10.0` %RH |
| 9-10 | Battery voltage | 2 | `uint16_be` mV |
| 11 | Device type / RFU | 1 | reserviert |
| 12-17 | MAC address | 6 | rohe MAC-Bytes |

## Dekodierformeln

```c
int16_t temp_raw = (int16_t)((p[5] << 8) | p[6]);
uint16_t hum_raw = (uint16_t)((p[7] << 8) | p[8]);
uint16_t batt_mv = (uint16_t)((p[9] << 8) | p[10]);

float temperature_c = temp_raw / 10.0f;
float humidity_rh   = hum_raw / 10.0f;
```

Beispiele aus der MOKO-Dokumentation:

| Rohwert | Dekodierter Wert |
|---|---|
| `00 C8` | 200 → 20,0 °C |
| `01 37` | 311 → 31,1 %RH |
| `0C 2B` | 3115 mV |

## Erkennung im Parser

Empfohlene Erkennung:

```text
Find AD Type 0x16
AND Service UUID == AB FE
AND Frame Type == 0x70
```

Parsen Sie nicht alle `0xABFE`-Frames als Temperatur/Luftfeuchte. MOKO definiert auch andere Frame-Typen, zum Beispiel:

| Frame-Typ | Bedeutung |
|---|---|
| `0x40` | Device Info |
| `0x50` | MOKO-eigener iBeacon-Response-Frame |
| `0x60` | Frame des 3-Achsen-Beschleunigungssensors |
| `0x70` | Temperatur- & Luftfeuchte-Frame |

## Offene Validierungspunkte

Prüfen Sie diese Punkte mit echten BLE-Mitschnitten Ihrer H4-P5202DH2/H4-Pro-Geräte:

- Welche Advertisement-Slots in Ihrer Konfiguration aktiviert sind.
- Ob der T&H-Frame `0x70` standardmäßig aktiv ist.
- Ob das Gerät in wechselnden Slots zusätzlich iBeacon- oder Eddystone-Frames sendet.
- Ob die MAC-Byte-Reihenfolge genau wie übertragen angezeigt oder an die Konvention Ihres Projekts angepasst werden soll.

## Vorlage für Mitschnitte

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

## Quellen

- MOKO BeaconX Pro APP User Manual V1.1, Customized T&H advertisement: https://devzone.nordicsemi.com/cfs-file/__key/communityserver-discussions-components-files/4/8255.MOKO-Standard-APP-User-Maunal_5F00_V1.1_5F00_20220301.pdf
- Datenblatt H4 Series Beacon: https://fcc.report/FCC-ID/2AO94-H4/5130724.pdf
- Produktseite MOKOSmart H4 Pro: https://www.mokosmart.com/mokosmart-h4-p5202dh2-beacon-ip66-waterproof-with-external-sensor/
