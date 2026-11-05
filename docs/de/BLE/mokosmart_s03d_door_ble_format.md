---
description: "BLE-Advertising-Format des MOKOSmart S03D Türsensors: ADV_IND mit Türstatus in Device-Status-Bit 3, Batterie und Zeitstempel sowie Scan Response."
---

# MOKOSmart S03D Door Sensor – BLE-Advertising-Datenformat

## Geltungsbereich

Dieses Dokument beschreibt das BLE-Advertising-Format des Bluetooth-Türsensors MOKOSmart S03D.

Der S03D verwendet ein eigenes Format, bestehend aus:

1. **ADV_IND**-Advertising-Paket: Tür-/Hall-Status, Batteriespannung, Zeitstempel, MAC, Major, Minor, RSSI@1m.
2. **SCAN_RSP**-Scan-Response-Paket: Sendeleistung und vollständiger lokaler Name.

Der wichtige Türstatus ist in **Device-Status-Bit 3** kodiert.

## Produktübersicht

| Merkmal | Wert |
|---|---|
| Produkt | MOKOSmart S03D Bluetooth Door Sensor |
| Sensorfunktion | Tür/Fenster offen/geschlossen über Hall-Sensor + Magnet |
| Haupt-ADV-Typ | `0xFF` Manufacturer Specific Data |
| Company ID in MOKO-Tabelle/Rohbeispielen | `0A 62` / MOKO Technology |
| Paketfamilie | Customized-PIR / Door Sensor packet |
| Bit für Türstatus | Device-Status-Bit 3 |
| Einheit Batterie | mV |
| Format Zeitstempel | `YY/MM/DD/HH:MM:SS` |

## Logik des Türstatus

Verwenden Sie für die Parser-Implementierung **Device-Status-Bit 3** aus dem ADV-Paket.

| Device-Status-Bit 3 | Türstatus | Magnetstatus |
|---:|---|---|
| `0` | Tür geschlossen | Magnet nähert sich |
| `1` | Tür offen | Magnet entfernt |

Hinweis: Das Handbuch beschreibt den elektrischen Status des Hall-Sensors zusätzlich separat. Für das BLE-Parsing weisen die Advertisement-Tabelle und das Paketbeispiel Bit 3 als Statusbit für Tür offen/geschlossen aus.

## ADV_IND-Paketformat

Die folgenden Offsets beziehen sich auf die vollständige Advertising-Payload.

| Offset | Feld | Länge | Beispiel | Beschreibung |
|---:|---|---:|---|---|
| 0 | ADV Length | 1 | `0x02` | Länge der Flags AD |
| 1 | ADV Type | 1 | `0x01` | Flags |
| 2 | Beacon Type / Flags | 1 | `0x04` | BR/EDR nicht unterstützt |
| 3 | ADV Length | 1 | `0x1A` | Länge der Herstellerdaten-AD |
| 4 | ADV Type | 1 | `0xFF` | Herstellerdaten |
| 5-6 | Company ID | 2 | `0A 62` | MOKO Technology Ltd laut MOKO-Tabelle |
| 7 | iBeacon Type | 1 | `0x02` | fest |
| 8 | iBeacon Length | 1 | `0x15` | 21 Bytes |
| 9 | Device Status | 1 | z. B. `0x09` | Bitfeld, enthält das Bit Tür offen/geschlossen |
| 10 | RFU | 1 | `0x00` | Reserviert |
| 11-16 | MAC address | 6 | Geräte-MAC | Aus dem Chipsatz gelesene MAC-Adresse |
| 17-22 | Timestamp | 6 | `16 03 1E 0D 3A 19` | `YY/MM/DD/HH:MM:SS` |
| 23-24 | Battery voltage | 2 | `0E 2A` | mV |
| 25-26 | Major | 2 | `00 00` | konfigurierbarer Gruppenwert |
| 27-28 | Minor | 2 | `00 00` | konfigurierbarer Geräte-ID-Wert |
| 29 | RSSI@1m | 1 | `0xB0` | kalibrierter RSSI bei 1 m, int8 vorzeichenbehaftet |

## Sicht auf die herstellerspezifische Payload

Wenn der Parser nur die Payload-Bytes nach dem AD-Typ `0xFF` erhält, verwenden Sie diese Tabelle:

