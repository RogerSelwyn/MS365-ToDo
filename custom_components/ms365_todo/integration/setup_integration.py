"""Do configuration setup."""

import logging
import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from ..classes.config_entry import MS365ConfigEntry
from .const_integration import PLATFORMS, YAML_TODO_LISTS_FILENAME
from .coordinator_integration import MS365SensorCordinator
from .filemgmt_integration import (
    build_yaml_file_path,
    build_yaml_filename,
)

_LOGGER = logging.getLogger(__name__)


async def async_do_setup(hass: HomeAssistant, entry: ConfigEntry, account):
    """Run the setup after we have everything configured."""

    _LOGGER.debug("Sensor setup - start")
    sensor_coordinator = MS365SensorCordinator(hass, entry, account)
    await sensor_coordinator.async_config_entry_first_refresh()
    _LOGGER.debug("Sensor setup - finish")
    return sensor_coordinator, sensor_coordinator.keys, PLATFORMS


async def async_integration_remove_entry(hass: HomeAssistant, entry: MS365ConfigEntry):
    """Integration specific entry removal."""
    yaml_filename = build_yaml_filename(entry, YAML_TODO_LISTS_FILENAME)
    yaml_filepath = build_yaml_file_path(hass, yaml_filename)
    if os.path.exists(yaml_filepath):
        await hass.async_add_executor_job(os.remove, yaml_filepath)
