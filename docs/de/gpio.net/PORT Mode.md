---
tags:
  - p4-io-jacks
  - gpio
  - port-mode
erstellt: 2026-06-17
status: description
description: "IO-Jack im PORT-Modus: 4-Bit-Digital-I/O an Pin0–Pin3 mit Ein-Byte-Befehlen von Port-8 zum Schreiben, Lesen, Setzen, Löschen und Umschalten von Bits."
---

# IO-Jack – PORT-Modus

> IO-Jack im PORT-Modus – digitale I/O mit 4 Bit.

---

## Funktionsweise

Im **PORT-Modus** liest und schreibt ein IO-Jack **4 Bit** (Pin3 · Pin2 · Pin1 · Pin0).

Jeder Befehl ist **ein einzelnes, zusammengesetztes Byte**: Bit 7 = feste **Kennung** `0`, Bits 6–4 = **Befehl** (C2 C1 C0), Bits 3–0 = **Daten** (Pin3…Pin0):

| Bitposition | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **Feld** | Kennung | C2 | C1 | C0 | **Pin3** | **Pin2** | **Pin1** | **Pin0** |
| | `0` | *Befehl* | *Befehl* | *Befehl* | *Daten* | *Daten* | *Daten* | *Daten* |

Daraus ergeben sich die Operationen und die Bestätigung – jeweils **als ein Byte**:

| Operation | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 | = Byte |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--|
| **Write** – 4 Bit schreiben | `0` | `0` | `0` | `0` | P3 | P2 | P1 | P0 | `0000 PPPP` |
| **Read** – Leseanfrage | `0` | `0` | `0` | `1` | f | f | f | f | `0001 ffff` |
| **Read-Antwort** – 4 gelesene Bit | `0` | `0` | `0` | `1` | P3 | P2 | P1 | P0 | `0001 PPPP` |
| **Set Bit** – Pins auf High | `0` | `0` | `1` | `0` | M3 | M2 | M1 | M0 | `0010 MMMM` |
| **Clear Bit** – Pins auf Low | `0` | `0` | `1` | `1` | M3 | M2 | M1 | M0 | `0011 MMMM` |
| **Toggle Bit** – Pins invertieren | `0` | `1` | `0` | `0` | M3 | M2 | M1 | M0 | `0100 MMMM` |
| **Return Code** – Bestätigung (nach dem Schreiben) | `0` | `1` | `1` | `1` | `0` | `0` | `0` | `0` | `0x70` = No Error |

- **P3…P0** = Zustand von Pin3…Pin0 (Daten-Nibble, `D3…D0`)
- **f** = **Lesefrequenzen** (Daten-Nibble beim Lesen): `0` = einmalig, `1–15` = Sekunden, `>16` = Millisekunden
- **M3…M0** = **Bitmaske**: `1` = Pin wird geändert, `0` = Pin bleibt unverändert
- Befehlscodes: `000` = Write/Value, `001` = Read, `010` = Set Bit, `011` = Clear Bit, `100` = Toggle Bit, `111` = Return Code

---

## Befehle im Detail

Alle drei Operationen folgen dem 4-Bit-Datenframe `0CCCDDDD` (1 Byte).

### Write – Read/Write Value (Code 0)

```
0 CCC DDDD  =  0 000 <Pin3 Pin2 Pin1 Pin0>
```

- `CCC = 000` → Befehl **0 (Read/Write Value)**
- `DDDD` = die 4 Pin-Zustände (PAD-Daten)

### Read – Read Command (Code 1)

```
0 CCC DDDD  =  0 001 <Read Frequencies>
```

- `CCC = 001` → Befehl **1 (Read Command)**
- `DDDD` = **Lesefrequenzen**: `0` = einmalig, `1–15` = Sekunden, `>16` = Millisekunden (periodisches Lesen)
- Die **Antwort** verwendet denselben Lesecode `001` mit den 4 gelesenen Bits im Daten-Nibble → `0001 PPPP`.

### Set Bit (Code 2)

```
0 CCC DDDD  =  0 010 <Bit Mask>
```

- `CCC = 010` → Befehl **2 (Set Bit)**
- `DDDD` = **Bitmaske**: Alle mit `1` markierten Pins werden auf **High** gesetzt, die übrigen bleiben unverändert.

### Clear Bit (Code 3)

```
0 CCC DDDD  =  0 011 <Bit Mask>
```

- `CCC = 011` → Befehl **3 (Clear Bit)**
- `DDDD` = **Bitmaske**: Alle mit `1` markierten Pins werden auf **Low** gesetzt, die übrigen bleiben unverändert.

### Toggle Bit (Code 4)

```
0 CCC DDDD  =  0 100 <Bit Mask>
```

- `CCC = 100` → Befehl **4 (Toggle Bit)**
- `DDDD` = **Bitmaske**: Alle mit `1` markierten Pins werden **invertiert**, die übrigen bleiben unverändert.

