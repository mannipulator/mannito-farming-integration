# Mannito Farming Integration - Class Reference

## Quick Class Overview

This document provides a comprehensive reference of all classes, data structures, and their relationships within the Mannito Farming Home Assistant integration.

## Core Integration Classes

### Entry Point Module (`__init__.py`)

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `async_setup_entry()` | Initialize integration | `hass`, `entry: ConfigEntry` | `bool` |
| `async_unload_entry()` | Clean up integration | `hass`, `entry: ConfigEntry` | `bool` |
| `async_update_options()` | Handle option updates | `hass`, `entry: ConfigEntry` | `None` |

## Data Models (`api.py`)

### Enumerations

#### DeviceType
```python
class DeviceType(StrEnum):
    FAN = "FAN"                    # Variable speed fans (1-100%)
    RELAY = "RELAY"                # On/off power relays  
    SOLENOID = "SOLENOID"          # On/off solenoid valves
    PUMP = "PUMP"                  # On/off fluid pumps
    OTHER = "OTHER"                # Undefined device types
    
    @classmethod
    def parse(cls, value: str) -> "DeviceType"  # Parse string to enum
```

#### SensorType
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
    OTHER = "OTHER"                         # Undefined types
    
    @classmethod
    def parse(cls, value: str) -> "SensorType"  # Parse string to enum
```

#### PluginType
```python
class PluginType(StrEnum):
    LIGHT_SCHEDULER = "LIGHT_SCHEDULER"           # Lighting automation
    DEVICE_SCHEDULER = "DEVICE_SCHEDULER"         # Device automation
    TEMPERATURE_CONTROLLER = "TEMPERATURE_CONTROLLER" # Climate control
    WIND_SIMULATOR = "WIND_SIMULATOR"             # Ventilation control
    WATER_CONTROLLER = "WATER_CONTROLLER"         # Irrigation control
    OTHER = "OTHER"                               # Undefined types
    
    @classmethod
    def parse(cls, value: str) -> "PluginType"    # Parse string to enum
```

### Data Classes

#### Device
```python
@dataclass
class Device:
    device_id: str              # Unique identifier (e.g., "FAN1")
    device_unique_id: str       # HA unique ID (e.g., "192.168.1.100_FAN1")
    device_type: DeviceType     # Type enumeration
    name: str                   # Human-readable name
    state: bool = False         # Current on/off state
    speed: Optional[int] = None # Current speed (fans only, 1-100)
    available: bool = True      # Device availability status
```

#### Sensor
```python
@dataclass  
class Sensor:
    sensor_id: str              # Unique identifier (e.g., "TEMP1")
    sensor_unique_id: str       # HA unique ID (e.g., "192.168.1.100_TEMP1")
    sensor_type: SensorType     # Type enumeration
    name: str                   # Human-readable name
    state_value: str = ""       # Current reading as string
    available: bool = True      # Sensor availability status
```

#### Plugin
```python
@dataclass
class Plugin:
    plugin_id: str              # Unique identifier (e.g., "LIGHT_SCHED")
    plugin_unique_id: str       # HA unique ID
    plugin_type: PluginType     # Type enumeration
    name: str                   # Human-readable name
    state: bool = False         # Current active state
    available: bool = True      # Plugin availability status
```

### Exception Classes

#### APIConnectionError
```python
class APIConnectionError(Exception):
    """Raised when API connection fails."""
    # Usage: Network timeouts, HTTP errors, unreachable controller
```

#### APIAuthError
```python
class APIAuthError(Exception):
    """Raised when API authentication fails."""
    # Usage: Invalid credentials, 401/403 responses
```

## Core API Client (`api.py`)

### API Class
```python
class API:
    """Handles all HTTP communication with mannito-controller."""
    
    # Attributes
    host: str                   # Controller IP/hostname
    auth: BasicAuth            # HTTP Basic Auth (optional)
    session: ClientSession     # aiohttp session
    connected: bool            # Connection status
    device_info: Dict[str, Any] # Cached device information
