---
tags:
  - p4-io-jacks
  - gpio
  - reference
erstellt: 2026-06-17
status: description
---

# P4-IO-Jacks — Interfaces (Overview)

> Overview of the four IO jacks and their operating modes.

---

## Overview

The P4 module provides **four IO jacks** (physical connectors): **IO-Jack 0 – IO-Jack 3**. Each jack supports four operating modes — the **most recently used interface access** determines the active mode:

| Mode     | Purpose                                                       |
| -------- | ------------------------------------------------------------ |
| **PORT** | Digital I/O with 4 bit (Pin0–Pin3)                            |
| **I²C**  | I²C master, read/write via tunneled byte streams              |
| **UART** | Serial interface, configurable (baud rate, parity, …)         |
| **SPI**  | SPI interface (configuration TBD)                              |

The four **ADC channels ADC0 – ADC3** are located **exclusively on IO-Jack 0**. The remaining jacks (1–3) have no ADC.

### Jack/Mode Matrix

| IO-Jack | PORT | I²C | UART | SPI | ADC |
|:--:|:--:|:--:|:--:|:--:|:--:|
| **IO-Jack 0** | ✓ | ✓ | ✓ | ✓ | **ADC0–ADC3** |
| **IO-Jack 1** | ✓ | ✓ | ✓ | ✓ | – |
| **IO-Jack 2** | ✓ | ✓ | ✓ | ✓ | – |
| **IO-Jack 3** | ✓ | ✓ | ✓ | ✓ | – |

> Each jack can only have **one** mode active at a time. The four ADC channels are available **only on IO-Jack 0**.

---

## Analog (ADC/DAC)

The four ADC channels (on IO-Jack 0) are addressed via the Ext-3 commands:

| Code | Command | Function |
|:--:|---|---|
| `40` | AnalogSetMode | ADC/DAC configuration (mode + 4-bit pad no.) |
| `41` | AnalogValue | Read/write analog value (+ 4-bit pad no.) |

## Addressing

- **Jack selection** happens in the transport address (MQTT topic / NATS subject): `…/<Jack>/<Interface>`, e.g. `…/0/uart`.
- **Pin/pad selection** within a jack via a PAD mask (4 bit) or a direct PAD address.

---

## Cross References

- Modes: [[PORT Mode]] · [[UART Mode]] · [[I2C Read & Write]]
- Transport: [[MQTT & NATS]]
