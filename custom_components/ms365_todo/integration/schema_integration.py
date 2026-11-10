"""Schema for MS365 Integration."""

import probatio

from homeassistant.components.todo import TodoItemStatus
from homeassistant.const import CONF_NAME
import homeassistant.helpers.config_validation as cv

from ..const import CONF_ENABLE_UPDATE
from .const_integration import (
    ATTR_CHECKLIST_ITEM_ID,
    ATTR_COMPLETED,
    ATTR_DESCRIPTION,
    ATTR_DUE,
    ATTR_NAME,
    ATTR_REMINDER,
    ATTR_REMOVE_DUE,
    ATTR_REMOVE_REMINDER,
    ATTR_STATUS,
    ATTR_SUBJECT,
    ATTR_TODO_ID,
    CONF_DUE_HOURS_BACKWARD_TO_GET,
    CONF_DUE_HOURS_FORWARD_TO_GET,
    CONF_SHOW_COMPLETED,
    CONF_TODO_LIST_ID,
    CONF_TRACK,
)

CONFIG_SCHEMA_INTEGRATION = {
    probatio.Optional(CONF_ENABLE_UPDATE, default=False): cv.boolean,
}

TODO_SERVICE_NEW_SCHEMA = {
    probatio.Required(ATTR_SUBJECT): cv.string,
    probatio.Optional(ATTR_DESCRIPTION): cv.string,
    probatio.Optional(ATTR_DUE): probatio.Any(cv.date, cv.datetime),
    probatio.Optional(ATTR_REMINDER): probatio.Any(cv.date, cv.datetime),
}

TODO_SERVICE_UPDATE_SCHEMA = probatio.All(
    cv.make_entity_service_schema(
        {
            probatio.Required(ATTR_TODO_ID): cv.string,
            probatio.Optional(ATTR_SUBJECT): cv.string,
            probatio.Optional(ATTR_DESCRIPTION): cv.string,
            probatio.Optional(ATTR_DUE): probatio.Any(cv.date, cv.datetime),
            probatio.Optional(ATTR_REMOVE_DUE): cv.boolean,
            probatio.Optional(ATTR_REMINDER): probatio.Any(cv.date, cv.datetime),
            probatio.Optional(ATTR_REMOVE_REMINDER): cv.boolean,
        }
    ),
    cv.has_at_most_one_key(ATTR_DUE, ATTR_REMOVE_DUE),
    cv.has_at_most_one_key(ATTR_REMINDER, ATTR_REMOVE_REMINDER),
)

TODO_SERVICE_DELETE_SCHEMA = {
    probatio.Required(ATTR_TODO_ID): cv.string,
}
TODO_SERVICE_COMPLETE_SCHEMA = {
    probatio.Required(ATTR_TODO_ID): cv.string,
    probatio.Required(ATTR_COMPLETED): bool,
}

TODO_SERVICE_NEW_STEP_SCHEMA = probatio.All(
    cv.make_entity_service_schema(
        {
            probatio.Required(ATTR_TODO_ID): cv.string,
            probatio.Required(ATTR_NAME): cv.string,
        }
    ),
)
TODO_SERVICE_UPDATE_STEP_SCHEMA = probatio.All(
    cv.make_entity_service_schema(
        {
            probatio.Required(ATTR_TODO_ID): cv.string,
            probatio.Required(ATTR_CHECKLIST_ITEM_ID): cv.string,
            probatio.Optional(ATTR_NAME): probatio.All(cv.string, probatio.Length(min=1)),
            probatio.Optional(ATTR_STATUS): probatio.In(
                {TodoItemStatus.NEEDS_ACTION, TodoItemStatus.COMPLETED},
            ),
        }
    ),
    cv.has_at_least_one_key(ATTR_NAME, ATTR_STATUS),
)
TODO_SERVICE_DELETE_STEP_SCHEMA = probatio.All(
    cv.make_entity_service_schema(
        {
            probatio.Required(ATTR_TODO_ID): cv.string,
            probatio.Required(ATTR_CHECKLIST_ITEM_ID): cv.string,
        }
    ),
)


YAML_TODO_LIST_SCHEMA = probatio.Schema(
    {
        probatio.Required(CONF_TODO_LIST_ID): cv.string,
        probatio.Required(CONF_NAME): cv.string,
        probatio.Optional(CONF_TRACK, default=True): cv.boolean,
        probatio.Optional(CONF_SHOW_COMPLETED, default=False): cv.boolean,
        probatio.Optional(CONF_DUE_HOURS_FORWARD_TO_GET): int,
        probatio.Optional(CONF_DUE_HOURS_BACKWARD_TO_GET): int,
    }
)
