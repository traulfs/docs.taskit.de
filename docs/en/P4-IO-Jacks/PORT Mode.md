---
tags:
  - p4-io-jacks
  - gpio
  - port-mode
erstellt: 2026-06-17
status: description
---

# IO-Jack — PORT Mode

> IO jack in PORT mode – digital I/O with 4 bit.

---

## How It Works

In **PORT mode**, an IO jack reads and writes **4 bit** (Pin3 · Pin2 · Pin1 · Pin0).

Every command is **a single, composite byte**: bit 7 = fixed **marker** `0`, bits 6–4 = **command** (C2 C1 C0), bits 3–0 = **data** (Pin3…Pin0):

| Bit position | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **Field** | Marker | C2 | C1 | C0 | **Pin3** | **Pin2** | **Pin1** | **Pin0** |
| | `0` | *Command* | *Command* | *Command* | *Data* | *Data* | *Data* | *Data* |

This gives the operations and the acknowledgment – each **as one byte**:

| Operation | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 | = Byte |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--|
| **Write** – write 4 bit | `0` | `0` | `0` | `0` | P3 | P2 | P1 | P0 | `0000 PPPP` |
| **Read** – read request | `0` | `0` | `0` | `1` | f | f | f | f | `0001 ffff` |
| **Read response** – 4 bit read | `0` | `0` | `0` | `1` | P3 | P2 | P1 | P0 | `0001 PPPP` |
| **Set Bit** – pins to high | `0` | `0` | `1` | `0` | M3 | M2 | M1 | M0 | `0010 MMMM` |
| **Clear Bit** – pins to low | `0` | `0` | `1` | `1` | M3 | M2 | M1 | M0 | `0011 MMMM` |
| **Toggle Bit** – invert pins | `0` | `1` | `0` | `0` | M3 | M2 | M1 | M0 | `0100 MMMM` |
| **Return Code** – acknowledgment (after write) | `0` | `1` | `1` | `1` | `0` | `0` | `0` | `0` | `0x70` = No Error |

- **P3…P0** = state of Pin3…Pin0 (data nibble, `D3…D0`)
- **f** = **read frequencies** (data nibble on read): `0` = once, `1–15` = seconds, `>16` = milliseconds
- **M3…M0** = **bit mask**: `1` = pin is changed, `0` = pin stays unchanged
- Command codes: `000` = Write/Value, `001` = Read, `010` = Set Bit, `011` = Clear Bit, `100` = Toggle Bit, `111` = Return Code

---

## Command Details

All three operations follow the 4-bit data frame `0CCCDDDD` (1 byte).

### Write — Read/Write Value (Code 0)

```
0 CCC DDDD  =  0 000 <Pin3 Pin2 Pin1 Pin0>
```

- `CCC = 000` → command **0 (Read/Write Value)**
- `DDDD` = the 4 pin states (PAD data)

### Read — Read Command (Code 1)

```
0 CCC DDDD  =  0 001 <Read Frequencies>
```

- `CCC = 001` → command **1 (Read Command)**
- `DDDD` = **read frequencies**: `0` = once, `1–15` = seconds, `>16` = milliseconds (periodic reading)
- The **response** uses the same read code `001` with the 4 read bits in the data nibble → `0001 PPPP`.

### Set Bit (Code 2)

```
0 CCC DDDD  =  0 010 <Bit Mask>
```

- `CCC = 010` → command **2 (Set Bit)**
- `DDDD` = **bit mask**: all pins marked with `1` are set to **high**, the rest stay unchanged.

### Clear Bit (Code 3)

```
0 CCC DDDD  =  0 011 <Bit Mask>
```

- `CCC = 011` → command **3 (Clear Bit)**
- `DDDD` = **bit mask**: all pins marked with `1` are set to **low**, the rest stay unchanged.

### Toggle Bit (Code 4)

```
0 CCC DDDD  =  0 100 <Bit Mask>
```

