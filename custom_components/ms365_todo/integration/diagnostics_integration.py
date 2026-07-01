"""Diagnostics support for MS365."""

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from ..classes.config_entry import MS365ConfigEntry
from .const_integration import CONF_TODO_LIST_ID, YAML_TODO_LISTS_FILENAME
from .filemgmt_integration import (
    build_yaml_file_path,
    build_yaml_filename,
    load_yaml_file,
)
from .schema_integration import YAML_TODO_LIST_SCHEMA

TO_REDACT = {CONF_TODO_LIST_ID}


async def async_integration_diagnostics(hass: HomeAssistant, entry: MS365ConfigEntry):
    """Get integration specific diagnostics."""
    yaml_filename = build_yaml_filename(entry, YAML_TODO_LISTS_FILENAME)
    yaml_filepath = build_yaml_file_path(hass, yaml_filename)
    ms365_task_dict = await hass.async_add_executor_job(
        load_yaml_file,
        yaml_filepath,
        CONF_TODO_LIST_ID,
        YAML_TODO_LIST_SCHEMA,
    )
    redacted_tasks = {
        f"**REDACTED{i}**": ms365_task_dict[key]
        for i, key in enumerate(ms365_task_dict.keys(), start=1)
    }

    return async_redact_data(redacted_tasks, TO_REDACT)
