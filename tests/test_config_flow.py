"""Test the Grow Controller config flow."""
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from custom_components.mannito_farming.const import DOMAIN
from custom_components.mannito_farming.api import APIConnectionError


@pytest.fixture
def mock_api():
    with patch("custom_components.mannito_farming.api.API") as mock_api_class:
        mock_instance = mock_api_class.return_value
        mock_instance.fetch_device_config = AsyncMock()
        yield mock_instance


async def test_config_flow_user_success(hass, mock_api):
    """Test a successful config flow."""
    mock_api.fetch_device_config.return_value = {
        "serial_number": "12345",
        "components": [
            {"ComponentType": "FAN", "ComponentName": "Fan1"},
            {"ComponentType": "SOLENOID", "ComponentName": "Valve1"},
        ],
    }

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"host": "192.168.1.100", "username": "user", "password": "pass"},
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Mannito Farming 12345"
    assert result["data"] == {
        "host": "192.168.1.100",
        "username": "user",
        "password": "pass",
        "device_info": mock_api.fetch_device_config.return_value,
    }


async def test_config_flow_user_cannot_connect(hass, mock_api):
    """Test config flow when the device cannot be connected."""
    mock_api.fetch_device_config.side_effect = APIConnectionError

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"host": "192.168.1.100", "username": "user", "password": "pass"},
    )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}