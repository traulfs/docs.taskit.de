---
tags:
  - senml
  - units
  - protocol
  - reference
  - iot
erstellt: 2026-05-20
quelle: RFC 8428, IANA SenML Unit Registry
status: reference
description: "Referenz der SenML-Einheitensymbole (RFC 8428, IANA-Registry) für das Feld u von Sensorwerten: SI-Basis- und abgeleitete Einheiten, Durchfluss, Optik u. a."
---

# SenML-Einheiten

> SenML (Sensor Measurement Lists, [RFC 8428](https://datatracker.ietf.org/doc/html/rfc8428)) definiert ein Datenformat für Sensorwerte. Das Feld `u` (Unit) gibt die physikalische Einheit eines Messwerts an. Die offiziellen Werte sind in der [IANA SenML Unit Registry](https://www.iana.org/assignments/senml/senml.xhtml#senml-units) aufgeführt.

Verwendet u. a. in: [[taskit BLE Manufacturer Advertisement]] (Byte 11), CoAP/LwM2M-Sensor-Payloads, MQTT-IoT-Anwendungen.

---

## 1. SI-Basiseinheiten

| Symbol | Einheit | Größe |
|---|---|---|
| `m` | Meter | Länge |
| `kg` | Kilogramm | Masse |
| `g` | Gramm | Masse (zulässig) |
| `s` | Sekunde | Zeit |
| `A` | Ampere | Elektrische Stromstärke |
| `K` | Kelvin | Thermodynamische Temperatur |
| `cd` | Candela | Lichtstärke |
| `mol` | Mol | Stoffmenge |

---

## 2. Abgeleitete SI-Einheiten

| Symbol | Einheit | Größe |
|---|---|---|
| `Hz` | Hertz | Frequenz |
| `rad` | Radiant | Winkel |
| `sr` | Steradiant | Raumwinkel |
| `N` | Newton | Kraft |
| `Pa` | Pascal | Druck, mechanische Spannung |
| `J` | Joule | Energie, Arbeit, Wärme |
| `W` | Watt | Leistung, Strahlungsfluss |
| `C` | Coulomb | Elektrische Ladung |
| `V` | Volt | Elektrische Spannung |
| `F` | Farad | Elektrische Kapazität |
| `Ohm` | Ohm | Elektrischer Widerstand |
| `S` | Siemens | Elektrischer Leitwert |
| `Wb` | Weber | Magnetischer Fluss |
| `T` | Tesla | Magnetische Flussdichte |
| `H` | Henry | Induktivität |
| `Cel` | Grad Celsius | Temperatur |
| `lm` | Lumen | Lichtstrom |
| `lx` | Lux | Beleuchtungsstärke |
| `Bq` | Becquerel | Radioaktivität |
| `Gy` | Gray | Energiedosis |
| `Sv` | Sievert | Äquivalentdosis |
| `kat` | Katal | Katalytische Aktivität |

---

## 3. Geometrie, Kinematik & Durchfluss

| Symbol | Einheit | Größe |
|---|---|---|
| `m2` | Quadratmeter | Fläche |
| `m3` | Kubikmeter | Volumen |
| `l` | Liter | Volumen |
| `m/s` | Meter pro Sekunde | Geschwindigkeit |
| `m/s2` | Meter pro Sekunde² | Beschleunigung |
| `m3/s` | Kubikmeter pro Sekunde | Volumenstrom |
| `l/s` | Liter pro Sekunde | Volumenstrom |

---

## 4. Optische & Strahlungseinheiten

| Symbol | Einheit | Größe |
|---|---|---|
| `W/m2` | Watt pro Quadratmeter | Bestrahlungsstärke |
| `cd/m2` | Candela pro Quadratmeter | Leuchtdichte |

---

## 5. Informations- & Zähleinheiten

| Symbol | Einheit | Größe |
|---|---|---|
| `bit` | Bit | Datenmenge |
| `bit/s` | Bit pro Sekunde | Datenrate |
| `count` | Zähler | Dimensionslose Anzahl |
| `/` | Verhältnis | Dimensionsloses Verhältnis |
| `1` | Dimensionslos | Reine Zahl |

---

## 6. Geokoordinaten

| Symbol | Einheit | Größe |
|---|---|---|
| `lat` | Grad nördlicher Breite | Breitengrad (WGS84) |
| `lon` | Grad östlicher Länge | Längengrad (WGS84) |

---

## 7. Spezial- & Sensoreinheiten

| Symbol | Einheit | Größe |
|---|---|---|
| `pH` | pH-Wert | Säuregrad (logarithmisch) |
| `dB` | Dezibel | Logarithmisches Verhältnis |
| `dBW` | Dezibelwatt | Leistungspegel |
| `Bspl` | Bel SPL | Schalldruckpegel |
| `NTU` | Nephelometric Turbidity Unit | Trübung |

---

## 8. Prozent- & Verhältniseinheiten

| Symbol | Einheit | Größe |
|---|---|---|
| `%` | Prozent | Verhältnis × 100 |
| `%RH` | Prozent relative Luftfeuchte | Luftfeuchte |
| `%EL` | Prozent verbleibend | Batterieladestand |
| `EL` | Verbleibende Sekunden | Verbleibende Batterielaufzeit |

---

## 9. Frequenz- & Drehzahleinheiten

| Symbol | Einheit | Größe |
|---|---|---|
| `1/s` | Pro Sekunde | Frequenz, Rate |
| `1/min` | Pro Minute | Drehzahl, Rate |
| `beat/min` | Schläge pro Minute | Herzfrequenz |
| `beats` | Anzahl der Schläge | Pulsereignisse |

---

## 10. Materialeigenschaften

| Symbol | Einheit | Größe |
|---|---|---|
| `S/m` | Siemens pro Meter | Elektrische Leitfähigkeit |
| `kg/m3` | Kilogramm pro Kubikmeter | Dichte |
| `J/m` | Joule pro Meter | Kraft / Energie pro Strecke |

---

## 11. Sekundäre Einheiten (mit Umrechnung)

Sekundäre Einheiten werden als primärer Wert im SenML-Feld `u` nicht empfohlen, sind aber in der IANA-Registry aufgeführt und in der Praxis verbreitet:

### 11.1 Zeit

| Symbol | Einheit | SI-Faktor |
|---|---|---|
| `ms` | Millisekunde | × 10⁻³ s |
| `min` | Minute | × 60 s |
| `h` | Stunde | × 3600 s |

### 11.2 Elektrische Energie & Leistung

| Symbol | Einheit | Bedeutung |
|---|---|---|
| `MHz` | Megahertz | × 10⁶ Hz |
| `kW` | Kilowatt | × 10³ W |
| `kVA` | Kilovoltampere | Scheinleistung |
| `kvar` | Kilovar | Blindleistung |
| `Wh` | Wattstunde | × 3600 J |
| `kWh` | Kilowattstunde | × 3,6 × 10⁶ J |
| `VAh` | Voltamperestunde | Scheinenergie |
| `varh` | Varstunde | Blindenergie |
| `kVAh` | Kilovoltamperestunde | Scheinenergie |
| `kvarh` | Kilovarstunde | Blindenergie |

### 11.3 Winkel

| Symbol | Einheit | SI-Faktor |
|---|---|---|
| `deg` | Grad | × π/180 rad |

---

## 12. Verwendung in SenML-Records

Beispiel für einen SenML-Record (CBOR/JSON):

```json
[
  { "n": "temperature", "u": "Cel", "v": 24.7 },
  { "n": "humidity",    "u": "%RH", "v": 58.3 },
  { "n": "pressure",    "u": "Pa",  "v": 101325 },
  { "n": "battery",     "u": "%EL", "v": 87 }
]
```

Das Feld `u` verweist immer auf eine **registrierte** SenML-Einheit aus der IANA-Tabelle.

---

## 13. Verwendung in taskit-Produkten

Im [[taskit BLE Manufacturer Advertisement]] werden in Byte 11 (SenML Unit ID) folgende numerische IDs verwendet (Position innerhalb der IANA-Registry):

| ID | SenML-Symbol | Produkt |
|---:|---|---|
| `55` | `Cel` | [[Measure2Go]] Blue RTD |
| `75` | `pH` | Measure2Go Blue pH-Meter |
| `143` | `mA` | Measure2Go Blue Loop RX / TX |

> ⚠️ Die numerischen IDs beruhen auf der Reihenfolge in der IANA-Registry. Ändert sich die Registry, können sich diese IDs verschieben – die taskit-Firmware definiert sie deshalb als feste Konstanten.

---

## 14. Quellen

- [RFC 8428 – Sensor Measurement Lists (SenML)](https://datatracker.ietf.org/doc/html/rfc8428)
- [IANA SenML Unit Registry](https://www.iana.org/assignments/senml/senml.xhtml#senml-units)
- [RFC 8798 – Additional SenML Units](https://datatracker.ietf.org/doc/html/rfc8798)
- Siehe auch: [[taskit BLE Manufacturer Advertisement]] · [[BLE/BLE Advertisement Format|BLE-Advertisement-Format]]
