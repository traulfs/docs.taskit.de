---
tags:
  - p4-io-jacks
  - gpio
  - reference
erstellt: 2026-06-17
status: description
description: "Übersicht der vier IO-Jacks des P4-Moduls und ihrer Betriebsmodi PORT, I²C, UART, SPI und ADC, mit Jack/Modus-Matrix und Adressierung."
---

# P4-IO-Jacks – Schnittstellen (Übersicht)

> Übersicht der vier IO-Jacks und ihrer Betriebsmodi.

---

## Übersicht

Das P4-Modul hat **vier IO-Jacks** (physische Anschlüsse): **IO-Jack 0 – IO-Jack 3**. Jeder Jack unterstützt vier Betriebsmodi – der **zuletzt verwendete Schnittstellenzugriff** bestimmt den aktiven Modus:

| Modus    | Zweck                                                                         |
| -------- | ----------------------------------------------------------------------------- |
| **PORT** | Digitale I/O mit 4 Bit (Pin0–Pin3) und Konfiguration der anderen Schnittstellen, |
|          | immer mit dem taskit-Port-8-Protokoll                                         |
| **I²C**  | I²C-Master, Lesen/Schreiben über getunnelte Byteströme                        |
| **UART** | Serielle Schnittstelle, konfigurierbar (Baudrate, Parität, …)                 |
| **SPI**  | SPI-Schnittstelle (Konfiguration noch offen)                                  |
| **ADC**. | ADC-Schnittstelle (Konfiguration noch offen)                                  |

Die vier **ADC-Kanäle ADC0 – ADC3** liegen **ausschließlich an IO-Jack 0**. Die übrigen Jacks (1–3) haben keinen ADC.

### Jack/Modus-Matrix

| IO-Jack | PORT | I²C | UART | SPI | ADC |
|:--:|:--:|:--:|:--:|:--:|:--:|
| **IO-Jack 0** | ✓ | ✓ | ✓ | ✓ | **ADC0–ADC3** |
| **IO-Jack 1** | ✓ | ✓ | ✓ | ✓ | – |
| **IO-Jack 2** | ✓ | ✓ | ✓ | ✓ | – |
| **IO-Jack 3** | ✓ | ✓ | ✓ | ✓ | – |

> Jeder Jack kann jeweils nur **einen** aktiven Modus haben. Die vier ADC-Kanäle stehen **nur an IO-Jack 0** zur Verfügung.

---

## Analog (ADC/DAC)

Die vier ADC-Kanäle (an IO-Jack 0) werden über die Ext-3-Befehle angesprochen:

| Code | Befehl | Funktion |
|:--:|---|---|
| `40` | AnalogSetMode | ADC/DAC-Konfiguration (Modus + 4-Bit-Pad-Nr.) |
| `41` | AnalogValue | Analogwert lesen/schreiben (+ 4-Bit-Pad-Nr.) |

## Adressierung

- Die **Jack-Auswahl** erfolgt in der Transportadresse (MQTT-Topic / NATS-Subject): `…/<Jack>/<Interface>`, z. B. `…/0/uart`.
- Die **Pin-/Pad-Auswahl** innerhalb eines Jacks erfolgt über eine PAD-Maske (4 Bit) oder eine direkte PAD-Adresse.

---

## Querverweise

- Modi: [[PORT Mode|PORT-Modus]] · [[UART Mode|UART-Modus]] · [[I2C Read & Write|I²C Lesen & Schreiben]]
- Transport: [[MQTT & NATS]]
- Konfiguration über HTTP: [[gpio.net/API.md|HTTP-REST-API]]
- Verfügbare Sensoren/Karten: [[IO-Nuts & Cards]]
