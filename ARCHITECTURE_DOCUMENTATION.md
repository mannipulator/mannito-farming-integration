# Mannito Farming Home Assistant Integration - Architecture Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Architecture](#core-architecture)
3. [API Interface Documentation](#api-interface-documentation)
4. [Data Models](#data-models)
5. [Core Classes](#core-classes)
6. [Platform Implementations](#platform-implementations)
7. [Integration Workflow](#integration-workflow)
8. [Configuration and Setup](#configuration-and-setup)

## System Overview

The Mannito Farming Home Assistant Integration is a custom integration that provides seamless communication between Home Assistant and the separate mannito-controller system. The integration enables Home Assistant to control and monitor farming devices through a well-defined REST API interface.

### System Components

- **Home Assistant Integration** (this repository): Provides the interface between Home Assistant and the controller
- **Mannito Controller** (separate repository): Physical/software controller that manages farming hardware
- **Communication Protocol**: REST API over HTTP with optional Basic Authentication

### Supported Device Types

- **Fans (10 units)**: Variable speed control (0-100%) with on/off capability
- **Solenoid Valves (5 units)**: On/off control for water flow management  
- **Relays (8 units)**: On/off control for power management
- **Pumps (4 units)**: On/off control for fluid management
- **Sensors**: Environmental monitoring (temperature, humidity, CO2, pH, EC, water levels, etc.)
- **Plugins**: Advanced control systems (schedulers, controllers, simulators)

## Core Architecture

The integration follows Home Assistant's standard patterns with a coordinator-based architecture for efficient data management and API communication.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Home Assistant Core                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Switch    │  │     Fan     │  │   Sensor    │  │  Light  │ │
│  │  Platform   │  │  Platform   │  │  Platform   │  │Platform │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                MannitoFarmingDataUpdateCoordinator              │
├─────────────────────────────────────────────────────────────────┤
│                         API Client                              │
├─────────────────────────────────────────────────────────────────┤
│                    HTTP REST API                                │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Mannito Controller                           │
│              (External System)                                 │
└─────────────────────────────────────────────────────────────────┘
```

## API Interface Documentation

### Base API Structure

The integration communicates with the mannito-controller through HTTP REST API endpoints. All endpoints are relative to the controller's base URL: `http://{CONTROLLER_HOST}/`

### Authentication

- **Type**: HTTP Basic Authentication (optional)
- **Headers**: `Authorization: Basic {base64(username:password)}`
- **Fallback**: No authentication if credentials not provided

### Core API Endpoints

#### Device Control Endpoints

| Method | Endpoint | Purpose | Expected Response |
|--------|----------|---------|-------------------|
| `GET` | `/api/device/{device_id}` | Get device state | `{"state": boolean, "speed": int}` |
| `POST` | `/api/device/{device_id}/on` | Turn device on | HTTP 200 on success |
| `POST` | `/api/device/{device_id}/off` | Turn device off | HTTP 200 on success |
| `POST` | `/api/device/{device_id}/value/{speed}` | Set fan speed | HTTP 200 on success |

#### Sensor Data Endpoints

| Method | Endpoint | Purpose | Expected Response |
|--------|----------|---------|-------------------|
| `GET` | `/api/sensor/{sensor_id}` | Get sensor reading | `{"value": string, "unit": string}` |

#### Plugin Control Endpoints

| Method | Endpoint | Purpose | Expected Response |
|--------|----------|---------|-------------------|
| `GET` | `/api/plugin/{plugin_id}` | Get plugin state | `{"state": boolean, "config": object}` |

#### Configuration Endpoints

| Method | Endpoint | Purpose | Expected Response |
|--------|----------|---------|-------------------|
| `GET` | `/api/config` | Get full configuration | Device, sensor, and plugin definitions |

### Expected Configuration Response Format

The controller must respond to `/api/config` with a JSON structure containing device, sensor, and plugin definitions:

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
    {
      "device_id": "FAN1",
      "device_name": "Exhaust Fan 1", 
      "device_type": "FAN"
    }
  ],
  "sensors": [
    {
      "sensor_id": "TEMP1",
      "sensor_name": "Temperature Sensor 1",
      "sensor_type": "TEMPERATURE"
    }
  ],
  "plugins": [
    {
      "plugin_id": "LIGHT_SCHED",
      "plugin_name": "Light Scheduler",
      "plugin_type": "LIGHT_SCHEDULER"
    }
  ]
}
```

## Data Models

### Device Types Enumeration

```python
class DeviceType(StrEnum):
    FAN = "FAN"           # Variable speed fans
    RELAY = "RELAY"       # On/off relays  
    SOLENOID = "SOLENOID" # Solenoid valves
    PUMP = "PUMP"         # Water/nutrient pumps
    OTHER = "OTHER"       # Undefined device types
```

### Sensor Types Enumeration

```python
class SensorType(StrEnum):
    HUMIDITY = "HUMIDITY"                    # Relative humidity (%)
    TEMPERATURE = "TEMPERATURE"              # Temperature (°C)
    CO2 = "CO2"                             # CO2 concentration (ppm)
    WATERLEVEL = "WATERLEVEL"               # Water level
    WATERFLOW = "WATERFLOW"                 # Water flow rate
    LEAF_TEMPERATURE = "LEAF_TEMPERATURE"    # Leaf temperature (°C)
    PH = "PH"                               # pH level (0-14)
    EC = "EC"                               # Electrical conductivity
    OTHER = "OTHER"                         # Undefined sensor types
```

### Plugin Types Enumeration

```python
class PluginType(StrEnum):
    LIGHT_SCHEDULER = "LIGHT_SCHEDULER"           # Lighting control
    DEVICE_SCHEDULER = "DEVICE_SCHEDULER"         # Device automation
    TEMPERATURE_CONTROLLER = "TEMPERATURE_CONTROLLER" # Climate control
    WIND_SIMULATOR = "WIND_SIMULATOR"             # Ventilation control
    WATER_CONTROLLER = "WATER_CONTROLLER"         # Irrigation control
    OTHER = "OTHER"                               # Undefined plugin types
```

### Core Data Classes

#### Device Data Model

```python
@dataclass
class Device:
    """Represents a controllable device in the farming system."""
    device_id: str              # Unique identifier
    device_unique_id: str       # Home Assistant unique ID
    device_type: DeviceType     # Type of device
    name: str                   # Human-readable name
    state: bool = False         # Current on/off state
    speed: Optional[int] = None # Current speed (fans only)
    available: bool = True      # Device availability status
```

#### Sensor Data Model

```python
@dataclass  
class Sensor:
    """Represents a sensor in the farming system."""
    sensor_id: str              # Unique identifier
    sensor_unique_id: str       # Home Assistant unique ID
    sensor_type: SensorType     # Type of sensor
    name: str                   # Human-readable name
    state_value: str = ""       # Current sensor reading
    available: bool = True      # Sensor availability status
```

#### Plugin Data Model

```python
@dataclass
class Plugin:
    """Represents a plugin/controller in the farming system."""
    plugin_id: str              # Unique identifier
    plugin_unique_id: str       # Home Assistant unique ID
    plugin_type: PluginType     # Type of plugin
    name: str                   # Human-readable name
    state: bool = False         # Current active state
    available: bool = True      # Plugin availability status
```

## Core Classes

### API Client Class

**File**: `custom_components/mannito_farming/api.py`

```python
class API:
    """API class to handle communication with the Mannito Farming controller."""
```

**Purpose**: Manages all HTTP communication with the mannito-controller, including device control, sensor reading, and configuration retrieval.

**Key Attributes**:
- `host: str` - Controller IP address or hostname
- `auth: BasicAuth` - Authentication credentials (optional)
- `session: ClientSession` - aiohttp session for HTTP requests
- `connected: bool` - Connection status
- `device_info: Dict[str, Any]` - Cached device information

**Key Methods**:

#### Connection Management
- `async_test_connection() -> bool` - Test connectivity to controller
- `fetch_device_config() -> Dict[str, Any]` - Retrieve full configuration
- `get_device_info() -> Dict[str, Any]` - Get cached device information

#### Device Control  
- `set_device_state(component_name: str, state: bool) -> bool` - Control device on/off
- `set_fan_speed(component_name: str, speed: int) -> bool` - Control fan speed
- `get_device_state(component_name: str) -> Dict[str, Any]` - Read device state

#### Sensor Reading
- `get_sensor_state(component_name: str) -> Dict[str, Any]` - Read sensor values

#### Plugin Management
- `get_plugin_state(plugin_name: str) -> Dict[str, Any]` - Read plugin state

#### Discovery
- `discover_devices() -> List[Device]` - Discover available devices
- `discover_sensors() -> List[Sensor]` - Discover available sensors

**Error Handling**:
- `APIConnectionError` - Raised for network/connectivity issues
- `APIAuthError` - Raised for authentication failures

### Data Update Coordinator

**File**: `custom_components/mannito_farming/coordinator.py`

```python
class MannitoFarmingDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Class to manage fetching data from the Mannito Farming controller."""
```

**Purpose**: Centralized data management and periodic updates from the controller. Implements Home Assistant's coordinator pattern for efficient data sharing between platforms.

**Key Attributes**:
- `hass: HomeAssistant` - Home Assistant instance
- `config_entry: ConfigEntry` - Integration configuration
- `host: str` - Controller hostname/IP
- `api: API` - API client instance
- `_devices: Dict[str, Device]` - Cached device states
- `_sensors: Dict[str, Sensor]` - Cached sensor states
- `device_info: Dict[str, Any]` - Device information cache

**Key Methods**:

#### Data Management
- `_async_update_data() -> Dict[str, Any]` - Periodic data refresh (every 30 seconds)
- `discover_and_update_devices() -> None` - Discover and cache all devices/sensors

#### Device Access
- `get_device(device_id: str) -> Optional[Device]` - Retrieve specific device
- `get_all_devices() -> List[Device]` - Get all known devices
- `get_sensor(sensor_id: str) -> Optional[Sensor]` - Retrieve specific sensor  
- `get_all_sensors() -> List[Sensor]` - Get all known sensors

#### Device Control
- `async_set_device_state(device_id: str, state: bool) -> bool` - Control device state
- `async_set_fan_speed(device_id: str, speed: int) -> bool` - Control fan speed

#### Device Information
- `get_device_info() -> DeviceInfo` - Get Home Assistant device info

**Update Cycle**:
1. Discovery phase: Fetch device/sensor configuration from controller
2. State update phase: Poll each device and sensor for current state
3. Availability tracking: Mark devices as available/unavailable based on response
4. Error handling: Handle network errors and mark devices unavailable

### Configuration Flow

**File**: `custom_components/mannito_farming/config_flow.py`

```python
class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mannito Farming."""
```

**Purpose**: Manages the integration setup process, including manual configuration and automatic discovery via mDNS/Zeroconf.

**Key Attributes**:
- `VERSION = 1` - Configuration version
- `CONNECTION_CLASS = CONN_CLASS_LOCAL_POLL` - Local polling connection

**Key Methods**:

#### Setup Steps
- `async_step_user(user_input) -> FlowResult` - Manual configuration entry
- `async_step_zeroconf(discovery_info) -> FlowResult` - Automatic discovery
- `async_step_confirm(user_input) -> FlowResult` - Confirm discovered device

#### Validation
- `_test_connection() -> FlowResult` - Validate controller connectivity

**Configuration Schema**:
```python
STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): str,           # Controller IP/hostname
    vol.Optional(CONF_USERNAME): str,       # Optional username
    vol.Optional(CONF_PASSWORD): str,       # Optional password
})
```

**Discovery Support**:
- mDNS service type: `_mannito-farming._tcp.local.`
- Automatic configuration when controller is discoverable

## Platform Implementations

### Switch Platform

**File**: `custom_components/mannito_farming/switch.py`

**Purpose**: Implements Home Assistant switch entities for on/off device control (valves, relays, pumps).

#### MannitoFarmingSwitch Class

```python
class MannitoFarmingSwitch(CoordinatorEntity[MannitoFarmingDataUpdateCoordinator], SwitchEntity):
    """Representation of a Mannito Farming switch."""
```

**Supported Device Types**:
- **Solenoid Valves**: 5 units for irrigation control
- **Relays**: 8 units for power management  
- **Pumps**: 4 units for fluid circulation

**Key Properties**:
- `is_on: bool` - Current switch state
- `available: bool` - Device availability
- `icon: str` - Dynamic icon based on state and type
- `device_info: DeviceInfo` - Device registration info

**Key Methods**:
- `async_turn_on(**kwargs)` - Turn device on
- `async_turn_off(**kwargs)` - Turn device off
- `_handle_coordinator_update()` - React to data updates

**Entity Descriptions**:
Each device type has predefined entity descriptions with appropriate icons:
- Valves: `mdi:water` / `mdi:water-off`
- Relays: `mdi:power-plug` / `mdi:power-plug-off`
- Pumps: `mdi:pump` / `mdi:pump-off`

### Fan Platform

**File**: `custom_components/mannito_farming/fan.py`

**Purpose**: Implements Home Assistant fan entities for variable speed control of ventilation fans.

#### MannitoFarmingFan Class

```python
class MannitoFarmingFan(CoordinatorEntity[MannitoFarmingDataUpdateCoordinator], FanEntity):
    """Representation of a Mannito Farming fan."""
```

**Supported Features**:
- `FanEntityFeature.SET_SPEED` - Variable speed control
- Speed range: 1-100%
- On/off control

**Key Properties**:
- `is_on: bool` - Fan running state
- `percentage: int` - Current speed percentage
- `speed_count: int` - Number of discrete speed levels (100)
- `supported_features` - SET_SPEED capability

**Key Methods**:
- `async_turn_on(percentage, **kwargs)` - Start fan at specified speed
- `async_turn_off(**kwargs)` - Stop fan
- `async_set_percentage(percentage)` - Set specific speed percentage

**Speed Conversion**:
- Internal range: 1-100 (controller format)
- Home Assistant percentage: 0-100%
- Conversion utilities handle mapping between formats

### Sensor Platform

**File**: `custom_components/mannito_farming/sensor.py`

**Purpose**: Implements Home Assistant sensor entities for environmental monitoring.

#### MannitoFarmingSensor Class

```python
class MannitoFarmingSensor(CoordinatorEntity[MannitoFarmingDataUpdateCoordinator], SensorEntity):
    """Representation of a Mannito Farming sensor."""
```

**Supported Sensor Types**:

| Type | Device Class | Unit | Description |
|------|-------------|------|-------------|
| CO2 | `SensorDeviceClass.CO2` | ppm | CO2 concentration |
| TEMPERATURE | `SensorDeviceClass.TEMPERATURE` | °C | Air temperature |
| HUMIDITY | `SensorDeviceClass.HUMIDITY` | % | Relative humidity |
| PH | `SensorDeviceClass.PH` | - | pH level |
| EC | - | - | Electrical conductivity |
| WATERLEVEL | - | - | Water level |
| WATERFLOW | - | - | Water flow rate |
| LEAF_TEMPERATURE | `SensorDeviceClass.TEMPERATURE` | °C | Leaf temperature |

**Key Properties**:
- `native_value: str` - Current sensor reading
- `device_class: str` - Home Assistant device class
- `unit_of_measurement: str` - Measurement unit
- `state_class: str` - State class for historical data

**Entity Descriptions**:
Pre-configured descriptions with appropriate device classes and units for each sensor type.

### Light Platform

**File**: `custom_components/mannito_farming/light.py`

**Purpose**: Implements Home Assistant light entities for grow light control (future functionality).

#### GrowControllerLight Class

```python
class GrowControllerLight(LightEntity):
    """Representation of a Mannito Farming light."""
```

**Current Status**: Placeholder implementation for future lighting control features.

**Supported Features**:
- `ColorMode.BRIGHTNESS` - Brightness control
- Basic on/off control

## Integration Workflow

### Setup and Initialization

1. **Entry Point** (`__init__.py`):
   ```python
   async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool
   ```
   - Creates coordinator instance
   - Performs initial data refresh
   - Forwards setup to all platforms
   - Registers update listener

2. **Coordinator Initialization**:
   - Establishes API connection
   - Discovers devices and sensors
   - Starts periodic update cycle (30-second interval)

3. **Platform Setup**:
   - Each platform queries coordinator for relevant entities
   - Creates entity instances based on discovered devices
   - Registers entities with Home Assistant

### Data Flow

```
Controller → API → Coordinator → Platforms → Home Assistant
     ↑                                              ↓
     └─────────── Device Commands ←─────────────────┘
```

1. **Data Retrieval**:
   - Coordinator polls controller every 30 seconds
   - Updates device states and sensor values
   - Marks devices as available/unavailable

2. **Command Execution**:
   - User interactions trigger platform methods
   - Platforms call coordinator control methods
   - Coordinator uses API to send commands to controller
   - State updates reflected in next polling cycle

### Error Handling

1. **Connection Errors**:
   - API methods raise `APIConnectionError`
   - Coordinator marks devices as unavailable
   - Entities show as unavailable in Home Assistant

2. **Authentication Errors**:
   - API methods raise `APIAuthError` 
   - Configuration flow shows authentication error
   - User prompted to verify credentials

3. **Device Errors**:
   - Individual device failures don't affect others
   - Unavailable devices marked with `available = False`
   - Coordinator continues polling other devices

### Update Lifecycle

1. **Discovery Phase** (startup and periodic):
   - Fetch `/api/config` from controller
   - Parse device, sensor, and plugin definitions
   - Create or update entity registry

2. **State Update Phase** (every 30 seconds):
   - Poll each device: `GET /api/device/{device_id}`
   - Poll each sensor: `GET /api/sensor/{sensor_id}`  
   - Update cached states and availability

3. **Command Phase** (on-demand):
   - Process user commands from Home Assistant
   - Send control commands to controller
   - Update local state cache immediately

## Configuration and Setup

### Integration Constants

**File**: `custom_components/mannito_farming/const.py`

```python
DOMAIN = "mannito_farming"                    # Integration domain
PLATFORMS = [Platform.SWITCH, Platform.FAN, Platform.SENSOR]  # Supported platforms
DEFAULT_UPDATE_INTERVAL = 30                 # Update frequency (seconds)
MDNS_SERVICE_TYPE = "_mannito-farming._tcp.local."  # Discovery service
```

### Device Capacity

```python
VALVE_COUNT = 5      # Solenoid valves
FAN_COUNT = 10       # Variable speed fans  
RELAY_COUNT = 8      # Power relays
PUMP_COUNT = 4       # Fluid pumps
```

### Entry Configuration

The integration stores the following configuration data:

```python
{
    CONF_HOST: "192.168.1.100",      # Controller IP/hostname
    CONF_USERNAME: "admin",          # Optional authentication
    CONF_PASSWORD: "password"        # Optional authentication  
}
```

### Home Assistant Device Registration

Each controller appears as a single device in Home Assistant with:

```python
DeviceInfo(
    identifiers={(DOMAIN, host)},
    name=device_name,
    manufacturer="Mannito",
    model=model_info,
    sw_version=firmware_version,
    hw_version=hardware_version,
    serial_number=serial_number,
    configuration_url=f"http://{host}"
)
```

All entities (switches, fans, sensors) are associated with this single device for logical grouping in the Home Assistant interface.

---

*This documentation serves as a comprehensive reference for both the Home Assistant integration and the mannito-controller system, enabling seamless coordination and development between both components.*