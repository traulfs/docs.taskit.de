---
tags:
  - p4-io-jacks
  - gpio
  - port-mode
erstellt: 2026-06-17
status: beschreibung
---

# IO-Jack — PORT Mode

> IO-Jack im PORT-Modus – digitale Ein-/Ausgabe von 4 Bit.

---

## Funktionsweise

Im **PORT Mode** liest und schreibt ein IO-Jack **4 Bit** (Pin3 · Pin2 · Pin1 · Pin0).

Jedes Kommando ist **ein einziges, zusammengesetztes Byte**: Bit 7 = fester **Marker** `0`, Bits 6–4 = **Kommando** (C2 C1 C0), Bits 3–0 = **Daten** (Pin3…Pin0):

| Bit-Position | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **Feld** | Marker | C2 | C1 | C0 | **Pin3** | **Pin2** | **Pin1** | **Pin0** |
| | `0` | *Kommando* | *Kommando* | *Kommando* | *Daten* | *Daten* | *Daten* | *Daten* |

Daraus ergeben sich die Operationen und die Quittung – jeweils **als ein Byte**:

| Operation | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 | = Byte |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--|
| **Write** – 4 Bit schreiben | `0` | `0` | `0` | `0` | P3 | P2 | P1 | P0 | `0000 PPPP` |
| **Read** – Leseanforderung | `0` | `0` | `0` | `1` | f | f | f | f | `0001 ffff` |
| **Read-Antwort** – 4 Bit gelesen | `0` | `0` | `0` | `1` | P3 | P2 | P1 | P0 | `0001 PPPP` |
| **Set Bit** – Pins auf High | `0` | `0` | `1` | `0` | M3 | M2 | M1 | M0 | `0010 MMMM` |
| **Clear Bit** – Pins auf Low | `0` | `0` | `1` | `1` | M3 | M2 | M1 | M0 | `0011 MMMM` |
| **Toggle Bit** – Pins invertieren | `0` | `1` | `0` | `0` | M3 | M2 | M1 | M0 | `0100 MMMM` |
| **Return Code** – Quittung (nach Write) | `0` | `1` | `1` | `1` | `0` | `0` | `0` | `0` | `0x70` = No Error |

- **P3…P0** = Zustand von Pin3…Pin0 (Daten-Nibble, `D3…D0`)
- **f** = **Read-Frequencies** (Daten-Nibble bei Read): `0` = einmalig, `1–15` = Sekunden, `>16` = Millisekunden
- **M3…M0** = **Bit-Maske**: `1` = Pin wird verändert, `0` = Pin bleibt unverändert
- Kommandocodes: `000` = Write/Value, `001` = Read, `010` = Set Bit, `011` = Clear Bit, `100` = Toggle Bit, `111` = Return Code

---

## Befehlsdetails

Alle drei Operationen folgen dem 4-Bit-Data-Frame `0CCCDDDD` (1 Byte).

### Write — Read/Write Value (Code 0)

```
0 CCC DDDD  =  0 000 <Pin3 Pin2 Pin1 Pin0>
```

- `CCC = 000` → Kommando **0 (Read/Write Value)**
- `DDDD` = die 4 Pin-Zustände (PAD-Daten)

### Read — Read-Command (Code 1)

```
0 CCC DDDD  =  0 001 <Read-Frequencies>
```

- `CCC = 001` → Kommando **1 (Read-Command)**
- `DDDD` = **Read-Frequencies**: `0` = einmalig, `1–15` = Sekunden, `>16` = Millisekunden (periodisches Lesen)
- Die **Antwort** nutzt denselben Read-Code `001` mit den 4 gelesenen Bit im Datennibble → `0001 PPPP`.

### Set Bit (Code 2)

```
0 CCC DDDD  =  0 010 <Bit-Maske>
```

- `CCC = 010` → Kommando **2 (Set Bit)**
- `DDDD` = **Bit-Maske**: alle mit `1` markierten Pins werden auf **High** gesetzt, die übrigen bleiben unverändert.

### Clear Bit (Code 3)

```
0 CCC DDDD  =  0 011 <Bit-Maske>
```

