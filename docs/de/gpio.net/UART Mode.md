---
tags:
  - p4-io-jacks
  - uart
  - uart-mode
erstellt: 2026-06-17
status: description
description: "IO-Jack im UART-Modus: Baudrate (300 bit/s bis 5 Mbit/s), Datenbits, Parität, Stoppbits und RS485 konfigurieren, dann rohe UART-Bytes senden und empfangen."
---

# IO-Jack – UART-Modus

> IO-Jack im UART-Modus – serielle Schnittstelle mit Konfiguration über `cfg` und Datenübertragung über `uart`.

---

## Funktionsweise

Im **UART-Modus** arbeitet ein IO-Jack als serielle Schnittstelle mit zwei Subtopics:

| Subtopic | Zweck |
|---|---|
| **`port`** | UART-Einstellungen setzen |
| **`uart`** | Rohe UART-Datenbytes senden / empfangen |

---

## Konfiguration (`port`)

Die Schnittstelle wird vor der Datenübertragung mit fünf Parametern konfiguriert. Kurzform: `Baudrate-Databits-Parity-Stopbits` (N = keine, E = gerade, O = ungerade):

| Konfiguration | Baudrate | Datenbits | Parität | Stoppbits | RS485 |
|---|--:|:--:|---|:--:|:--:|
| **Standard** · `115200-8-N-1` | 115.200 | 8 | keine | 1 | aus |
| **Klassisch** · `9600-8-N-1` | 9.600 | 8 | keine | 1 | aus |
| **7 Bit, gerade** · `9600-7-E-1` | 9.600 | 7 | gerade | 1 | aus |
| **RS485-Bus** · `500000-8-N-1` | 500.000 | 8 | keine | 1 | **ein** |
| **High Speed** · `3000000-8-N-1` | 3.000.000 | 8 | keine | 1 | aus |

---

## Parameter

**Baudrate**

| Baudrate (bit/s) | Konstante | Code |
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
| ein | `UartRS485` |

**Uart Rx**

| RS485 | Konstante |
|---|---|
| ein | *(Standard)* |
| aus | `Uart Receive off` |

---

## 16-Bit-Konfigurationswort

Die Konfiguration wird über `cfg` mit dem Befehl **Config UART** übertragen (Code 25, nur im 16-Bit-Frame verfügbar). Die Payload ist **ein 16-Bit-Wort** – zusammengesetzt durch **bitweises ODER** der Feldwerte:

| Bits | Feld | Werte |
|:--:|---|---|
| **15**    | Uart RX   | aus `0x8000` · ein `0x0000` |
| **14**    | RS485     | aus `0x0000` · ein `0x4000` |
| **12–13** | Datenbits | 8 `0x0000` · 9 `0x1000` · 7 `0x2000` |
| **10–11** | Parität   | keine `0x0000` · gerade `0x0400` · ungerade `0x0c00` |
| **7–8**   | Stoppbits | 1 `0x0000` · 1,5 `0x0100` · 2 `0x0200` |
| **0–7**   | Baudrate  | Code aus der Tabelle oben |

**Beispiele:**

| Konfiguration | = Konfigurationswort |
|---|:--:|
| `115200-8-N-1` | **`0x0008`** |
| `9600-8-N-1` | **`0x0005`** |
| `9600-7-E-1` | **`0x2405`** |
| `500000-8-N-1` (RS485) | **`0x800A`** |
| `3000000-8-N-1` | **`0x000C`** |

### Übertragung: 4 Bytes für 16 Bit Daten

`Config UART` wird mit **Code 25** im **16-Bit-Frame** übertragen. Dieser Frame ist **4 Bytes** lang, obwohl Befehlscode (6 Bit) und Konfigurationswort (16 Bit) zusammen nur 22 Bit Nutzdaten ergeben – der Rest sind feste **Kennungsbits**, die den Frame selbstsynchronisierend machen: Jedes Byte beginnt entweder mit `1110` (Lead-Byte, einmal) oder mit `10` (Folgebyte, 3×).

```
Byte 0:  1 1 1 0  │ C5 C4 C3 C2
Byte 1:  1 0      │ C1 C0 D15 D14 D13 D12
Byte 2:  1 0      │ D11 D10 D9 D8 D7 D6
Byte 3:  1 0      │ D5 D4 D3 D2 D1 D0
```

- **C5…C0** = Befehlscode (6 Bit) → hier **25** = `011001`
- **D15…D0** = Konfigurationswort (16 Bit) → z. B. `0x0008` = `0000 0000 0000 1000`

### Aufbau per Shift & Maske

Statt Bit für Bit lässt sich jedes Byte mit **Shift (`>>`)** und **Maske (`&`)** direkt aus `Code` und `Word` berechnen:

```
Byte0 = 0xE0 | (Code >> 2)                    // Lead byte:      1110 + upper 4 bits of the code
Byte1 = 0x80 | ((Code & 0x03) << 4)           // Continuation 1: lower 2 bits of the code
             | (Word >> 12)                  //               + upper 4 bits of the data (15–12)
Byte2 = 0x80 | ((Word >> 6) & 0x3F)           // Continuation 2: middle 6 bits of the data (11–6)
Byte3 = 0x80 | (Word & 0x3F)                  // Continuation 3: lower 6 bits of the data (5–0)
```

- `0xE0` = `1110 0000` → Kennung des Lead-Bytes
- `0x80` = `1000 0000` → Kennung des Folgebytes
- `0x03` = maskiert die unteren **2 Bits** (Rest des Codes)
- `0x3F` = maskiert die unteren **6 Bits** (ein Datenblock)

**Angewendet auf `115200-8-N-1`** (`Code = 25`, `Word = 0x0008`):

```
Byte0 = 0xE0 | (25 >> 2)                       = 0xE0 | 0x06        = 0xE6
Byte1 = 0x80 | ((25 & 0x03) << 4) | (0x0008 >> 12)
      = 0x80 | (1 << 4)           | 0x00       = 0x80 | 0x10 | 0x00 = 0x90
Byte2 = 0x80 | ((0x0008 >> 6) & 0x3F)           = 0x80 | 0x00        = 0x80
Byte3 = 0x80 | (0x0008 & 0x3F)                  = 0x80 | 0x08        = 0x88
```

→ Vollständiger Frame: **`E6 90 80 88`**

Der Empfänger kehrt die Formeln um: `Code = ((Byte0 & 0x0F) << 2) | ((Byte1 >> 4) & 0x03)`, `Word = ((Byte1 & 0x0F) << 12) | ((Byte2 & 0x3F) << 6) | (Byte3 & 0x3F)`. Aus `Code = 25` (Config UART) und `Word = 0x0008` lassen sich dann die Tabellen für Baudrate/Datenbits/Parität/Stoppbits oben rückwärts anwenden.

---

## Querverweise

- Transport & Subtopics: [[MQTT & NATS]]
- Übersicht: [[P4-IO-Jacks Interfaces|P4-IO-Jacks – Schnittstellen]]
