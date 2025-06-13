# Mannito Controller API Specification

## Overview

This document specifies the exact API requirements that the mannito-controller must implement to work seamlessly with the Home Assistant integration. This specification ensures reliable communication and proper functionality between both systems.

## Required HTTP API Endpoints

The mannito-controller must implement these REST API endpoints for the Home Assistant integration to function correctly.

### Base URL Structure

All endpoints are relative to the controller's base URL:
```
http://{CONTROLLER_IP_OR_HOSTNAME}/
```

### Authentication

- **Type**: HTTP Basic Authentication (optional)
- **Implementation**: If authentication is enabled, all endpoints must support the `Authorization` header
- **Format**: `Authorization: Basic {base64(username:password)}`
- **Fallback**: If no authentication is configured, endpoints should work without the header

## Core API Endpoints

### 1. Configuration Endpoint

#### GET /api/config

**Purpose**: Provides the complete system configuration including all devices, sensors, and plugins.

**Requirements**:
- Must return HTTP 200 on success
- Must return valid JSON response
- Must include device, sensor, and plugin arrays
- Must include system information

**Required Response Format**:
```json
{
  "model": "string",                    // Controller model name
  "firmware_version": "string",         // Firmware version
  "hardware_version": "string",         // Hardware version  
  "serial_number": "string",            // Unique serial number
  "manufacturer": "string",             // Manufacturer name (default: "Mannito")
  "name": "string",                     // Controller name
  "uptime": "string",                   // System uptime information
  "ip_address": "string",               // Controller IP address
  "devices": [                          // Array of controllable devices
    {
      "device_id": "string",            // Unique device identifier
      "device_name": "string",          // Human-readable device name
      "device_type": "enum"             // Device type (see Device Types)
    }
  ],
  "sensors": [                          // Array of readable sensors
    {
      "sensor_id": "string",            // Unique sensor identifier  
      "sensor_name": "string",          // Human-readable sensor name
      "sensor_type": "enum"             // Sensor type (see Sensor Types)
    }
  ],
  "plugins": [                          // Array of plugin systems (optional)
    {
      "plugin_id": "string",            // Unique plugin identifier
      "plugin_name": "string",          // Human-readable plugin name  
      "plugin_type": "enum"             // Plugin type (see Plugin Types)
    }
  ]
}
```

**Error Handling**:
- Return HTTP 500 for internal errors
- Return HTTP 403 for authentication failures
- Never return empty response - always include at least empty arrays

### 2. Device State Query

#### GET /api/device/{device_id}

**Purpose**: Retrieves the current state of a specific device.

**Path Parameters**:
- `device_id`: The unique identifier of the device (from configuration)

**Required Response Format**:
```json
{
  "state": boolean,                     // true = on/enabled, false = off/disabled
  "speed": integer                      // Speed value 1-100 (fans only, optional)
}
```

**Requirements**:
- Return HTTP 200 with state data for available devices
- Return HTTP 404 for unknown device_id
- Return empty response `{}` for temporarily unavailable devices
- For non-fan devices, `speed` field is optional
- For fan devices, include `speed` field even when off (can be 0)

**Examples**:
```json
// Fan device response
{"state": true, "speed": 75}

// Switch/relay/pump device response  
{"state": false}

// Device temporarily unavailable
{}
```

### 3. Device Control Endpoints

#### POST /api/device/{device_id}/on

**Purpose**: Turn a device on/enable it.

**Path Parameters**:
- `device_id`: The unique identifier of the device

**Requirements**:
- Return HTTP 200 on successful state change
- Return HTTP 404 for unknown device_id
- Return HTTP 500 for control failures
- No response body required

**Implementation Notes**:
- For fans, this should enable the fan at its last known speed
- For other devices, this sets the state to active/on

#### POST /api/device/{device_id}/off

**Purpose**: Turn a device off/disable it.

**Path Parameters**:
- `device_id`: The unique identifier of the device

**Requirements**:
- Return HTTP 200 on successful state change
- Return HTTP 404 for unknown device_id  
- Return HTTP 500 for control failures
- No response body required

**Implementation Notes**:
- For fans, this should stop the fan but remember the speed setting
- For other devices, this sets the state to inactive/off

#### POST /api/device/{device_id}/value/{speed}

**Purpose**: Set the speed/value of a device (primarily for fans).

**Path Parameters**:
- `device_id`: The unique identifier of the device
- `speed`: Integer value from 1-100 representing percentage

