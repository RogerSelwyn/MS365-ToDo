"""To-Do utilities processes."""

from homeassistant.helpers import entity_registry
from homeassistant.util import slugify

from ..classes.config_entry import MS365ConfigEntry
from ..const import CONF_ENTITY_NAME
from .const_integration import TODO_ENTITY_ID_FORMAT


def build_todo_entity_id(device_id, entity_name):
    """Build todo entity_id."""
    name = f"{entity_name}_{device_id}"
    return TODO_ENTITY_ID_FORMAT.format(slugify(name))


async def async_delete_todo(hass, config_entry: MS365ConfigEntry, todo):
    """Delete a ToDo List."""
    entity_id = build_todo_entity_id(todo, config_entry.data[CONF_ENTITY_NAME])
    ent_reg = entity_registry.async_get(hass)
    entities = entity_registry.async_entries_for_config_entry(
        ent_reg, config_entry.entry_id
    )
    for entity in entities:
        if entity.entity_id == entity_id:
            ent_reg.async_remove(entity_id)
            return
