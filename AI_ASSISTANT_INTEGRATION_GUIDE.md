# AI Assistant Integration Guide

## Purpose

This document is specifically designed for AI assistants (like GitHub Copilot) working on the mannito-controller repository. It provides essential information about how the Home Assistant integration expects the controller to behave, enabling seamless development coordination between both systems.

## Critical Integration Points

### 1. API Contract Requirements

The mannito-controller **MUST** implement these exact HTTP endpoints:

```http
GET  /api/config                          # System configuration
GET  /api/device/{device_id}              # Device state query
POST /api/device/{device_id}/on           # Turn device on
POST /api/device/{device_id}/off          # Turn device off  
POST /api/device/{device_id}/value/{1-100} # Set fan speed
GET  /api/sensor/{sensor_id}              # Sensor reading
GET  /api/plugin/{plugin_id}              # Plugin state (optional)
```

### 2. Required Response Formats

#### Configuration Response (/api/config)
```json
{
  "model": "string",
  "firmware_version": "string", 
  "hardware_version": "string",
  "serial_number": "string",
  "manufacturer": "string",
  "name": "string", 
  "uptime": "string",
  "ip_address": "string",
  "devices": [
    {"device_id": "FAN1", "device_name": "Exhaust Fan", "device_type": "FAN"}
  ],
  "sensors": [
    {"sensor_id": "TEMP1", "sensor_name": "Temperature", "sensor_type": "TEMPERATURE"}  
  ],
  "plugins": [
    {"plugin_id": "LIGHT_SCHED", "plugin_name": "Light Scheduler", "plugin_type": "LIGHT_SCHEDULER"}
  ]
}
```

#### Device State Response (/api/device/{id})
```json
{"state": true, "speed": 75}    // For fans
{"state": false}                // For other devices
{}                             // For unavailable devices
```

#### Sensor Reading Response (/api/sensor/{id})
```json
{"value": "23.5", "unit": "°C"}  // With unit
{"value": "6.8"}                 // Without unit
{}                              // For unavailable sensors
```

### 3. Expected Device Types

Use these **exact** string values in device_type field:

| Type | Purpose | Control | Speed Control |
|------|---------|---------|---------------|
| `"FAN"` | Variable speed fans | on/off | 1-100 |
| `"SOLENOID"` | Solenoid valves | on/off | No |
| `"RELAY"` | Power relays | on/off | No |
| `"PUMP"` | Fluid pumps | on/off | No |

### 4. Expected Sensor Types

Use these **exact** string values in sensor_type field:

| Type | Unit | Description |
|------|------|-------------|
| `"TEMPERATURE"` | °C | Air temperature |
| `"HUMIDITY"` | % | Relative humidity |
| `"CO2"` | ppm | CO2 concentration |
| `"PH"` | - | pH level |
| `"EC"` | µS/cm | Electrical conductivity |
| `"WATERLEVEL"` | - | Water level |
| `"WATERFLOW"` | - | Water flow rate |
| `"LEAF_TEMPERATURE"` | °C | Leaf temperature |

## Home Assistant Integration Behavior

### What the Integration Does

1. **Startup Sequence**:
   - Calls `/api/config` to discover devices/sensors
   - Creates Home Assistant entities for each discovered item
   - Starts 30-second polling cycle

2. **Periodic Updates** (every 30 seconds):
   - Polls `/api/device/{id}` for each device
   - Polls `/api/sensor/{id}` for each sensor
   - Updates entity states in Home Assistant

3. **User Commands**:
   - Switch on: `POST /api/device/{id}/on`
   - Switch off: `POST /api/device/{id}/off`
   - Fan speed: `POST /api/device/{id}/value/{speed}`

4. **Error Handling**:
   - HTTP 200 = success
   - HTTP 404 = unknown device/sensor
   - Empty `{}` response = temporarily unavailable
   - Other errors = mark as unavailable

### What the Integration Expects

#### Device Control Responses
- Control commands should return HTTP 200 on success
- No response body needed for control commands
- State changes should be reflected in next state query

#### Device State Consistency
- Device state should persist between calls
- Fan speed should be remembered when turned off/on
- Unavailable devices should return empty `{}`

#### Sensor Reading Behavior
- Sensor values should be current/recent readings
- Values must be returned as strings (even numbers)
- Unavailable sensors should return empty `{}`

## Controller Development Guidelines

### Required Implementation Patterns

#### Device State Management
```python
# Controller should maintain device states
device_states = {
    "FAN1": {"state": True, "speed": 75},
    "VALVE1": {"state": False},
    "PUMP1": {"state": True}
}

# Device control endpoint implementation
@app.route('/api/device/<device_id>/on', methods=['POST'])
def turn_device_on(device_id):
    if device_id in device_states:
        device_states[device_id]["state"] = True
        # For fans, use last known speed or default
        if device_type == "FAN" and "speed" not in device_states[device_id]:
            device_states[device_id]["speed"] = 50  # Default speed
        return '', 200
    return '', 404
```

#### Sensor Reading Management
```python
# Controller should provide current sensor readings
sensor_readings = {
    "TEMP1": {"value": "23.5", "unit": "°C"},
    "HUM1": {"value": "65", "unit": "%"},
    "CO2_1": {"value": "450", "unit": "ppm"}
}

# Sensor reading endpoint implementation  
@app.route('/api/sensor/<sensor_id>', methods=['GET'])
def get_sensor_reading(sensor_id):
    if sensor_id in sensor_readings:
        return jsonify(sensor_readings[sensor_id])
    return '', 404
```

