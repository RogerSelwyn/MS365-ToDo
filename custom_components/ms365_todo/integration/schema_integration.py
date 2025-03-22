"""Schema for MS365 Integration."""

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import CONF_NAME

from ..const import CONF_ENABLE_UPDATE
from .const_integration import (
    ATTR_COMPLETED,
    ATTR_DESCRIPTION,
    ATTR_DUE,
    ATTR_REMINDER,
    ATTR_REMOVE_DUE,
    ATTR_REMOVE_REMINDER,
    ATTR_SUBJECT,
    ATTR_TODO_ID,
    CONF_DUE_HOURS_BACKWARD_TO_GET,
    CONF_DUE_HOURS_FORWARD_TO_GET,
    CONF_SHOW_COMPLETED,
    CONF_TODO_LIST_ID,
    CONF_TRACK,
)

CONFIG_SCHEMA_INTEGRATION = {
    vol.Optional(CONF_ENABLE_UPDATE, default=False): cv.boolean,
}

TODO_SERVICE_NEW_SCHEMA = {
    vol.Required(ATTR_SUBJECT): cv.string,
    vol.Optional(ATTR_DESCRIPTION): cv.string,
    vol.Optional(ATTR_DUE): vol.Any(cv.date, cv.datetime),
    vol.Optional(ATTR_REMINDER): vol.Any(cv.date, cv.datetime),
}

TODO_SERVICE_UPDATE_SCHEMA = vol.All(
    cv.make_entity_service_schema(
        {
            vol.Required(ATTR_TODO_ID): cv.string,
            vol.Optional(ATTR_SUBJECT): cv.string,
            vol.Optional(ATTR_DESCRIPTION): cv.string,
            vol.Optional(ATTR_DUE): vol.Any(cv.date, cv.datetime),
            vol.Optional(ATTR_REMOVE_DUE): cv.boolean,
            vol.Optional(ATTR_REMINDER): vol.Any(cv.date, cv.datetime),
            vol.Optional(ATTR_REMOVE_REMINDER): cv.boolean,
        }
    ),
    cv.has_at_most_one_key(ATTR_DUE, ATTR_REMOVE_DUE),
    cv.has_at_most_one_key(ATTR_REMINDER, ATTR_REMOVE_REMINDER),
)

TODO_SERVICE_DELETE_SCHEMA = {
    vol.Required(ATTR_TODO_ID): cv.string,
}
TODO_SERVICE_COMPLETE_SCHEMA = {
    vol.Required(ATTR_TODO_ID): cv.string,
    vol.Required(ATTR_COMPLETED): bool,
}

YAML_TODO_LIST_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TODO_LIST_ID): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_TRACK, default=True): cv.boolean,
        vol.Optional(CONF_SHOW_COMPLETED, default=False): cv.boolean,
        vol.Optional(CONF_DUE_HOURS_FORWARD_TO_GET): int,
        vol.Optional(CONF_DUE_HOURS_BACKWARD_TO_GET): int,
    }
)
