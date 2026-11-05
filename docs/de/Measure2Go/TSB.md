---
description: "TSB (Tiny Serial Bus): Go-Bibliothek und Protokoll für Embedded-Systeme über UART oder TCP; COBS-Framing, CRC-16, Zugriff auf I2C, UART, GPIO und Modbus."
---

# TSB – Tiny Serial Bus

TSB ist eine Go-Bibliothek für die Kommunikation mit Embedded-Systemen über serielle Verbindungen (UART/serielle Schnittstelle) oder TCP-Netzwerke. Sie bietet ein einheitliches Protokoll-Framework, um Hardware-Schnittstellen wie I2C, UART, SPI und GPIO-Ports anzusprechen.

```
Module: github.com/traulfs/tsb
Go:     >= 1.20
```

---

## Inhaltsverzeichnis

1. [Protokollarchitektur](#protokollarchitektur)
2. [Server – Verbindungsaufbau](#server-verbindungsaufbau)
3. [I2C](#i2c)
4. [UART](#uart)
5. [GPIO-Port](#gpio-port)
6. [Modbus](#modbus)
7. [Core-API (tsb.go)](#core-api-tsbgo)

---

## Protokollarchitektur

Jedes TSB-Paket besteht aus vier Feldern:

| Feld      | Länge          | Bedeutung                                                         |
|-----------|----------------|-------------------------------------------------------------------|
| Channel   | variabel       | Routing-Adresse; bei Zwischenbytes ist Bit 7 gesetzt              |
| Type      | variabel       | Protokolltyp (0x00–0x7F)                                          |
| Payload   | 0–250 Bytes    | Nutzdaten                                                         |
| CRC-16    | 2 Bytes        | Prüfsumme über Channel + Type + Payload (little-endian)          |

Das vollständig kodierte Paket wird mit **COBS** (Consistent Overhead Byte Stuffing) gerahmt und mit einem `0x00`-Byte abgeschlossen.

### TsbData

```go
type TsbData struct {
    Ch      []byte // Channel
    Typ     []byte // Type
    Payload []byte // Payload (max. 250 bytes)
}
```

---

## Server – Verbindungsaufbau

Ein `Server` verwaltet bis zu **8 Jacks** (unabhängige Geräteanschlüsse) und leitet eingehende Pakete anhand von Jack-Nummer und Protokolltyp weiter.

### Konstruktoren

```go
// Serial connection
server, err := tsb.NewSerialServer("/dev/ttyUSB0", 115200)

// TCP connection
server, err := tsb.NewTcpServer("localhost:3001")
```

### Methoden

```go
server.Close()

// Register a callback for a specific jack and protocol type
server.SetCallback(jack byte, typ byte, f func(*TsbData))
```

### Jacks

Jeder Jack hat 128 nach Typ indizierte Byte-Kanäle. Eingehende Bytes werden automatisch an den passenden Kanal geliefert oder an einen registrierten Callback übergeben.

| Konstante     | Wert | Bedeutung                       |
|---------------|------|---------------------------------|
| `MaxJacks`    | 8    | Maximale Anzahl Jacks           |
| `JackModeReg` | 0x80 | Modusregister                   |
| `JackUartReg` | 0x82 | UART-Register                   |
| `JackPortReg` | 0x86 | Port-Register                   |
| `JackI2cReg`  | 0x88 | I2C-Register                    |

| Jack-Modus   | Wert |
|--------------|------|
| `JackPort`   | 1    |
| `JackI2c`    | 2    |
| `JackUart`   | 3    |
| `JackSpi`    | 4    |

---

## I2C

### Konstruktor

```go
i2c, err := tsb.NewI2c(adr uint8, jack byte, server *Server) (*I2C, error)
```

Setzt den Jack-Modus auf I2C und initialisiert die Slave-Adresse.

### Adresse setzen

```go
err = i2c.SetAdr(adr byte) error
```

### Rohdatenübertragung

```go
n, err := i2c.Write(buf []byte) (int, error)  // max. 127 bytes
n, err := i2c.Read(buf []byte)  (int, error)  // max. 127 bytes
```

### Registeroperationen

| Methode                                               | Beschreibung                           |
|-------------------------------------------------------|----------------------------------------|
| `ReadRegU8(reg) (byte, error)`                        | 8-Bit-Wert lesen                       |
| `WriteRegU8(reg, value) error`                        | 8-Bit-Wert schreiben                   |
| `ReadRegBytes(reg, n) ([]byte, int, error)`           | n Bytes ab Register lesen              |
| `ReadRegU16BE(reg) (uint16, error)`                   | 16 Bit big-endian lesen                |
| `WriteRegU16BE(reg, value) error`                     | 16 Bit big-endian schreiben            |
| `ReadRegU16LE(reg) (uint16, error)`                   | 16 Bit little-endian lesen             |
| `WriteRegU16LE(reg, value) error`                     | 16 Bit little-endian schreiben         |
| `ReadRegS16BE(reg) (int16, error)`                    | 16 Bit vorzeichenbehaftet BE lesen     |
| `WriteRegS16BE(reg, value) error`                     | 16 Bit vorzeichenbehaftet BE schreiben |
| `ReadRegS16LE(reg) (int16, error)`                    | 16 Bit vorzeichenbehaftet LE lesen     |
| `WriteRegS16LE(reg, value) error`                     | 16 Bit vorzeichenbehaftet LE schreiben |

### Beispiel

```go
server, _ := tsb.NewSerialServer("/dev/ttyUSB0", 115200)
defer server.Close()

i2c, _ := tsb.NewI2c(0x50, 5, server)

val, err := i2c.ReadRegU8(0x20)
err = i2c.WriteRegU16BE(0x24, 0x1234)
data, _, err := i2c.ReadRegBytes(0x30, 2)
```

---

## UART

### Konstruktor

```go
uart, err := tsb.NewUart(jack byte, server *Server) (*UART, error)
```

### Konfiguration

```go
err = uart.Config(rs485, baud, databits, parity, stopbits uint16) error
```

Die Parameter werden mit einem bitweisen ODER kombiniert:

**Baudrate:**

| Konstante          | Wert |
|--------------------|------|
| `UartBaudAuto`     | 0    |
| `UartBaud9600`     | –    |
| `UartBaud115200`   | –    |
| `UartBaud230400`   | –    |
| `UartBaud460800`   | –    |
| `UartBaud921600`   | –    |
| `UartBaud1000000`  | –    |
| `UartBaud3000000`  | –    |
| *(weitere)*        | –    |

**Stoppbits:**

| Konstante        | Wert   |
|------------------|--------|
| `UartStopbits1`  | 0x0000 |
| `UartStopbits15` | 0x0100 |
| `UartStopbits2`  | 0x0200 |

**Parität:**

| Konstante        | Wert   |
|------------------|--------|
| `UartParityNone` | 0x0000 |
| `UartParityEven` | 0x0400 |
| `UartParityOdd`  | 0x0800 |

**Datenbits:**

| Konstante    | Wert   |
|--------------|--------|
| `UartData8`  | 0x0000 |
| `UartData7`  | 0x2000 |
| `UartData6`  | 0x3000 |
| `UartData5`  | 0x4000 |
| `UartData9`  | 0x1000 |

**RS485:**

| Konstante   | Wert   |
|-------------|--------|
| `UartRS485` | 0x8000 |

### Datenübertragung

```go
n, err := uart.Write(b []byte) (int, error)  // non-blocking
n, err := uart.Read(b []byte)  (int, error)  // blocks until first byte
```

### Beispiel

```go
uart, _ := tsb.NewUart(5, server)
uart.Config(0, tsb.UartBaud115200, tsb.UartData8, tsb.UartParityNone, tsb.UartStopbits1)

uart.Write([]byte("Hello\n"))

buf := make([]byte, 256)
n, _ := uart.Read(buf)
fmt.Printf("Received: %s\n", buf[:n])
```

---

## GPIO-Port

### Konstruktor

```go
port, err := tsb.NewPort(jack byte, server *Server) (*Port, error)
```

### Pads

| Konstante      | Wert | Bedeutung      |
|----------------|------|----------------|
| `PortPad0`     | 1    | GPIO-Pad 0     |
| `PortPad1`     | 2    | GPIO-Pad 1     |
| `PortPad2`     | 4    | GPIO-Pad 2     |
| `PortPad3`     | 8    | GPIO-Pad 3     |
| `PortAllPads`  | 15   | Alle Pads 0–3  |

### Port-Befehle

| Konstante                     | Wert | Aktion                            |
|-------------------------------|------|-----------------------------------|
| `PortcharReadWrite`           | 0x00 | Lesen/Schreiben                   |
| `PortcharRead`                | 0x01 | Lesen                             |
| `PortcharSetOutput`           | 0x02 | Ausgang auf High setzen           |
| `PortcharClearOutput`         | 0x03 | Ausgang auf Low setzen            |
| `PortcharToggleOutput`        | 0x04 | Ausgang umschalten                |
| `PortcharNotification`        | 0x05 | Benachrichtigung aktivieren       |
| `PortcharDelay`               | 0x06 | Verzögerung                       |
| `PortcharSetDirection`        | 0x08 | Als Ausgang konfigurieren         |
| `PortcharClearDirection`      | 0x09 | Als Eingang konfigurieren         |
| `PortcharSetPullEnable`       | 0x0A | Pull-up aktivieren                |
| `PortcharClearPullEnable`     | 0x0B | Pull-up deaktivieren              |
| `PortcharSetNotification`     | 0x0C | Pad-Benachrichtigung aktivieren   |
| `PortcharClearNotification`   | 0x0D | Pad-Benachrichtigung deaktivieren |
| `PortcharSetLED`              | 0x10 | LED setzen                        |
| `PortcharClearLED`            | 0x11 | LED löschen                       |
| `PortcharToggleLED`           | 0x12 | LED umschalten                    |

### Hilfsfunktion

```go
cmd := tsb.PortCharNibble(code byte, value int) []byte
```

Kodiert Port-Befehle mit einem Nibble-Wert in das Übertragungsformat.

### Datenübertragung

```go
n, err := port.Write(b []byte) (int, error)
n, err := port.Read(b []byte)  (int, error)
```

### Beispiel

```go
port, _ := tsb.NewPort(1, server)

// Configure pads 0+1 as inputs with notification
port.Write(tsb.PortCharNibble(tsb.PortcharClearDirection, 0x03))
port.Write(tsb.PortCharNibble(tsb.PortcharSetNotification, 0x03))

// Toggle LED on pad 0
port.Write(tsb.PortCharNibble(tsb.PortcharToggleLED, 1))

// Read notifications
buf := make([]byte, 256)
n, _ := port.Read(buf)
```

---

## Modbus

Modbus wird intern verwendet, um die Hardware-Register der Jacks zu konfigurieren.

### Funktion

```go
err = tsb.ModbusWriteSingleRegister(adr uint16, jack byte, server *Server, value uint16) error
```

### Funktionscodes

| Konstante                         | Wert | Bedeutung                      |
|-----------------------------------|------|--------------------------------|
| `MbFcReadHoldingRegister`         | 0x03 | Holding-Register lesen         |
| `MbFcWriteSingleRegister`         | 0x06 | Einzelnes Register schreiben   |
| `MbFcWriteMultipleRegister`       | 0x10 | Mehrere Register schreiben     |

### Registeradressen

| Konstante          | Adresse | Bedeutung                |
|--------------------|---------|--------------------------|
| `ModeRegisterAdr`  | 0x0002  | Jack-Modus               |
| `PortRegisterAdr`  | 0x0004  | GPIO-Konfiguration       |
| `UartRegisterAdr`  | 0x0006  | UART-Konfiguration       |
| `I2cRegisterAdr`   | 0x0008  | I2C-Konfiguration        |
| `SpiRegisterAdr`   | 0x000A  | SPI-Konfiguration        |

---

## Core-API (tsb.go)

### Kodierung/Dekodierung

```go
// Convert a channel string ("3.4.5") into a byte array
b := tsb.Channel2Bytes(ch string) []byte

// Encode TsbData into wire format (Ch + Typ + Payload + CRC16)
raw := tsb.Encode(td TsbData) []byte

// Decode wire format into TsbData (verifies CRC)
td, err := tsb.Decode(packet []byte) (TsbData, error)

// COBS encoding
encoded := tsb.CobsEncode(p []byte) []byte
decoded, err := tsb.CobsDecode(b []byte) ([]byte, error)
```

### Goroutinen für Datenströme

```go
// Background goroutine: reads COBS packets from io.Reader, delivers TsbData
dataCh, doneCh := tsb.GetData(r io.Reader, chanLen int) (chan TsbData, chan struct{})

// Background goroutine: encodes TsbData and writes to io.Writer
sendCh := tsb.PutData(w io.Writer, chanLen int) chan TsbData
```

### Debug-Flags

```go
tsb.Verbose      = true  // Protocol trace
tsb.ErrorVerbose = true  // Extended error output
```

### Protokolltypen

| Konstante       | Wert | Verwendung                     |
|-----------------|------|--------------------------------|
| `TypRaw`        | 0x01 | Rohdaten (UART, SPI)           |
| `TypText`       | 0x02 | Textdaten                      |
| `TypPort`       | 0x03 | GPIO-Port                      |
| `TypI2c`        | 0x04 | I2C                            |
| `TypSpi`        | 0x05 | SPI                            |
| `TypModbus`     | 0x07 | Modbus                         |
| `TypAtCmd`      | 0x09 | AT-Befehle                     |
| `TypCoap`       | 0x21 | CoAP                           |
| `TypCbor`       | 0x31 | CBOR                           |
| `TypCan`        | 0x41 | CAN-Bus                        |
| `TypInflux`     | 0x75 | InfluxDB                       |
| `TypLog`        | 0x7D | Log                            |
| `TypWarning`    | 0x7E | Warnung                        |
| `TypError`      | 0x7F | Fehler                         |

### Grenzwerte

| Konstante    | Wert | Bedeutung                       |
|--------------|------|---------------------------------|
| `Buflen`     | 1000 | Pufferlänge                     |
| `MaxTyp`     | 127  | Maximaler Typwert               |
| `MaxPayload` | 250  | Maximale Payload-Größe          |
