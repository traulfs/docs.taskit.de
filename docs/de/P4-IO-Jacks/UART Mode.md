---
tags:
  - p4-io-jacks
  - uart
  - uart-mode
erstellt: 2026-06-17
status: beschreibung
---

# IO-Jack — UART Mode

> IO-Jack im UART-Modus — serielle Schnittstelle mit Konfiguration über `cfg` und Datentransfer über `uart`.

---

## Funktionsweise

Im **UART Mode** arbeitet ein IO-Jack als serielle Schnittstelle mit zwei Subtopics:

| Subtopic | Zweck |
|---|---|
| **`cfg`** | UART-Einstellungen setzen |
| **`uart`** | rohe UART-Datenbytes senden / empfangen |

---

## Konfiguration (`cfg`)

Die Schnittstelle wird vor dem Datentransfer mit fünf Parametern konfiguriert. Kurzform: `Baudrate-Datenbits-Parität-Stoppbits` (N = keine, E = gerade, O = ungerade):

| Konfiguration | Baudrate | Datenbits | Parität | Stoppbits | RS485 |
|---|--:|:--:|---|:--:|:--:|
| **Standard** · `115200-8-N-1` | 115.200 | 8 | keine | 1 | aus |
| **Klassisch** · `9600-8-N-1` | 9.600 | 8 | keine | 1 | aus |
| **7-Bit, gerade** · `9600-7-E-1` | 9.600 | 7 | gerade | 1 | aus |
| **RS485-Bus** · `500000-8-N-1` | 500.000 | 8 | keine | 1 | **an** |
| **High-Speed** · `3000000-8-N-1` | 3.000.000 | 8 | keine | 1 | aus |

---

## Parameter

**Baudrate**

| Baudrate (Bit/s) | Konstante | Code |
|---:|---|:--:|
| 300 | `UartBaud300` | `0x00` |
| 600 | `UartBaud600` | `0x01` |
| 1.200 | `UartBaud1200` | `0x02` |
| 2.400 | `UartBaud2400` | `0x03` |
| 4.800 | `UartBaud4800` | `0x04` |
| 9.600 | `UartBaud9600` | `0x05` |
| 19.200 | `UartBaud19200` | `0x06` |
| 38.400 | `UartBaud38400` | `0x07` |
| 115.200 | `UartBaud115200` | `0x08` |
| 230.400 | `UartBaud230400` | `0x09` |
| 500.000 | `UartBaud500000` | `0x0A` |
| 1.000.000 | `UartBaud1000000` | `0x0B` |
| 3.000.000 | `UartBaud3000000` | `0x0C` |
| 5.000.000 | `UartBaud5000000` | `0x0D` |

**Datenbits**

| Datenbits | Konstante | Wert |
|:--:|---|:--:|
| 7 | `UartData7` | `0x2000` |
| **8** | `UartData8` | `0x0000` |
| 9 | `UartData9` | `0x1000` |

**Parität**

| Parität | Konstante | Wert |
|---|---|:--:|
| keine | `UartParityNone` | `0x0000` |
| gerade | `UartParityEven` | `0x0400` |
| ungerade | `UartParityOdd` | `0x0800` |

**Stoppbits**

| Stoppbits | Konstante | Wert |
|:--:|---|:--:|
| 1 | `UartStopbits1` | `0x0000` |
| 1,5 | `UartStopbits15` | `0x0100` |
| 2 | `UartStopbits2` | `0x0200` |

**RS485**

| RS485 | Konstante |
|---|---|
| aus | *(Standard)* |
| an | `UartRS485` |

---

## 16-Bit-Konfigurationswort

Die Konfiguration wird über `cfg` mit dem Befehl **Config UART** (Code 25, nur im 16-Bit-Frame verfügbar) übertragen. Die Nutzdaten sind **ein 16-Bit-Wort** — zusammengesetzt durch **bitweise ODER-Verknüpfung** der Feldwerte:

| Bits | Feld | Werte |
|:--:|---|---|
| **15** | RS485 | aus `0x0000` · an `0x8000` |
| **12–14** | Datenbits | 8 `0x0000` · 9 `0x1000` · 7 `0x2000` |
| **10–11** | Parität | keine `0x0000` · gerade `0x0400` · ungerade `0x0800` |
| **8–9** | Stoppbits | 1 `0x0000` · 1,5 `0x0100` · 2 `0x0200` |
| **0–7** | Baudrate | Code aus obiger Tabelle |

