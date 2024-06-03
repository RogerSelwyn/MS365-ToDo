"""To-Do utilities processes."""

from homeassistant.util import slugify

from .const_integration import TODO_ENTITY_ID_FORMAT


def build_todo_entity_id(device_id, entity_name):
    """Build todo entity_id."""
    name = f"{device_id}_{entity_name}"
    return TODO_ENTITY_ID_FORMAT.format(slugify(name))