| Payload-Offset | Feld | Länge | Dekodierung |
|---:|---|---:|---|
| 0-1 | Company ID | 2 | `0A 62` laut MOKO-Rohbeispiel |
| 2 | iBeacon Type | 1 | `0x02` |
| 3 | iBeacon Length | 1 | `0x15` |
| 4 | Device Status | 1 | Bitfeld |
| 5 | RFU | 1 | reserviert |
| 6-11 | MAC address | 6 | rohe MAC-Bytes |
| 12-17 | Timestamp | 6 | `YY MM DD HH MM SS` |
| 18-19 | Battery voltage | 2 | `uint16_be`, mV |
| 20-21 | Major | 2 | `uint16_be` |
| 22-23 | Minor | 2 | `uint16_be` |
| 24 | RSSI@1m | 1 | `int8_t`, dBm |

## Bitfeld Device Status

| Bits | Name | Bedeutung |
|---:|---|---|
| 7-6 | RFU | reserviert |
| 5-4 | PIR delay response status | `10` = hohe Verzögerung, `01` = mittlere Verzögerung, `00` = geringe Verzögerung |
| 3 | Door Open/Close status | `0` = geschlossen, `1` = offen |
| 2-1 | PIR sensor sensitivity | `10` = hoch, `01` = mittel, `00` = niedrig |
| 0 | PIR sensor detection status | `0` = keine wirksame Bewegung, `1` = wirksame Bewegung erkannt |

Für die Türerkennung beim S03D wird normalerweise nur Bit 3 benötigt.

## Dekodierformeln

```c
uint8_t status = p[4];
bool door_open = (status & (1u << 3)) != 0;

uint16_t battery_mv = ((uint16_t)p[18] << 8) | p[19];
uint16_t major      = ((uint16_t)p[20] << 8) | p[21];
uint16_t minor      = ((uint16_t)p[22] << 8) | p[23];
int8_t rssi_1m      = (int8_t)p[24];
```

Umrechnung des Zeitstempels:

```c
uint8_t year   = p[12];  // YY
uint8_t month  = p[13];
uint8_t day    = p[14];
uint8_t hour   = p[15];
uint8_t minute = p[16];
uint8_t second = p[17];
```

## SCAN_RSP-Paketformat

| Offset | Feld | Länge | Beispiel | Beschreibung |
|---:|---|---:|---|---|
| 0 | ADV Length | 1 | `0x02` | Länge der TX Power AD |
| 1 | ADV Type | 1 | `0x0A` | TX Power Level |
| 2 | TX Power | 1 | `0xF4` | int8 vorzeichenbehaftet, dBm; Beispiel `-12 dBm` |
| 3 | ADV Length | 1 | variabel | Länge des Complete Local Name |
| 4 | ADV Type | 1 | `0x09` | Complete Local Name |
| 5..n | Device name | 1-10 | ASCII | Gerätename |
| nach dem Namen | Serial ID | 1-5 | ASCII-Ziffern | Serien-ID, Bereich 0-99999 |

## Erkennung im Parser

Empfohlene Erkennung:

```text
Find AD Type 0xFF
AND raw payload starts with 0A 62 02 15
AND payload length is sufficient for Device Status + MAC + Timestamp + Battery + Major + Minor + RSSI@1m
```

Für den Türstatus:

```text
status = payload[4]
door_open = (status & 0x08) != 0
```

## Offene Validierungspunkte

Prüfen Sie diese Punkte mit echten BLE-Mitschnitten Ihrer S03D-Geräte:

- Ob Ihre Firmware dieses ältere Format MK PIR / Customized-PIR oder das neuere Format „Sensor info“ von MK Sensor verwendet.
- Ob die Company ID genau wie in den MOKO-Beispielen roh als `0A 62` übertragen wird.
- Ob der Zeitstempel immer gültig ist oder nach einem Batteriewechsel / Reset nicht gesetzt sein kann.
- Ob die Scan Response für Ihr Gateway benötigt wird oder ignoriert werden kann.

## Vorlage für Mitschnitte

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

## Quellen

- MOKO Door Sensor User Manual V1.1, 2024-12-24: https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2025/03/S03D-Door-Sensor-User-Maunal_V1.1_20241224.pdf
- Produktseite MOKOSmart S03D: https://www.mokosmart.com/bluetooth-door-sensor/
