---
tags:
  - protocol
  - encoding
  - unicode
  - utf8
  - reference
erstellt: 2026-05-14
status: reference
description: "Wie UTF-8 Unicode-Codepunkte in 1 bis 4 Bytes kodiert: Bytemuster je Codepunktbereich, ASCII-Kompatibilität und Kodierbeispiele Schritt für Schritt."
---

# UTF-8-Kodierung

> UTF-8 (Unicode Transformation Format – 8-bit) ist die weltweit am häufigsten verwendete Zeichenkodierung. Sie kodiert alle Unicode-Zeichen (über 1,1 Millionen mögliche Zeichen) in 1 bis 4 Bytes.

---

## Grundprinzip

Unicode ordnet jedem Zeichen eine eindeutige Nummer zu – den **Codepunkt** (z. B. `U+0041` = „A“). UTF-8 legt fest, wie dieser Codepunkt als Bytefolge gespeichert wird.

**Wichtige Eigenschaften:**
- **Variable Länge** – 1 bis 4 Bytes pro Zeichen
- **Abwärtskompatibel zu ASCII** – die ersten 128 Zeichen (U+0000–U+007F) sind identisch mit ASCII (1 Byte)
- **Selbstsynchronisierend** – der Anfang eines Zeichens lässt sich an jeder Stelle eines Bytestroms erkennen
- **Kein Problem mit der Byte-Reihenfolge** – anders als bei UTF-16/UTF-32 (kein BOM nötig)

---

## Bytekodierung nach Codepunktbereich

| Codepunktbereich | Bytes | Bytemuster | Nutzbare Bits |
|---|---|---|---|
| U+0000 – U+007F | 1 | `0xxxxxxx` | 7 Bit |
| U+0080 – U+07FF | 2 | `110xxxxx 10xxxxxx` | 11 Bit |
| U+0800 – U+FFFF | 3 | `1110xxxx 10xxxxxx 10xxxxxx` | 15 Bit |
| U+10000 – U+10FFFF | 4 | `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx` | 21 Bit |

### Erklärung der Bitmuster

- Das **erste Byte** bestimmt die Gesamtlänge:
  - `0xxxxxxx` → 1-Byte-Zeichen (ASCII)
  - `110xxxxx` → 2-Byte-Zeichen (führend `110`)
  - `1110xxxx` → 3-Byte-Zeichen (führend `1110`)
  - `11110xxx` → 4-Byte-Zeichen (führend `11110`)
- **Folgebytes** beginnen immer mit `10xxxxxx` (Kennung: Folgebyte)
- Die `x`-Bits enthalten den eigentlichen Codepunktwert (Big Endian)

---

## Schritt für Schritt: Ein Zeichen kodieren

### Beispiel 1: „A“ (U+0041)

```
Code point:  0x0041 = 0b01000001

Range:       U+0000–U+007F  →  1 byte
Pattern:     0xxxxxxx

Result:      0b01000001  =  0x41
```

→ Identisch mit ASCII: **`0x41`**

---

### Beispiel 2: „ä“ (U+00E4)

```
Code point:  0x00E4 = 0b11100100

Range:       U+0080–U+07FF  →  2 bytes
Pattern:     110xxxxx  10xxxxxx
             110 00011  10 100100
                  ↑↑↑     ↑↑↑↑↑↑
             upper 5 bits   lower 6 bits of 0xE4

Result:      0b11000011  0b10100100  =  0xC3  0xA4
```

→ UTF-8: **`0xC3 0xA4`**

---

### Beispiel 3: „€“ (U+20AC)

```
Code point:  0x20AC = 0b0010 000010 101100

Range:       U+0800–U+FFFF  →  3 bytes
Pattern:     1110xxxx  10xxxxxx  10xxxxxx
             1110 0010  10 000010  10 101100

Result:      0xE2  0x82  0xAC
```

→ UTF-8: **`0xE2 0x82 0xAC`**

---

### Beispiel 4: 😀 Emoji (U+1F600)

```
Code point:  0x1F600 = 0b000 011111 011000 000000

Range:       U+10000–U+10FFFF  →  4 bytes
Pattern:     11110xxx  10xxxxxx  10xxxxxx  10xxxxxx
             11110 000  10 011111  10 011000  10 000000

Result:      0xF0  0x9F  0x98  0x80
```

