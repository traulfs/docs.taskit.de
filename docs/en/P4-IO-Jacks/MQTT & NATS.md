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
---

# P4-IO-Jacks — Transport via MQTT & NATS

The IO jacks are addressed via **NATS** and **MQTT**. Both use the four-part scheme **Module → Jack → Interface → Direction**:

| Transport | Separator | Scheme                                  |
| --------- | :-----: | --------------------------------------- |
| **NATS**  |   `.`   | `ModuleSubject.Jack.Interface.Direction` |
| **MQTT**  |   `/`   | `ModuleTopic/Jack/Interface/Direction`   |

**Direction:** `r` = subscribe (*input byte stream*) · `w` = publish (*output byte stream*)

**Example** – module `gpio_abcdef123456`, jack 0, reading UART:

```
NATS:  gpio_abcdef123456.0.uart.r
MQTT:  gpio_abcdef123456/0/uart/r
```

- **ModuleSubject / ModuleTopic** = module ID, e.g. `gpio_abcdef123456` (`gpio_` + MAC identifier).
- **Jack** = `0 … 3` (which of the four IO jacks, see [[P4-IO-Jacks Interfaces]]).
- **Interface** = operating mode / channel:

| Interface | Meaning |
|---|---|
| `port` | Digital I/O (4 bit) → [[PORT Mode]] |
| `i2c` | I²C transfers → [[I2C Read & Write]] |
| `uart` | serial payload data → [[UART Mode]] |
| `spi` | SPI data stream |
| `adc` | Analog input (**IO-Jack 0 only**, ADC0–ADC3) |
| `cfg` | **Configuration** of the respective jack (Port-8 encoded) |

---

## Byte Stream Content

What is carried in the byte stream depends on the interface – **not** every interface uses Port-8:

| Interface | Stream content |
|---|---|
| `port` | **Port-8 encoded** – 4-bit read/write ([[PORT Mode]]) |
| `cfg` | Configuration of the jack (e.g. mode switching, UART settings) |
| `uart` | raw UART payload data (bytes, **not** Port-8) → [[UART Mode]] |
| `i2c` | length-prefixed I²C protocol (**not** Port-8) → [[I2C Read & Write]] |
| `spi` | SPI data stream |
| `adc` | Analog values |

- **Directions:**
  - *Output byte stream* (publish / write): data or commands **to** the module.
  - *Input byte stream* (subscribe / read): data, responses & events **from** the module.

---

## Cross References

- Protocol: [[taskit port-8]]
- Modes: [[PORT Mode]] · [[UART Mode]] · [[I2C Read & Write]]
- Overview: [[P4-IO-Jacks Interfaces]]
