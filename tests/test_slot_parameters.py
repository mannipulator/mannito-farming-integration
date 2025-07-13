"""Test for slot parameter functionality."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from custom_components.mannito_farming.api import API, SlotParameter, SlotSensorType


class TestSlotParameters:
    """Test slot parameter functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock()
        self.api = API("192.168.1.100", "user", "pass", self.mock_session)

    async def test_discover_slot_parameters_success(self):
        """Test successful slot parameter discovery."""
        # Mock the bulk response with slots data
        mock_response = {
            "devices": [],
            "sensors": [],
            "slots": [
                {
                    "name": "Default Slot",
                    "parameters": [
                        {
                            "parameter": "AIR_TEMPERATURE",
                            "value": 20
                        },
                        {
                            "parameter": "AIR_HUMIDITY", 
                            "value": 50
                        },
                        {
                            "parameter": "LEAF_TEMPERATURE",
                            "value": 0
                        }
                    ]
                },
                {
                    "name": "Night Slot",
                    "parameters": [
                        {
                            "parameter": "AIR_TEMPERATURE",
                            "value": 18
                        },
                        {
                            "parameter": "AIR_HUMIDITY",
                            "value": 60
                        }
                    ]
                }
            ]
        }
        
        # Mock the get_all_device_states method
        self.api.get_all_device_states = AsyncMock(return_value=mock_response)
        
        # Call the method under test
        slot_parameters = await self.api.discover_slot_parameters()
        
        # Verify results
        assert len(slot_parameters) == 5  # 3 from Default + 2 from Night
        
        # Check Default Slot parameters
        default_temp = next((p for p in slot_parameters if p.parameter_id == "slot_default_slot_air_temperature"), None)
        assert default_temp is not None
        assert default_temp.slot_name == "Default Slot"
        assert default_temp.parameter == SlotSensorType.AIR_TEMPERATURE
        assert default_temp.value == 20
        assert default_temp.name == "Default Slot - Air Temperature"
        
        default_humidity = next((p for p in slot_parameters if p.parameter_id == "slot_default_slot_air_humidity"), None)
        assert default_humidity is not None
        assert default_humidity.slot_name == "Default Slot"
        assert default_humidity.parameter == SlotSensorType.AIR_HUMIDITY
        assert default_humidity.value == 50
        
        # Check Night Slot parameters
        night_temp = next((p for p in slot_parameters if p.parameter_id == "slot_night_slot_air_temperature"), None)
        assert night_temp is not None
        assert night_temp.slot_name == "Night Slot"
        assert night_temp.value == 18

    async def test_discover_slot_parameters_empty_response(self):
        """Test slot parameter discovery with empty response."""
        # Mock empty response
        self.api.get_all_device_states = AsyncMock(return_value={})
        
        # Call the method under test
        slot_parameters = await self.api.discover_slot_parameters()
        
        # Verify results
        assert len(slot_parameters) == 0

    async def test_discover_slot_parameters_invalid_parameter(self):
        """Test slot parameter discovery with invalid parameter type."""
        # Mock response with invalid parameter
        mock_response = {
            "slots": [
                {
                    "name": "Test Slot",
                    "parameters": [
                        {
                            "parameter": "INVALID_PARAMETER",
                            "value": 123
                        }
                    ]
                }
            ]
        }
        
        self.api.get_all_device_states = AsyncMock(return_value=mock_response)
        
        # Call the method under test
        slot_parameters = await self.api.discover_slot_parameters()
        
        # Verify results - should still create parameter with OTHER type
        assert len(slot_parameters) == 1
        assert slot_parameters[0].parameter == SlotSensorType.OTHER

    def test_slot_sensor_type_parse(self):
        """Test SlotSensorType parsing."""
        # Test valid values
        assert SlotSensorType.parse("AIR_TEMPERATURE") == SlotSensorType.AIR_TEMPERATURE
        assert SlotSensorType.parse("air_temperature") == SlotSensorType.AIR_TEMPERATURE
        assert SlotSensorType.parse("AIR_HUMIDITY") == SlotSensorType.AIR_HUMIDITY
        assert SlotSensorType.parse("LEAF_TEMPERATURE") == SlotSensorType.LEAF_TEMPERATURE
        
        # Test invalid value
        with pytest.raises(ValueError):
            SlotSensorType.parse("INVALID")

    def test_slot_parameter_dataclass(self):
        """Test SlotParameter dataclass."""
        slot_param = SlotParameter(
            slot_name="Test Slot",
            parameter=SlotSensorType.AIR_TEMPERATURE,
            parameter_id="slot_test_air_temperature",
            parameter_unique_id="192.168.1.100_slot_test_air_temperature",
            name="Test Slot - Air Temperature",
            value=25.5,
            available=True
        )
        
        assert slot_param.slot_name == "Test Slot"
        assert slot_param.parameter == SlotSensorType.AIR_TEMPERATURE
        assert slot_param.parameter_id == "slot_test_air_temperature"
        assert slot_param.value == 25.5
        assert slot_param.available is True