→ UTF-8: **`0xF0 0x9F 0x98 0x80`**

---

## Selbstsynchronisation

Eine Besonderheit von UTF-8 ist, dass sich die Rolle jedes einzelnen Bytes sofort erkennen lässt:

| Bytewert | Bedeutung |
|---|---|
| `0x00–0x7F` (`0xxxxxxx`) | Einzelnes ASCII-Zeichen |
| `0xC0–0xDF` (`110xxxxx`) | Beginn eines 2-Byte-Zeichens |
| `0xE0–0xEF` (`1110xxxx`) | Beginn eines 3-Byte-Zeichens |
| `0xF0–0xF7` (`11110xxx`) | Beginn eines 4-Byte-Zeichens |
| `0x80–0xBF` (`10xxxxxx`) | Folgebyte |

→ Bei einem Übertragungsfehler findet der Empfänger den nächsten gültigen Zeichenanfang zuverlässig, indem er auf ein Byte wartet, das **nicht** mit `10` beginnt.

---

## Ungültige Bytefolgen

UTF-8 definiert ausdrücklich **verbotene** Folgen:

| Folge | Problem |
|---|---|
| `0xFE`, `0xFF` | In UTF-8 nicht definiert |
| Überlange Kodierung | z. B. `0xC0 0x80` für `U+0000` (verboten) |
| Surrogate `U+D800–U+DFFF` | Nur für UTF-16 reserviert, in UTF-8 unzulässig |
| Codepunkte > U+10FFFF | Außerhalb des Unicode-Bereichs |
| Alleinstehendes Folgebyte | `10xxxxxx` ohne vorangehendes Lead-Byte |

---

## BOM (Byte Order Mark)

UTF-8 benötigt kein BOM, da keine Byte-Reihenfolge (Endianness) angegeben werden muss. Manche Programme fügen dennoch `EF BB BF` am Dateianfang ein – das ist optional und kann Probleme verursachen (z. B. in Shell-Skripten).

---

## Vergleich: UTF-8, UTF-16, UTF-32

| Eigenschaft | UTF-8 | UTF-16 | UTF-32 |
|---|---|---|---|
| Bytes pro Zeichen | 1–4 | 2 oder 4 | 4 (fest) |
| ASCII-kompatibel | ✅ Ja | ❌ Nein | ❌ Nein |
| BOM erforderlich | Nein | Ja (LE/BE) | Ja (LE/BE) |
| Speicherbedarf (lateinisch) | Gering (1 Byte) | Mittel (2 Bytes) | Hoch (4 Bytes) |
| Speicherbedarf (CJK) | Mittel (3 Bytes) | Gering (2 Bytes) | Hoch (4 Bytes) |
| Selbstsynchronisierend | ✅ Ja | ❌ Nein | ✅ Ja |
| Nutzungsanteil (Web) | ~98 % | Selten | Selten |

---

## taskit-Port-Kodierung (Erweiterung)

Das taskit-gpio.net-Protokoll verwendet für Port-Befehle eine an UTF-8 angelehnte Kodierung:

| Modus | Bereich | Kodierung |
|---|---|---|
| **Nibble Mode** | 0x00–0x7F | `'0' C2 C1 C0 D3 D2 D1 D0` – 4-Bit-Daten |
| **Byte Mode** | 0x80–0x7FF | `'110' C2 C1 C0 D7 D6  '10' D5..D0` – 8-Bit-Daten |
| **Nicht verwendet** | 0x800–0xFFFF | reserviert |
| **Word Mode / Extended** | 0x10000–0x10FFFF | `'11110' C2..C0  '10' C4 C3 D15..D12  '10' D11..D6  '10' D5..D0` – 16-Bit-Daten |

→ `C` = Befehls-/Ereignisbit · `D` = Datenbit · Aufbau analog zu den UTF-8-Lead-Bytes

Siehe auch: `portchar_260514.key`

---

## Referenzen

- RFC 3629 – UTF-8, a transformation format of ISO 10646
- Unicode-Standard: https://www.unicode.org/standard/standard.html
- Wikipedia: https://en.wikipedia.org/wiki/UTF-8
