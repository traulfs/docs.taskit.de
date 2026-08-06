---
tags:
  - taskit
  - gpio
  - protocol
  - port-8
  - reference
quelle: portchar_260514.key
erstellt: 2026-05-18
status: reference
---

# taskit Port-8 – Protocol Description

> Port-8 is the command and data encoding format of the taskit gpio.net modules. It transmits commands and data words in three frame sizes (4 / 8 / 16 bit) over an 8-bit-oriented serial bus (TSB) or UART.

---

## 1. Introduction

Port-8 is a **self-synchronizing, length-encoded protocol**, closely modeled on the **UTF-8 principle**: every frame starts with a lead byte whose leading bits indicate the total length, followed by continuation bytes with the prefix `10`.

Application: **GPIO control** (setting/reading/toggling PADs) and **configuration** (direction, pull-up/pull-down, notification).

---

## 2. Frame Formats

Port-8 defines **three frame sizes**, identified by the bit pattern of the first byte (lead byte). Continuation bytes always start with `10`, analogous to UTF-8.

### 2.1 Overview Table

| Bytes | Lead byte pattern | Command bits | Data bits | Frame type |
|---|---|---|---|---|
| 1 | `0CCCDDDD` | 3 (C2–C0) | 4 | **4-bit** |
| 2 | `110CCCDD 10DDDDDD` | 3 (C2–C0) | 8 | **8-bit** |
| 4 | `1110CCCC 10CCDDDD 10DDDDDD 10DDDDDD` | 6 (C5–C0) | 16 | **16-bit** |

### 2.2 Legend

| Symbol | Meaning |
|---|---|
| `D` | Data bit (payload) |
| `C` | Command bit (command code) |
| `0`/`1` | Fixed bit pattern for frame identification |

### 2.3 Bit Layouts

Each cell corresponds to one bit of the byte. The label below each byte shows the byte-bit position (7 = MSB, 0 = LSB).

#### 2.3.1 · 4-bit — 1 byte — `0CCCDDDD`

```
Byte 0:
┌───┬───┬───┬───┬───┬───┬───┬───┐
│  0│ C2│ C1│ C0│ D3│ D2│ D1│ D0│
└───┴───┴───┴───┴───┴───┴───┴───┘
   7   6   5   4   3   2   1   0
```

3 command bits (`C2–C0`) → codes 0–7. 4 data bits.

#### 2.3.2 · 8-bit — 2 bytes — `110CCCDD 10DDDDDD`

```
Byte 0:
┌───┬───┬───┬───┬───┬───┬───┬───┐
│  1│  1│  0│ C2│ C1│ C0│ D7│ D6│
└───┴───┴───┴───┴───┴───┴───┴───┘
   7   6   5   4   3   2   1   0

Byte 1:
┌───┬───┬───┬───┬───┬───┬───┬───┐
│  1│  0│ D5│ D4│ D3│ D2│ D1│ D0│
└───┴───┴───┴───┴───┴───┴───┴───┘
   7   6   5   4   3   2   1   0
```

3 command bits (`C2–C0`) → codes 0–7. 8 data bits.

#### 2.3.3 · 16-bit — 4 bytes — `1110CCCC 10CCDDDD 10DDDDDD 10DDDDDD`

```
Byte 0:
┌───┬───┬───┬───┬───┬───┬───┬───┐
│  1│  1│  1│  0│ C5│ C4│ C3│ C2│
└───┴───┴───┴───┴───┴───┴───┴───┘
   7   6   5   4   3   2   1   0

Byte 1:
┌───┬───┬───┬───┬───┬───┬───┬───┐
│  1│  0│ C1│ C0│D15│D14│D13│D12│
└───┴───┴───┴───┴───┴───┴───┴───┘
   7   6   5   4   3   2   1   0

Byte 2:
┌───┬───┬───┬───┬───┬───┬───┬───┐
│  1│  0│D11│D10│ D9│ D8│ D7│ D6│
└───┴───┴───┴───┴───┴───┴───┴───┘
   7   6   5   4   3   2   1   0

Byte 3:
┌───┬───┬───┬───┬───┬───┬───┬───┐
│  1│  0│ D5│ D4│ D3│ D2│ D1│ D0│
└───┴───┴───┴───┴───┴───┴───┴───┘
   7   6   5   4   3   2   1   0
```

6 command bits (`C5–C0`) → codes 0–63. 16 data bits – **no padding needed**, the bits add up exactly (4+2 command bits, 4+6+6 data bits).

> 4 of the 6 command bits (`C5–C2`) fit into byte 0 (4 bits remain free after the fixed `1110` prefix); the remaining 2 bits (`C1 C0`) sit at the start of byte 1, right before the data. This gives the 16-bit frame **eight times as many command codes** as the 4-/8-bit frame (0–63 instead of 0–7).

