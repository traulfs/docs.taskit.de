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
description: "taskit Port-8: selbstsynchronisierende Befehls- und Datenkodierung der gpio.net-Module nach UTF-8-Vorbild, mit 4-, 8- und 16-Bit-Frames über TSB oder UART."
---

# taskit Port-8 – Protokollbeschreibung

> Port-8 ist das Kodierungsformat für Befehle und Daten der taskit-gpio.net-Module. Es überträgt Befehle und Datenwörter in drei Frame-Größen (4 / 8 / 16 Bit) über einen 8-Bit-orientierten seriellen Bus (TSB) oder UART.

---

## 1. Einführung

Port-8 ist ein **selbstsynchronisierendes, längenkodiertes Protokoll**, eng angelehnt an das **UTF-8-Prinzip**: Jeder Frame beginnt mit einem Lead-Byte, dessen führende Bits die Gesamtlänge angeben, gefolgt von Folgebytes mit dem Präfix `10`.

Anwendung: **GPIO-Steuerung** (PADs setzen/lesen/umschalten) und **Konfiguration** (Richtung, Pull-up/Pull-down, Benachrichtigung).

---

## 2. Frame-Formate

Port-8 definiert **drei Frame-Größen**, erkennbar am Bitmuster des ersten Bytes (Lead-Byte). Folgebytes beginnen immer mit `10`, analog zu UTF-8.

### 2.1 Übersichtstabelle

| Bytes | Muster des Lead-Bytes | Befehlsbits | Datenbits | Frame-Typ |
|---|---|---|---|---|
| 1 | `0CCCDDDD` | 3 (C2–C0) | 4 | **4 Bit** |
| 2 | `110CCCDD 10DDDDDD` | 3 (C2–C0) | 8 | **8 Bit** |
| 4 | `1110CCCC 10CCDDDD 10DDDDDD 10DDDDDD` | 6 (C5–C0) | 16 | **16 Bit** |

### 2.2 Legende

| Symbol | Bedeutung |
|---|---|
| `D` | Datenbit (Payload) |
| `C` | Befehlsbit (Befehlscode) |
| `0`/`1` | Festes Bitmuster zur Frame-Erkennung |

### 2.3 Bit-Layouts

Jede Zelle entspricht einem Bit des Bytes. Die Beschriftung unter jedem Byte zeigt die Bitposition im Byte (7 = MSB, 0 = LSB).

#### 2.3.1 · 4 Bit – 1 Byte – `0CCCDDDD`

```
Byte 0:
┌───┬───┬───┬───┬───┬───┬───┬───┐
│  0│ C2│ C1│ C0│ D3│ D2│ D1│ D0│
└───┴───┴───┴───┴───┴───┴───┴───┘
   7   6   5   4   3   2   1   0
```

3 Befehlsbits (`C2–C0`) → Codes 0–7. 4 Datenbits.

#### 2.3.2 · 8 Bit – 2 Bytes – `110CCCDD 10DDDDDD`

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

3 Befehlsbits (`C2–C0`) → Codes 0–7. 8 Datenbits.

#### 2.3.3 · 16 Bit – 4 Bytes – `1110CCCC 10CCDDDD 10DDDDDD 10DDDDDD`

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

6 Befehlsbits (`C5–C0`) → Codes 0–63. 16 Datenbits – **kein Auffüllen nötig**, die Bits gehen genau auf (4+2 Befehlsbits, 4+6+6 Datenbits).

> 4 der 6 Befehlsbits (`C5–C2`) passen in Byte 0 (nach dem festen Präfix `1110` bleiben 4 Bits frei); die übrigen 2 Bits (`C1 C0`) stehen am Anfang von Byte 1, direkt vor den Daten. Damit hat der 16-Bit-Frame **achtmal so viele Befehlscodes** wie der 4-/8-Bit-Frame (0–63 statt 0–7).

---

## 3. Befehle

