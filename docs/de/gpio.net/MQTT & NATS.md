---
tags:
  - taskit
  - p4-io-jacks
  - mqtt
  - nats
  - port-8
  - transport
erstellt: 2026-06-17
status: description
quelle_port8: "[[taskit port-8]]"
description: "Adressierung der P4-IO-Jacks über MQTT-Topics und NATS-Subjects (Modul, Jack, Interface, Richtung) und Inhalt des Bytestroms je Schnittstelle."
---

# P4-IO-Jacks – Transport über MQTT & NATS

Die IO-Jacks werden über **NATS** und **MQTT** angesprochen. Beide verwenden das vierteilige Schema **Modul → Jack → Interface → Richtung**:

| Transport | Trennzeichen | Schema                                  |
| --------- | :-----: | --------------------------------------- |
| **NATS**  |   `.`   | `ModuleSubject.Jack.Interface.Direction` |
| **MQTT**  |   `/`   | `ModuleTopic/Jack/Interface/Direction`   |

**Richtung (Direction):** `r` = abonnieren (*Eingangsbytestrom*) · `w` = veröffentlichen (*Ausgangsbytestrom*)

**Beispiel** – Modul `gpio_abcdef123456`, Jack 0, UART lesen:

```
NATS:  gpio_abcdef123456.0.uart.r
MQTT:  gpio_abcdef123456/0/uart/r
```

- **ModuleSubject / ModuleTopic** = Modul-ID, z. B. `gpio_abcdef123456` (`gpio_` + MAC-Kennung).
- **Jack** = `0 … 3` (welcher der vier IO-Jacks, siehe [[P4-IO-Jacks Interfaces|P4-IO-Jacks – Schnittstellen]]).
- **Interface** = Betriebsmodus / Kanal:

| Interface | Bedeutung |
|---|---|
| `port` | Digitale I/O (4 Bit) → [[PORT Mode|PORT-Modus]] |
| `i2c` | I²C-Übertragungen → [[I2C Read & Write|I²C Lesen & Schreiben]] |
| `uart` | serielle Nutzdaten → [[UART Mode|UART-Modus]] |
| `spi` | SPI-Datenstrom |
| `adc` | Analogeingang (**nur IO-Jack 0**, ADC0–ADC3) |

---

## Inhalt des Bytestroms

Was im Bytestrom übertragen wird, hängt von der Schnittstelle ab – **nicht** jede Schnittstelle verwendet Port-8:

| Interface | Inhalt des Stroms |
|---|---|
| `port` | **Port-8-kodiert** – 4 Bit lesen/schreiben ([[PORT Mode|PORT-Modus]]) |
| `uart` | rohe UART-Nutzdaten (Bytes, **nicht** Port-8) → [[UART Mode|UART-Modus]] |
| `i2c` | längenpräfixiertes I²C-Protokoll (**nicht** Port-8) → [[I2C Read & Write|I²C Lesen & Schreiben]] |
| `spi` | SPI-Datenstrom |
| `adc` | Analogwerte |

- **Richtungen:**
  - *Ausgangsbytestrom* (Publish / Schreiben): Daten oder Befehle **an** das Modul.
  - *Eingangsbytestrom* (Subscribe / Lesen): Daten, Antworten & Ereignisse **vom** Modul.

---

## Querverweise

- Protokoll: [[taskit port-8|taskit Port-8]]
- Modi: [[PORT Mode|PORT-Modus]] · [[UART Mode|UART-Modus]] · [[I2C Read & Write|I²C Lesen & Schreiben]]
- Übersicht: [[P4-IO-Jacks Interfaces|P4-IO-Jacks – Schnittstellen]]