---

## 3. Commands

| Code | Name | Data | Description | Datasize |
|:---:|---|---|---|---|
| **0**  | Write Value | PAD Data | | 4 / 8 / 16 bit |
| **1**  | Read-Command | Read frequencies | | 4 / 8 / 16 bit |
| **2**  | Set Output | PAD Mask | | 4 / 8 / 16 bit |
| **3**  | Clear Output | PAD Mask | | 4 / 8 / 16 bit |
| **4**  | Toggle Output | PAD Mask | | 4 / 8 / 16 bit |
| **5**  | Notification | PAD no. + level | | 4 / 8 / 16 bit |
| **6**  | I2C Read/Write | 8-bit mode | | 4 / 8 / 16 bit |
| **7**  | Return Code | Error / code | | 4 / 8 / 16 bit |
| **8**  | Set Direction | PAD Mask | | 16-bit only |
| **9**  | Clear Direction | PAD Mask | | 16-bit only |
| **10** | Set PullEnable | PAD Mask | | 16-bit only |
| **11** | Clear PullEnable | PAD Mask | | 16-bit only |
| **12** | Set Notification | PAD Mask | | 16-bit only |
| **13** | Clear Notification | PAD Mask | | 16-bit only |
| **14** | Pull Direction | 0/1 per PAD | | 16-bit only |
| **15** | Delay | Delay in ms | | 16-bit only |
| **16** | Set LED | LED Mask | | 16-bit only |
| **17** | Clear LED | LED Mask | | 16-bit only |
| **18** | Toggle LED | LED Mask | | 16-bit only |
| **19** | Config Read | – | | 16-bit only |
| **20** | Config Write | – | | 16-bit only |
| **21** | — reserved — | – | | 16-bit only |
| **22** | — reserved — | – | | 16-bit only |
| **23** | — reserved — | – | | 16-bit only |
| **24** | — reserved — | – | | 16-bit only |
| **25** | — reserved — | – | | 16-bit only |
| **26** | — reserved — | – | | 16-bit only |
| **27** | — reserved — | – | | 16-bit only |
| **28** | — reserved — | – | | 16-bit only |
| **29** | — reserved — | – | | 16-bit only |
| **30** | — reserved — | – | | 16-bit only |
| **31** | — reserved — | – | | 16-bit only |
| **32** | Reset Hardware  | – |                    | 16-bit only |
| **33** | Read HW Version | – | for example "3.01" | 2 x 16-bit |
| **34** | Read SW Version | – | for example "3.01" | 2 x 16-bit |
| **35** | Read MAC  | - |  | 3 x 16-bit |
| **36** | Read Name | - |  | n x 16-bit |
| **37** | — reserved — | – | | 16-bit only |
| **38** | — reserved — | – | | 16-bit only |
| **39** | — reserved — | – | | 16-bit only |
| **40** | — reserved — | – | | 16-bit only |
| **41** | — reserved — | – | | 16-bit only |
| **42** | — reserved — | – | | 16-bit only |
| **43** | — reserved — | – | | 16-bit only |
| **44** | — reserved — | – | | 16-bit only |
| **45** | — reserved — | – | | 16-bit only |
| **46** | — reserved — | – | | 16-bit only |
| **47** | — reserved — | – | | 16-bit only |
| **48** | — reserved — | – | | 16-bit only |
| **49** | — reserved — | – | | 16-bit only |
| **50** | — reserved — | – | | 16-bit only |
| **51** | — reserved — | – | | 16-bit only |
| **52** | — reserved — | – | | 16-bit only |
| **53** | — reserved — | – | | 16-bit only |
| **54** | — reserved — | – | | 16-bit only |
| **55** | — reserved — | – | | 16-bit only |
| **56** | — reserved — | – | | 16-bit only |
| **57** | — reserved — | – | | 16-bit only |
| **58** | — reserved — | – | | 16-bit only |
| **59** | — reserved — | – | | 16-bit only |
| **60** | — reserved — | – | | 16-bit only |
| **61** | — reserved — | – | | 16-bit only |
| **62** | — reserved — | – | | 16-bit only |
| **63** | — reserved — | – | | 16-bit only |

- **PAD Mask**: bitfield, each set bit addresses one PAD (width = data width of the frame: 4 / 8 / 16 bit).
- Codes **0–7** fit in 3 bits and are therefore usable in **all three** frame sizes.
- Codes **8–63** require more than 3 command bits and are therefore **only available in the 16-bit frame** (6 command bits, codes 0–63). Codes **16–63** are currently **reserved/unassigned**.
- **Pull configuration**: requires two commands – first `Set PullEnable` (10), then `Pull Direction` (14) to select pull-up/pull-down.

---

## 4. Cross References

- [[UTF-8 Kodierung]] – Fundamentals of UTF-8 encoding
