# docs.taskit.de

Technische Dokumentation der [taskit GmbH](https://www.taskit.de) (Berlin) zu Sensornetzwerken, BLE-Formaten und IO-Modulen.

## Inhalt

### [Measure2Go](docs/Measure2Go/)

Drahtloses Sensornetzwerk-System, das kabelgebundene Sensoren in 2,4-GHz-Funkgeräte umwandelt — mit Gateways, Edge-Geräten (Raspberry Pi CM4) und Cloud-Anbindung.

- [Measure2Go](docs/Measure2Go/Measure2Go.md) — Produkt- und Systemübersicht
- [TSB](docs/Measure2Go/TSB.md) — Taskit Sensor Bus, mit Architekturdiagrammen ([Excalidraw](docs/Measure2Go/TSB%20-%20Architektur.excalidraw.md), [Mermaid](docs/Measure2Go/TSB%20-%20Architektur%20(Mermaid).md))
- [taskit port-8](docs/Measure2Go/taskit%20port-8.md) — Port-8-Protokoll
- [SenML Units](docs/Measure2Go/SenML%20Units.md) — Einheiten-Referenz
- Grundlagen: [IEEE 754 Float 32-Bit](docs/Measure2Go/IEEE%20754%20Float%2032-Bit.md), [UTF-8 Kodierung](docs/Measure2Go/UTF-8%20Kodierung.md)

### [BLE](docs/BLE/)

Bluetooth-Low-Energy-Advertisement-Formate verschiedener Hersteller.

- [BLE Advertisement Format](docs/BLE/BLE%20Advertisement%20Format.md) — allgemeines Format
- [taskit BLE Manufacturer Advertisement](docs/BLE/taskit%20BLE%20Manufacturer%20Advertisement.md)
- Hersteller-Formate: [Ruuvi RuuviTag](docs/BLE/ruuvi_ruuvitag_ble_format.md), [MokoSmart H4/P5202DH2](docs/BLE/mokosmart_h4_p5202dh2_ble_format.md), [MokoSmart S02R (ToF)](docs/BLE/mokosmart_s02r_tof_ble_format.md), [MokoSmart S03D (Tür)](docs/BLE/mokosmart_s03d_door_ble_format.md)

### [BEACON-LINE](docs/BEACON-LINE/)

BLE-Scanning-System mit BlineServer.

- Advertisement-Ausgabe in [JSON](docs/BEACON-LINE/BEACON-LINE%20Advertisement%20in%20JSON%20Format.md)- und [CSV](docs/BEACON-LINE/BEACON-LINE%20Advertisement%20in%20CSV%20Format.md)-Format
- [Benutzerverwaltung Konzept](docs/BEACON-LINE/Benutzerverwaltung%20Konzept.md) — cloudbasierte Benutzerverwaltung mit Supabase
- Architekturdiagramme (Excalidraw): [Decoding](docs/BEACON-LINE/BEACON-LINE%20Decoding.excalidraw.md), [Scanning Standalone](docs/BEACON-LINE/BEACON-LINE%20Scanning%20Standalone.excalidraw.md), [mit BlineServer](docs/BEACON-LINE/BEACON-LINE%20with%20BlineServer.excalidraw.md)

### [P4-IO-Jacks](docs/P4-IO-Jacks/)

Die vier IO-Jacks des P4-Moduls und ihre Betriebsmodi.

- [Interfaces (Übersicht)](docs/P4-IO-Jacks/P4-IO-Jacks%20Interfaces.md)
- Betriebsmodi: [PORT](docs/P4-IO-Jacks/PORT%20Mode.md), [I²C Read & Write](docs/P4-IO-Jacks/I2C%20Read%20%26%20Write.md), [UART](docs/P4-IO-Jacks/UART%20Mode.md)
- [MQTT & NATS](docs/P4-IO-Jacks/MQTT%20%26%20NATS.md) — Messaging-Anbindung

## Hinweise

- Die Dokumente sind als [Obsidian](https://obsidian.md)-Vault gepflegt; `.excalidraw.md`-Dateien benötigen das [Excalidraw-Plugin](https://github.com/zsviczian/obsidian-excalidraw-plugin) zur Bearbeitung.
- Diagramme im Mermaid-Format werden direkt auf GitHub gerendert.
