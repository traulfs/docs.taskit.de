---
tags:
  - senml
  - units
  - protokoll
  - referenz
  - iot
erstellt: 2026-05-20
quelle: RFC 8428, IANA SenML Unit Registry
status: referenz
---

# SenML Units

> SenML (Sensor Measurement Lists, [RFC 8428](https://datatracker.ietf.org/doc/html/rfc8428)) definiert ein Datenformat für Sensorwerte. Das `u`-Feld (unit) gibt die physikalische Einheit eines Messwertes an. Die offiziellen Werte sind in der [IANA SenML Unit Registry](https://www.iana.org/assignments/senml/senml.xhtml#senml-units) verzeichnet.

Verwendung u. a. in: [[taskit BLE Manufacturer Advertisement]] (Byte 11), CoAP-/LwM2M-Sensorpayloads, MQTT-IoT-Anwendungen.

---

## 1. SI-Basiseinheiten

| Symbol | Einheit | Größe |
|---|---|---|
| `m` | Meter | Länge |
| `kg` | Kilogramm | Masse |
| `g` | Gramm | Masse (zugelassen) |
| `s` | Sekunde | Zeit |
| `A` | Ampere | elektrische Stromstärke |
| `K` | Kelvin | thermodynamische Temperatur |
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
| `J` | Joule | Energie, Arbeit, Wärmemenge |
| `W` | Watt | Leistung, Strahlungsfluss |
| `C` | Coulomb | elektrische Ladung |
| `V` | Volt | elektrische Spannung |
| `F` | Farad | elektrische Kapazität |
| `Ohm` | Ohm | elektrischer Widerstand |
| `S` | Siemens | elektrische Leitfähigkeit |
| `Wb` | Weber | magnetischer Fluss |
| `T` | Tesla | magnetische Flussdichte |
| `H` | Henry | Induktivität |
| `Cel` | Grad Celsius | Temperatur |
| `lm` | Lumen | Lichtstrom |
| `lx` | Lux | Beleuchtungsstärke |
| `Bq` | Becquerel | Radioaktivität |
| `Gy` | Gray | Energiedosis |
| `Sv` | Sievert | Äquivalentdosis |
| `kat` | Katal | Katalytische Aktivität |

---

## 3. Geometrie, Kinematik & Strömung

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
| `count` | Zähler | dimensionsloser Zählerwert |
| `/` | Verhältnis | dimensionsloses Verhältnis |
| `1` | dimensionslos | reine Zahl |

---

## 6. Geokoordinaten

| Symbol | Einheit | Größe |
|---|---|---|
| `lat` | Grad nördliche Breite | Breitengrad (WGS84) |
| `lon` | Grad östliche Länge | Längengrad (WGS84) |

---

## 7. Spezial- & Sensor-Einheiten

| Symbol | Einheit | Größe |
|---|---|---|
| `pH` | pH-Wert | Säuregrad (logarithmisch) |
| `dB` | Dezibel | logarithmisches Verhältnis |
| `dBW` | Dezibel-Watt | Leistungspegel |
| `Bspl` | Bel SPL | Schalldruckpegel |
| `NTU` | Nephelometric Turbidity Unit | Trübung |

---

## 8. Prozent- & Anteilseinheiten

| Symbol | Einheit | Größe |
|---|---|---|
| `%` | Prozent | Verhältnis × 100 |
| `%RH` | Prozent rel. Feuchte | Luftfeuchtigkeit |
| `%EL` | Prozent verbleibend | Batterie-Ladestand |
| `EL` | Sekunden verbleibend | verbleibende Batterielaufzeit |

---

## 9. Frequenz- & Drehzahl-Einheiten

| Symbol | Einheit | Größe |
|---|---|---|
| `1/s` | pro Sekunde | Frequenz, Rate |
| `1/min` | pro Minute | Drehzahl, Rate |
| `beat/min` | Schläge pro Minute | Herzfrequenz |
| `beats` | Anzahl Schläge | Pulsereignisse |

---

## 10. Materialeigenschaften

| Symbol | Einheit | Größe |
|---|---|---|
| `S/m` | Siemens pro Meter | elektrische Leitfähigkeit |
| `kg/m3` | Kilogramm pro Kubikmeter | Dichte |
| `J/m` | Joule pro Meter | Kraft / Energie pro Strecke |

---

## 11. Sekundäre Einheiten (mit Umrechnung)

Sekundäre Einheiten werden im SenML-Feld `u` nicht als Primärwert empfohlen, sind aber in der IANA-Registry verzeichnet und in der Praxis verbreitet:

### 11.1 Zeit

| Symbol | Einheit | SI-Faktor |
|---|---|---|
| `ms` | Millisekunde | × 10⁻³ s |
| `min` | Minute | × 60 s |
| `h` | Stunde | × 3 600 s |

### 11.2 Elektrische Energie & Leistung

| Symbol | Einheit | Bedeutung |
|---|---|---|
| `MHz` | Megahertz | × 10⁶ Hz |
| `kW` | Kilowatt | × 10³ W |
| `kVA` | Kilo-Voltampere | Scheinleistung |
| `kvar` | Kilo-Var | Blindleistung |
| `Wh` | Wattstunde | × 3 600 J |
| `kWh` | Kilowattstunde | × 3,6 × 10⁶ J |
| `VAh` | Voltampere-Stunde | Scheinarbeit |
| `varh` | Var-Stunde | Blindarbeit |
| `kVAh` | Kilo-Voltampere-Stunde | Scheinarbeit |
| `kvarh` | Kilo-Var-Stunde | Blindarbeit |

### 11.3 Winkel

| Symbol | Einheit | SI-Faktor |
|---|---|---|
| `deg` | Grad | × π/180 rad |

---

## 12. Verwendung in SenML-Records

Beispiel-SenML-Record (CBOR/JSON):

```json
[
  { "n": "temperature", "u": "Cel", "v": 24.7 },
  { "n": "humidity",    "u": "%RH", "v": 58.3 },
  { "n": "pressure",    "u": "Pa",  "v": 101325 },
  { "n": "battery",     "u": "%EL", "v": 87 }
]
```

Das `u`-Feld referenziert immer eine **registrierte** SenML-Einheit aus der IANA-Tabelle.

---

## 13. Verwendung in taskit-Produkten

Im [[taskit BLE Manufacturer Advertisement]] Byte 11 (SenML Unit ID) werden die folgenden numerischen IDs verwendet (Position innerhalb der IANA-Registry):

| ID | SenML Symbol | Produkt |
|---:|---|---|
| `55` | `Cel` | [[Measure2Go]] Blue RTD |
| `75` | `pH` | Measure2Go Blue pH-Meter |
| `143` | `mA` | Measure2Go Blue Loop RX / TX |

> ⚠️ Die numerischen IDs basieren auf der Reihenfolge in der IANA-Registry. Bei einer Änderung der Registry können sich diese IDs verschieben – die taskit-Firmware definiert sie daher als feste Konstanten.

---

## 14. Quellen

- [RFC 8428 – Sensor Measurement Lists (SenML)](https://datatracker.ietf.org/doc/html/rfc8428)
- [IANA SenML Unit Registry](https://www.iana.org/assignments/senml/senml.xhtml#senml-units)
- [RFC 8798 – Additional SenML Units](https://datatracker.ietf.org/doc/html/rfc8798)
- Verwandt: [[taskit BLE Manufacturer Advertisement]] · [[BLE/BLE Advertisement Format]]
