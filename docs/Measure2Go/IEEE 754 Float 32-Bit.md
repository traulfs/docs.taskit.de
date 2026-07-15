---
tags:
  - protokoll
  - datenformat
  - technik
  - embedded
erstellt: 2026-05-10
---

# IEEE 754 – 32-Bit Float (Single Precision)

Der **IEEE 754 Standard** definiert das am weitesten verbreitete Format zur Darstellung von Gleitkommazahlen in digitalen Systemen. Die 32-Bit-Variante (Single Precision) wird in Embedded-Systemen, Sensordaten und Protokollen wie BLE häufig verwendet.

---

## 1. Bitstruktur

```
Bit:  31       30     23 22                    0
      ┌────────┬─────────┬───────────────────────┐
      │  Sign  │Exponent │        Mantissa        │
      │  1 Bit │  8 Bit  │        23 Bit          │
      └────────┴─────────┴───────────────────────┘
         S        EEEEEEEE   MMMMMMMMMMMMMMMMMMMMMMM
```

| Feld | Bits | Beschreibung |
|---|---|---|
| **Sign (S)** | 1 | `0` = positiv, `1` = negativ |
| **Exponent (E)** | 8 | Gespeichert mit Bias 127 (Excess-127) |
| **Mantissa (M)** | 23 | Nachkommastellen der normalisierten Zahl |

---

## 2. Berechnung des Wertes

### Normalisierte Zahlen (E ≠ 0 und E ≠ 255)

$$\text{Wert} = (-1)^S \times 2^{(E - 127)} \times (1{,}M)$$

Die führende `1` vor der Mantissa ist **implizit** – sie wird nicht gespeichert (Hidden Bit).

**Beispiel: `0 10000000 10000000000000000000000`**

```
S = 0           → positiv
E = 10000000₂ = 128 → Exponent = 128 - 127 = 1
M = 10000000... → 1,5 (implizite 1 + 0,5)

Wert = +1 × 2¹ × 1,5 = 3,0
```

### Denormalisierte Zahlen (E = 0, M ≠ 0)

Für sehr kleine Zahlen nahe null – keine implizite führende 1:

$$\text{Wert} = (-1)^S \times 2^{-126} \times (0{,}M)$$

---

## 3. Spezialbelegungen

| S | Exponent E | Mantissa M | Bedeutung |
|---|---|---|---|
| 0 | `00000000` | `000...0` | **+0** |
| 1 | `00000000` | `000...0` | **−0** |
| 0 | `00000000` | ≠ 0 | **+Denormalisiert** |
| 1 | `00000000` | ≠ 0 | **−Denormalisiert** |
| 0 | `11111111` | `000...0` | **+∞ (Infinity)** |
| 1 | `11111111` | `000...0` | **−∞ (Infinity)** |
| × | `11111111` | ≠ 0 | **NaN** (Not a Number) |

---

## 4. Wertebereich & Genauigkeit

| Eigenschaft | Wert |
|---|---|
| Kleinste positive normalisierte Zahl | ≈ 1,18 × 10⁻³⁸ |
| Größte positive Zahl | ≈ 3,40 × 10³⁸ |
| Kleinste denormalisierte Zahl | ≈ 1,40 × 10⁻⁴⁵ |
| Dezimale Genauigkeit | ≈ 7 signifikante Stellen |
| Epsilon (kleinste darstellbare Differenz zu 1,0) | ≈ 1,19 × 10⁻⁷ |

---

## 5. Beispiele

| Dezimalwert | Binär (S · E · M) | Hex |
|---|---|---|
| `0.0` | `0 00000000 00000000000000000000000` | `0x00000000` |
| `1.0` | `0 01111111 00000000000000000000000` | `0x3F800000` |
| `-1.0` | `1 01111111 00000000000000000000000` | `0xBF800000` |
| `2.0` | `0 10000000 00000000000000000000000` | `0x40000000` |
| `0.5` | `0 01111110 00000000000000000000000` | `0x3F000000` |
| `3.14159` | `0 10000000 10010000111111011010111` | `0x40490FDB` |
| `+∞` | `0 11111111 00000000000000000000000` | `0x7F800000` |
| `NaN` | `0 11111111 10000000000000000000000` | `0x7FC00000` |

---

## 6. Byte-Reihenfolge (Endianness)

Ein 32-Bit Float belegt **4 Bytes**. Die Reihenfolge im Speicher hängt von der Plattform ab:

**Beispiel: `1.0` = `0x3F800000`**

| Format | Byte 0 | Byte 1 | Byte 2 | Byte 3 |
|---|---|---|---|---|
| **Big Endian** | `0x3F` | `0x80` | `0x00` | `0x00` |
| **Little Endian** | `0x00` | `0x00` | `0x80` | `0x3F` |

> ⚠️ BLE überträgt Daten standardmäßig **Little Endian** – bei der Übertragung von Float-Werten in BLE-Paketen (z.B. [[taskit BLE Manufacturer Advertisement]]) ist dies zu beachten.

---

## 7. Konvertierung – Schritt für Schritt

**Dezimal → IEEE 754 (Beispiel: `−6.5`)**

```
1. Vorzeichen: negativ → S = 1

2. Betrag in Binär: 6.5 = 110.1₂

3. Normalisieren: 1.101 × 2²
                  └─┤ Exponent = 2

4. Exponent speichern: E = 2 + 127 = 129 = 10000001₂

5. Mantissa (ohne führende 1): 101 00000000000000000000

6. Ergebnis:
   S=1  E=10000001  M=10100000000000000000000
   → 1 10000001 10100000000000000000000
   → 0xC0D00000
```

---

## 8. Verwendung in Embedded / BLE

In Sensordaten (z.B. Measure2Go, [[taskit BLE Manufacturer Advertisement]]) wird IEEE 754 Float oft durch **ganzzahlige Festkomma-Werte** ersetzt, um:
- Speicherplatz zu sparen (2 Byte int16 statt 4 Byte float)
- Berechnungsaufwand auf Mikrocontrollern zu reduzieren
- Endianness-Probleme zu vermeiden

**Beispiel:** Temperatur 24,7 °C als `int16` mit Faktor 10:
```
24,7 °C × 10 = 247 = 0x00F7  (2 Bytes statt 4)
```

---

## 9. Vergleich: Float-Formate im Überblick

| Format | Bits | Exponent | Mantissa | Genauigkeit |
|---|---|---|---|---|
| **Half Precision** | 16 | 5 | 10 | ≈ 3 Stellen |
| **Single Precision** | 32 | 8 | 23 | ≈ 7 Stellen |
| **Double Precision** | 64 | 11 | 52 | ≈ 15 Stellen |
| **Extended** | 80 | 15 | 64 | ≈ 18 Stellen |

---

## Quellen

- [IEEE 754-2019 Standard](https://ieeexplore.ieee.org/document/8766229)
- [Wikipedia: IEEE 754](https://de.wikipedia.org/wiki/IEEE_754)
- Verwandt: [[BLE Advertisement Format]] | [[taskit BLE Manufacturer Advertisement]]
