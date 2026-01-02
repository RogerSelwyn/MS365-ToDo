"""Todo processing."""

import logging
from datetime import datetime, timedelta

from homeassistant.components.todo import TodoItem, TodoListEntity
from homeassistant.components.todo.const import TodoItemStatus
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from O365.utils.query import (  # pylint: disable=no-name-in-module, import-error
    QueryBuilder,
)

from ..classes.config_entry import MS365ConfigEntry
from ..classes.entity import MS365Entity
from ..const import (
    ATTR_DATA,
    CONF_ENTITY_KEY,
    CONF_ENTITY_TYPE,
    EVENT_HA_EVENT,
)
from .const_integration import (
    ATTR_ALL_TODOS,
    ATTR_COMPLETED,
    ATTR_CREATED,
    ATTR_DUE,
    ATTR_ID,
    ATTR_OVERDUE_TODOS,
    ATTR_STATUS,
    ATTR_TITLE,
    ATTR_TODO_ID,
    CONF_DUE_HOURS_BACKWARD_TO_GET,
    CONF_DUE_HOURS_FORWARD_TO_GET,
    CONF_SHOW_COMPLETED,
    CONF_TODO_LIST,
    DOMAIN,
    EVENT_COMPLETED_PLANNER_TASK,
    EVENT_NEW_PLANNER_TASK,
    TODO_PLANNER,
)

_LOGGER = logging.getLogger(__name__)


async def async_planner_integration_setup_entry(
    hass: HomeAssistant,
    entry: MS365ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up the MS365 platform."""

    coordinator = entry.runtime_data.coordinator
    plannerentities = [
        MS365Planner(
            hass,
            coordinator,
            key[CONF_NAME],
            entry,
            key[CONF_ENTITY_KEY],
            key[CONF_UNIQUE_ID],
        )
        for key in entry.runtime_data.sensors
        if key[CONF_ENTITY_TYPE] == TODO_PLANNER
    ]
    async_add_entities(plannerentities, False)

    return True


class MS365Planner(MS365Entity, TodoListEntity):  # pylint: disable=abstract-method
    """MS365 Planner processing."""

    def __init__(
        self,
        hass,
        coordinator,
        name,
        entry: MS365ConfigEntry,
        entity_id,
        unique_id,
    ):
        """Initialise the Planner List."""
        super().__init__(coordinator, entry, name, entity_id, unique_id)

        self.todo_last_created = dt_util.utcnow() - timedelta(minutes=5)
        self.todo_last_completed = dt_util.utcnow() - timedelta(minutes=5)
        self._ha_timezone = dt_util.DEFAULT_TIME_ZONE
        self._zero_date = datetime(1, 1, 1, 0, 0, 0, tzinfo=self._ha_timezone)
        self._state = None
        self._todo_items = None
        self._extra_attributes = None
        self._update_status(hass)

    @property
    def state(self):
        """Todo state."""
        return self._state

    @property
    def todo_items(self):
        """List of Todos."""
        return self._todo_items

    @property
    def extra_state_attributes(self):
        """Device state attributes."""
        return self._extra_attributes

    def _handle_coordinator_update(self) -> None:
        self._update_status(self.hass)
        self.async_write_ha_state()

    def _update_status(self, hass):
        todos = self.coordinator.data[self.entity_key][ATTR_DATA]
        self._state = sum(not task.completed_date for task in todos)
        self._todo_items = []
        self._todo_items.extend(
            TodoItem(
                uid=todo.object_id,
                summary=todo.title,
                status=_get_status(todo),
                due=todo.due_date_time,
            )
            for todo in todos
        )
        self._extra_attributes = self._update_extra_state_attributes(todos)

        todo_last_completed = self._zero_date
        todo_last_created = self._zero_date
        for todo in todos:
            if todo.completed_date and todo.completed_date > self.todo_last_completed:
                _raise_event_external(
                    hass,
                    EVENT_COMPLETED_PLANNER_TASK,
                    todo.object_id,
                    ATTR_COMPLETED,
                    todo.completed_date,
                )
                if todo.completed_date > todo_last_completed:
                    todo_last_completed = todo.completed_date
            if todo.created_date and todo.created_date > self.todo_last_created:
                _raise_event_external(
                    hass,
                    EVENT_NEW_PLANNER_TASK,
                    todo.object_id,
                    ATTR_CREATED,
                    todo.created_date,
                )
                if todo.created_date > todo_last_created:
                    todo_last_created = todo.created_date

        if todo_last_completed > self._zero_date:
            self.todo_last_completed = todo_last_completed
        if todo_last_created > self._zero_date:
            self.todo_last_created = todo_last_created

    def _update_extra_state_attributes(self, todos):
        """Extra state attributes."""
        all_todos = []
        overdue_todos = []
        for item in todos:
            todo = {
                ATTR_TITLE: item.title,
                ATTR_ID: item.object_id,
                ATTR_STATUS: _get_status(item),
            }
            if item.due_date_time:
                todo[ATTR_DUE] = item.due_date_time
                if item.due_date_time < dt_util.utcnow():
                    overdue_todo = {
                        ATTR_TITLE: item.title,
                        ATTR_ID: item.object_id,
                        ATTR_DUE: item.due_date_time,
                    }
                    overdue_todos.append(overdue_todo)

            all_todos.append(todo)

        extra_attributes = {ATTR_ALL_TODOS: all_todos}
        if overdue_todos:
            extra_attributes[ATTR_OVERDUE_TODOS] = overdue_todos
        return extra_attributes


def _get_status(todo):
    return (
        TodoItemStatus.COMPLETED if todo.completed_date else TodoItemStatus.NEEDS_ACTION
    )


def _raise_event_external(hass, event_type, todo_id, time_type, task_datetime):
    hass.bus.fire(
        f"{DOMAIN}_{event_type}",
        {ATTR_TODO_ID: todo_id, time_type: task_datetime, EVENT_HA_EVENT: False},
    )
    _LOGGER.debug("%s - %s - %s", event_type, todo_id, task_datetime)


def build_todo_query(builder: QueryBuilder, key):
    """Build query for To Do."""
    ms365_task = key[CONF_TODO_LIST]
    show_completed = ms365_task[CONF_SHOW_COMPLETED]
    query = builder.select()
    if not show_completed:
        query = query & builder.unequal("status", "completed")
    start_offset = ms365_task.get(CONF_DUE_HOURS_BACKWARD_TO_GET)
    end_offset = ms365_task.get(CONF_DUE_HOURS_FORWARD_TO_GET)
    if start_offset:
        start = dt_util.utcnow() + timedelta(hours=start_offset)
        query = query & builder.greater_equal(
            "due", start.strftime("%Y-%m-%dT%H:%M:%S")
        )
    if end_offset:
        end = dt_util.utcnow() + timedelta(hours=end_offset)
        query = query & builder.less_equal("due", end.strftime("%Y-%m-%dT%H:%M:%S"))
    return query
