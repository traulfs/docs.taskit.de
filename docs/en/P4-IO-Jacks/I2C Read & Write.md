---
tags:
  - taskit
  - p4-io-jacks
  - i2c
  - i2c-mode
erstellt: 2026-06-17
status: description
---

# IO-Jack — I²C Read & Write

## How It Works

In **I²C mode**, the IO jack becomes an I²C master. Read/write transfers and setting/reading the I²C address are carried out via **a single command byte**, followed by the actual byte stream.

This byte is **composite**: bit 7 = **R/W marker** (`0` = read, `1` = write), bits 6–0 = **length** (`1–127` = number of data bytes; `0` = address operation):

| Bit position | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **Field** | R/W | L6 | L5 | L4 | L3 | L2 | L1 | L0 |
| | Marker | *Length (0–127)* | *Length* | *Length* | *Length* | *Length* | *Length* | *Length* |

This gives four operations – command byte plus data bytes as applicable:

| Operation | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 | = Byte |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--|
| **Read I²C** (n bytes) | `0` | L6 | L5 | L4 | L3 | L2 | L1 | L0 | `0nnn nnnn` (n = 1–127) |
| **Write I²C** (n bytes) | `1` | L6 | L5 | L4 | L3 | L2 | L1 | L0 | `1nnn nnnn` (= 128 + n) |
| **Read I²C Address** | `0` | `0` | `0` | `0` | `0` | `0` | `0` | `0` | `0x00` |
| **Write I²C Address** | `1` | `0` | `0` | `0` | `0` | `0` | `0` | `0` | `0x80` |

The subsequent byte stream and the response:

| Operation | Further bytes | Response |
|---|---|---|
| **Read I²C** | – | n data bytes (`byte 1 … byte n`) |
| **Write I²C** | n data bytes | *n bytes written* |
| **Read I²C Address** | – | current I²C address |
| **Write I²C Address** | Address byte | Confirmation |

> Example values: `0x00` = read address, `0x80` = write address, `0x01` = read with length 1 → *one byte written*.

---

## Protocol Details

### Read I²C

```
Request:   Length  [1–127]
Response:  Byte₁  Byte₂  …  Byteₙ         (n = Length)
```

### Write I²C

```
Request:   (128 + Length) [129–255]   Byte₁  Byte₂  …  Byteₙ
Response:  "n bytes written"
```

### Address Operations

| Action | Request | Response |
|---|:--:|---|
| Read I²C Address | `0x00` | I²C address |
| Write I²C Address | `0x80` (128) | Confirmation |

---

## Cross References

- Transport: [[MQTT & NATS]] (subtopic `i2c`)
- Overview: [[P4-IO-Jacks Interfaces]]
