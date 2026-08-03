---
tags:
  - projekt
  - taskit
  - iot
  - sensor
quelle: https://www.taskit.de/produkte/sensor-netzwerke/info-zu-measure2go/
erstellt: 2026-04-30
---

# Measure2Go

**Measure2Go** ist ein drahtloses Sensornetzwerk-System der taskit GmbH (Berlin). Es wandelt kabelgebundene Sensoren in 2,4-GHz-Funkgeräte um und ermöglicht lokale sowie ferngesteuerte Messungen mit Datensicherheit und Internetauthentizität.

## Übersicht

Das System bietet eine vollständige Infrastruktur für hunderte drahtlos verbundener Sensoren, inklusive:
- **Gateways** zum Datentransport (auch Cellular-BLE)
- **Edge-Geräte** auf Basis des Raspberry Pi CM4 Moduls
- **Cloud-Anbindung** (measure2go.taskit.de) – out of the box, nur Stromversorgung nötig
- **Apps** für Android & iOS zur Sensorkonfiguration und Kalibrierung

---

## Produkte

### BlueRTD
- Temperaturmessgerät für PT100/PT1000-Sonden
- Übertragung via 2,4-GHz-Funk
- Temperaturbereich: **-200 bis 600 °C** (je nach Sensor)
- Genauigkeit: ±0,5 °C

### Blue pH-Meter
- Drahtlose pH-Messung
- Übertragung via 2,4 GHz

### BlueLoopRx
- Wandelt jeden Sensor mit Loop-Speisung in ein Funkgerät um

### BlueLoopTx
- Macht Aktoren über ein einzelnes Kabel funkfähig

### Sensor Gateway Cellular-BLE
- Gateway mit Mobilfunk (Cellular) und Bluetooth Low Energy
- Vorkonfiguriert für Measure2Go Cloud

---

## Technische Details

| Merkmal | Wert |
|---|---|
| Funk | 2,4 GHz |
| Temperaturbereich | -200 bis 600 °C |
| Batterielaufzeit | Bis zu 2 Jahre (abhängig von Abtastrate) |
| Edge-Plattform | Raspberry Pi CM4 |
| App | Android & iOS |
| Cloud | measure2go.taskit.de |

---

## Anwendungsfälle

- Industrielle Temperaturüberwachung
- pH-Überwachung in Produktionsprozessen
- Drahtlose Integration bestehender (kabelgebundener) Sensoren
- Aufbau großer Sensornetzwerke (hunderte Knoten)

---

## Verwandte Notizen

- [[TSB]] – Tiny Serial Bus: Go-Bibliothek & Protokoll-Referenz
- [[TSB - Architektur (Mermaid)]] – Architektur-Diagramm (Mermaid) + Redesign-Konzept
- [[TSB - Architektur.excalidraw]] – Visuelle Architektur-Übersicht
- [[SenML Units]] – Einheiten-Kodierung für Sensor-Payloads
- [[IEEE 754 Float 32-Bit]] – Fließkomma-Format für Messwerte
- [[taskit port-8]] – 8-Port-Hardware-Plattform

---

## Links

- [Info zu Measure2Go – taskit.de](https://www.taskit.de/produkte/sensor-netzwerke/info-zu-measure2go/)
- [Measure2Go (English) – taskit.de](https://taskit.de/en/products/sensor-networks/measure2go/)
- [Measure2Go Shop](https://measure2go.taskit.de/products/measure2go-sensor-group)
- [Gateway Cellular-BLE](https://www.taskit.de/en/products/gateways/iot-gateways/66/gateway-cellular-ble)
- [Sensor Netzwerke – taskit.de](https://www.taskit.de/produkte/sensor-netzwerke/)

---

## Kontakt

taskit GmbH, Berlin  
Tel.: +49 (0) 30 611 295 - 0
