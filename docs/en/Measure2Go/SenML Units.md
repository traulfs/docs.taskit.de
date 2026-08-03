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
---

# SenML Units

> SenML (Sensor Measurement Lists, [RFC 8428](https://datatracker.ietf.org/doc/html/rfc8428)) defines a data format for sensor values. The `u` field (unit) specifies the physical unit of a measurement. The official values are listed in the [IANA SenML Unit Registry](https://www.iana.org/assignments/senml/senml.xhtml#senml-units).

Used, among others, in: [[taskit BLE Manufacturer Advertisement]] (byte 11), CoAP/LwM2M sensor payloads, MQTT IoT applications.

---

## 1. SI Base Units

| Symbol | Unit | Quantity |
|---|---|---|
| `m` | Meter | Length |
| `kg` | Kilogram | Mass |
| `g` | Gram | Mass (permitted) |
| `s` | Second | Time |
| `A` | Ampere | Electric current |
| `K` | Kelvin | Thermodynamic temperature |
| `cd` | Candela | Luminous intensity |
| `mol` | Mole | Amount of substance |

---

## 2. Derived SI Units

| Symbol | Unit | Quantity |
|---|---|---|
| `Hz` | Hertz | Frequency |
| `rad` | Radian | Angle |
| `sr` | Steradian | Solid angle |
| `N` | Newton | Force |
| `Pa` | Pascal | Pressure, mechanical stress |
| `J` | Joule | Energy, work, heat |
| `W` | Watt | Power, radiant flux |
| `C` | Coulomb | Electric charge |
| `V` | Volt | Electric voltage |
| `F` | Farad | Electric capacitance |
| `Ohm` | Ohm | Electric resistance |
| `S` | Siemens | Electric conductance |
| `Wb` | Weber | Magnetic flux |
| `T` | Tesla | Magnetic flux density |
| `H` | Henry | Inductance |
| `Cel` | Degree Celsius | Temperature |
| `lm` | Lumen | Luminous flux |
| `lx` | Lux | Illuminance |
| `Bq` | Becquerel | Radioactivity |
| `Gy` | Gray | Absorbed dose |
| `Sv` | Sievert | Equivalent dose |
| `kat` | Katal | Catalytic activity |

---

## 3. Geometry, Kinematics & Flow

| Symbol | Unit | Quantity |
|---|---|---|
| `m2` | Square meter | Area |
| `m3` | Cubic meter | Volume |
| `l` | Liter | Volume |
| `m/s` | Meter per second | Velocity |
| `m/s2` | Meter per second² | Acceleration |
| `m3/s` | Cubic meter per second | Volumetric flow rate |
| `l/s` | Liter per second | Volumetric flow rate |

---

## 4. Optical & Radiation Units

| Symbol | Unit | Quantity |
|---|---|---|
| `W/m2` | Watt per square meter | Irradiance |
| `cd/m2` | Candela per square meter | Luminance |

---

## 5. Information & Counting Units

| Symbol | Unit | Quantity |
|---|---|---|
| `bit` | Bit | Amount of data |
| `bit/s` | Bit per second | Data rate |
| `count` | Counter | Dimensionless count |
| `/` | Ratio | Dimensionless ratio |
| `1` | Dimensionless | Pure number |

---

## 6. Geo-Coordinates

| Symbol | Unit | Quantity |
|---|---|---|
| `lat` | Degree north latitude | Latitude (WGS84) |
| `lon` | Degree east longitude | Longitude (WGS84) |

---

## 7. Specialized & Sensor Units

| Symbol | Unit | Quantity |
|---|---|---|
| `pH` | pH value | Acidity (logarithmic) |
| `dB` | Decibel | Logarithmic ratio |
| `dBW` | Decibel-watt | Power level |
| `Bspl` | Bel SPL | Sound pressure level |
| `NTU` | Nephelometric Turbidity Unit | Turbidity |

---

## 8. Percentage & Ratio Units

| Symbol | Unit | Quantity |
|---|---|---|
| `%` | Percent | Ratio × 100 |
| `%RH` | Percent relative humidity | Humidity |
| `%EL` | Percent remaining | Battery charge level |
| `EL` | Seconds remaining | Remaining battery life |

---

## 9. Frequency & Rotational Speed Units

| Symbol | Unit | Quantity |
|---|---|---|
| `1/s` | Per second | Frequency, rate |
| `1/min` | Per minute | Rotational speed, rate |
| `beat/min` | Beats per minute | Heart rate |
| `beats` | Number of beats | Pulse events |

---

## 10. Material Properties

| Symbol | Unit | Quantity |
|---|---|---|
| `S/m` | Siemens per meter | Electric conductivity |
| `kg/m3` | Kilogram per cubic meter | Density |
| `J/m` | Joule per meter | Force / energy per distance |

---

## 11. Secondary Units (with Conversion)

Secondary units are not recommended as the primary value in the SenML `u` field, but are listed in the IANA registry and commonly used in practice:

### 11.1 Time

| Symbol | Unit | SI Factor |
|---|---|---|
| `ms` | Millisecond | × 10⁻³ s |
| `min` | Minute | × 60 s |
| `h` | Hour | × 3600 s |

### 11.2 Electrical Energy & Power

| Symbol | Unit | Meaning |
|---|---|---|
| `MHz` | Megahertz | × 10⁶ Hz |
| `kW` | Kilowatt | × 10³ W |
| `kVA` | Kilovolt-ampere | Apparent power |
| `kvar` | Kilovar | Reactive power |
| `Wh` | Watt-hour | × 3600 J |
| `kWh` | Kilowatt-hour | × 3.6 × 10⁶ J |
| `VAh` | Volt-ampere-hour | Apparent energy |
| `varh` | Var-hour | Reactive energy |
| `kVAh` | Kilovolt-ampere-hour | Apparent energy |
| `kvarh` | Kilovar-hour | Reactive energy |

### 11.3 Angle

| Symbol | Unit | SI Factor |
|---|---|---|
| `deg` | Degree | × π/180 rad |

---

## 12. Usage in SenML Records

Example SenML record (CBOR/JSON):

```json
[
  { "n": "temperature", "u": "Cel", "v": 24.7 },
  { "n": "humidity",    "u": "%RH", "v": 58.3 },
  { "n": "pressure",    "u": "Pa",  "v": 101325 },
  { "n": "battery",     "u": "%EL", "v": 87 }
]
```

The `u` field always references a **registered** SenML unit from the IANA table.

---

## 13. Usage in taskit Products

In the [[taskit BLE Manufacturer Advertisement]] byte 11 (SenML Unit ID), the following numeric IDs are used (position within the IANA registry):

| ID | SenML Symbol | Product |
|---:|---|---|
| `55` | `Cel` | [[Measure2Go]] Blue RTD |
| `75` | `pH` | Measure2Go Blue pH-Meter |
| `143` | `mA` | Measure2Go Blue Loop RX / TX |

> ⚠️ The numeric IDs are based on the order in the IANA registry. If the registry changes, these IDs may shift – the taskit firmware therefore defines them as fixed constants.

---

## 14. Sources

- [RFC 8428 – Sensor Measurement Lists (SenML)](https://datatracker.ietf.org/doc/html/rfc8428)
- [IANA SenML Unit Registry](https://www.iana.org/assignments/senml/senml.xhtml#senml-units)
- [RFC 8798 – Additional SenML Units](https://datatracker.ietf.org/doc/html/rfc8798)
- Related: [[taskit BLE Manufacturer Advertisement]] · [[BLE/BLE Advertisement Format]]
