---
tags:
  - taskit
  - p4-io-jacks
  - i2c
  - i2c-mode
erstellt: 2026-06-17
status: description
description: "IO-Jack im I²C-Modus: Der Jack arbeitet als I²C-Master; ein Befehlsbyte (R/W-Bit plus 7-Bit-Länge) wählt Lesen, Schreiben oder I²C-Adressoperationen."
---

# IO-Jack – I²C Lesen & Schreiben

## Funktionsweise

Im **I²C-Modus** wird der IO-Jack zum I²C-Master. Lese-/Schreibübertragungen sowie das Setzen und Lesen der I²C-Adresse erfolgen über **ein einzelnes Befehlsbyte**, gefolgt vom eigentlichen Bytestrom.

Dieses Byte ist **zusammengesetzt**: Bit 7 = **R/W-Kennung** (`0` = Lesen, `1` = Schreiben), Bits 6–0 = **Länge** (`1–127` = Anzahl der Datenbytes; `0` = Adressoperation):

| Bitposition | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **Feld** | R/W | L6 | L5 | L4 | L3 | L2 | L1 | L0 |
| | Kennung | *Länge (0–127)* | *Länge* | *Länge* | *Länge* | *Länge* | *Länge* | *Länge* |

Daraus ergeben sich vier Operationen – Befehlsbyte plus ggf. Datenbytes:

| Operation | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 | = Byte |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--|
| **I²C lesen** (n Bytes) | `0` | L6 | L5 | L4 | L3 | L2 | L1 | L0 | `0nnn nnnn` (n = 1–127) |
| **I²C schreiben** (n Bytes) | `1` | L6 | L5 | L4 | L3 | L2 | L1 | L0 | `1nnn nnnn` (= 128 + n) |
| **I²C-Adresse lesen** | `0` | `0` | `0` | `0` | `0` | `0` | `0` | `0` | `0x00` |
| **I²C-Adresse schreiben** | `1` | `0` | `0` | `0` | `0` | `0` | `0` | `0` | `0x80` |

Der nachfolgende Bytestrom und die Antwort:

| Operation | Weitere Bytes | Antwort |
|---|---|---|
| **I²C lesen** | – | n Datenbytes (`Byte 1 … Byte n`) |
| **I²C schreiben** | n Datenbytes | *n bytes written* |
| **I²C-Adresse lesen** | – | aktuelle I²C-Adresse |
| **I²C-Adresse schreiben** | Adressbyte | Bestätigung |

> Beispielwerte: `0x00` = Adresse lesen, `0x80` = Adresse schreiben, `0x01` = Lesen mit Länge 1 → *one byte written*.

---

## Protokolldetails

### I²C lesen

```
Request:   Length  [1–127]
Response:  Byte₁  Byte₂  …  Byteₙ         (n = Length)
```

### I²C schreiben

```
Request:   (128 + Length) [129–255]   Byte₁  Byte₂  …  Byteₙ
Response:  "n bytes written"
```

### Adressoperationen

| Aktion | Anfrage | Antwort |
|---|:--:|---|
| I²C-Adresse lesen | `0x00` | I²C-Adresse |
| I²C-Adresse schreiben | `0x80` (128) | Bestätigung |

---

## Querverweise

- Transport: [[MQTT & NATS]] (Subtopic `i2c`)
- Übersicht: [[P4-IO-Jacks Interfaces|P4-IO-Jacks – Schnittstellen]]
