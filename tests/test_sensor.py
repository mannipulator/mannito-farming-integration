"""Test sensor platform for Mannito Farming."""
from unittest.mock import Mock

from homeassistant.components.sensor import SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.mannito_farming.api import Sensor
from custom_components.mannito_farming.sensor import (
    MannitoFarmingSensor,
    MannitoFarmingSensorEntityDescription,
)


class TestMannitoFarmingSensorValueValidation:
    """Test sensor value validation for measurement sensors."""

    def setup_method(self):
        """Set up test fixtures."""
        self.hass = Mock(spec=HomeAssistant)
        self.config_entry = Mock(spec=ConfigEntry)
        self.config_entry.entry_id = "test_entry"

        # Create a mock coordinator
        self.coordinator = Mock()
        self.coordinator._sensors = {}
        self.coordinator.last_update_success = True
        self.coordinator.get_device_info.return_value = Mock()

        # Create a sensor description for measurement sensor (like temperature)
        self.measurement_description = MannitoFarmingSensorEntityDescription(
            key="TEMPERATURE",
            translation_key="temperature",
            device_class="temperature",
            native_unit_of_measurement="°C",
            state_class=SensorStateClass.MEASUREMENT
        )

        # Create a sensor description for non-measurement sensor
        self.non_measurement_description = MannitoFarmingSensorEntityDescription(
            key="STATUS",
            translation_key="status",
            device_class="",
            state_class=""
        )

    def create_sensor_entity(self, description, device_id="test_sensor"):
        """Create a sensor entity for testing."""
        return MannitoFarmingSensor(
            coordinator=self.coordinator,
            entry=self.config_entry,
            device_id=device_id,
            description=description,
            name="Test Sensor",
        )

    def test_measurement_sensor_with_valid_numeric_value(self):
        """Test that measurement sensor returns valid numeric values."""
        # Setup
        sensor_entity = self.create_sensor_entity(self.measurement_description)

        # Create mock sensor with valid numeric value
        mock_sensor = Mock(spec=Sensor)
        mock_sensor.state_value = "23.5"
        mock_sensor.available = True
        self.coordinator._sensors["test_sensor"] = mock_sensor

        # Test
        value = sensor_entity.native_value

        # Assert
        assert value == "23.5"

    def test_measurement_sensor_with_empty_string_returns_none(self):
        """Test that measurement sensor returns None for empty string."""
        # Setup
        sensor_entity = self.create_sensor_entity(self.measurement_description)

        # Create mock sensor with empty string
        mock_sensor = Mock(spec=Sensor)
        mock_sensor.state_value = ""
        mock_sensor.available = True
        self.coordinator._sensors["test_sensor"] = mock_sensor

        # Test
        value = sensor_entity.native_value

        # Assert
        assert value is None

    def test_measurement_sensor_with_none_value_returns_none(self):
        """Test that measurement sensor returns None for None value."""
        # Setup
        sensor_entity = self.create_sensor_entity(self.measurement_description)

        # Create mock sensor with None value
        mock_sensor = Mock(spec=Sensor)
        mock_sensor.state_value = None
        mock_sensor.available = True
        self.coordinator._sensors["test_sensor"] = mock_sensor

        # Test
        value = sensor_entity.native_value

        # Assert
        assert value is None

    def test_measurement_sensor_with_non_numeric_string_returns_none(self):
        """Test that measurement sensor returns None for non-numeric strings."""
        # Setup
        sensor_entity = self.create_sensor_entity(self.measurement_description)

        # Create mock sensor with non-numeric string
        mock_sensor = Mock(spec=Sensor)
        mock_sensor.state_value = "error"
        mock_sensor.available = True
        self.coordinator._sensors["test_sensor"] = mock_sensor

        # Test
        value = sensor_entity.native_value

        # Assert
        assert value is None

    def test_measurement_sensor_with_integer_value(self):
        """Test that measurement sensor returns valid integer values."""
        # Setup
        sensor_entity = self.create_sensor_entity(self.measurement_description)

        # Create mock sensor with integer value (as string from API)
        mock_sensor = Mock(spec=Sensor)
        mock_sensor.state_value = "42"
        mock_sensor.available = True
        self.coordinator._sensors["test_sensor"] = mock_sensor

        # Test
        value = sensor_entity.native_value

        # Assert
        assert value == "42"

    def test_non_measurement_sensor_allows_string_values(self):
        """Test that non-measurement sensors can return string values."""
        # Setup
        sensor_entity = self.create_sensor_entity(self.non_measurement_description)

        # Create mock sensor with string value
        mock_sensor = Mock(spec=Sensor)
        mock_sensor.state_value = "offline"
        mock_sensor.available = True
        self.coordinator._sensors["test_sensor"] = mock_sensor

        # Test
        value = sensor_entity.native_value

        # Assert
        assert value == "offline"

    def test_non_measurement_sensor_allows_empty_string(self):
        """Test that non-measurement sensors can return empty strings."""
        # Setup
        sensor_entity = self.create_sensor_entity(self.non_measurement_description)

        # Create mock sensor with empty string
        mock_sensor = Mock(spec=Sensor)
        mock_sensor.state_value = ""
        mock_sensor.available = True
        self.coordinator._sensors["test_sensor"] = mock_sensor

        # Test
        value = sensor_entity.native_value

        # Assert
        assert value == ""

    def test_sensor_not_found_returns_none(self):
        """Test that missing sensor returns None."""
        # Setup
        sensor_entity = self.create_sensor_entity(self.measurement_description)
        # Don't add sensor to coordinator._sensors

        # Test
        value = sensor_entity.native_value

        # Assert
        assert value is None

    def test_measurement_sensor_with_float_in_string(self):
        """Test that measurement sensor handles float values in string format."""
        # Setup
        sensor_entity = self.create_sensor_entity(self.measurement_description)

        # Create mock sensor with float string
        mock_sensor = Mock(spec=Sensor)
        mock_sensor.state_value = "23.456"
        mock_sensor.available = True
        self.coordinator._sensors["test_sensor"] = mock_sensor

        # Test
        value = sensor_entity.native_value

        # Assert
        assert value == "23.456"

    def test_measurement_sensor_with_negative_value(self):
        """Test that measurement sensor handles negative values."""
        # Setup
        sensor_entity = self.create_sensor_entity(self.measurement_description)

        # Create mock sensor with negative value
        mock_sensor = Mock(spec=Sensor)
        mock_sensor.state_value = "-5.2"
        mock_sensor.available = True
        self.coordinator._sensors["test_sensor"] = mock_sensor

        # Test
        value = sensor_entity.native_value

        # Assert
        assert value == "-5.2"
