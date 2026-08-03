---
tags:
  - protocol
  - data-format
  - technology
  - embedded
erstellt: 2026-05-10
---

# IEEE 754 – 32-Bit Float (Single Precision)

The **IEEE 754 standard** defines the most widely used format for representing floating-point numbers in digital systems. The 32-bit variant (single precision) is commonly used in embedded systems, sensor data, and protocols such as BLE.

---

## 1. Bit Structure

```
Bit:  31       30     23 22                    0
      ┌────────┬─────────┬───────────────────────┐
      │  Sign  │Exponent │        Mantissa        │
      │  1 Bit │  8 Bit  │        23 Bit          │
      └────────┴─────────┴───────────────────────┘
         S        EEEEEEEE   MMMMMMMMMMMMMMMMMMMMMMM
```

| Field | Bits | Description |
|---|---|---|
| **Sign (S)** | 1 | `0` = positive, `1` = negative |
| **Exponent (E)** | 8 | Stored with bias 127 (excess-127) |
| **Mantissa (M)** | 23 | Fractional part of the normalized number |

---

## 2. Calculating the Value

### Normalized Numbers (E ≠ 0 and E ≠ 255)

$$\text{Value} = (-1)^S \times 2^{(E - 127)} \times (1.M)$$

The leading `1` before the mantissa is **implicit** – it is not stored (hidden bit).

**Example: `0 10000000 10000000000000000000000`**

```
S = 0           → positive
E = 10000000₂ = 128 → Exponent = 128 - 127 = 1
M = 10000000... → 1.5 (implicit 1 + 0.5)

Value = +1 × 2¹ × 1.5 = 3.0
```

### Denormalized Numbers (E = 0, M ≠ 0)

For very small numbers near zero – no implicit leading 1:

$$\text{Value} = (-1)^S \times 2^{-126} \times (0.M)$$

---

## 3. Special Values

| S | Exponent E | Mantissa M | Meaning |
|---|---|---|---|
| 0 | `00000000` | `000...0` | **+0** |
| 1 | `00000000` | `000...0` | **−0** |
| 0 | `00000000` | ≠ 0 | **+Denormalized** |
| 1 | `00000000` | ≠ 0 | **−Denormalized** |
| 0 | `11111111` | `000...0` | **+∞ (Infinity)** |
| 1 | `11111111` | `000...0` | **−∞ (Infinity)** |
| × | `11111111` | ≠ 0 | **NaN** (Not a Number) |

---

## 4. Range & Precision

| Property | Value |
|---|---|
| Smallest positive normalized number | ≈ 1.18 × 10⁻³⁸ |
| Largest positive number | ≈ 3.40 × 10³⁸ |
| Smallest denormalized number | ≈ 1.40 × 10⁻⁴⁵ |
| Decimal precision | ≈ 7 significant digits |
| Epsilon (smallest representable difference from 1.0) | ≈ 1.19 × 10⁻⁷ |

---

## 5. Examples

| Decimal value | Binary (S · E · M) | Hex |
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

## 6. Byte Order (Endianness)

A 32-bit float occupies **4 bytes**. The order in memory depends on the platform:

**Example: `1.0` = `0x3F800000`**

| Format | Byte 0 | Byte 1 | Byte 2 | Byte 3 |
|---|---|---|---|---|
| **Big Endian** | `0x3F` | `0x80` | `0x00` | `0x00` |
| **Little Endian** | `0x00` | `0x00` | `0x80` | `0x3F` |

> ⚠️ BLE transmits data as **little endian** by default – this must be taken into account when transmitting float values in BLE packets (e.g. [[taskit BLE Manufacturer Advertisement]]).

---

## 7. Conversion – Step by Step

**Decimal → IEEE 754 (example: `−6.5`)**

```
1. Sign: negative → S = 1

2. Magnitude in binary: 6.5 = 110.1₂

3. Normalize: 1.101 × 2²
              └─┤ Exponent = 2

4. Store exponent: E = 2 + 127 = 129 = 10000001₂

5. Mantissa (without leading 1): 101 00000000000000000000

6. Result:
   S=1  E=10000001  M=10100000000000000000000
   → 1 10000001 10100000000000000000000
   → 0xC0D00000
```

---

## 8. Use in Embedded / BLE

In sensor data (e.g. Measure2Go, [[taskit BLE Manufacturer Advertisement]]), IEEE 754 float is often replaced by **fixed-point integer values** to:
- Save memory (2-byte int16 instead of 4-byte float)
- Reduce computation effort on microcontrollers
- Avoid endianness issues

**Example:** Temperature 24.7 °C as `int16` with a factor of 10:
```
24.7 °C × 10 = 247 = 0x00F7  (2 bytes instead of 4)
```

---

## 9. Comparison: Float Formats Overview

| Format | Bits | Exponent | Mantissa | Precision |
|---|---|---|---|---|
| **Half Precision** | 16 | 5 | 10 | ≈ 3 digits |
| **Single Precision** | 32 | 8 | 23 | ≈ 7 digits |
| **Double Precision** | 64 | 11 | 52 | ≈ 15 digits |
| **Extended** | 80 | 15 | 64 | ≈ 18 digits |

---

## Sources

- [IEEE 754-2019 Standard](https://ieeexplore.ieee.org/document/8766229)
- [Wikipedia: IEEE 754](https://en.wikipedia.org/wiki/IEEE_754)
- Related: [[BLE Advertisement Format]] | [[taskit BLE Manufacturer Advertisement]]