**Beispiele:**

| Konfiguration | = Konfigwort |
|---|:--:|
| `115200-8-N-1` | **`0x0008`** |
| `9600-8-N-1` | **`0x0005`** |
| `9600-7-E-1` | **`0x2405`** |
| `500000-8-N-1` (RS485) | **`0x800A`** |
| `3000000-8-N-1` | **`0x000C`** |

### Übertragung: 4 Bytes für 16 Bit Daten

`Config UART` wird mit **Code 25** im **16-Bit-Frame** übertragen. Dieser Frame ist **4 Bytes** lang, obwohl Kommandocode (6 Bit) und Konfigwort (16 Bit) zusammen nur 22 Bit Nutzinhalt ergeben – der Rest sind feste **Kennungsbits**, die den Frame selbstsynchronisierend machen: jedes Byte beginnt entweder mit `1110` (Lead-Byte, einmalig) oder `10` (Folge-Byte, 3×).

```
Byte 0:  1 1 1 0 │ C5 C4 C3 C2
Byte 1:  1 0      │ C1 C0 D15 D14 D13 D12
Byte 2:  1 0      │ D11 D10 D9 D8 D7 D6
Byte 3:  1 0      │ D5 D4 D3 D2 D1 D0
```

- **C5…C0** = Kommandocode (6 Bit) → hier **25** = `011001`
- **D15…D0** = Konfigwort (16 Bit) → z. B. `0x0008` = `0000 0000 0000 1000`

### Aufbau per Shift & Maske

Statt Bit für Bit lässt sich jedes Byte direkt per **Shift (`>>`)** und **Maske (`&`)** aus `Code` und `Wort` berechnen:

```
Byte0 = 0xE0 | (Code >> 2)                    // Lead-Byte:    1110 + obere 4 Bit des Codes
Byte1 = 0x80 | ((Code & 0x03) << 4)           // Folge-Byte 1: untere 2 Bit des Codes
              | (Wort >> 12)                  //             + obere 4 Bit der Daten (15–12)
Byte2 = 0x80 | ((Wort >> 6) & 0x3F)           // Folge-Byte 2: mittlere 6 Bit der Daten (11–6)
Byte3 = 0x80 | (Wort & 0x3F)                  // Folge-Byte 3: untere 6 Bit der Daten (5–0)
```

- `0xE0` = `1110 0000` → Lead-Byte-Kennung
- `0x80` = `1000 0000` → Folge-Byte-Kennung
- `0x03` = untere **2 Bit** maskieren (Rest des Codes)
- `0x3F` = untere **6 Bit** maskieren (ein Daten-Häppchen)

**Eingesetzt für `115200-8-N-1`** (`Code = 25`, `Wort = 0x0008`):

```
Byte0 = 0xE0 | (25 >> 2)                       = 0xE0 | 0x06        = 0xE6
Byte1 = 0x80 | ((25 & 0x03) << 4) | (0x0008 >> 12)
      = 0x80 | (1 << 4)           | 0x00       = 0x80 | 0x10 | 0x00 = 0x90
Byte2 = 0x80 | ((0x0008 >> 6) & 0x3F)           = 0x80 | 0x00        = 0x80
Byte3 = 0x80 | (0x0008 & 0x3F)                  = 0x80 | 0x08        = 0x88
```

→ Vollständiges Frame: **`E6 90 80 88`**

Der Empfänger kehrt die Formeln um: `Code = ((Byte0 & 0x0F) << 2) | ((Byte1 >> 4) & 0x03)`, `Wort = ((Byte1 & 0x0F) << 12) | ((Byte2 & 0x3F) << 6) | (Byte3 & 0x3F)`. Aus `Code = 25` (Config UART) und `Wort = 0x0008` lassen sich dann die Baudrate-/Datenbits-/Paritäts-/Stoppbits-Tabellen von oben rückwärts anwenden.

---

## Querverweise

- Transport & Subtopics: [[MQTT & NATS]]
- Übersicht: [[P4-IO-Jacks Interfaces]]