> Set/Clear/Toggle Bit wirken über die Maske **gezielt** – anders als **Write**, das immer alle 4 Pins auf einmal überschreibt.

### Return Code (Code 7)

```
0 CCC DDDD  =  0 111 0000  =  0x70   → No Error
```

- `CCC = 111` → Befehl **7 (Return Code)**
- `DDDD = 0000` → Fehlercode **0 = No Error**

| Return Code (Byte) | Bedeutung |
|:--:|---|
| `0x70` | No Error |
| `0x71` | Bad Request |
| `0x72` | Not Found |
| `0x73` | Request Timeout |

### Mehr als 4 Pins

Der 4-Bit-Frame adressiert 4 PADs. Für breitere Ports werden dieselben Befehle im **8- oder 16-Bit-Frame** verwendet (PAD-Maske entsprechend breit, 8/16 Bit).

---

## Port-Konfiguration

Für portweite Einstellungen (über einzelne Pin-Operationen hinaus) gibt es den Befehl **Config Port** (Code 28, nur im 16-Bit-Frame) – analog zu Config UART/SPI/I²C. Die konkreten Konfigurationsinhalte sind derzeit nicht spezifiziert.

---

## LED-Steuerung

Zusätzlich zu den Pins lassen sich die **Modul-LEDs** ansprechen. Dafür werden **nicht** die 4-Bit-Grundbefehle für Pins verwendet, sondern eigene Befehle (**Set LED** Code 16, **Clear LED** Code 17, **Toggle LED** Code 18) mit einem **breiteren Frame** (16 Bit statt 1 Byte):

| Code | Funktion | Daten | Wirkung |
|:--:|---|---|---|
| **16** | **Set LED** | LED-Maske | ausgewählte LEDs **einschalten** |
| **17** | **Clear LED** | LED-Maske | ausgewählte LEDs **ausschalten** |
| **18** | **Toggle LED** | LED-Maske | ausgewählte LEDs **umschalten** |

- **LED-Maske**: Bitfeld, ein Bit pro LED (`1` = LED wird geändert, `0` = LED bleibt unverändert).
- Die LED-Operationen können **unabhängig vom aktuellen Betriebsmodus des Jacks** (PORT/I²C/UART/SPI) verwendet werden – anders als die Pin-Befehle, die nur im PORT-Modus gelten.

### Beispiel: LED 1 (rot) und LED 2 (grün)

| Bitposition | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **LED** | – | – | – | – | – | – | **LED2** (grün) | **LED1** (rot) |

| Aktion | Bit 1 (grün) | Bit 0 (rot) | LED-Maske |
|---|:--:|:--:|:--:|
| **Set LED** – nur LED 1 (rot) einschalten | `0` | `1` | `0x01` |
| **Set LED** – nur LED 2 (grün) einschalten | `1` | `0` | `0x02` |
| **Set LED** – beide LEDs einschalten | `1` | `1` | `0x03` |
| **Clear LED** – nur LED 1 (rot) ausschalten | `0` | `1` | `0x01` |
| **Toggle LED** – beide LEDs umschalten | `1` | `1` | `0x03` |

> Die LED-Befehle (Code 16–18) gehören zur selben Gruppe von 16-Bit-Befehlen wie die Config-Befehle (Code 25–30) – erkennbar am größeren Frame, nicht am 1-Byte-Format der Pin-Operationen.

### Übertragung: 4 Bytes für 16 Bit Daten

Die LED-Maske wird als **16-Bit-Datenwort** übertragen, aber **nicht** als 2 Rohbytes gesendet – der vollständige Befehl (Code + Maske) belegt **4 Bytes** (1 Lead-Byte + 3 Folgebytes), da jedes Byte 2 Kennungsbits für die Selbstsynchronisation reserviert:

| Byte | Inhalt |
|:--:|---|
| **0** (Lead) | Frame-Kennung + Befehlscode (oberer Teil) |
| **1** | Befehlscode (Rest) + Datenbits 15–12 |
| **2** | Datenbits 11–6 |
| **3** | Datenbits 5–0 |

Vollständige Frames für unser Beispiel (LED 1 = rot, LED 2 = grün):

| Aktion | LED-Maske | = 4-Byte-Frame |
|---|:--:|:--:|
| **Set LED** – LED 1 (rot) ein | `0x0001` | `E4 80 80 81` |
| **Set LED** – beide LEDs ein | `0x0003` | `E4 80 80 83` |
| **Clear LED** – LED 1 (rot) aus | `0x0001` | `E4 90 80 81` |
| **Toggle LED** – beide LEDs umschalten | `0x0003` | `E4 A0 80 83` |

---

## Querverweise

- Übersicht: [[P4-IO-Jacks Interfaces|P4-IO-Jacks – Schnittstellen]]
- Transport: [[MQTT & NATS]]
