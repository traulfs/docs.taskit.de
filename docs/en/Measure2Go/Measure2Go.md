---
tags:
  - project
  - taskit
  - iot
  - sensor
quelle: https://www.taskit.de/en/products/sensor-networks/measure2go/
erstellt: 2026-04-30
---

# Measure2Go

**Measure2Go** is a wireless sensor network system by taskit GmbH (Berlin). It converts wired sensors into 2.4 GHz radio devices, enabling local and remote measurements with data security and internet authenticity.

## Overview

The system provides a complete infrastructure for hundreds of wirelessly connected sensors, including:
- **Gateways** for data transport (including Cellular-BLE)
- **Edge devices** based on the Raspberry Pi CM4 module
- **Cloud connectivity** (measure2go.taskit.de) – out of the box, only power supply required
- **Apps** for Android & iOS for sensor configuration and calibration

---

## Products

### BlueRTD
- Temperature measuring device for PT100/PT1000 probes
- Transmission via 2.4 GHz radio
- Temperature range: **-200 to 600 °C** (depending on sensor)
- Accuracy: ±0.5 °C

### Blue pH-Meter
- Wireless pH measurement
- Transmission via 2.4 GHz

### BlueLoopRx
- Converts any loop-powered sensor into a radio device

### BlueLoopTx
- Makes actuators wireless-capable via a single cable

### Sensor Gateway Cellular-BLE
- Gateway with cellular and Bluetooth Low Energy
- Pre-configured for the Measure2Go Cloud

---

## Technical Details

| Feature | Value |
|---|---|
| Radio | 2.4 GHz |
| Temperature range | -200 to 600 °C |
| Battery life | Up to 2 years (depending on sampling rate) |
| Edge platform | Raspberry Pi CM4 |
| App | Android & iOS |
| Cloud | measure2go.taskit.de |

---

## Use Cases

- Industrial temperature monitoring
- pH monitoring in production processes
- Wireless integration of existing (wired) sensors
- Building large sensor networks (hundreds of nodes)

---

## Related Notes

- [[TSB]] – Tiny Serial Bus: Go library & protocol reference
- [[TSB - Architektur (Mermaid)]] – Architecture diagram (Mermaid) + redesign concept
- [[TSB - Architektur.excalidraw]] – Visual architecture overview
- [[SenML Units]] – Unit encoding for sensor payloads
- [[IEEE 754 Float 32-Bit]] – Floating-point format for measured values
- [[taskit port-8]] – 8-port hardware platform

---

## Links

- [Measure2Go info – taskit.de](https://www.taskit.de/en/products/sensor-networks/measure2go/)
- [Measure2Go (Deutsch) – taskit.de](https://www.taskit.de/produkte/sensor-netzwerke/info-zu-measure2go/)
- [Measure2Go Shop](https://measure2go.taskit.de/products/measure2go-sensor-group)
- [Gateway Cellular-BLE](https://www.taskit.de/en/products/gateways/iot-gateways/66/gateway-cellular-ble)
- [Sensor Networks – taskit.de](https://www.taskit.de/en/products/sensor-networks/)

---

## Contact

taskit GmbH, Berlin
Phone: +49 (0) 30 611 295 - 0
