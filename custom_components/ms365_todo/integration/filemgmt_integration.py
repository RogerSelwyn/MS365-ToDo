"""To-Do file management processes."""

import logging

import yaml
from homeassistant.const import CONF_NAME
from voluptuous.error import Error as VoluptuousError

from ..const import (
    CONF_ENTITY_NAME,
)
from ..helpers.config_entry import MS365ConfigEntry
from ..helpers.filemgmt import build_config_file_path
from .const_integration import (
    CONF_TODO_LIST_ID,
    CONF_TRACK,
    YAML_TODO_LISTS_FILENAME,
)
from .schema_integration import YAML_TODO_LIST_SCHEMA

_LOGGER = logging.getLogger(__name__)


def load_yaml_file(path, item_id, item_schema):
    """Load the ms365 yaml file."""
    items = {}
    try:
        with open(path, encoding="utf8") as file:
            data = yaml.safe_load(file)
            if data is None:
                return {}
            for item in data:
                try:
                    items[item[item_id]] = item_schema(item)
                except VoluptuousError as exception:
                    # keep going
                    _LOGGER.warning("Invalid Data: %s", exception)
    except FileNotFoundError:
        # When YAML file could not be loaded/did not contain a dict
        return {}

    return items


def _write_yaml_file(yaml_filepath, cal):
    with open(yaml_filepath, "a", encoding="UTF8") as out:
        out.write("\n")
        yaml.dump([cal], out, default_flow_style=False, encoding="UTF8")
        out.close()


def _get_task_list_info(yaml_todo_list, track_new_devices):
    """Convert data from MS365 into DEVICE_SCHEMA."""
    return YAML_TODO_LIST_SCHEMA(
        {
            CONF_TODO_LIST_ID: yaml_todo_list.folder_id,
            CONF_NAME: yaml_todo_list.name,
            CONF_TRACK: track_new_devices,
        }
    )


async def async_update_todo_list_file(
    entry: MS365ConfigEntry, yaml_todo_list, hass, track_new_devices
):
    """Update the todo file."""
    path = build_yaml_filename(entry, YAML_TODO_LISTS_FILENAME)
    yaml_filepath = build_config_file_path(hass, path)
    existing_task_lists = await hass.async_add_executor_job(
        load_yaml_file, yaml_filepath, CONF_TODO_LIST_ID, YAML_TODO_LIST_SCHEMA
    )
    yaml_todo_list = _get_task_list_info(yaml_todo_list, track_new_devices)
    if yaml_todo_list[CONF_TODO_LIST_ID] in existing_task_lists:
        return
    await hass.async_add_executor_job(_write_yaml_file, yaml_filepath, yaml_todo_list)


def build_yaml_filename(conf: MS365ConfigEntry, filename):
    """Create the token file name."""

    return filename.format(f"_{conf.data.get(CONF_ENTITY_NAME)}")


def read_todo_yaml_file(yaml_filepath):
    """Read the yaml file."""
    with open(yaml_filepath, encoding="utf8") as file:
        return yaml.safe_load(file)


def write_todo_yaml_file(yaml_filepath, contents):
    """Write the yaml file."""
    with open(yaml_filepath, "w", encoding="UTF8") as out:
        yaml.dump(contents, out, default_flow_style=False, encoding="UTF8")
