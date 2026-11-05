---
description: "BLE-Advertising-Format des MOKOSmart S02R ToF-Sensor-Beacons: herstellerspezifische Daten mit Entfernung in mm, Batteriespannung und MAC-Suffix."
---

# MOKOSmart S02R ToF Sensor Beacon – BLE-Advertising-Datenformat

## Geltungsbereich

Dieses Dokument beschreibt das BLE-Advertising-Datenformat des MOKOSmart S02R / TOF Ranging Sensor Beacon.

Das Gerät sendet ein eigenes Sensorpaket mit der per ToF gemessenen Entfernung, der Batteriespannung, Benutzerdaten und einem kurzen MAC-Suffix. Die relevanten BLE-Daten befinden sich in der AD-Struktur **Manufacturer Specific Data** (`AD Type = 0xFF`).

## Produktübersicht

| Merkmal | Wert |
|---|---|
| Produkt | MOKOSmart S02R / TOF Ranging Sensor Beacon |
| Sensorfunktion | Time-of-Flight-Entfernungs- / Abstandsmessung |
| Einheit Entfernung | Millimeter |
| Haupt-BLE-Format | Eigene Manufacturer Specific Data |
| Haupt-AD-Typ | `0xFF` |
| Standard-Herstellercode | logisch `0x0059` / Nordic Semiconductor laut MOKO-Anleitung |
| Optionaler Herstellercode | logisch `0x0A62` / MOKO Technology, konfigurierbar |
| Standard-Beacon-Code | logisch `0x6C07` |
| Sub Type | `0x01` = ToF Sensor |
| Byte-Reihenfolge | Little Endian laut MOKO-Anleitung |

## Übersicht des BLE-Advertisements

Eine typische Legacy-BLE-Advertising-Payload enthält:

```text
02 01 06
12 FF <manufacturer-specific-payload>
07 09 4D 4B 20 54 4F 46
```

Bedeutung:

| Teil | Bedeutung |
|---|---|
| `02 01 06` | Flags |
| `12 FF ...` | Manufacturer Specific Data |
| `07 09 4D 4B 20 54 4F 46` | Complete Local Name: `MK TOF` |

Hinweis: Die AD-Länge der Manufacturer Specific Data ist normalerweise `0x12` für die 17-Byte-Herstellerpayload plus das AD-Typ-Byte. Bei manchen Textextraktionen der PDF-Tabelle erscheint `0x1A`; verwenden Sie zur Validierung des Parsers echte Rohpakete und die Anzahl der Felder.

## ADV-Paketformat

Die folgenden Offsets beziehen sich auf die vollständige Advertising-Payload einschließlich der Bytes für AD-Länge und AD-Typ.

| Offset | Feld | Länge | Beispiel | Beschreibung |
|---:|---|---:|---|---|
| 0 | AD1 Length | 1 | `0x02` | Länge der Flags AD |
| 1 | AD1 Type | 1 | `0x01` | Flags |
| 2 | AD1 Flags | 1 | `0x06` | LE General Discoverable, BR/EDR nicht unterstützt |
| 3 | AD2 Length | 1 | `0x12` | Länge der Herstellerdaten-AD |
| 4 | AD2 Type | 1 | `0xFF` | Manufacturer Specific Data |
| 5-6 | MFG Code | 2 | roh `59 00` | Logisch `0x0059`, little endian |
| 7-8 | Beacon Code | 2 | roh `07 6C` | Logisch `0x6C07`, little endian |
| 9-10 | Tag Battery | 2 | roh z. B. `EA 0B` | Batteriespannung in mV, little endian |
| 11 | Event Status | 1 | `0xFF` | Reserviert, Standard `0xFF` |
| 12-13 | Temperature | 2 | `FF FF` | Reserviert, Standard `0xFFFF` |
| 14-15 | Ranging Distance | 2 | roh z. B. `78 00` | Entfernung in mm, little endian |
| 16-17 | User Data | 2 | `FF FF` | Vom Benutzer konfigurierbare ID / Tag-Daten |
| 18 | Sub Type | 1 | `0x01` | `0x01` = ToF Sensor |
| 19-20 | MAC Suffix | 2 | gerätespezifisch | Letzte 4 Hex-Ziffern der MAC-Adresse |
| 21 | Reserved | 1 | `0xFF` | Reserviert |

## Sicht auf die herstellerspezifische Payload

Wenn der Parser nur die `0xFF`-Payload ohne AD-Länge und AD-Typ erhält, verwenden Sie diese Offset-Tabelle:

| Payload-Offset | Feld | Länge | Dekodierung |
|---:|---|---:|---|
| 0-1 | MFG Code | 2 | `uint16_le` |
| 2-3 | Beacon Code | 2 | `uint16_le` |
| 4-5 | Battery voltage | 2 | `uint16_le`, mV |
| 6 | Event Status | 1 | reserviert |
| 7-8 | Temperature | 2 | reserviert / derzeit `0xFFFF` |
| 9-10 | Ranging Distance | 2 | `uint16_le`, mm |
| 11-12 | User Data | 2 | `uint16_le` |
| 13 | Sub Type | 1 | `0x01` = ToF Sensor |
| 14-15 | MAC Suffix | 2 | letzte 2 Bytes der MAC |
| 16 | Reserved | 1 | reserviert |

## Dekodierformeln

```c
uint16_t mfg_code      = p[0]  | (p[1]  << 8);
uint16_t beacon_code   = p[2]  | (p[3]  << 8);
uint16_t battery_mv    = p[4]  | (p[5]  << 8);
uint16_t distance_mm   = p[9]  | (p[10] << 8);
uint16_t user_data     = p[11] | (p[12] << 8);
uint8_t  subtype       = p[13];
```

## Erkennung im Parser

Empfohlene Erkennung:

```text
AD Type == 0xFF
AND MFG Code == 0x0059 or 0x0A62
AND Beacon Code == 0x6C07
AND Sub Type == 0x01
```

Identifizieren Sie dieses Produkt nicht allein anhand der Payload-Länge. Firmware-Versionen oder konfigurierte Hersteller-/Beacon-Codes können sich ändern.

## Scan Response

Die Scan Response enthält normalerweise den Gerätenamen.

| Offset | Feld | Länge | Beispiel | Beschreibung |
|---:|---|---:|---|---|
| 0 | AD Length | 1 | `0x07` | Länge der Namens-AD |
| 1 | AD Type | 1 | `0x09` | Complete Local Name |
| 2..n | Device Name | 1-20 | ASCII `MK TOF` | Gerätename |

## Offene Validierungspunkte

Prüfen Sie diese Punkte mit echten BLE-Mitschnitten Ihrer Geräte:

- Ob Ihr bestellter S02R den Herstellercode `0x0059` oder `0x0A62` verwendet.
- Ob der Beacon-Code `0x6C07` bleibt.
- Ob die AD2-Länge in Rohmitschnitten immer `0x12` ist.
- Ob die Entfernung bei jedem Advertising-Intervall oder nur im konfigurierten ToF-Messintervall aktualisiert wird.

## Vorlage für Mitschnitte

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

## Quellen

- MOKO TOF Ranging Sensor User Guide V1.1, 2024-08-21: https://robu-prod-media.s3.ap-south-1.amazonaws.com/uploads/2025/03/TOF-Sensor-User-Guide_V1.1_20240821-Standard-Version.pdf
- Produktseite MOKOSmart S02R: https://www.mokosmart.com/tof-sensor-beacon/
