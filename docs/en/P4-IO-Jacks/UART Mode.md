---
tags:
  - p4-io-jacks
  - uart
  - uart-mode
erstellt: 2026-06-17
status: description
---

# IO-Jack — UART Mode

> IO jack in UART mode — serial interface with configuration via `cfg` and data transfer via `uart`.

---

## How It Works

In **UART mode**, an IO jack operates as a serial interface with two subtopics:

| Subtopic | Purpose |
|---|---|
| **`cfg`** | Set UART settings |
| **`uart`** | Send / receive raw UART data bytes |

---

## Configuration (`cfg`)

The interface is configured with five parameters before data transfer. Short form: `Baudrate-Databits-Parity-Stopbits` (N = none, E = even, O = odd):

| Configuration | Baud rate | Data bits | Parity | Stop bits | RS485 |
|---|--:|:--:|---|:--:|:--:|
| **Standard** · `115200-8-N-1` | 115,200 | 8 | none | 1 | off |
| **Classic** · `9600-8-N-1` | 9,600 | 8 | none | 1 | off |
| **7-bit, even** · `9600-7-E-1` | 9,600 | 7 | even | 1 | off |
| **RS485 bus** · `500000-8-N-1` | 500,000 | 8 | none | 1 | **on** |
| **High speed** · `3000000-8-N-1` | 3,000,000 | 8 | none | 1 | off |

---

## Parameters

**Baud Rate**

| Baud rate (bit/s) | Constant | Code |
|---:|---|:--:|
| 300 | `UartBaud300` | `0x00` |
| 600 | `UartBaud600` | `0x01` |
| 1,200 | `UartBaud1200` | `0x02` |
| 2,400 | `UartBaud2400` | `0x03` |
| 4,800 | `UartBaud4800` | `0x04` |
| 9,600 | `UartBaud9600` | `0x05` |
| 19,200 | `UartBaud19200` | `0x06` |
| 38,400 | `UartBaud38400` | `0x07` |
| 115,200 | `UartBaud115200` | `0x08` |
| 230,400 | `UartBaud230400` | `0x09` |
| 500,000 | `UartBaud500000` | `0x0A` |
| 1,000,000 | `UartBaud1000000` | `0x0B` |
| 3,000,000 | `UartBaud3000000` | `0x0C` |
| 5,000,000 | `UartBaud5000000` | `0x0D` |

**Data Bits**

| Data bits | Constant | Value |
|:--:|---|:--:|
| 7 | `UartData7` | `0x2000` |
| **8** | `UartData8` | `0x0000` |
| 9 | `UartData9` | `0x1000` |

**Parity**

| Parity | Constant | Value |
|---|---|:--:|
| none | `UartParityNone` | `0x0000` |
| even | `UartParityEven` | `0x0400` |
| odd | `UartParityOdd` | `0x0800` |

**Stop Bits**

| Stop bits | Constant | Value |
|:--:|---|:--:|
| 1 | `UartStopbits1` | `0x0000` |
| 1.5 | `UartStopbits15` | `0x0100` |
| 2 | `UartStopbits2` | `0x0200` |

**RS485**

| RS485 | Constant |
|---|---|
| off | *(default)* |
| on | `UartRS485` |

---

## 16-Bit Configuration Word

The configuration is transmitted via `cfg` with the **Config UART** command (code 25, available in the 16-bit frame only). The payload is **one 16-bit word** — assembled by **bitwise OR** of the field values:

| Bits | Field | Values |
|:--:|---|---|
| **15** | RS485 | off `0x0000` · on `0x8000` |
| **12–14** | Data bits | 8 `0x0000` · 9 `0x1000` · 7 `0x2000` |
| **10–11** | Parity | none `0x0000` · even `0x0400` · odd `0x0800` |
| **8–9** | Stop bits | 1 `0x0000` · 1.5 `0x0100` · 2 `0x0200` |
| **0–7** | Baud rate | code from the table above |

**Examples:**

| Configuration | = Config word |
|---|:--:|
| `115200-8-N-1` | **`0x0008`** |
| `9600-8-N-1` | **`0x0005`** |
| `9600-7-E-1` | **`0x2405`** |
| `500000-8-N-1` (RS485) | **`0x800A`** |
| `3000000-8-N-1` | **`0x000C`** |

### Transmission: 4 Bytes for 16 Bit of Data

`Config UART` is transmitted with **code 25** in the **16-bit frame**. This frame is **4 bytes** long, even though the command code (6 bit) and config word (16 bit) together amount to only 22 bits of payload — the rest are fixed **marker bits** that make the frame self-synchronizing: every byte starts with either `1110` (lead byte, once) or `10` (continuation byte, 3×).

```
Byte 0:  1 1 1 0 │ C5 C4 C3 C2
Byte 1:  1 0      │ C1 C0 D15 D14 D13 D12
Byte 2:  1 0      │ D11 D10 D9 D8 D7 D6
Byte 3:  1 0      │ D5 D4 D3 D2 D1 D0
```

- **C5…C0** = command code (6 bit) → here **25** = `011001`
- **D15…D0** = config word (16 bit) → e.g. `0x0008` = `0000 0000 0000 1000`

### Building It via Shift & Mask

Instead of bit by bit, each byte can be computed directly from `Code` and `Word` using **shift (`>>`)** and **mask (`&`)**:

```
Byte0 = 0xE0 | (Code >> 2)                    // Lead byte:      1110 + upper 4 bits of the code
Byte1 = 0x80 | ((Code & 0x03) << 4)           // Continuation 1: lower 2 bits of the code
              | (Word >> 12)                  //               + upper 4 bits of the data (15–12)
Byte2 = 0x80 | ((Word >> 6) & 0x3F)           // Continuation 2: middle 6 bits of the data (11–6)
Byte3 = 0x80 | (Word & 0x3F)                  // Continuation 3: lower 6 bits of the data (5–0)
```

- `0xE0` = `1110 0000` → lead byte marker
- `0x80` = `1000 0000` → continuation byte marker
- `0x03` = masks the lower **2 bits** (remainder of the code)
- `0x3F` = masks the lower **6 bits** (one data chunk)

**Applied to `115200-8-N-1`** (`Code = 25`, `Word = 0x0008`):

```
Byte0 = 0xE0 | (25 >> 2)                       = 0xE0 | 0x06        = 0xE6
Byte1 = 0x80 | ((25 & 0x03) << 4) | (0x0008 >> 12)
      = 0x80 | (1 << 4)           | 0x00       = 0x80 | 0x10 | 0x00 = 0x90
Byte2 = 0x80 | ((0x0008 >> 6) & 0x3F)           = 0x80 | 0x00        = 0x80
Byte3 = 0x80 | (0x0008 & 0x3F)                  = 0x80 | 0x08        = 0x88
```

→ Complete frame: **`E6 90 80 88`**

The receiver reverses the formulas: `Code = ((Byte0 & 0x0F) << 2) | ((Byte1 >> 4) & 0x03)`, `Word = ((Byte1 & 0x0F) << 12) | ((Byte2 & 0x3F) << 6) | (Byte3 & 0x3F)`. From `Code = 25` (Config UART) and `Word = 0x0008`, the baud rate/data bits/parity/stop bits tables above can then be applied in reverse.

---

## Cross References

- Transport & subtopics: [[MQTT & NATS]]
- Overview: [[P4-IO-Jacks Interfaces]]
