---
tags:
  - taskit
  - gpio
  - protokoll
  - port-8
  - referenz
quelle: portchar_260514.key
erstellt: 2026-05-18
status: referenz
---

# taskit Port-8 – Protokollbeschreibung

> Port-8 ist das Befehls- und Datenkodierungsformat der taskit gpio.net Module. Es überträgt Kommandos und Datenwörter in drei Frame-Größen (4 / 8 / 16 Bit) über einen 8-Bit-orientierten seriellen Bus (TSB) oder UART.

---

## 1. Einführung

Port-8 ist ein **selbstsynchronisierendes, längenkodiertes Protokoll**, eng an das **UTF-8-Prinzip** angelehnt: jedes Frame beginnt mit einem Lead-Byte, dessen führende Bits die Gesamtlänge angeben, gefolgt von Continuation-Bytes mit dem Präfix `10`.

Anwendung: **GPIO-Steuerung** (PADs setzen/lesen/togglen) und **Konfiguration** (Direction, PullUp/PullDown, Notification).

---

## 2. Frame-Formate

Port-8 kennt **drei Frame-Größen**, identifiziert über das Bitmuster des ersten Bytes (Lead-Byte). Continuation-Bytes beginnen analog zu UTF-8 immer mit `10`.

### 2.1 Übersichtstabelle

| Bytes | Lead-Byte-Muster | Command-Bits | Daten-Bits | Frame-Typ |
|---|---|---|---|---|
| 1 | `0CCCDDDD` | 3 (C2–C0) | 4 | **4 Bit** |
| 2 | `110CCCDD 10DDDDDD` | 3 (C2–C0) | 8 | **8 Bit** |
| 4 | `1110CCCC 10CCDDDD 10DDDDDD 10DDDDDD` | 6 (C5–C0) | 16 | **16 Bit** |

### 2.2 Legende

| Symbol | Bedeutung |
|---|---|
| `D` | Databit (Nutzdaten) |
| `C` | Command-Bit (Befehlscode) |
| `0`/`1` | Festes Bitmuster zur Frame-Identifikation |

### 2.3 Bit-Layouts

Jede Zelle entspricht einem Bit des Bytes. Die Beschriftung unter jedem Byte gibt die Byte-Bit-Position an (7 = MSB, 0 = LSB).

#### 2.3.1 · 4 Bit — 1 Byte — `0CCCDDDD`

```
Byte 0:
┌───┬───┬───┬───┬───┬───┬───┬───┐
│  0│ C2│ C1│ C0│ D3│ D2│ D1│ D0│
└───┴───┴───┴───┴───┴───┴───┴───┘
   7   6   5   4   3   2   1   0
```

3 Command-Bits (`C2–C0`) → Codes 0–7. 4 Daten-Bits.

#### 2.3.2 · 8 Bit — 2 Bytes — `110CCCDD 10DDDDDD`

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

3 Command-Bits (`C2–C0`) → Codes 0–7. 8 Daten-Bits.

#### 2.3.3 · 16 Bit — 4 Bytes — `1110CCCC 10CCDDDD 10DDDDDD 10DDDDDD`

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

6 Command-Bits (`C5–C0`) → Codes 0–63. 16 Daten-Bits – **kein Padding nötig**, die Bits gehen exakt auf (4+2 Command-Bits, 4+6+6 Daten-Bits).

> 4 der 6 Command-Bits (`C5–C2`) passen in Byte 0 (nach dem festen `1110`-Präfix bleiben 4 Bit frei); die restlichen 2 Bits (`C1 C0`) stehen am Anfang von Byte 1, direkt vor den Daten. Dadurch stehen im 16-Bit-Frame **achtmal so viele Befehlscodes** zur Verfügung wie im 4-/8-Bit-Frame (0–63 statt 0–7).

---

## 3. Befehle