**Requirements**:
- Return HTTP 200 on successful speed change
- Return HTTP 404 for unknown device_id
- Return HTTP 400 for invalid speed values (outside 1-100 range)
- Return HTTP 500 for control failures
- No response body required

**Implementation Notes**:
- Setting speed should automatically turn the device on
- Speed 0 should be equivalent to turning the device off
- Only fan-type devices need to implement speed control
- Non-fan devices may ignore this endpoint or return HTTP 400

### 4. Sensor Data Endpoints

#### GET /api/sensor/{sensor_id}

**Purpose**: Retrieves the current reading from a specific sensor.

**Path Parameters**:
- `sensor_id`: The unique identifier of the sensor (from configuration)

**Required Response Format**:
```json
{
  "value": "string",                    // Current sensor reading as string
  "unit": "string"                      // Unit of measurement (optional)
}
```

**Requirements**:
- Return HTTP 200 with sensor data for available sensors
- Return HTTP 404 for unknown sensor_id
- Return empty response `{}` for temporarily unavailable sensors
- Value should be provided as string to handle various data types
- Unit field is optional but recommended

**Examples**:
```json
// Temperature sensor
{"value": "23.5", "unit": "°C"}

// Humidity sensor
{"value": "65", "unit": "%"}

// pH sensor  
{"value": "6.8"}

// Sensor temporarily unavailable
{}
```

### 5. Plugin State Endpoints (Optional)

#### GET /api/plugin/{plugin_id}

**Purpose**: Retrieves the current state of a plugin/controller system.

**Path Parameters**:
- `plugin_id`: The unique identifier of the plugin (from configuration)

**Response Format**:
```json
{
  "state": boolean,                     // Plugin active/inactive state
  "config": object                      // Plugin-specific configuration (optional)
}
```

**Requirements**:
- This endpoint is optional - implement only if plugin systems are supported
- Return HTTP 200 with plugin data for available plugins
- Return HTTP 404 for unknown plugin_id
- Return empty response `{}` for temporarily unavailable plugins

## Data Type Specifications

### Device Types

The controller must use these exact string values in the `device_type` field:

| Type | Description | Control Methods | Speed Control |
|------|-------------|-----------------|---------------|
| `"FAN"` | Variable speed fans | on/off/speed | Yes (1-100) |
| `"SOLENOID"` | Solenoid valves | on/off | No |
| `"RELAY"` | Power relays | on/off | No |
| `"PUMP"` | Fluid pumps | on/off | No |
| `"OTHER"` | Undefined device types | on/off | No |

### Sensor Types

The controller must use these exact string values in the `sensor_type` field:

| Type | Description | Typical Unit | Home Assistant Class |
|------|-------------|--------------|---------------------|
| `"TEMPERATURE"` | Air temperature | °C | Temperature |
| `"HUMIDITY"` | Relative humidity | % | Humidity |
| `"CO2"` | CO2 concentration | ppm | CO2 |
| `"PH"` | pH level | - | pH |
| `"EC"` | Electrical conductivity | µS/cm | - |
| `"WATERLEVEL"` | Water level | cm/% | - |
| `"WATERFLOW"` | Water flow rate | L/min | - |
| `"LEAF_TEMPERATURE"` | Leaf temperature | °C | Temperature |
| `"OTHER"` | Undefined sensor types | - | - |

### Plugin Types (Optional)

If the controller supports plugin systems, use these string values:

| Type | Description |
|------|-------------|
| `"LIGHT_SCHEDULER"` | Lighting control automation |
| `"DEVICE_SCHEDULER"` | Device scheduling automation |
| `"TEMPERATURE_CONTROLLER"` | Climate control automation |
| `"WIND_SIMULATOR"` | Ventilation control automation |
| `"WATER_CONTROLLER"` | Irrigation control automation |
| `"OTHER"` | Undefined plugin types |

## Implementation Requirements

### Response Times

- Configuration endpoint (`/api/config`): Must respond within 5 seconds
- Device state queries: Must respond within 2 seconds
- Device control commands: Must complete within 3 seconds
- Sensor readings: Must respond within 2 seconds

### Error Handling

#### HTTP Status Codes

- `200 OK`: Successful operation
- `400 Bad Request`: Invalid parameters (e.g., speed out of range)
- `403 Forbidden`: Authentication failure
- `404 Not Found`: Unknown device/sensor/plugin ID
- `500 Internal Server Error`: Controller malfunction

#### Response Bodies for Errors

Error responses should include descriptive messages when possible:
```json
{
  "error": "string",                    // Error description
  "code": "string"                      // Error code (optional)
}
```

