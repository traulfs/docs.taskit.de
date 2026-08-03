---
tags:
  - taskit
  - p4-io-jacks
  - mqtt
  - nats
  - port-8
  - transport
erstellt: 2026-06-17
status: beschreibung
quelle_port8: "[[taskit port-8]]"
---

# P4-IO-Jacks — Transport über MQTT & NATS

Die IO-Jacks werden über **NATS** und **MQTT** angesprochen. Beide nutzen das viergliedrige Schema **Modul → Jack → Interface → Direction**:

| Transport | Trenner | Schema                                  |
| --------- | :-----: | --------------------------------------- |
| **NATS**  |   `.`   | `ModulSubject.Jack.Interface.Direction` |
| **MQTT**  |   `/`   | `ModulTopic/Jack/Interface/Direction`   |

**Richtung:** `r` = Subscribe (*Input Byte Stream*) · `w` = Publish (*Output Byte Stream*)

**Beispiel** – Modul `gpio_abcdef123456`, Jack 0, UART lesen:

```
NATS:  gpio_abcdef123456.0.uart.r
MQTT:  gpio_abcdef123456/0/uart/r
```

- **ModulSubject / ModulTopic** = Modul-ID, z. B. `gpio_abcdef123456` (`gpio_` + MAC-Kennung).
- **Jack** = `0 … 3` (welcher der vier IO-Jacks, siehe [[P4-IO-Jacks Interfaces]]).
- **Interface** = Betriebsmodus / Kanal:

| Interface | Bedeutung |
|---|---|
| `port` | Digital-I/O (4 Bit) → [[PORT Mode]] |
| `i2c` | I²C-Transfers → [[I2C Read & Write]] |
| `uart` | serielle Nutzdaten → [[UART Mode]] |
| `spi` | SPI-Datenstrom |
| `adc` | Analog-Eingang (**nur IO-Jack 0**, ADC0–ADC3) |
| `cfg` | **Konfiguration** des jeweiligen Jacks (Port-8-kodiert) |

---

## Inhalt des Byte-Streams

Was im Byte-Stream steht, hängt vom Interface ab – **nicht** jedes Interface nutzt Port-8:

| Interface | Stream-Inhalt |
|---|---|
| `port` | **Port-8-kodiert** – 4-Bit Read/Write ([[PORT Mode]]) |
| `cfg` | Konfiguration des Jacks (z. B. Modus-Umschaltung, UART-Einstellungen) |
| `uart` | rohe UART-Nutzdaten (Bytes, **kein** Port-8) → [[UART Mode]] |
| `i2c` | längenpräfixiertes I²C-Protokoll (**kein** Port-8) → [[I2C Read & Write]] |
| `spi` | SPI-Datenstrom |
| `adc` | Analog-Werte |

- **Richtungen:**
  - *Output Byte Stream* (Publish / Write): Daten bzw. Befehle **an** das Modul.
  - *Input Byte Stream* (Subscribe / Read): Daten, Antworten & Events **vom** Modul.

---

## Querverweise

- Protokoll: [[taskit port-8]]
- Modi: [[PORT Mode]] · [[UART Mode]] · [[I2C Read & Write]]
- Übersicht: [[P4-IO-Jacks Interfaces]]
