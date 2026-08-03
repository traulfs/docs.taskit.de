# Proposed BeaconLine MQTT JSON Interface for flespi

**Document revision:** 1.1  
**Date:** 2026-07-16  
**Prepared by:** taskit GmbH  
**Status:** Draft for customer technical review — proposed interface, not yet released  

---

## 1. Purpose

The customer platform processes MQTT data through flespi and requires structured JSON payloads instead of CSV strings.

taskit therefore proposes adding a configurable MQTT JSON output mode to the BeaconLine software. The new mode will represent each BLE advertisement observation as one JSON object. It will preserve the information currently available in the BeaconLine CSV record while using native JSON types and providing the `ident` and `timestamp` values needed for the proposed flespi device and event-time mapping.

This document defines the proposed payload. The final interface will be frozen after the customer confirms the identification model, observation handling, and MQTT connection settings.

---

## 2. MQTT message framing

Each MQTT `PUBLISH` message will contain exactly one complete JSON object representing one BLE advertisement observation.

The payload will be:

- valid UTF-8 JSON;
- one observation per MQTT message;
- not a CSV string;
- not multiple newline-separated JSON objects;
- not a JSON object encoded inside a quoted string.

The identifiers in the following example are illustrative. Actual gateway and anchor identifiers are deployment-specific.

```json
{
  "ident": "404cca5bbf1e",
  "timestamp": 1779364221.617,
  "timestamp_ms": 1779364221617,
  "anchor": "example-anchor-01",
  "mac": "404cca5bbf1e",
  "rssi": -80,
  "connectable": true,
  "adv_hex": "0201061bff7b0120000c8e404cca5bbf1e335f676173330000000000208044",
  "node_name": "taskit_m2go.Mems"
}
```

The example timestamp represents:

```text
2026-05-21T11:50:21.617Z
```

---

## 3. Payload fields

| Field | JSON type | Required | Description |
|---|---|:---:|---|
| `ident` | string | Yes | Device identifier used by the flespi MQTT channel |
| `timestamp` | number | Yes | Reception timestamp as Unix time in seconds, UTC; the fractional part preserves millisecond precision |
| `timestamp_ms` | integer | Yes | Original BeaconLine reception timestamp as Unix time in milliseconds, UTC |
| `anchor` | string | Yes | Identifier of the BeaconLine anchor that received the advertisement |
| `mac` | string | Yes | BLE source address as 12 lowercase hexadecimal characters without separators |
| `rssi` | integer | Yes | Received signal strength in dBm |
| `connectable` | boolean | Yes | `true` for a connectable advertisement, otherwise `false` |
| `adv_hex` | string | Yes | Raw BLE advertising data encoded as lowercase hexadecimal |
| `node_name` | string or `null` | Yes | Complete Local Name or configured node name; `null` when no name is available |

The order of fields in a JSON object is not significant. Receivers must access values by field name.

---

## 4. Field rules

### 4.1 `ident`

flespi requires each message to be associated with an `ident`, supplied either in the JSON payload or through the MQTT topic. This proposal supplies it explicitly in the JSON payload.

The proposed initial mapping is:

```text
ident = stable BLE source address
```

Example:

```json
{
  "ident": "404cca5bbf1e"
}
```

This model allows observations of the same beacon or sensor received by different BeaconLine anchors to be associated with one flespi device.

The customer should confirm that this matches its flespi device model.

If a BLE device uses a rotating random address, its source address is not a stable device identifier. Such devices require an alternative stable identifier or a different device-identification model.

### 4.2 `timestamp` and `timestamp_ms`

The `timestamp` field is provided in Unix seconds for direct processing as the message timestamp:

```json
{
  "timestamp": 1779364221.617
}
```

The original millisecond value is retained separately:

```json
{
  "timestamp_ms": 1779364221617
}
```

Both values represent the same reception event.

### 4.3 `anchor`

`anchor` identifies the BeaconLine reception source. The value is deployment-specific and should be treated as an opaque string by the receiving platform.

```json
{
  "anchor": "example-anchor-01"
}
```

### 4.4 `mac`

The BLE source address:

- contains exactly 12 hexadecimal characters;
- uses lowercase characters;
- contains no colons or hyphens;
- contains no `0x` prefix.

```json
{
  "mac": "404cca5bbf1e"
}
```

### 4.5 `rssi`

`rssi` is a signed JSON integer in dBm and represents the signal strength measured by the specified anchor.

```json
{
  "rssi": -80
}
```

### 4.6 `connectable`

`connectable` is a native JSON Boolean, not a string:

```json
{
  "connectable": true
}
```

### 4.7 `adv_hex`

`adv_hex` contains the raw BLE advertising data:

