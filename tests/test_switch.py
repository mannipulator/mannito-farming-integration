from unittest.mock import AsyncMock, patch
import pytest
from homeassistant.components.switch import SwitchEntity
from custom_components.mannito_farming.switch import GrowControllerSwitch

@pytest.fixture
def mock_coordinator():
    with patch("custom_components.mannito_farming.coordinator.MannitoFarmingDataUpdateCoordinator") as mock:
        instance = mock.return_value
        instance.async_control_device = AsyncMock()
        instance.async_fetch_device_state = AsyncMock()
        yield instance

async def test_switch_turn_on(hass, mock_coordinator):
    """Test turning on the switch."""
    switch = GrowControllerSwitch(mock_coordinator, None, "RELAY_1", "Test Switch", "RELAIS")
    mock_coordinator.async_control_device.return_value = True

    await switch.async_turn_on()

    assert switch.is_on
    mock_coordinator.async_control_device.assert_called_once_with("RELAY_1", True)

async def test_switch_turn_off(hass, mock_coordinator):
    """Test turning off the switch."""
    switch = GrowControllerSwitch(mock_coordinator, None, "RELAY_1", "Test Switch", "RELAIS")
    mock_coordinator.async_control_device.return_value = True

    await switch.async_turn_off()

    assert not switch.is_on
    mock_coordinator.async_control_device.assert_called_once_with("RELAY_1", False)

async def test_switch_update(hass, mock_coordinator):
    """Test updating the switch state."""
    switch = GrowControllerSwitch(mock_coordinator, None, "RELAY_1", "Test Switch", "RELAIS")
    mock_coordinator.async_fetch_device_state.return_value = {"state": True}

    await switch.async_update()

    assert switch.is_on
    mock_coordinator.async_fetch_device_state.assert_called_once_with("RELAY_1")