### Configuration Management

#### Dynamic Configuration
```python
# Controller should maintain current device/sensor configuration
config = {
    "model": "Mannito Controller v1.0",
    "firmware_version": "1.2.3",
    "devices": [],  # Populate with actual devices
    "sensors": [],  # Populate with actual sensors
    "plugins": []   # Optional plugin systems
}

# Add devices dynamically
def add_device(device_id, device_name, device_type):
    config["devices"].append({
        "device_id": device_id,
        "device_name": device_name,
        "device_type": device_type
    })
```

### Error Handling Patterns

#### Graceful Degradation
```python
# Handle temporary device failures gracefully
@app.route('/api/device/<device_id>', methods=['GET'])  
def get_device_state(device_id):
    try:
        # Attempt to read actual device state
        actual_state = hardware.read_device_state(device_id)
        return jsonify(actual_state)
    except HardwareError:
        # Return empty response for temporary failures
        return jsonify({})  # Integration will mark as unavailable
    except DeviceNotFound:
        return '', 404      # Permanent error
```

#### Authentication Support
```python
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    # Implement credential verification
    return check_credentials(username, password)

@app.route('/api/config')
@auth.login_required  # Apply to all endpoints if auth enabled
def get_config():
    return jsonify(config)
```

## Common Development Patterns

### Device ID Conventions
The integration works with any device IDs, but these patterns are recommended:
```python
# Recommended device ID patterns
fan_ids = ["FAN1", "FAN2", "FAN3", ...]       # Up to FAN10
valve_ids = ["VALVE1", "VALVE2", ...]         # Up to VALVE5  
relay_ids = ["RELAY1", "RELAY2", ...]         # Up to RELAY8
pump_ids = ["PUMP1", "PUMP2", ...]            # Up to PUMP4

# Sensor ID patterns
sensor_ids = ["TEMP1", "HUM1", "CO2_1", "PH1", ...]
```

### State Persistence
```python
# Persist device states across controller restarts
import json

def save_device_states():
    with open('device_states.json', 'w') as f:
        json.dump(device_states, f)

def load_device_states():
    try:
        with open('device_states.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}  # Default empty state
```

### Speed Control Implementation
```python
# Fan speed control implementation
@app.route('/api/device/<device_id>/value/<int:speed>', methods=['POST'])
def set_fan_speed(device_id, speed):
    if device_id not in device_states:
        return '', 404
        
    if not (1 <= speed <= 100):
        return '', 400  # Invalid speed range
        
    # Setting speed automatically turns fan on
    device_states[device_id]["state"] = True
    device_states[device_id]["speed"] = speed
    
    # Send command to actual hardware
    hardware.set_fan_speed(device_id, speed)
    
    return '', 200
```

## Testing and Validation

### Required Test Endpoints

Before deploying, ensure these tests pass:

```bash
# Test configuration discovery
curl -X GET http://controller/api/config | jq

# Test device control
curl -X POST http://controller/api/device/FAN1/on
curl -X GET http://controller/api/device/FAN1 | jq

# Test fan speed control  
curl -X POST http://controller/api/device/FAN1/value/75
curl -X GET http://controller/api/device/FAN1 | jq

# Test sensor reading
curl -X GET http://controller/api/sensor/TEMP1 | jq
```

### Integration Testing

1. **Start the controller with sample devices/sensors**
2. **Add the integration in Home Assistant** 
3. **Verify all entities are created correctly**
4. **Test device controls from HA interface**
5. **Verify sensor readings update every 30 seconds**

## Key Success Criteria

✅ **Configuration endpoint returns valid JSON with all required fields**  
✅ **All declared devices respond to state queries**  
✅ **Device control commands work and persist state**  
✅ **Fan speed control works correctly (1-100 range)**  
✅ **Sensor readings return current values**  
✅ **HTTP status codes are correct (200/404/500)**  
✅ **Empty responses `{}` used for temporary unavailability**  
✅ **Authentication works if implemented**  
✅ **API responds within required timeouts (2-5 seconds)**

## Common Pitfalls to Avoid

❌ **Don't return null/undefined in JSON responses**  
❌ **Don't use different case for device/sensor types (must be UPPERCASE)**  
❌ **Don't forget to implement empty `{}` responses for unavailable devices**  
❌ **Don't return errors for temporary device failures - use empty responses**  
❌ **Don't implement speed control for non-fan devices**  
❌ **Don't forget to make speed setting turn the device on**  
❌ **Don't use inconsistent device IDs between configuration and control**

## Integration Troubleshooting

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Devices not discovered | Missing `/api/config` endpoint | Implement configuration endpoint |
| Entities show as unavailable | Control endpoints return errors | Return empty `{}` for temporary failures |
| Fan speed doesn't work | Missing `/value/{speed}` endpoint | Implement speed control for fans |
| States don't update | Wrong response format | Check JSON response format |
| Authentication fails | Missing Basic Auth support | Implement HTTP Basic Auth |

---

*This guide ensures that mannito-controller development is perfectly aligned with Home Assistant integration expectations, enabling seamless operation of both systems.*