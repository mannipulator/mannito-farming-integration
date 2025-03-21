"""Test the Grow Controller config flow."""
from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.components.grow_controller.const import DOMAIN
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_SENSORS

from tests.common import MockConfigEntry

pytestmark = pytest.mark.usefixtures("mock_setup_entry")

VALID_CONFIG = {
    CONF_HOST: "192.168.1.100",
    CONF_USERNAME: "test_user",
    CONF_PASSWORD: "test_pass",
}

VALID_SENSOR_CONFIG = {
    CONF_SENSORS: ["sensor.test_sensor1", "sensor.test_sensor2"],
}

@pytest.fixture(autouse=True)
def mock_setup():
    """Mock setup entry."""
    with patch("homeassistant.components.grow_controller.async_setup_entry", return_value=True):
        yield

async def test_form(hass):
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}

    with patch(
        "homeassistant.components.grow_controller.config_flow.GrowControllerConfigFlow.async_step_sensor"
    ) as mock_step_sensor:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            VALID_CONFIG,
        )
        assert result2["type"] == "form"
        assert result2["step_id"] == "sensor"
        mock_step_sensor.assert_called_once()

async def test_form_invalid_host(hass):
    """Test we handle invalid host."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_HOST: "invalid_host",
            CONF_USERNAME: "test_user",
            CONF_PASSWORD: "test_pass",
        },
    )

    assert result2["type"] == "form"
    assert result2["errors"] == {CONF_HOST: "invalid_host"}

async def test_form_sensor_selection(hass):
    """Test sensor selection step."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        VALID_CONFIG,
    )

    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        VALID_SENSOR_CONFIG,
    )

    assert result3["type"] == "create_entry"
    assert result3["title"] == f"Grow Controller {VALID_CONFIG[CONF_HOST]}"
    assert result3["data"] == {
        **VALID_CONFIG,
        **VALID_SENSOR_CONFIG,
    }

async def test_form_no_sensors(hass):
    """Test we handle no sensors selected."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        VALID_CONFIG,
    )

    result3 = await hass.config_entries.flow.async_configure(
        result2["flow_id"],
        {CONF_SENSORS: []},
    )

    assert result3["type"] == "form"
    assert result3["errors"] == {CONF_SENSORS: "no_sensors_selected"}

async def test_abort_if_already_setup(hass):
    """Test we abort if already setup."""
    MockConfigEntry(
        domain=DOMAIN,
        data=VALID_CONFIG,
    ).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == "abort"
    assert result["reason"] == "already_configured" 