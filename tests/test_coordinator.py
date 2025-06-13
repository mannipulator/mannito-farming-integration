"""Test the Grow Controller coordinator."""
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.components.grow_controller.coordinator import (
    GrowControllerDataUpdateCoordinator,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_SENSORS, CONF_USERNAME
from homeassistant.core import HomeAssistant

VALID_CONFIG = {
    CONF_HOST: "192.168.1.100",
    CONF_USERNAME: "test_user",
    CONF_PASSWORD: "test_pass",
    CONF_SENSORS: ["sensor.test_sensor1", "sensor.test_sensor2"],
}

@pytest.fixture
def mock_hass():
    """Create a mock hass object."""
    hass = MagicMock(spec=HomeAssistant)
    hass.states = MagicMock()
    return hass

@pytest.fixture
def coordinator(mock_hass):
    """Create a coordinator instance."""
    return GrowControllerDataUpdateCoordinator(
        mock_hass,
        VALID_CONFIG[CONF_HOST],
        VALID_CONFIG[CONF_USERNAME],
        VALID_CONFIG[CONF_PASSWORD],
        VALID_CONFIG[CONF_SENSORS],
    )

async def test_coordinator_initialization(coordinator):
    """Test coordinator initialization."""
    assert coordinator.host == VALID_CONFIG[CONF_HOST]
    assert coordinator.username == VALID_CONFIG[CONF_USERNAME]
    assert coordinator.password == VALID_CONFIG[CONF_PASSWORD]
    assert coordinator.sensors == VALID_CONFIG[CONF_SENSORS]

async def test_update_external_sensors_success(coordinator, mock_hass):
    """Test successful external sensor update."""
    # Mock sensor states
    mock_hass.states.get.side_effect = [
        MagicMock(state="25.5", attributes={"unit_of_measurement": "°C"}),
        MagicMock(state="45", attributes={"unit_of_measurement": "%"}),
    ]

    # Mock successful API response
    mock_response = AsyncMock()
    mock_response.status = 200
    coordinator.session.post.return_value.__aenter__.return_value = mock_response

    await coordinator._update_external_sensors()

    # Verify API call
    coordinator.session.post.assert_called_once()
    call_args = coordinator.session.post.call_args
    assert call_args[0][0] == f"http://{VALID_CONFIG[CONF_HOST]}:80/api/sensor"
    assert call_args[1]["auth"] == (VALID_CONFIG[CONF_USERNAME], VALID_CONFIG[CONF_PASSWORD])

    # Verify sensor data
    sensor_data = call_args[1]["json"]
    assert len(sensor_data) == 2
    assert sensor_data["sensor.test_sensor1"]["state"] == "25.5"
    assert sensor_data["sensor.test_sensor2"]["state"] == "45"

async def test_update_external_sensors_api_error(coordinator, mock_hass):
    """Test external sensor update with API error."""
    # Mock sensor states
    mock_hass.states.get.side_effect = [
        MagicMock(state="25.5", attributes={"unit_of_measurement": "°C"}),
    ]

    # Mock failed API response
    mock_response = AsyncMock()
    mock_response.status = 500
    mock_response.text.return_value = "Internal Server Error"
    coordinator.session.post.return_value.__aenter__.return_value = mock_response

    await coordinator._update_external_sensors()

    # Verify error was logged
    coordinator.logger.error.assert_called_with(
        "Error updating external sensors: %s",
        "Internal Server Error",
    )

async def test_set_device_state_success(coordinator):
    """Test successful device state setting."""
    # Mock successful API response
    mock_response = AsyncMock()
    mock_response.status = 200
    coordinator.session.post.return_value.__aenter__.return_value = mock_response

    result = await coordinator.async_set_device_state("test_device", "on")

    assert result is True
    coordinator.session.post.assert_called_once()
    call_args = coordinator.session.post.call_args
    assert call_args[0][0] == f"http://{VALID_CONFIG[CONF_HOST]}:80/api/device/test_device"
    assert call_args[1]["json"] == {"state": "on"}
    assert call_args[1]["auth"] == (VALID_CONFIG[CONF_USERNAME], VALID_CONFIG[CONF_PASSWORD])

async def test_set_device_state_failure(coordinator):
    """Test failed device state setting."""
    # Mock failed API response
    mock_response = AsyncMock()
    mock_response.status = 500
    coordinator.session.post.return_value.__aenter__.return_value = mock_response

    result = await coordinator.async_set_device_state("test_device", "on")

    assert result is False
    coordinator.logger.error.assert_called()

async def test_get_device_state_success(coordinator):
    """Test successful device state getting."""
    # Mock successful API response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"state": "on", "brightness": 255}
    coordinator.session.get.return_value.__aenter__.return_value = mock_response

    result = await coordinator.async_get_device_state("test_device")

    assert result == {"state": "on", "brightness": 255}
    coordinator.session.get.assert_called_once()
    call_args = coordinator.session.get.call_args
    assert call_args[0][0] == f"http://{VALID_CONFIG[CONF_HOST]}:80/api/device/test_device"
    assert call_args[1]["auth"] == (VALID_CONFIG[CONF_USERNAME], VALID_CONFIG[CONF_PASSWORD])

async def test_get_device_state_failure(coordinator):
    """Test failed device state getting."""
    # Mock failed API response
    mock_response = AsyncMock()
    mock_response.status = 500
    coordinator.session.get.return_value.__aenter__.return_value = mock_response

    result = await coordinator.async_get_device_state("test_device")

    assert result == {}
    coordinator.logger.error.assert_called()