| Code | Name | Daten | Nutzbar in |
|:---:|---|---|---|
| **0** | Read/Write Value | PAD Data | 4 / 8 / 16 Bit |
| **1** | Read-Command | Read-Frequencies | 4 / 8 / 16 Bit |
| **2** | Set Output | PAD Mask | 4 / 8 / 16 Bit |
| **3** | Clear Output | PAD Mask | 4 / 8 / 16 Bit |
| **4** | Toggle Output | PAD Mask | 4 / 8 / 16 Bit |
| **5** | Notification | PAD-Nr + Pegel | 4 / 8 / 16 Bit |
| **6** | I2C Read/Write | 8-Bit-Mode | 4 / 8 / 16 Bit |
| **7** | Return Code | Error / Code | 4 / 8 / 16 Bit |
| **8** | Set Direction | PAD Mask | nur 16 Bit |
| **9** | Clear Direction | PAD Mask | nur 16 Bit |
| **10** | Set PullEnable | PAD Mask | nur 16 Bit |
| **11** | Clear PullEnable | PAD Mask | nur 16 Bit |
| **12** | Set Notification | PAD Mask | nur 16 Bit |
| **13** | Clear Notification | PAD Mask | nur 16 Bit |
| **14** | Pull Direction | 0/1 pro PAD | nur 16 Bit |
| **15** | Delay | Delay in ms | nur 16 Bit |
| **16** | Set LED | LED Mask | nur 16 Bit |
| **17** | Clear LED | LED Mask | nur 16 Bit |
| **18** | Toggle LED | LED Mask | nur 16 Bit |
| **19** | — reserviert — | – | nur 16 Bit |
| **20** | — reserviert — | – | nur 16 Bit |
| **21** | — reserviert — | – | nur 16 Bit |
| **22** | — reserviert — | – | nur 16 Bit |
| **23** | — reserviert — | – | nur 16 Bit |
| **24** | — reserviert — | – | nur 16 Bit |
| **25** | Config UART | siehe [[UART Mode]] | nur 16 Bit |
| **26** | Config SPI | Konfigurationswort | nur 16 Bit |
| **27** | Config I2C | Konfigurationswort | nur 16 Bit |
| **28** | Config Port | Konfigurationswort | nur 16 Bit |
| **29** | Config ADC | Konfigurationswort | nur 16 Bit |
| **30** | Config DAC | Konfigurationswort | nur 16 Bit |
| **31** | — reserviert — | – | nur 16 Bit |
| **32** | — reserviert — | – | nur 16 Bit |
| **33** | — reserviert — | – | nur 16 Bit |
| **34** | — reserviert — | – | nur 16 Bit |
| **35** | — reserviert — | – | nur 16 Bit |
| **36** | — reserviert — | – | nur 16 Bit |
| **37** | — reserviert — | – | nur 16 Bit |
| **38** | — reserviert — | – | nur 16 Bit |
| **39** | — reserviert — | – | nur 16 Bit |
| **40** | — reserviert — | – | nur 16 Bit |
| **41** | — reserviert — | – | nur 16 Bit |
| **42** | — reserviert — | – | nur 16 Bit |
| **43** | — reserviert — | – | nur 16 Bit |
| **44** | — reserviert — | – | nur 16 Bit |
| **45** | — reserviert — | – | nur 16 Bit |
| **46** | — reserviert — | – | nur 16 Bit |
| **47** | — reserviert — | – | nur 16 Bit |
| **48** | — reserviert — | – | nur 16 Bit |
| **49** | — reserviert — | – | nur 16 Bit |
| **50** | — reserviert — | – | nur 16 Bit |
| **51** | — reserviert — | – | nur 16 Bit |
| **52** | — reserviert — | – | nur 16 Bit |
| **53** | — reserviert — | – | nur 16 Bit |
| **54** | — reserviert — | – | nur 16 Bit |
| **55** | — reserviert — | – | nur 16 Bit |
| **56** | — reserviert — | – | nur 16 Bit |
| **57** | — reserviert — | – | nur 16 Bit |
| **58** | — reserviert — | – | nur 16 Bit |
| **59** | — reserviert — | – | nur 16 Bit |
| **60** | — reserviert — | – | nur 16 Bit |
| **61** | — reserviert — | – | nur 16 Bit |
| **62** | — reserviert — | – | nur 16 Bit |
| **63** | — reserviert — | – | nur 16 Bit |

- **PAD Mask**: Bitfeld, jedes gesetzte Bit adressiert ein PAD (Breite = Datenbreite des Frames: 4 / 8 / 16 Bit).
- Codes **0–7** passen in 3 Bit und sind daher in **allen drei** Frame-Größen nutzbar.
- Codes **8–63** benötigen mehr als 3 Command-Bits und sind daher **ausschließlich im 16-Bit-Frame** verfügbar (6 Command-Bits, Codes 0–63). Codes **16–63** sind aktuell **reserviert/unbelegt**.
- **Pull-Konfiguration**: Erfordert zwei Befehle – erst `Set PullEnable` (10), dann `Pull Direction` (14) zur Auswahl von PullUp/PullDown.

---

## 4. Querverweise

- [[Powerpoint/portchar_260514]] – Originale Folien-Dokumentation
- [[UTF-8 Kodierung]] – Grundlagen der UTF-8-Kodierung