- lowercase hexadecimal characters;
- an even number of characters;
- no spaces or separators;
- no `0x` prefix;
- up to 62 hexadecimal characters for the currently supported legacy BLE advertisement data.

```json
{
  "adv_hex": "0201061bff7b0120000c8e404cca5bbf1e335f676173330000000000208044"
}
```

The decoding of taskit-specific manufacturer data is documented separately.

### 4.8 `node_name`

When a node name is known:

```json
{
  "node_name": "taskit_m2go.Mems"
}
```

When no node name is available:

```json
{
  "node_name": null
}
```

---

## 5. Proposed MQTT topic

The MQTT topic will be configurable.

Proposed structure:

```text
beaconline/advertisements/<gateway-id>/<anchor-id>
```

Illustrative example:

```text
beaconline/advertisements/example-gateway/example-anchor-01
```

Because `ident` is included directly in the JSON payload, the flespi channel does not need to derive the device identifier from the topic.

The final topic structure will be agreed with the customer.

---

## 6. Multiple-anchor observations

The same BLE advertisement may be received by more than one BeaconLine anchor.

In this case, BeaconLine will generate separate observations. They may contain the same:

- `ident`;
- `mac`;
- `adv_hex`.

They will normally differ in:

- `anchor`;
- `rssi`;
- `timestamp`;
- `timestamp_ms`.

These are separate physical reception observations and must not automatically be treated as duplicate MQTT deliveries.

The proposed default behavior is to publish every observation. The customer should confirm whether gateway-side filtering, strongest-RSSI selection, time-window aggregation, or another deduplication rule is required.

---

## 7. MQTT connection settings

The following values will be agreed separately for the customer environment:

- broker host and port;
- MQTT version;
- authentication credentials or flespi token;
- TLS requirements;
- publish topic;
- QoS;
- retain behavior;
- client identifier;
- session and reconnection behavior;
- optional offline buffering.

This payload specification does not assume unconfirmed broker-specific values.

---

## 8. Customer confirmation requested

Before implementation is finalized, please confirm:

1. Should `ident` represent the BLE beacon or sensor using its stable BLE source address?
2. Should BeaconLine publish every observation received by every anchor, or is gateway-side filtering, aggregation, or deduplication required?
3. Are the proposed JSON fields and field names acceptable?
4. Which MQTT topic and connection settings should be used?
5. Must devices with rotating BLE addresses be supported?
6. Is the integration uplink-only, or is MQTT command delivery to BeaconLine also required?

After confirmation, taskit will finalize and implement the agreed BeaconLine MQTT JSON output mode.

---

## 9. JSON Schema

The following schema defines the proposed payload contract.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "BeaconLine BLE Advertisement Observation",
  "type": "object",
  "required": [
    "ident",
    "timestamp",
    "timestamp_ms",
    "anchor",
    "mac",
    "rssi",
    "connectable",
    "adv_hex",
    "node_name"
  ],
  "properties": {
    "ident": {
      "type": "string",
      "minLength": 1
    },
    "timestamp": {
      "type": "number",
      "minimum": 0
    },
    "timestamp_ms": {
      "type": "integer",
      "minimum": 0
    },
    "anchor": {
      "type": "string",
      "minLength": 1
    },
    "mac": {
      "type": "string",
      "pattern": "^[0-9a-f]{12}$"
    },
    "rssi": {
      "type": "integer"
    },
    "connectable": {
      "type": "boolean"
    },
    "adv_hex": {
      "type": "string",
      "pattern": "^(?:[0-9a-f]{2}){0,31}$"
    },
    "node_name": {
      "type": ["string", "null"]
    }
  },
  "additionalProperties": true
}
```

Receivers should ignore unknown additional fields to allow backward-compatible extensions.

---

## 10. Implementation verification

The implementation will be verified using the agreed customer configuration to ensure that:

1. BeaconLine connects to the agreed MQTT broker.
2. The flespi MQTT channel receives the configured topic.
3. Each MQTT payload is parsed as one structured JSON object.
4. The expected `ident` is resolved.
5. The supplied `timestamp` is processed as the message timestamp.
6. Numbers and Booleans retain their native JSON types.
7. `node_name: null` is accepted.
8. Observations received by different anchors remain distinguishable.
9. Reconnection and delivery behavior match the agreed MQTT settings.

---

## 11. References

- flespi MQTT protocol: <https://flespi.com/protocols/mqtt>
- flespi custom MQTT parameter mapping: <https://flespi.com/blog/custom-naming-scheme-for-mqtt-message-parameters>
- taskit BeaconLine advertisement CSV format
- taskit BeaconLine advertisement JSON format
- taskit BLE manufacturer advertisement format

---

## 12. Review status

This document reflects taskit's proposed implementation based on the customer's stated flespi requirement.

The final payload and MQTT configuration will be frozen after technical confirmation by the customer.