- `CCC = 011` → Kommando **3 (Clear Bit)**
- `DDDD` = **Bit-Maske**: alle mit `1` markierten Pins werden auf **Low** gesetzt, die übrigen bleiben unverändert.

### Toggle Bit (Code 4)

```
0 CCC DDDD  =  0 100 <Bit-Maske>
```

- `CCC = 100` → Kommando **4 (Toggle Bit)**
- `DDDD` = **Bit-Maske**: alle mit `1` markierten Pins werden **invertiert**, die übrigen bleiben unverändert.

> Set/Clear/Toggle Bit wirken **selektiv** über die Maske – im Gegensatz zu **Write**, das immer alle 4 Pins auf einmal überschreibt.

### Return Code (Code 7)

```
0 CCC DDDD  =  0 111 0000  =  0x70   → No Error
```

- `CCC = 111` → Kommando **7 (Return Code)**
- `DDDD = 0000` → Error-Code **0 = No Error**

| Return Code (Byte) | Bedeutung |
|:--:|---|
| `0x70` | No Error |
| `0x71` | Bad Request |
| `0x72` | Not Found |
| `0x73` | Request Timeout |

### Mehr als 4 Pins

Der 4-Bit-Frame adressiert 4 PADs. Für breitere Ports werden dieselben Befehle im **8- oder 16-Bit-Frame** verwendet (PAD-Maske entsprechend 8/16 Bit).

---

## Port-Konfiguration

Für portweite Einstellungen (jenseits einzelner Pin-Operationen) gibt es den Befehl **Config Port** (Code 28, nur im 16-Bit-Frame) – analog zu Config UART/SPI/I²C. Die konkreten Konfigurationsinhalte sind aktuell nicht spezifiziert.

---

## LED-Steuerung

Zusätzlich zu den Pins lassen sich die **Modul-LEDs** ansprechen. Das läuft **nicht** über die 4-Bit-Basic-Kommandos der Pins, sondern über eigene Befehle (**Set LED** Code 16, **Clear LED** Code 17, **Toggle LED** Code 18) mit **breiterem Frame** (16 Bit statt 1 Byte):

| Code | Funktion | Daten | Wirkung |
|:--:|---|---|---|
| **16** | **Set LED** | LED-Maske | selektierte LEDs **einschalten** |
| **17** | **Clear LED** | LED-Maske | selektierte LEDs **ausschalten** |
| **18** | **Toggle LED** | LED-Maske | selektierte LEDs **umschalten** |

- **LED-Maske**: Bitfeld, ein Bit pro LED (`1` = LED wird verändert, `0` = LED bleibt unverändert).
- Die LED-Operationen sind **unabhängig vom aktuellen Betriebsmodus** des Jacks (PORT/I²C/UART/SPI) nutzbar – anders als die Pin-Kommandos, die nur im PORT Mode gelten.

### Beispiel: LED 1 (rot) und LED 2 (grün)

| Bit-Position | 7 | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
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

Die LED-Maske wird als **16-Bit-Datenwort** übertragen, aber **nicht** als 2 rohe Bytes gesendet – das komplette Kommando (Code + Maske) belegt **4 Bytes** (1 Lead-Byte + 3 Folge-Bytes), da jedes Byte 2 Kennungsbits für die Selbstsynchronisation reserviert:

| Byte | Inhalt |
|:--:|---|
| **0** (Lead) | Frame-Kennung + Kommandocode (High-Teil) |
| **1** | Kommandocode (Rest) + Datenbits 15–12 |
| **2** | Datenbits 11–6 |
| **3** | Datenbits 5–0 |

Vollständige Frames für unser Beispiel (LED 1 = rot, LED 2 = grün):

| Aktion | LED-Maske | = 4-Byte-Frame |
|---|:--:|:--:|
| **Set LED** – LED 1 (rot) an | `0x0001` | `E4 80 80 81` |
| **Set LED** – beide LEDs an | `0x0003` | `E4 80 80 83` |
| **Clear LED** – LED 1 (rot) aus | `0x0001` | `E4 90 80 81` |
| **Toggle LED** – beide LEDs umschalten | `0x0003` | `E4 A0 80 83` |

---

## Querverweise

- Übersicht: [[P4-IO-Jacks Interfaces]]
- Transport: [[MQTT & NATS]]