| Code | Name | Daten | Beschreibung | Datengröße |
|:---:|---|---|---|---|
| **0**  | Write Value | PAD-Daten | | 4 / 8 / 16 Bit |
| **1**  | Read-Command | Lesefrequenzen | | 4 / 8 / 16 Bit |
| **2**  | Set Output | PAD-Maske | | 4 / 8 / 16 Bit |
| **3**  | Clear Output | PAD-Maske | | 4 / 8 / 16 Bit |
| **4**  | Toggle Output | PAD-Maske | | 4 / 8 / 16 Bit |
| **5**  | Notification | PAD-Nr. + Pegel | | 4 / 8 / 16 Bit |
| **6**  | I2C Read/Write | 8-Bit-Modus | | 4 / 8 / 16 Bit |
| **7**  | Return Code | Fehler / Code | | 4 / 8 / 16 Bit |
| **8**  | Set Direction | PAD-Maske | | nur 16 Bit |
| **9**  | Clear Direction | PAD-Maske | | nur 16 Bit |
| **10** | Set PullEnable | PAD-Maske | | nur 16 Bit |
| **11** | Clear PullEnable | PAD-Maske | | nur 16 Bit |
| **12** | Set Notification | PAD-Maske | | nur 16 Bit |
| **13** | Clear Notification | PAD-Maske | | nur 16 Bit |
| **14** | Pull Direction | 0/1 pro PAD | | nur 16 Bit |
| **15** | Delay | Verzögerung in ms | | nur 16 Bit |
| **16** | Set LED | LED-Maske | | nur 16 Bit |
| **17** | Clear LED | LED-Maske | | nur 16 Bit |
| **18** | Toggle LED | LED-Maske | | nur 16 Bit |
| **19** | Read  | – | | nur 16 Bit |
| **20** | UART Config Write | – | | nur 16 Bit |
| **21** | UART Config Read  | – | | nur 16 Bit |
| **22** | I2C  Config Write | – | | nur 16 Bit |
| **23** | I2C  Config Read  | – | | nur 16 Bit |
| **24** | SPI  Config Write | – | noch offen | nur 16 Bit |
| **25** | SPI  Config Read  | – | noch offen | nur 16 Bit |
| **26** | ADC  Config Write | – | noch offen | nur 16 Bit |
| **27** | ADC  Config Read  | – | noch offen | nur 16 Bit |
| **28** | DAC  Config Write | – | noch offen | nur 16 Bit |
| **29** | DAC  Config Read  | – | noch offen | nur 16 Bit |
| **30** | — reserviert —    | – | | nur 16 Bit |
| **31** | — reserviert —    | – | | nur 16 Bit |
| **32** | Reset Hardware    | – |                    | nur 16 Bit |
| **33** | Read HW Version   | – | z. B. „3.01“ | 2 × 16 Bit |
| **34** | Read SW Version   | – | z. B. „3.01“ | 2 × 16 Bit |
| **35** | Read MAC          | - | | 3 × 16 Bit |
| **36** | Write Name        | Index des Namens | | n × 16 Bit |
| **37** | Read  Name        | Index des Namens | | n × 16 Bit |
| **38** | — reserviert —    | – | | nur 16 Bit |
| **39** | — reserviert —    | – | | nur 16 Bit |
| **40** | — reserviert —    | – | | nur 16 Bit |
| **41** | — reserviert —    | – | | nur 16 Bit |
| **42** | — reserviert —    | – | | nur 16 Bit |
| **43** | — reserviert —    | – | | nur 16 Bit |
| **44** | — reserviert —    | – | | nur 16 Bit |
| **45** | — reserviert —    | – | | nur 16 Bit |
| **46** | — reserviert —    | – | | nur 16 Bit |
| **47** | — reserviert —    | – | | nur 16 Bit |
| **48** | — reserviert —    | – | | nur 16 Bit |
| **49** | — reserviert — | – | | nur 16 Bit |
| **50** | — reserviert — | – | | nur 16 Bit |
| **51** | — reserviert — | – | | nur 16 Bit |
| **52** | — reserviert — | – | | nur 16 Bit |
| **53** | — reserviert — | – | | nur 16 Bit |
| **54** | — reserviert — | – | | nur 16 Bit |
| **55** | — reserviert — | – | | nur 16 Bit |
| **56** | — reserviert — | – | | nur 16 Bit |
| **57** | — reserviert — | – | | nur 16 Bit |
| **58** | — reserviert — | – | | nur 16 Bit |
| **59** | — reserviert — | – | | nur 16 Bit |
| **60** | — reserviert — | – | | nur 16 Bit |
| **61** | — reserviert — | – | | nur 16 Bit |
| **62** | — reserviert — | – | | nur 16 Bit |
| **63** | — reserviert — | – | | nur 16 Bit |


