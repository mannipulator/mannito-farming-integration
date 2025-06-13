from unittest.mock import AsyncMock, patch

import pytest

from custom_components.mannito_farming.fan import GrowControllerFan


@pytest.fixture
def mock_coordinator():
    with patch("custom_components.mannito_farming.coordinator.MannitoFarmingDataUpdateCoordinator") as mock:
        instance = mock.return_value
        instance.async_control_device = AsyncMock()
        instance.async_fetch_device_state = AsyncMock()
        yield instance

async def test_fan_turn_on(hass, mock_coordinator):
    """Test turning on the fan."""
    fan = GrowControllerFan(mock_coordinator, None, "FAN1", "Test Fan")
    mock_coordinator.async_control_device.return_value = True

    await fan.async_turn_on(percentage=50)

    assert fan.is_on
    assert fan.percentage == 50
    mock_coordinator.async_control_device.assert_called_once_with("FAN1", True)

async def test_fan_turn_off(hass, mock_coordinator):
    """Test turning off the fan."""
    fan = GrowControllerFan(mock_coordinator, None, "FAN1", "Test Fan")
    mock_coordinator.async_control_device.return_value = True

    await fan.async_turn_off()

    assert not fan.is_on
    mock_coordinator.async_control_device.assert_called_once_with("FAN1", False)

async def test_fan_update(hass, mock_coordinator):
    """Test updating the fan state."""
    fan = GrowControllerFan(mock_coordinator, None, "FAN1", "Test Fan")
    mock_coordinator.async_fetch_device_state.return_value = {"speed": "medium"}

    await fan.async_update()

    assert fan.is_on
    assert fan.percentage == 50
    mock_coordinator.async_fetch_device_state.assert_called_once_with("FAN1")