```

#### Connection Management Methods
| Method | Purpose | Parameters | Returns | Exceptions |
|--------|---------|------------|---------|------------|
| `async_test_connection()` | Test controller connectivity | None | `bool` | None |
| `fetch_device_config()` | Get full configuration | None | `Dict[str, Any]` | `APIConnectionError` |
| `get_device_info()` | Get cached device info | None | `Dict[str, Any]` | None |

#### Device Control Methods
| Method | Purpose | Parameters | Returns | Exceptions |
|--------|---------|------------|---------|------------|
| `set_device_state()` | Control device on/off | `component_name: str`, `state: bool` | `bool` | None |
| `set_fan_speed()` | Control fan speed | `component_name: str`, `speed: int` | `bool` | None |
| `get_device_state()` | Read device state | `component_name: str` | `Dict[str, Any]` | `APIConnectionError` |

#### Sensor Reading Methods
| Method | Purpose | Parameters | Returns | Exceptions |
|--------|---------|------------|---------|------------|
| `get_sensor_state()` | Read sensor value | `component_name: str` | `Dict[str, Any]` | `APIConnectionError` |

#### Plugin Management Methods
| Method | Purpose | Parameters | Returns | Exceptions |
|--------|---------|------------|---------|------------|
| `get_plugin_state()` | Read plugin state | `plugin_name: str` | `Dict[str, Any]` | `APIConnectionError` |

#### Discovery Methods
| Method | Purpose | Parameters | Returns | Exceptions |
|--------|---------|------------|---------|------------|
| `discover_devices()` | Find all devices | None | `List[Device]` | `APIConnectionError` |
| `discover_sensors()` | Find all sensors | None | `List[Sensor]` | None |

## Data Update Coordinator (`coordinator.py`)

### MannitoFarmingDataUpdateCoordinator
```python
class MannitoFarmingDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    """Manages data updates and caching for the integration."""
    
    # Attributes
    hass: HomeAssistant                    # HA instance
    config_entry: ConfigEntry              # Integration config
    host: str                              # Controller hostname
    username: Optional[str]                # Auth username
    password: Optional[str]                # Auth password
    session: ClientSession                 # HTTP session
    api: API                              # API client instance
    _devices: Dict[str, Device]           # Device cache
    _sensors: Dict[str, Sensor]           # Sensor cache
    device_info: Dict[str, Any]           # Device info cache