Indizes der Namen
   - 00 reserviert
   - 01 Hardwaretyp, z. B. P4-IO-Jacks
   - 02 Hardwarename (benutzerdefiniert)
   - 03-0F reserviert

   - 10 Name von Jack0 (benutzerdefiniert)
   - 11 An Jack0 angeschlossene HW
   - 12 taskit-HW-Nr. an Jack0
   - 13-17 reserviert
   - 18 Name von Jack0-Pin0 (benutzerdefiniert)
   - 19 Name von Jack0-Pin1 (benutzerdefiniert)
   - 1A Name von Jack0-Pin2 (benutzerdefiniert)
   - 1B Name von Jack0-Pin3 (benutzerdefiniert)
   - 1C-1F reserviert

   - 20 Name von Jack1 (benutzerdefiniert)
   - 21 An Jack1 angeschlossene HW
   - 22-27 reserviert
   - 28 Name von Jack1-Pin0 (benutzerdefiniert)
   - 29 Name von Jack1-Pin1 (benutzerdefiniert)
   - 2A Name von Jack1-Pin2 (benutzerdefiniert)
   - 2B Name von Jack1-Pin3 (benutzerdefiniert)
   - 2C-2F reserviert

   - 30 Name von Jack2 (benutzerdefiniert)
   - 31 An Jack2 angeschlossene HW
   - 32-37 reserviert
   - 38 Name von Jack2-Pin0 (benutzerdefiniert)
   - 39 Name von Jack2-Pin1 (benutzerdefiniert)
   - 3A Name von Jack2-Pin2 (benutzerdefiniert)
   - 3B Name von Jack2-Pin3 (benutzerdefiniert)
   - 3C-1F reserviert

   - 40 Name von Jack3 (benutzerdefiniert)
   - 41 An Jack3 angeschlossene HW
   - 42-47 reserviert
   - 48 Name von Jack3-Pin0 (benutzerdefiniert)
   - 49 Name von Jack3-Pin1 (benutzerdefiniert)
   - 4A Name von Jack3-Pin2 (benutzerdefiniert)
   - 4B Name von Jack3-Pin3 (benutzerdefiniert)
   - 4C-4F reserviert


### 3.1 Standardnamen & Verhalten der Oberfläche

- Namen (Hardware, Jack, Pin) sind mit **sinnvollen Standardwerten vorbelegt** (z. B. `Jack0`, `Jack0-Pin0`) statt leer – `Write Name` (36) wird nur benötigt, um einen Standardwert zu überschreiben.
- Namen werden **direkt in der Jack-Ansicht** der Konfigurationsoberfläche neben dem jeweiligen Jack/Pin angezeigt – eine eigene Seite ist dafür nicht nötig.
- Namen sind **direkt in der Jack-Ansicht bearbeitbar** (Inline-Bearbeitung über `Write Name` (36) / `Read Name` (37)), nicht über einen separaten Einstellungsbildschirm.
- Das **Burger-Menü** enthält nur **Import** und **Export** – Benennung und weitere Jack-Einstellungen befinden sich in der Jack-Ansicht selbst.

- **PAD-Maske**: Bitfeld, jedes gesetzte Bit adressiert ein PAD (Breite = Datenbreite des Frames: 4 / 8 / 16 Bit).
- Die Codes **0–7** passen in 3 Bits und sind daher in **allen drei** Frame-Größen verwendbar.
- Die Codes **8–63** benötigen mehr als 3 Befehlsbits und sind daher **nur im 16-Bit-Frame** verfügbar (6 Befehlsbits, Codes 0–63). Die Codes **16–63** sind derzeit **reserviert/nicht belegt**.
- **Pull-Konfiguration**: erfordert zwei Befehle – zuerst `Set PullEnable` (10), dann `Pull Direction` (14), um Pull-up/Pull-down zu wählen.

---

## 4. Querverweise

- [[UTF-8 Kodierung|UTF-8-Kodierung]] – Grundlagen der UTF-8-Kodierung
