---
tags:
  - protocol
  - encoding
  - unicode
  - utf8
  - reference
erstellt: 2026-05-14
status: reference
---

# UTF-8 Encoding

> UTF-8 (Unicode Transformation Format – 8-bit) is the most widely used character encoding in the world. It encodes all Unicode characters (over 1.1 million possible characters) in 1 to 4 bytes.

---

## Basic Principle

Unicode assigns a unique number to every character – the **code point** (e.g. `U+0041` = "A"). UTF-8 defines how this code point is stored as a sequence of bytes.

**Key properties:**
- **Variable length** – 1 to 4 bytes per character
- **Backward-compatible with ASCII** – the first 128 characters (U+0000–U+007F) are identical to ASCII (1 byte)
- **Self-synchronizing** – the start of a character can be identified at any point in a byte stream
- **No byte-order issue** – unlike UTF-16/UTF-32 (no BOM needed)

---

## Byte Encoding by Code Point Range

| Code point range | Bytes | Byte pattern | Usable bits |
|---|---|---|---|
| U+0000 – U+007F | 1 | `0xxxxxxx` | 7 bits |
| U+0080 – U+07FF | 2 | `110xxxxx 10xxxxxx` | 11 bits |
| U+0800 – U+FFFF | 3 | `1110xxxx 10xxxxxx 10xxxxxx` | 15 bits |
| U+10000 – U+10FFFF | 4 | `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx` | 21 bits |

### Explanation of the Bit Patterns

- **First byte** determines the total length:
  - `0xxxxxxx` → 1-byte character (ASCII)
  - `110xxxxx` → 2-byte character (leading `110`)
  - `1110xxxx` → 3-byte character (leading `1110`)
  - `11110xxx` → 4-byte character (leading `11110`)
- **Continuation bytes** always start with `10xxxxxx` (marker: continuation byte)
- The `x` bits contain the actual code point value (big-endian)

---

## Step by Step: Encoding a Character

### Example 1: "A" (U+0041)

```
Code point:  0x0041 = 0b01000001

Range:       U+0000–U+007F  →  1 byte
Pattern:     0xxxxxxx

Result:      0b01000001  =  0x41
```

→ Identical to ASCII: **`0x41`**

---

### Example 2: "ä" (U+00E4)

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

### Example 3: "€" (U+20AC)

```
Code point:  0x20AC = 0b0010 000010 101100

Range:       U+0800–U+FFFF  →  3 bytes
Pattern:     1110xxxx  10xxxxxx  10xxxxxx
             1110 0010  10 000010  10 101100

Result:      0xE2  0x82  0xAC
```

→ UTF-8: **`0xE2 0x82 0xAC`**

---

### Example 4: 😀 Emoji (U+1F600)

```
Code point:  0x1F600 = 0b000 011111 011000 000000

Range:       U+10000–U+10FFFF  →  4 bytes
Pattern:     11110xxx  10xxxxxx  10xxxxxx  10xxxxxx
             11110 000  10 011111  10 011000  10 000000

Result:      0xF0  0x9F  0x98  0x80
```

→ UTF-8: **`0xF0 0x9F 0x98 0x80`**

---

## Self-Synchronization

A distinctive feature of UTF-8 is that the role of any given byte can be identified immediately:

| Byte value | Meaning |
|---|---|
| `0x00–0x7F` (`0xxxxxxx`) | Single ASCII character |
| `0xC0–0xDF` (`110xxxxx`) | Start of a 2-byte character |
| `0xE0–0xEF` (`1110xxxx`) | Start of a 3-byte character |
| `0xF0–0xF7` (`11110xxx`) | Start of a 4-byte character |
| `0x80–0xBF` (`10xxxxxx`) | Continuation byte |

→ In the event of a transmission error, the receiver can reliably find the next valid character start by waiting for a byte that does **not** begin with `10`.

---

## Invalid Byte Sequences

UTF-8 explicitly defines **forbidden** sequences:

| Sequence | Problem |
|---|---|
| `0xFE`, `0xFF` | Not defined in UTF-8 |
| Overlong encoding | e.g. `0xC0 0x80` for `U+0000` (forbidden) |
| Surrogate pairs `U+D800–U+DFFF` | Reserved for UTF-16 only, illegal in UTF-8 |
| Code points > U+10FFFF | Outside the Unicode range |
| Standalone continuation byte | `10xxxxxx` without a preceding lead byte |

---

## BOM (Byte Order Mark)

UTF-8 does not need a BOM, since no byte order (endianness) needs to be specified. Some programs still insert `EF BB BF` at the start of a file – this is optional and can cause problems (e.g. in shell scripts).

---

## Comparison: UTF-8, UTF-16, UTF-32

| Property | UTF-8 | UTF-16 | UTF-32 |
|---|---|---|---|
| Bytes per character | 1–4 | 2 or 4 | 4 (fixed) |
| ASCII-compatible | ✅ Yes | ❌ No | ❌ No |
| BOM required | No | Yes (LE/BE) | Yes (LE/BE) |
| Memory usage (Latin) | Low (1 byte) | Medium (2 bytes) | High (4 bytes) |
| Memory usage (CJK) | Medium (3 bytes) | Low (2 bytes) | High (4 bytes) |
| Self-synchronizing | ✅ Yes | ❌ No | ✅ Yes |
| Usage share (web) | ~98% | Rare | Rare |

---

## Taskit Port Encoding (Extension)

The taskit gpio.net protocol uses a UTF-8-inspired encoding for port commands:

| Mode | Range | Encoding |
|---|---|---|
| **Nibble Mode** | 0x00–0x7F | `'0' C2 C1 C0 D3 D2 D1 D0` – 4-bit data |
| **Byte Mode** | 0x80–0x7FF | `'110' C2 C1 C0 D7 D6  '10' D5..D0` – 8-bit data |
| **Not used** | 0x800–0xFFFF | reserved |
| **Word Mode / Extended** | 0x10000–0x10FFFF | `'11110' C2..C0  '10' C4 C3 D15..D12  '10' D11..D6  '10' D5..D0` – 16-bit data |

→ `C` = command/event bit · `D` = data bit · structure analogous to UTF-8 lead bytes

See also: `portchar_260514.key`

---

## References

- RFC 3629 – UTF-8, a transformation format of ISO 10646
- Unicode Standard: https://www.unicode.org/standard/standard.html
- Wikipedia: https://en.wikipedia.org/wiki/UTF-8