```

#### Data Management Methods
| Method | Purpose | Parameters | Returns | Exceptions |
|--------|---------|------------|---------|------------|
| `_async_update_data()` | Periodic data refresh | None | `Dict[str, Any]` | `UpdateFailed` |
| `discover_and_update_devices()` | Device discovery | None | `None` | None |

#### Device Access Methods
| Method | Purpose | Parameters | Returns |
|--------|---------|------------|---------|
| `get_device()` | Get specific device | `device_id: str` | `Optional[Device]` |
| `get_all_devices()` | Get all devices | None | `List[Device]` |
| `get_sensor()` | Get specific sensor | `sensor_id: str` | `Optional[Sensor]` |
| `get_all_sensors()` | Get all sensors | None | `List[Sensor]` |

#### Device Control Methods
| Method | Purpose | Parameters | Returns |
|--------|---------|------------|---------|
| `async_set_device_state()` | Control device | `device_id: str`, `state: bool` | `bool` |
| `async_set_fan_speed()` | Control fan speed | `device_id: str`, `speed: int` | `bool` |

#### Device Information Methods
| Method | Purpose | Parameters | Returns |
|--------|---------|------------|---------|
| `get_device_info()` | Get HA device info | None | `DeviceInfo` |

## Configuration Flow (`config_flow.py`)

### ConfigFlow
```python
class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handles integration setup and configuration."""
    
    # Class Attributes
    VERSION = 1                           # Config version
    CONNECTION_CLASS = CONN_CLASS_LOCAL_POLL  # Connection type
    
    # Instance Attributes  
    _host: Optional[str]                  # Discovered/entered host
    _username: Optional[str]              # Authentication username
    _password: Optional[str]              # Authentication password
```

#### Configuration Steps
| Method | Purpose | Parameters | Returns |
|--------|---------|------------|---------|
| `async_step_user()` | Manual configuration | `user_input: Optional[Dict]` | `FlowResult` |
| `async_step_zeroconf()` | Auto discovery | `discovery_info: Dict` | `FlowResult` |
| `async_step_confirm()` | Confirm discovery | `user_input: Optional[Dict]` | `FlowResult` |

#### Validation Methods
| Method | Purpose | Parameters | Returns |
|--------|---------|------------|---------|
| `_test_connection()` | Validate connectivity | None | `FlowResult` |

## Platform Implementations

### Switch Platform (`switch.py`)

#### MannitoFarmingSwitchEntityDescription
```python
@dataclass
class MannitoFarmingSwitchEntityDescription(SwitchEntityDescription):
    """Entity description for switch devices."""
    
    device_type: str = ""         # Device type identifier
    icon_on: str | None = None    # Icon when on
    icon_off: str | None = None   # Icon when off
```

#### MannitoFarmingSwitch
```python
class MannitoFarmingSwitch(CoordinatorEntity, SwitchEntity):
    """Switch entity for on/off devices (valves, relays, pumps)."""
    
    # Attributes
    coordinator: MannitoFarmingDataUpdateCoordinator  # Data coordinator
    _device_id: str                                   # Device identifier
    entity_description: MannitoFarmingSwitchEntityDescription  # Entity config
```

#### Switch Entity Properties
| Property | Purpose | Returns | Notes |
|----------|---------|---------|-------|
| `is_on` | Current switch state | `bool` | Based on device.state |
| `available` | Entity availability | `bool` | Based on device availability |
| `icon` | Dynamic icon | `str` | Changes based on state |
| `device_info` | Device registration | `DeviceInfo` | Links to controller device |

#### Switch Control Methods
| Method | Purpose | Parameters | Returns |
|--------|---------|------------|---------|
| `async_turn_on()` | Turn device on | `**kwargs` | `None` |
| `async_turn_off()` | Turn device off | `**kwargs` | `None` |
| `_handle_coordinator_update()` | Process data updates | None | `None` |

### Fan Platform (`fan.py`)

#### MannitoFarmingFanEntityDescription
```python
@dataclass
class MannitoFarmingFanEntityDescription(FanEntityDescription):
    """Entity description for fan devices."""
    
    device_type: str = DEVICE_TYPE_FAN    # Device type
    icon_on: str | None = None            # Icon when running
    icon_off: str | None = None           # Icon when stopped
```

#### MannitoFarmingFan
```python
class MannitoFarmingFan(CoordinatorEntity, FanEntity):
    """Fan entity for variable speed control."""
    
    # Attributes
    coordinator: MannitoFarmingDataUpdateCoordinator  # Data coordinator
    _device_id: str                                   # Device identifier
    entity_description: MannitoFarmingFanEntityDescription  # Entity config
    
    # Constants
    SPEED_RANGE = (1, 100)                           # Internal speed range
    _attr_supported_features = FanEntityFeature.SET_SPEED  # Supported features
    _attr_speed_count = 100                          # Discrete speed levels
```

#### Fan Entity Properties
| Property | Purpose | Returns | Notes |
|----------|---------|---------|-------|
| `is_on` | Fan running state | `bool` | Based on device.state |
| `percentage` | Current speed % | `Optional[int]` | 0-100 or None if off |
| `speed_count` | Speed levels | `int` | Always 100 |
| `available` | Entity availability | `bool` | Based on device availability |

#### Fan Control Methods
| Method | Purpose | Parameters | Returns |
|--------|---------|------------|---------|
| `async_turn_on()` | Start fan | `percentage: Optional[int]`, `**kwargs` | `None` |
| `async_turn_off()` | Stop fan | `**kwargs` | `None` |
| `async_set_percentage()` | Set speed | `percentage: int` | `None` |

### Sensor Platform (`sensor.py`)

#### MannitoFarmingSensorEntityDescription
```python
@dataclass
class MannitoFarmingSensorEntityDescription(SensorEntityDescription):
    """Entity description for sensors."""
    
    device_class: str = ""                      # HA device class
    native_unit_of_measurement: str | None = None  # Measurement unit
    state_class: str = ""                       # State class for history
```

#### MannitoFarmingSensor
```python
class MannitoFarmingSensor(CoordinatorEntity, SensorEntity):
    """Sensor entity for environmental monitoring."""
    
    # Attributes
    coordinator: MannitoFarmingDataUpdateCoordinator  # Data coordinator
    _device_id: str                                   # Sensor identifier
    entity_description: MannitoFarmingSensorEntityDescription  # Entity config
```

#### Sensor Entity Properties
| Property | Purpose | Returns | Notes |
|----------|---------|---------|-------|
| `native_value` | Current reading | `str | None` | Raw sensor value |
| `available` | Entity availability | `bool` | Based on sensor availability |
| `device_info` | Device registration | `DeviceInfo` | Links to controller device |

### Light Platform (`light.py`)

#### GrowControllerLight
```python
class GrowControllerLight(LightEntity):
    """Light entity for grow light control (future feature)."""
    
    # Attributes
    coordinator: MannitoFarmingDataUpdateCoordinator  # Data coordinator
    _device_id: str                                   # Light identifier
    _name: str                                        # Light name
    
    # Supported Features
    _attr_color_mode = ColorMode.BRIGHTNESS          # Brightness control
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}  # Color modes
```

## Constants and Configuration (`const.py`)

### Domain Configuration
```python
DOMAIN = "mannito_farming"                    # Integration domain
PLATFORMS = [Platform.SWITCH, Platform.FAN, Platform.SENSOR]  # Active platforms
```

### Update Configuration
```python
DEFAULT_UPDATE_INTERVAL = 30                 # Update frequency (seconds)
```

### Discovery Configuration
```python
MDNS_SERVICE_TYPE = "_mannito-farming._tcp.local."  # mDNS service type
```

### Device Type Constants
```python
DEVICE_TYPE_VALVE = "valve"                   # Valve type identifier
DEVICE_TYPE_FAN = "fan"                       # Fan type identifier  
DEVICE_TYPE_RELAY = "relay"                   # Relay type identifier
DEVICE_TYPE_PUMP = "pump"                     # Pump type identifier
```

### Device Capacity Constants
```python
VALVE_COUNT = 5                               # Number of valves
FAN_COUNT = 10                                # Number of fans
RELAY_COUNT = 8                               # Number of relays
PUMP_COUNT = 4                                # Number of pumps
```

## Entity Description Maps

### Switch Entity Descriptions
```python
SWITCH_DESCRIPTIONS_MAP = {
    "SOLENOID": MannitoFarmingSwitchEntityDescription(
        translation_key="valve",
        key="SOLENOID", 
        device_type=DEVICE_TYPE_VALVE,
        icon_on="mdi:water",
        icon_off="mdi:water-off"
    ),
    "RELAY": MannitoFarmingSwitchEntityDescription(
        translation_key="relay",
        key="RELAY",
        device_type=DEVICE_TYPE_RELAY, 
        icon_on="mdi:power-plug",
        icon_off="mdi:power-plug-off"
    ),
    "PUMP": MannitoFarmingSwitchEntityDescription(
        translation_key="pump",
        key="PUMP",
        device_type=DEVICE_TYPE_PUMP,
        icon_on="mdi:pump", 
        icon_off="mdi:pump-off"
    )
}
```

### Fan Entity Descriptions
```python
FAN_DESCRIPTIONS_MAP = {
    "FAN": MannitoFarmingFanEntityDescription(
        key="FAN",
        translation_key="fan",
        device_type=DEVICE_TYPE_FAN,
        icon_on="mdi:fan",
        icon_off="mdi:fan-off"
    )
}
```

### Sensor Entity Descriptions
```python
SENSOR_DESCRIPTIONS_MAP = {
    "CO2": MannitoFarmingSensorEntityDescription(
        key="CO2",
        translation_key="co2",
        device_class=SensorDeviceClass.CO2
    ),
    "TEMPERATURE": MannitoFarmingSensorEntityDescription(
        key="TEMPERATURE", 
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT
    ),
    "HUMIDITY": MannitoFarmingSensorEntityDescription(
        key="HUMIDITY",
        translation_key="humidity", 
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT
    ),
    "PH": MannitoFarmingSensorEntityDescription(
        key="PH",
        translation_key="ph",
        device_class=SensorDeviceClass.PH,
        state_class=SensorStateClass.MEASUREMENT
    ),
    "EC": MannitoFarmingSensorEntityDescription(
        key="EC",
        translation_key="ec",
        state_class=SensorStateClass.MEASUREMENT
    )
}
```

## Class Relationships Diagram

```
ConfigFlow
    ↓ creates
ConfigEntry
    ↓ initializes
MannitoFarmingDataUpdateCoordinator
    ↓ contains
API ←→ HTTP ←→ Mannito Controller
    ↓ manages
Device/Sensor/Plugin (data classes)
    ↓ exposes to
Platform Entities (Switch/Fan/Sensor/Light)
    ↓ registers with
Home Assistant Core
```

## Data Flow Summary

1. **Initialization**: ConfigFlow → ConfigEntry → Coordinator → API
2. **Discovery**: API.discover_devices/sensors() → Device/Sensor objects → Coordinator cache
3. **State Updates**: Coordinator._async_update_data() → API.get_device_state() → Device.state
4. **Control Commands**: Entity.async_turn_on() → Coordinator.async_set_device_state() → API.set_device_state()
5. **State Propagation**: Coordinator update → Entity._handle_coordinator_update() → HA state update

---

*This reference provides quick access to all classes and their interfaces for development and integration purposes.*