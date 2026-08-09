# TSB – Tiny Serial Bus

TSB is a Go library for communicating with embedded systems over serial connections (UART/serial port) or TCP networks. It provides a unified protocol framework for addressing hardware interfaces such as I2C, UART, SPI, and GPIO ports.

```
Module: github.com/traulfs/tsb
Go:     >= 1.20
```

---

## Table of Contents

1. [Protocol Architecture](#protocol-architecture)
2. [Server – Connection Setup](#server-connection-setup)
3. [I2C](#i2c)
4. [UART](#uart)
5. [GPIO Port](#gpio-port)
6. [Modbus](#modbus)
7. [Core API (tsb.go)](#core-api-tsbgo)

---

## Protocol Architecture

Every TSB packet consists of four fields:

| Field     | Length         | Meaning                                                          |
|-----------|----------------|-------------------------------------------------------------------|
| Channel   | variable       | Routing address; intermediate bytes have bit 7 set               |
| Type      | variable       | Protocol type (0x00–0x7F)                                        |
| Payload   | 0–250 bytes    | Payload data                                                      |
| CRC-16    | 2 bytes        | Checksum over Channel + Type + Payload (little-endian)           |

The fully encoded packet is framed with **COBS** (Consistent Overhead Byte Stuffing) and terminated with a `0x00` byte.

### TsbData

```go
type TsbData struct {
    Ch      []byte // Channel
    Typ     []byte // Type
    Payload []byte // Payload (max. 250 bytes)
}
```

---

## Server – Connection Setup

A `Server` manages up to **8 jacks** (independent device connectors) and routes incoming packets based on jack number and protocol type.

### Constructors

```go
// Serial connection
server, err := tsb.NewSerialServer("/dev/ttyUSB0", 115200)

// TCP connection
server, err := tsb.NewTcpServer("localhost:3001")
```

### Methods

```go
server.Close()

// Register a callback for a specific jack and protocol type
server.SetCallback(jack byte, typ byte, f func(*TsbData))
```

### Jacks

Each jack has 128 type-indexed byte channels. Incoming bytes are automatically delivered to the matching channel or passed to a registered callback.

| Constant      | Value | Meaning                        |
|---------------|-------|---------------------------------|
| `MaxJacks`    | 8    | Maximum number of jacks         |
| `JackModeReg` | 0x80 | Mode register                   |
| `JackUartReg` | 0x82 | UART register                   |
| `JackPortReg` | 0x86 | Port register                   |
| `JackI2cReg`  | 0x88 | I2C register                    |

| Jack Mode    | Value |
|--------------|-------|
| `JackPort`   | 1    |
| `JackI2c`    | 2    |
| `JackUart`   | 3    |
| `JackSpi`    | 4    |

---

## I2C

### Constructor

```go
i2c, err := tsb.NewI2c(adr uint8, jack byte, server *Server) (*I2C, error)
```

Sets the jack mode to I2C and initializes the slave address.

### Setting the Address

```go
err = i2c.SetAdr(adr byte) error
```

### Raw Data Transfer

```go
n, err := i2c.Write(buf []byte) (int, error)  // max. 127 bytes
n, err := i2c.Read(buf []byte)  (int, error)  // max. 127 bytes
```

### Register Operations

| Method                                                | Description                          |
|--------------------------------------------------------|---------------------------------------|
| `ReadRegU8(reg) (byte, error)`                       | Read an 8-bit value                    |
| `WriteRegU8(reg, value) error`                       | Write an 8-bit value                   |
| `ReadRegBytes(reg, n) ([]byte, int, error)`          | Read n bytes starting at register      |
| `ReadRegU16BE(reg) (uint16, error)`                  | Read 16-bit big-endian                 |
| `WriteRegU16BE(reg, value) error`                    | Write 16-bit big-endian                |
| `ReadRegU16LE(reg) (uint16, error)`                  | Read 16-bit little-endian              |
| `WriteRegU16LE(reg, value) error`                    | Write 16-bit little-endian             |
| `ReadRegS16BE(reg) (int16, error)`                   | Read 16-bit signed BE                  |
| `WriteRegS16BE(reg, value) error`                    | Write 16-bit signed BE                 |
| `ReadRegS16LE(reg) (int16, error)`                   | Read 16-bit signed LE                  |
| `WriteRegS16LE(reg, value) error`                    | Write 16-bit signed LE                 |

### Example

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

### Constructor

```go
uart, err := tsb.NewUart(jack byte, server *Server) (*UART, error)
```

### Configuration

```go
err = uart.Config(rs485, baud, databits, parity, stopbits uint16) error
```

The parameters are combined with a bitwise OR:

**Baud rate:**

| Constant           | Value |
|--------------------|-------|
| `UartBaudAuto`     | 0    |
| `UartBaud9600`     | –    |
| `UartBaud115200`   | –    |
| `UartBaud230400`   | –    |
| `UartBaud460800`   | –    |
| `UartBaud921600`   | –    |
| `UartBaud1000000`  | –    |
| `UartBaud3000000`  | –    |
| *(more)*           | –    |

**Stop bits:**

| Constant         | Value  |
|------------------|--------|
| `UartStopbits1`  | 0x0000 |
| `UartStopbits15` | 0x0100 |
| `UartStopbits2`  | 0x0200 |

**Parity:**

| Constant         | Value  |
|------------------|--------|
| `UartParityNone` | 0x0000 |
| `UartParityEven` | 0x0400 |
| `UartParityOdd`  | 0x0800 |

**Data bits:**

| Constant     | Value  |
|--------------|--------|
| `UartData8`  | 0x0000 |
| `UartData7`  | 0x2000 |
| `UartData6`  | 0x3000 |
| `UartData5`  | 0x4000 |
| `UartData9`  | 0x1000 |

**RS485:**

| Constant    | Value  |
|-------------|--------|
| `UartRS485` | 0x8000 |

### Data Transfer

```go
n, err := uart.Write(b []byte) (int, error)  // non-blocking
n, err := uart.Read(b []byte)  (int, error)  // blocks until first byte
```

### Example

```go
uart, _ := tsb.NewUart(5, server)
uart.Config(0, tsb.UartBaud115200, tsb.UartData8, tsb.UartParityNone, tsb.UartStopbits1)

uart.Write([]byte("Hello\n"))

buf := make([]byte, 256)
n, _ := uart.Read(buf)
fmt.Printf("Received: %s\n", buf[:n])
```

---

## GPIO Port

### Constructor

```go
port, err := tsb.NewPort(jack byte, server *Server) (*Port, error)
```

### Pads

| Constant       | Value | Meaning        |
|----------------|-------|----------------|
| `PortPad0`     | 1    | GPIO pad 0     |
| `PortPad1`     | 2    | GPIO pad 1     |
| `PortPad2`     | 4    | GPIO pad 2     |
| `PortPad3`     | 8    | GPIO pad 3     |
| `PortAllPads`  | 15   | All pads 0–3   |

### Port Commands

| Constant                     | Value | Action                          |
|-------------------------------|-------|-----------------------------------|
| `PortcharReadWrite`          | 0x00 | Read/write                        |
| `PortcharRead`               | 0x01 | Read                               |
| `PortcharSetOutput`          | 0x02 | Set output high                   |
| `PortcharClearOutput`        | 0x03 | Set output low                    |
| `PortcharToggleOutput`       | 0x04 | Toggle output                     |
| `PortcharNotification`       | 0x05 | Enable notification                |
| `PortcharDelay`              | 0x06 | Delay                              |
| `PortcharSetDirection`       | 0x08 | Configure as output                |
| `PortcharClearDirection`     | 0x09 | Configure as input                 |
| `PortcharSetPullEnable`      | 0x0A | Enable pull-up                     |
| `PortcharClearPullEnable`    | 0x0B | Disable pull-up                    |
| `PortcharSetNotification`    | 0x0C | Enable pad notification            |
| `PortcharClearNotification`  | 0x0D | Disable pad notification           |
| `PortcharSetLED`             | 0x10 | Set LED                            |
| `PortcharClearLED`           | 0x11 | Clear LED                          |
| `PortcharToggleLED`          | 0x12 | Toggle LED                         |

### Helper Function

```go
cmd := tsb.PortCharNibble(code byte, value int) []byte
```

Encodes port commands with a nibble value into the wire format.

### Data Transfer

```go
n, err := port.Write(b []byte) (int, error)
n, err := port.Read(b []byte)  (int, error)
```

### Example

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

Modbus is used internally to configure hardware registers of the jacks.

### Function

```go
err = tsb.ModbusWriteSingleRegister(adr uint16, jack byte, server *Server, value uint16) error
```

### Function Codes

| Constant                          | Value | Meaning                      |
|------------------------------------|-------|--------------------------------|
| `MbFcReadHoldingRegister`        | 0x03 | Read holding register          |
| `MbFcWriteSingleRegister`        | 0x06 | Write single register          |
| `MbFcWriteMultipleRegister`      | 0x10 | Write multiple registers       |

### Register Addresses

| Constant           | Address | Meaning                |
|---------------------|---------|--------------------------|
| `ModeRegisterAdr`  | 0x0002  | Jack mode                |
| `PortRegisterAdr`  | 0x0004  | GPIO configuration        |
| `UartRegisterAdr`  | 0x0006  | UART configuration        |
| `I2cRegisterAdr`   | 0x0008  | I2C configuration         |
| `SpiRegisterAdr`   | 0x000A  | SPI configuration         |

---

## Core API (tsb.go)

### Encoding/Decoding

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

### Goroutines for Data Streams

```go
// Background goroutine: reads COBS packets from io.Reader, delivers TsbData
dataCh, doneCh := tsb.GetData(r io.Reader, chanLen int) (chan TsbData, chan struct{})

// Background goroutine: encodes TsbData and writes to io.Writer
sendCh := tsb.PutData(w io.Writer, chanLen int) chan TsbData
```

### Debug Flags

```go
tsb.Verbose      = true  // Protocol trace
tsb.ErrorVerbose = true  // Extended error output
```

### Protocol Types

| Constant        | Value | Usage                        |
|-----------------|-------|--------------------------------|
| `TypRaw`        | 0x01 | Raw data (UART, SPI)           |
| `TypText`       | 0x02 | Text data                       |
| `TypPort`       | 0x03 | GPIO port                       |
| `TypI2c`        | 0x04 | I2C                              |
| `TypSpi`        | 0x05 | SPI                              |
| `TypModbus`     | 0x07 | Modbus                          |
| `TypAtCmd`      | 0x09 | AT commands                     |
| `TypCoap`       | 0x21 | CoAP                             |
| `TypCbor`       | 0x31 | CBOR                             |
| `TypCan`        | 0x41 | CAN bus                          |
| `TypInflux`     | 0x75 | InfluxDB                         |
| `TypLog`        | 0x7D | Log                               |
| `TypWarning`    | 0x7E | Warning                          |
| `TypError`      | 0x7F | Error                             |

### Limits

| Constant     | Value | Meaning                       |
|--------------|-------|---------------------------------|
| `Buflen`     | 1000 | Buffer length                    |
| `MaxTyp`     | 127  | Maximum type value                |
| `MaxPayload` | 250  | Maximum payload size               |
