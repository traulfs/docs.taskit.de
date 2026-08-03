---
tags:
  - taskit
  - p4-io-jacks
  - i2c
  - i2c-mode
erstellt: 2026-06-17
status: beschreibung
---

# IO-Jack — I²C Read & Write

## Funktionsweise

Im **I²C Mode** wird der IO-Jack zum I²C-Master. Read-/Write-Transfers und das Setzen/Lesen der I²C-Adresse laufen über **ein einziges Kommandobyte**, gefolgt vom eigentlichen Byte-Stream.

Dieses Byte ist **zusammengesetzt**: Bit 7 = **R/W-Marker** (`0` = Read, `1` = Write), Bits 6–0 = **Länge** (`1–127` = Anzahl Datenbytes; `0` = Adress-Operation):

| Bit-Position | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **Feld** | R/W | L6 | L5 | L4 | L3 | L2 | L1 | L0 |
| | Marker | *Länge (0–127)* | *Länge* | *Länge* | *Länge* | *Länge* | *Länge* | *Länge* |

Daraus ergeben sich die vier Operationen – Kommandobyte plus ggf. Datenbytes:

| Operation | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 | = Byte |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--|
| **Read I²C** (n Bytes) | `0` | L6 | L5 | L4 | L3 | L2 | L1 | L0 | `0nnn nnnn` (n = 1–127) |
| **Write I²C** (n Bytes) | `1` | L6 | L5 | L4 | L3 | L2 | L1 | L0 | `1nnn nnnn` (= 128 + n) |
| **Read I²C Address** | `0` | `0` | `0` | `0` | `0` | `0` | `0` | `0` | `0x00` |
| **Write I²C Address** | `1` | `0` | `0` | `0` | `0` | `0` | `0` | `0` | `0x80` |

Der anschließende Byte-Stream und die Rückmeldung:

| Operation | weitere Bytes | Response |
|---|---|---|
| **Read I²C** | – | n Datenbytes (`1. Byte … n. Byte`) |
| **Write I²C** | n Datenbytes | *n bytes written* |
| **Read I²C Address** | – | aktuelle I²C-Adresse |
| **Write I²C Address** | Adressbyte | Bestätigung |

> Beispielwerte: `0x00` = Adresse lesen, `0x80` = Adresse schreiben, `0x01` = Read mit Länge 1 → *one byte written*.

---

## Protokoll-Details

### Read I²C

```
Request:   Length  [1–127]
Response:  Byte₁  Byte₂  …  Byteₙ         (n = Length)
```

### Write I²C

```
Request:   (128 + Length) [129–255]   Byte₁  Byte₂  …  Byteₙ
Response:  „n bytes written"
```

### Adress-Operationen

| Aktion | Request | Response |
|---|:--:|---|
| Read I²C Address | `0x00` | I²C-Adresse |
| Write I²C Address | `0x80` (128) | Bestätigung |

---

## Querverweise

- Transport: [[MQTT & NATS]] (Subtopic `i2c`)
- Übersicht: [[P4-IO-Jacks Interfaces]]