- `CCC = 100` → command **4 (Toggle Bit)**
- `DDDD` = **bit mask**: all pins marked with `1` are **inverted**, the rest stay unchanged.

> Set/Clear/Toggle Bit act **selectively** via the mask – unlike **Write**, which always overwrites all 4 pins at once.

### Return Code (Code 7)

```
0 CCC DDDD  =  0 111 0000  =  0x70   → No Error
```

- `CCC = 111` → command **7 (Return Code)**
- `DDDD = 0000` → error code **0 = No Error**

| Return Code (byte) | Meaning |
|:--:|---|
| `0x70` | No Error |
| `0x71` | Bad Request |
| `0x72` | Not Found |
| `0x73` | Request Timeout |

### More than 4 Pins

The 4-bit frame addresses 4 PADs. For wider ports, the same commands are used in the **8- or 16-bit frame** (PAD mask sized accordingly, 8/16 bit).

---

## Port Configuration

For port-wide settings (beyond individual pin operations), there is the **Config Port** command (code 28, 16-bit frame only) – analogous to Config UART/SPI/I²C. The specific configuration contents are not currently specified.

---

## LED Control

In addition to the pins, the **module LEDs** can be addressed. This does **not** use the 4-bit basic pin commands, but its own commands (**Set LED** code 16, **Clear LED** code 17, **Toggle LED** code 18) with a **wider frame** (16 bit instead of 1 byte):

| Code | Function | Data | Effect |
|:--:|---|---|---|
| **16** | **Set LED** | LED mask | **turn on** selected LEDs |
| **17** | **Clear LED** | LED mask | **turn off** selected LEDs |
| **18** | **Toggle LED** | LED mask | **toggle** selected LEDs |

- **LED mask**: bitfield, one bit per LED (`1` = LED is changed, `0` = LED stays unchanged).
- The LED operations can be used **independently of the jack's current operating mode** (PORT/I²C/UART/SPI) – unlike the pin commands, which only apply in PORT mode.

### Example: LED 1 (red) and LED 2 (green)

| Bit position | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **LED** | – | – | – | – | – | – | **LED2** (green) | **LED1** (red) |

| Action | Bit 1 (green) | Bit 0 (red) | LED mask |
|---|:--:|:--:|:--:|
| **Set LED** – turn on LED 1 (red) only | `0` | `1` | `0x01` |
| **Set LED** – turn on LED 2 (green) only | `1` | `0` | `0x02` |
| **Set LED** – turn on both LEDs | `1` | `1` | `0x03` |
| **Clear LED** – turn off LED 1 (red) only | `0` | `1` | `0x01` |
| **Toggle LED** – toggle both LEDs | `1` | `1` | `0x03` |

> The LED commands (code 16–18) belong to the same group of 16-bit commands as the config commands (code 25–30) – recognizable by the larger frame, not the 1-byte format of the pin operations.

### Transmission: 4 Bytes for 16 Bit of Data

The LED mask is transmitted as a **16-bit data word**, but is **not** sent as 2 raw bytes – the complete command (code + mask) occupies **4 bytes** (1 lead byte + 3 continuation bytes), since each byte reserves 2 marker bits for self-synchronization:

| Byte | Content |
|:--:|---|
| **0** (lead) | Frame marker + command code (high part) |
| **1** | Command code (rest) + data bits 15–12 |
| **2** | Data bits 11–6 |
| **3** | Data bits 5–0 |

Complete frames for our example (LED 1 = red, LED 2 = green):

| Action | LED mask | = 4-byte frame |
|---|:--:|:--:|
| **Set LED** – LED 1 (red) on | `0x0001` | `E4 80 80 81` |
| **Set LED** – both LEDs on | `0x0003` | `E4 80 80 83` |
| **Clear LED** – LED 1 (red) off | `0x0001` | `E4 90 80 81` |
| **Toggle LED** – toggle both LEDs | `0x0003` | `E4 A0 80 83` |

---

## Cross References

- Overview: [[P4-IO-Jacks Interfaces]]
- Transport: [[MQTT & NATS]]
