---
tags:
  - protokoll
  - kodierung
  - unicode
  - utf8
  - referenz
erstellt: 2026-05-14
status: referenz
---

# UTF-8 Kodierung

> UTF-8 (Unicode Transformation Format – 8-bit) ist die weltweit am häufigsten verwendete Zeichenkodierung. Sie kodiert alle Unicode-Zeichen (über 1,1 Millionen mögliche Zeichen) in 1 bis 4 Bytes.

---

## Grundprinzip

Unicode weist jedem Zeichen eine eindeutige Nummer zu – den **Code Point** (z. B. `U+0041` = „A"). UTF-8 legt fest, wie dieser Code Point als Folge von Bytes gespeichert wird.

**Wichtige Eigenschaften:**
- **Variabel lang** – 1 bis 4 Bytes pro Zeichen
- **Rückwärtskompatibel zu ASCII** – die ersten 128 Zeichen (U+0000–U+007F) sind identisch mit ASCII (1 Byte)
- **Selbstsynchronisierend** – in einem Byte-Strom lässt sich jederzeit der Anfang eines Zeichens erkennen
- **Keine Byte-Order-Problematik** – im Gegensatz zu UTF-16/UTF-32 (kein BOM nötig)

---

## Byte-Kodierung nach Code-Point-Bereich

| Code-Point-Bereich | Bytes | Byte-Muster | Nutzbits |
|---|---|---|---|
| U+0000 – U+007F | 1 | `0xxxxxxx` | 7 Bit |
| U+0080 – U+07FF | 2 | `110xxxxx 10xxxxxx` | 11 Bit |
| U+0800 – U+FFFF | 3 | `1110xxxx 10xxxxxx 10xxxxxx` | 15 Bit |
| U+10000 – U+10FFFF | 4 | `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx` | 21 Bit |

### Erklärung der Bit-Muster

- **Erstes Byte** bestimmt die Gesamtlänge:
  - `0xxxxxxx` → 1-Byte-Zeichen (ASCII)
  - `110xxxxx` → 2-Byte-Zeichen (führendes `110`)
  - `1110xxxx` → 3-Byte-Zeichen (führendes `1110`)
  - `11110xxx` → 4-Byte-Zeichen (führendes `11110`)
- **Folge-Bytes** beginnen immer mit `10xxxxxx` (Kennzeichen: Continuation Byte)
- Die `x`-Bits enthalten den eigentlichen Code-Point-Wert (Big-Endian)

---

## Schritt-für-Schritt: Kodierung eines Zeichens

### Beispiel 1: „A" (U+0041)

```
Code Point:  0x0041 = 0b01000001

Bereich:     U+0000–U+007F  →  1 Byte
Muster:      0xxxxxxx

Ergebnis:    0b01000001  =  0x41
```

→ Identisch mit ASCII: **`0x41`**

---

### Beispiel 2: „ä" (U+00E4)

```
Code Point:  0x00E4 = 0b11100100

Bereich:     U+0080–U+07FF  →  2 Bytes
Muster:      110xxxxx  10xxxxxx
             110 00011  10 100100
                  ↑↑↑     ↑↑↑↑↑↑
             obere 5 Bit   untere 6 Bit von 0xE4

Ergebnis:    0b11000011  0b10100100  =  0xC3  0xA4
```

→ UTF-8: **`0xC3 0xA4`**

---

### Beispiel 3: „€" (U+20AC)

```
Code Point:  0x20AC = 0b0010 000010 101100

Bereich:     U+0800–U+FFFF  →  3 Bytes
Muster:      1110xxxx  10xxxxxx  10xxxxxx
             1110 0010  10 000010  10 101100

Ergebnis:    0xE2  0x82  0xAC
```

→ UTF-8: **`0xE2 0x82 0xAC`**

---

### Beispiel 4: 😀 Emoji (U+1F600)

```
Code Point:  0x1F600 = 0b000 011111 011000 000000

Bereich:     U+10000–U+10FFFF  →  4 Bytes
Muster:      11110xxx  10xxxxxx  10xxxxxx  10xxxxxx
             11110 000  10 011111  10 011000  10 000000

Ergebnis:    0xF0  0x9F  0x98  0x80
```

→ UTF-8: **`0xF0 0x9F 0x98 0x80`**

---

## Selbstsynchronisierung

Ein besonderes Merkmal von UTF-8 ist, dass man aus jedem beliebigen Byte sofort erkennt, welche Rolle es spielt:

| Byte-Wert | Bedeutung |
|---|---|
| `0x00–0x7F` (`0xxxxxxx`) | Einzelnes ASCII-Zeichen |
| `0xC0–0xDF` (`110xxxxx`) | Anfang eines 2-Byte-Zeichens |
| `0xE0–0xEF` (`1110xxxx`) | Anfang eines 3-Byte-Zeichens |
| `0xF0–0xF7` (`11110xxx`) | Anfang eines 4-Byte-Zeichens |
| `0x80–0xBF` (`10xxxxxx`) | Continuation Byte (Folge-Byte) |

→ Bei einem Übertragungsfehler kann der Empfänger den nächsten gültigen Zeichenanfang zuverlässig finden, indem er auf ein Byte wartet, das **nicht** mit `10` beginnt.

---

## Ungültige Byte-Sequenzen

UTF-8 kennt explizit **verbotene** Sequenzen:

| Sequenz | Problem |
|---|---|
| `0xFE`, `0xFF` | In UTF-8 nicht definiert |
| Overlong encoding | z. B. `0xC0 0x80` für `U+0000` (verboten) |
| Surrogat-Paare `U+D800–U+DFFF` | Nur für UTF-16 reserviert, in UTF-8 illegal |
| Code Points > U+10FFFF | Außerhalb des Unicode-Raums |
| Einzelnes Continuation Byte | `10xxxxxx` ohne vorhergehendes Lead-Byte |

---

## BOM (Byte Order Mark)

UTF-8 benötigt kein BOM, da keine Byte-Reihenfolge (Endianness) festgelegt werden muss. Manche Programme fügen dennoch `EF BB BF` am Dateianfang ein – dies ist optional und kann zu Problemen führen (z. B. in Shell-Skripten).

---

## Vergleich: UTF-8, UTF-16, UTF-32

| Eigenschaft | UTF-8 | UTF-16 | UTF-32 |
|---|---|---|---|
| Bytes pro Zeichen | 1–4 | 2 oder 4 | 4 (fest) |
| ASCII-kompatibel | ✅ Ja | ❌ Nein | ❌ Nein |
| BOM nötig | Nein | Ja (LE/BE) | Ja (LE/BE) |
| Speicherbedarf (Latein) | Gering (1 Byte) | Mittel (2 Byte) | Hoch (4 Byte) |
| Speicherbedarf (CJK) | Mittel (3 Byte) | Gering (2 Byte) | Hoch (4 Byte) |
| Selbstsynchronisierend | ✅ Ja | ❌ Nein | ✅ Ja |
| Verbreitung (Web) | ~98 % | Selten | Selten |

---

## Taskit Port-Encoding (Erweiterung)

Das taskit gpio.net Protokoll verwendet eine an UTF-8 angelehnte Kodierung für Port-Befehle:

| Mode | Bereich | Kodierung |
|---|---|---|
| **Nibble Mode** | 0x00–0x7F | `'0' C2 C1 C0 D3 D2 D1 D0` – 4-Bit-Daten |
| **Byte Mode** | 0x80–0x7FF | `'110' C2 C1 C0 D7 D6  '10' D5..D0` – 8-Bit-Daten |
| **Not used** | 0x800–0xFFFF | reserviert |
| **Word Mode / Extended** | 0x10000–0x10FFFF | `'11110' C2..C0  '10' C4 C3 D15..D12  '10' D11..D6  '10' D5..D0` – 16-Bit-Daten |

→ `C` = Command/Eventbit · `D` = Databit · Struktur analog zu UTF-8-Lead-Bytes

Siehe auch: [[Powerpoint/portchar_260514]]

---

## Referenzen

- RFC 3629 – UTF-8, a transformation format of ISO 10646
- Unicode Standard: https://www.unicode.org/standard/standard.html
- Wikipedia: https://de.wikipedia.org/wiki/UTF-8
