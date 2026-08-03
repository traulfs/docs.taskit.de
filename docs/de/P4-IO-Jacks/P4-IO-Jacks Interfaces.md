---
tags:
  - p4-io-jacks
  - gpio
  - referenz
erstellt: 2026-06-17
status: beschreibung
---

# P4-IO-Jacks — Interfaces (Übersicht)

> Übersicht der vier IO-Jacks und ihrer Betriebsmodi.

---

## Überblick

Das P4-Modul stellt **vier IO-Jacks** (physische Anschlüsse) bereit: **IO-Jack 0 – IO-Jack 3**. Jeder Jack unterstützt vier Betriebsmodi — der **zuletzt genutzte Interface-Zugriff** bestimmt den aktiven Modus:

| Modus    | Zweck                                                        |
| -------- | ------------------------------------------------------------ |
| **PORT** | Digitale Ein-/Ausgabe von 4 Bit (Pin0–Pin3)                  |
| **I²C**  | I²C-Master, Read/Write über getunnelte Byte-Streams          |
| **UART** | Serielle Schnittstelle, konfigurierbar (Baudrate, Parität …) |
| **SPI**  | SPI-Schnittstelle (Konfiguration TBD)                        |

Die vier **ADC-Kanäle ADC0 – ADC3** liegen **ausschließlich an IO-Jack 0**. Die übrigen Jacks (1–3) haben keinen ADC.

### Jack-/Modus-Matrix

| IO-Jack | PORT | I²C | UART | SPI | ADC |
|:--:|:--:|:--:|:--:|:--:|:--:|
| **IO-Jack 0** | ✓ | ✓ | ✓ | ✓ | **ADC0–ADC3** |
| **IO-Jack 1** | ✓ | ✓ | ✓ | ✓ | – |
| **IO-Jack 2** | ✓ | ✓ | ✓ | ✓ | – |
| **IO-Jack 3** | ✓ | ✓ | ✓ | ✓ | – |

> Jeder Jack kann **immer nur einen** Modus gleichzeitig aktiv haben. Die vier ADC-Kanäle stehen **nur an IO-Jack 0** zur Verfügung.

---

## Analog (ADC/DAC)

Die vier ADC-Kanäle (an IO-Jack 0) werden über die Ext-3-Befehle angesprochen:

| Code | Befehl | Funktion |
|:--:|---|---|
| `40` | AnalogSetMode | ADC/DAC-Konfiguration (Mode + 4-Bit PadNr) |
| `41` | AnalogValue | Analog-Wert lesen/schreiben (+ 4-Bit PadNr) |

## Adressierung

- **Jack-Auswahl** erfolgt in der Transport-Adresse (MQTT-Topic / NATS-Subject): `…/<Jack>/<Interface>`, z. B. `…/0/uart`.
- **Pin-/Pad-Auswahl** innerhalb eines Jacks über PAD-Maske (4 Bit) oder direkte PAD-Adresse.

---

## Querverweise

- Modi: [[PORT Mode]] · [[UART Mode]] · [[I2C Read & Write]]
- Transport: [[MQTT & NATS]]
