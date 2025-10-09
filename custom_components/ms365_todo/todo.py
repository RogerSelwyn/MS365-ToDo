"""Todo processing."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .classes.config_entry import MS365ConfigEntry

# from .integration.planner_integration import async_planner_integration_setup_entry
from .integration.todo_integration import async_todo_integration_setup_entry


async def async_setup_entry(
    hass: HomeAssistant,  # pylint: disable=unused-argument
    entry: MS365ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the MS365 platform."""

    await async_todo_integration_setup_entry(hass, entry, async_add_entities)
    # await async_planner_integration_setup_entry(hass, entry, async_add_entities)
    return True
