"""Do configuration setup."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .coordinator_integration import MS365SensorCordinator

_LOGGER = logging.getLogger(__name__)


async def async_do_setup(hass: HomeAssistant, entry: ConfigEntry, account):
    """Run the setup after we have everything configured."""

    _LOGGER.debug("Sensor setup - start")
    sensor_coordinator = MS365SensorCordinator(hass, entry, account)
    sensor_keys = await sensor_coordinator.async_setup_entries()
    if sensor_keys:
        await sensor_coordinator.async_config_entry_first_refresh()
    _LOGGER.debug("Sensor setup - finish")
    return sensor_coordinator, sensor_keys