### Content Type

- All responses must use `Content-Type: application/json`
- All request bodies (if any) should expect `application/json`

### Device Availability

The integration determines device availability based on:
- HTTP response status (200 = available, other = unavailable)
- Empty response body `{}` = temporarily unavailable
- Network timeouts = unavailable

### Concurrent Requests

The controller should handle multiple simultaneous requests:
- Support at least 10 concurrent API requests
- Implement proper request queuing if hardware limitations exist
- Avoid blocking device control during sensor readings

## Testing and Validation

### Mandatory Test Cases

Controllers should pass these basic tests:

1. **Configuration Discovery**:
   ```bash
   curl -X GET http://controller/api/config
   # Should return valid JSON with devices/sensors arrays
   ```

2. **Device Control**:
   ```bash
   curl -X POST http://controller/api/device/FAN1/on
   curl -X GET http://controller/api/device/FAN1
   # Should show {"state": true, "speed": X}
   ```

3. **Speed Control** (for fans):
   ```bash
   curl -X POST http://controller/api/device/FAN1/value/50
   curl -X GET http://controller/api/device/FAN1  
   # Should show {"state": true, "speed": 50}
   ```

4. **Sensor Reading**:
   ```bash
   curl -X GET http://controller/api/sensor/TEMP1
   # Should return {"value": "XX.X", "unit": "°C"}
   ```

### Integration Test Checklist

- [ ] Configuration endpoint returns all required fields
- [ ] All declared devices respond to state queries
- [ ] All declared sensors provide readings
- [ ] Device control commands work correctly  
- [ ] Speed control works for fan devices
- [ ] Error codes are returned appropriately
- [ ] Authentication works if implemented
- [ ] Concurrent requests are handled properly
- [ ] Response times meet requirements
- [ ] JSON format is valid and consistent

## Example Controller Implementation

### Minimal Configuration Response

```json
{
  "model": "Mannito Controller v1.0",
  "firmware_version": "1.2.3", 
  "hardware_version": "Rev C",
  "serial_number": "MC001234",
  "manufacturer": "Mannito",
  "name": "Greenhouse Controller",
  "uptime": "5 days, 3 hours",
  "ip_address": "192.168.1.100",
  "devices": [
    {"device_id": "FAN1", "device_name": "Exhaust Fan", "device_type": "FAN"},
    {"device_id": "VALVE1", "device_name": "Water Valve", "device_type": "SOLENOID"},
    {"device_id": "PUMP1", "device_name": "Nutrient Pump", "device_type": "PUMP"}
  ],
  "sensors": [
    {"sensor_id": "TEMP1", "sensor_name": "Air Temperature", "sensor_type": "TEMPERATURE"},
    {"sensor_id": "HUM1", "sensor_name": "Air Humidity", "sensor_type": "HUMIDITY"}
  ],
  "plugins": []
}
```

### Device State Examples

```json
// Fan at 75% speed
{"state": true, "speed": 75}

// Valve closed
{"state": false}

// Pump running  
{"state": true}
```

### Sensor Reading Examples

```json
// Temperature reading
{"value": "24.3", "unit": "°C"}

// Humidity reading
{"value": "68", "unit": "%"}

// pH reading
{"value": "6.5"}
```

## Integration Behavior

### Data Update Cycle

The Home Assistant integration will:
1. Call `/api/config` on startup and periodically for device discovery
2. Poll device states every 30 seconds via `/api/device/{id}`
3. Poll sensor readings every 30 seconds via `/api/sensor/{id}`
4. Send control commands immediately when user interacts with devices

### Expected Device IDs

The integration expects these device ID patterns (but supports any string):
- Fans: `FAN1`, `FAN2`, ..., `FAN10`
- Valves: `VALVE1`, `VALVE2`, ..., `VALVE5` or `SOLENOID1`, etc.
- Relays: `RELAY1`, `RELAY2`, ..., `RELAY8`
- Pumps: `PUMP1`, `PUMP2`, ..., `PUMP4`

### Expected Sensor IDs

Common sensor ID patterns (but supports any string):
- Temperature: `TEMP1`, `TEMPERATURE1`, `AIR_TEMP`, etc.
- Humidity: `HUM1`, `HUMIDITY1`, `AIR_HUM`, etc.
- CO2: `CO2_1`, `CO2`, etc.

---

*This specification ensures seamless integration between the mannito-controller and Home Assistant. Implementing all required endpoints according to this specification will provide full compatibility with the Home Assistant integration.*