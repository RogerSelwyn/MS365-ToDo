"""Todo processing."""

import logging
from datetime import datetime, timedelta

from homeassistant.components.todo import TodoItem, TodoListEntity
from homeassistant.components.todo.const import TodoItemStatus, TodoListEntityFeature
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt

from .classes.entity import MS365Entity
from .const import (
    ATTR_DATA,
    CONF_ENTITY_TYPE,
    DATETIME_FORMAT,
    EVENT_HA_EVENT,
)
from .helpers.config_entry import MS365ConfigEntry
from .integration.const_integration import (
    ATTR_ALL_TODOS,
    ATTR_COMPLETED,
    ATTR_CREATED,
    ATTR_DESCRIPTION,
    ATTR_DUE,
    ATTR_OVERDUE_TODOS,
    ATTR_REMINDER,
    ATTR_STATUS,
    ATTR_SUBJECT,
    ATTR_TODO_ID,
    CONF_DUE_HOURS_BACKWARD_TO_GET,
    CONF_DUE_HOURS_FORWARD_TO_GET,
    CONF_ENABLE_UPDATE,
    CONF_ENTITY_KEY,
    CONF_MS365_TODO_FOLDER,
    CONF_SHOW_COMPLETED,
    CONF_TODO_LIST,
    CONF_TRACK_NEW,
    DOMAIN,
    EVENT_COMPLETED_TODO,
    EVENT_DELETE_TODO,
    EVENT_NEW_TODO,
    EVENT_UNCOMPLETED_TODO,
    EVENT_UPDATE_TODO,
    PERM_TASKS_READWRITE,
    TODO_TODO,
)
from .integration.filemgmt_integration import async_update_todo_list_file
from .integration.schema_integration import (
    TODO_SERVICE_COMPLETE_SCHEMA,
    TODO_SERVICE_DELETE_SCHEMA,
    TODO_SERVICE_NEW_SCHEMA,
    TODO_SERVICE_UPDATE_SCHEMA,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: MS365ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the MS365 platform."""

    account = entry.runtime_data.account

    is_authenticated = account.is_authenticated
    if not is_authenticated:
        return False

    coordinator = entry.runtime_data.coordinator
    todoentities = [
        MS365TodoList(
            hass,
            coordinator,
            key[CONF_MS365_TODO_FOLDER],
            key[CONF_NAME],
            key[CONF_TODO_LIST],
            entry,
            key[CONF_ENTITY_KEY],
            key[CONF_UNIQUE_ID],
        )
        for key in entry.runtime_data.sensors
        if key[CONF_ENTITY_TYPE] == TODO_TODO
    ]
    async_add_entities(todoentities, False)
    await _async_setup_register_services(entry)

    return True


async def _async_setup_register_services(entry: MS365ConfigEntry):
    perms = entry.runtime_data.permissions
    await _async_setup_todo_services(entry, perms)


async def _async_setup_todo_services(entry: MS365ConfigEntry, perms):
    if not entry.data.get(CONF_ENABLE_UPDATE):
        return

    platform = entity_platform.async_get_current_platform()
    if perms.validate_authorization(PERM_TASKS_READWRITE):
        platform.async_register_entity_service(
            "new_todo",
            TODO_SERVICE_NEW_SCHEMA,
            "async_new_todo",
        )
        platform.async_register_entity_service(
            "update_todo",
            TODO_SERVICE_UPDATE_SCHEMA,
            "async_update_todo",
        )
        platform.async_register_entity_service(
            "delete_todo",
            TODO_SERVICE_DELETE_SCHEMA,
            "async_delete_todo",
        )
        platform.async_register_entity_service(
            "complete_todo",
            TODO_SERVICE_COMPLETE_SCHEMA,
            "async_complete_todo",
        )


class MS365TodoList(MS365Entity, TodoListEntity):  # pylint: disable=abstract-method
    """MS365 To-Do processing."""

    def __init__(
        self,
        hass,
        coordinator,
        ms365_todo_folder,
        name,
        yaml_todo_list,
        entry: MS365ConfigEntry,
        entity_id,
        unique_id,
    ):
        """Initialise the To-Do List."""
        super().__init__(coordinator, entry, name, entity_id, unique_id)
        self.todolist = ms365_todo_folder
        self._show_completed = yaml_todo_list.get(CONF_SHOW_COMPLETED)

        self.todo_last_created = dt.utcnow() - timedelta(minutes=5)
        self.todo_last_completed = dt.utcnow() - timedelta(minutes=5)
        self._zero_date = datetime(1, 1, 1, 0, 0, 0, tzinfo=dt.DEFAULT_TIME_ZONE)
        self._state = None
        self._todo_items = None
        self._extra_attributes = None
        self._update_status(hass)
        if entry.data.get(CONF_ENABLE_UPDATE):
            self._attr_supported_features = (
                TodoListEntityFeature.CREATE_TODO_ITEM
                | TodoListEntityFeature.UPDATE_TODO_ITEM
                | TodoListEntityFeature.DELETE_TODO_ITEM
                | TodoListEntityFeature.SET_DUE_DATE_ON_ITEM
                | TodoListEntityFeature.SET_DESCRIPTION_ON_ITEM
            )

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
        self._state = sum(not task.completed for task in todos)
        self._todo_items = []
        for todo in todos:
            completed = (
                TodoItemStatus.COMPLETED
                if todo.completed
                else TodoItemStatus.NEEDS_ACTION
            )
            self._todo_items.append(
                TodoItem(
                    uid=todo.task_id,
                    summary=todo.subject,
                    status=completed,
                    description=todo.body,
                    due=todo.due,
                )
            )

            self._extra_attributes = self._update_extra_state_attributes(todos)

        todo_last_completed = self._zero_date
        todo_last_created = self._zero_date
        for todo in todos:
            if todo.completed and todo.completed > self.todo_last_completed:
                _raise_event_external(
                    hass,
                    EVENT_COMPLETED_TODO,
                    todo.task_id,
                    ATTR_COMPLETED,
                    todo.completed,
                )
                if todo.completed > todo_last_completed:
                    todo_last_completed = todo.completed
            if todo.created and todo.created > self.todo_last_created:
                _raise_event_external(
                    hass, EVENT_NEW_TODO, todo.task_id, ATTR_CREATED, todo.created
                )
                if todo.created > todo_last_created:
                    todo_last_created = todo.created

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
                ATTR_SUBJECT: item.subject,
                ATTR_TODO_ID: item.task_id,
                ATTR_STATUS: item._Task__status,
            }
            if item.body:
                todo[ATTR_DESCRIPTION] = item.body
            if self._show_completed:
                todo[ATTR_COMPLETED] = (
                    item.completed.strftime(DATETIME_FORMAT)
                    if item.completed
                    else False
                )
            if item.due:
                due = item.due.date()
                todo[ATTR_DUE] = due
                if due < dt.utcnow().date():
                    overdue_todo = {
                        ATTR_SUBJECT: item.subject,
                        ATTR_TODO_ID: item.task_id,
                        ATTR_DUE: due,
                    }
                    if item.is_reminder_on:
                        overdue_todo[ATTR_REMINDER] = item.reminder
                    overdue_todos.append(overdue_todo)

            if item.is_reminder_on:
                todo[ATTR_REMINDER] = item.reminder

            all_todos.append(todo)

        extra_attributes = {ATTR_ALL_TODOS: all_todos}
        if overdue_todos:
            extra_attributes[ATTR_OVERDUE_TODOS] = overdue_todos
        return extra_attributes

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Add an item to the To-do list."""
        await self.async_new_todo(
            subject=item.summary, description=item.description, due=item.due
        )

    async def async_new_todo(self, subject, description=None, due=None, reminder=None):
        """Create a new task for this task list."""
        if not self._validate_task_permissions():
            return False

        new_ms365_todo = self.todolist.new_task()
        await self._async_save_todo(new_ms365_todo, subject, description, due, reminder)
        self._raise_event(EVENT_NEW_TODO, new_ms365_todo.task_id)
        self.todo_last_created = new_ms365_todo.created
        await self.coordinator.async_refresh()
        return True

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Add an item to the To-do list."""
        ms365_todo = await self.hass.async_add_executor_job(
            self.todolist.get_task, item.uid
        )
        if (
            item.summary != ms365_todo.subject
            or item.description != ms365_todo.body
            or (item.due and item.due != ms365_todo.due)
        ):
            await self.async_update_todo(
                todo_id=item.uid,
                subject=item.summary,
                description=item.description,
                due=item.due,
                ms365_todo=ms365_todo,
                hatodo=True,
            )
        if item.status:
            completed = None
            if item.status == TodoItemStatus.COMPLETED and not ms365_todo.completed:
                completed = True
            elif item.status == TodoItemStatus.NEEDS_ACTION and ms365_todo.completed:
                completed = False
            if completed is not None:
                await self.async_complete_todo(
                    item.uid, completed, ms365_todo=ms365_todo
                )

    async def async_update_todo(
        self,
        todo_id,
        subject=None,
        description=None,
        due=None,
        reminder=None,
        ms365_todo=None,
        hatodo=False,
    ):
        """Update a task for this task list."""
        if not self._validate_task_permissions():
            return False

        if not ms365_todo:
            ms365_todo = await self.hass.async_add_executor_job(
                self.todolist.get_task, todo_id
            )
        await self._async_save_todo(
            ms365_todo, subject, description, due, reminder, hatodo
        )
        self._raise_event(EVENT_UPDATE_TODO, todo_id)
        await self.coordinator.async_refresh()
        return True

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """Delete items from the To-do list."""
        for todo_id in uids:
            await self.async_delete_todo(todo_id)

    async def async_delete_todo(self, todo_id):
        """Delete task for this task list."""
        if not self._validate_task_permissions():
            return False

        ms365_todo = await self.hass.async_add_executor_job(
            self.todolist.get_task, todo_id
        )
        await self.hass.async_add_executor_job(ms365_todo.delete)
        self._raise_event(EVENT_DELETE_TODO, todo_id)
        await self.coordinator.async_refresh()
        return True

    async def async_complete_todo(self, todo_id, completed, ms365_todo=None):
        """Complete task for this task list."""
        if not self._validate_task_permissions():
            return False

        if not ms365_todo:
            ms365_todo = await self.hass.async_add_executor_job(
                self.todolist.get_task, todo_id
            )
        if completed:
            await self._async_complete_task(ms365_todo, todo_id)
        else:
            await self._async_uncomplete_task(ms365_todo, todo_id)

        await self.coordinator.async_refresh()
        return True

    async def _async_complete_task(self, ms365_todo, todo_id):
        if ms365_todo.completed:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="todo_completed",
            )
        ms365_todo.mark_completed()
        self.hass.async_add_executor_job(ms365_todo.save)
        self._raise_event(EVENT_COMPLETED_TODO, todo_id)
        self.todo_last_completed = dt.utcnow()

    async def _async_uncomplete_task(self, ms365_todo, todo_id):
        if not ms365_todo.completed:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="todo_not_completed",
            )
        ms365_todo.mark_uncompleted()
        self.hass.async_add_executor_job(ms365_todo.save)
        self._raise_event(EVENT_UNCOMPLETED_TODO, todo_id)

    async def _async_save_todo(
        self, ms365_todo, subject, description, due, reminder, hatodo=False
    ):
        # sourcery skip: raise-from-previous-error
        if subject or hatodo:
            ms365_todo.subject = subject
        if description or hatodo:
            ms365_todo.body = description

        if due:
            if isinstance(due, str):
                try:
                    if len(due) > 10:
                        ms365_todo.due = dt.parse_datetime(due).date()
                    else:
                        ms365_todo.due = dt.parse_date(due)
                except ValueError:
                    raise ServiceValidationError(  # pylint: disable=raise-missing-from
                        translation_domain=DOMAIN,
                        translation_key="due_date_invalid",
                        translation_placeholders={
                            "due": due,
                        },
                    )
            else:
                ms365_todo.due = due

        if reminder:
            ms365_todo.reminder = reminder

        await self.hass.async_add_executor_job(ms365_todo.save)

    def _raise_event(self, event_type, todo_id):
        self.hass.bus.fire(
            f"{DOMAIN}_{event_type}",
            {ATTR_TODO_ID: todo_id, EVENT_HA_EVENT: True},
        )
        _LOGGER.debug("%s - %s", event_type, todo_id)

    def _validate_task_permissions(self):
        return self._validate_permissions(
            PERM_TASKS_READWRITE,
            f"Not authorised to create new To-Do - requires permission: {PERM_TASKS_READWRITE}",
        )


def _raise_event_external(hass, event_type, todo_id, time_type, task_datetime):
    hass.bus.fire(
        f"{DOMAIN}_{event_type}",
        {ATTR_TODO_ID: todo_id, time_type: task_datetime, EVENT_HA_EVENT: False},
    )
    _LOGGER.debug("%s - %s - %s", event_type, todo_id, task_datetime)


def build_todo_query(key, todo):
    """Build query for To-Do."""
    ms365_task = key[CONF_TODO_LIST]
    show_completed = ms365_task[CONF_SHOW_COMPLETED]
    query = todo.new_query()
    if not show_completed:
        query = query.on_attribute("status").unequal("completed")
    start_offset = ms365_task.get(CONF_DUE_HOURS_BACKWARD_TO_GET)
    end_offset = ms365_task.get(CONF_DUE_HOURS_FORWARD_TO_GET)
    if start_offset:
        start = dt.utcnow() + timedelta(hours=start_offset)
        query.chain("and").on_attribute("due").greater_equal(
            start.strftime("%Y-%m-%dT%H:%M:%S")
        )
    if end_offset:
        end = dt.utcnow() + timedelta(hours=end_offset)
        query.chain("and").on_attribute("due").less_equal(
            end.strftime("%Y-%m-%dT%H:%M:%S")
        )
    return query


async def async_scan_for_todo_lists(hass, account, entry):
    """Scan for new task lists."""

    todos = account.tasks()

    todolists = await hass.async_add_executor_job(todos.list_folders)
    track = entry.options.get(CONF_TRACK_NEW, True)
    for todo in todolists:
        await async_update_todo_list_file(
            entry,
            todo,
            hass,
            track,
        )
