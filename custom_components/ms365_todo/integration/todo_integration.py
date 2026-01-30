"""Todo processing."""

import logging
from datetime import datetime, timedelta

from homeassistant.components.todo import TodoItem, TodoListEntity
from homeassistant.components.todo.const import TodoItemStatus, TodoListEntityFeature
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.core import (
    HomeAssistant,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util
from O365.utils.query import (  # pylint: disable=no-name-in-module, import-error
    QueryBuilder,
)
from requests.exceptions import HTTPError

from ..classes.config_entry import MS365ConfigEntry
from ..classes.entity import MS365Entity
from ..const import (
    ATTR_DATA,
    CONF_ENABLE_UPDATE,
    CONF_ENTITY_KEY,
    CONF_ENTITY_TYPE,
    DATETIME_FORMAT,
    EVENT_HA_EVENT,
)
from .const_integration import (
    ATTR_ALL_TODOS,
    ATTR_CHECKLIST_ITEM_ID,
    ATTR_CHECKLIST_ITEMS,
    ATTR_COMPLETED,
    ATTR_CREATED,
    ATTR_DESCRIPTION,
    ATTR_DUE,
    ATTR_ID,
    ATTR_IS_CHECKED,
    ATTR_NAME,
    ATTR_OVERDUE_TODOS,
    ATTR_REMINDER,
    ATTR_STATUS,
    ATTR_SUBJECT,
    ATTR_TODO_ID,
    CONF_DUE_HOURS_BACKWARD_TO_GET,
    CONF_DUE_HOURS_FORWARD_TO_GET,
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
from .filemgmt_integration import (
    async_check_for_deleted_todos,
    async_update_todo_list_file,
)
from .schema_integration import (
    TODO_SERVICE_COMPLETE_SCHEMA,
    TODO_SERVICE_DELETE_SCHEMA,
    TODO_SERVICE_DELETE_STEP_SCHEMA,
    TODO_SERVICE_NEW_SCHEMA,
    TODO_SERVICE_NEW_STEP_SCHEMA,
    TODO_SERVICE_UPDATE_SCHEMA,
    TODO_SERVICE_UPDATE_STEP_SCHEMA,
)

_LOGGER = logging.getLogger(__name__)


async def async_todo_integration_setup_entry(
    hass: HomeAssistant,
    entry: MS365ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> bool:
    """Set up the MS365 platform."""

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
            supports_response=SupportsResponse.OPTIONAL,
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
        platform.async_register_entity_service(
            "new_todo_checklist_item",
            TODO_SERVICE_NEW_STEP_SCHEMA,
            "async_new_todo_checklist_item",
            supports_response=SupportsResponse.OPTIONAL,
        )
        platform.async_register_entity_service(
            "update_todo_checklist_item",
            TODO_SERVICE_UPDATE_STEP_SCHEMA,
            "async_update_todo_checklist_item",
        )
        platform.async_register_entity_service(
            "delete_todo_checklist_item",
            TODO_SERVICE_DELETE_STEP_SCHEMA,
            "async_delete_todo_checklist_item",
        )


class MS365TodoList(MS365Entity, TodoListEntity):  # pylint: disable=abstract-method
    """MS365 To Do processing."""

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
        """Initialise the To Do List."""
        super().__init__(coordinator, entry, name, entity_id, unique_id)
        self.todolist = ms365_todo_folder
        self._show_completed = yaml_todo_list.get(CONF_SHOW_COMPLETED)

        self.todo_last_created = dt_util.utcnow() - timedelta(minutes=5)
        self.todo_last_completed = dt_util.utcnow() - timedelta(minutes=5)
        self._ha_timezone = dt_util.DEFAULT_TIME_ZONE
        self._zero_date = datetime(1, 1, 1, 0, 0, 0, tzinfo=self._ha_timezone)
        self._state = None
        self._todo_items = None
        self._extra_attributes = None
        self._update_status(hass)
        if entry.data.get(CONF_ENABLE_UPDATE):
            self._attr_supported_features = (
                TodoListEntityFeature.CREATE_TODO_ITEM
                | TodoListEntityFeature.UPDATE_TODO_ITEM
                | TodoListEntityFeature.DELETE_TODO_ITEM
                | TodoListEntityFeature.SET_DUE_DATETIME_ON_ITEM
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
                    due=todo.reminder if todo.is_reminder_on else todo.due,
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
                    hass,
                    EVENT_NEW_TODO,
                    todo.task_id,
                    ATTR_CREATED,
                    todo.created,
                    todo.subject,
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
                ATTR_STATUS: item.status,
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
                todo[ATTR_DUE] = item.due
                if item.due < dt_util.utcnow():
                    overdue_todo = {
                        ATTR_SUBJECT: item.subject,
                        ATTR_TODO_ID: item.task_id,
                        ATTR_DUE: item.due,
                    }
                    if item.is_reminder_on:
                        overdue_todo[ATTR_REMINDER] = item.reminder
                    overdue_todos.append(overdue_todo)

            if item.is_reminder_on:
                todo[ATTR_REMINDER] = item.reminder

            if cl_items := list(item.checklist_items):
                todo[ATTR_CHECKLIST_ITEMS] = [
                    {
                        ATTR_NAME: cl_item.displayname,
                        ATTR_IS_CHECKED: cl_item.is_checked,
                        ATTR_ID: cl_item.item_id,
                    }
                    for cl_item in cl_items
                ]

            all_todos.append(todo)

        extra_attributes = {ATTR_ALL_TODOS: all_todos}
        if overdue_todos:
            extra_attributes[ATTR_OVERDUE_TODOS] = overdue_todos
        return extra_attributes

    async def async_create_todo_item(self, item: TodoItem) -> None:
        """Add an item to the To Do list."""
        reminder = item.due if isinstance(item.due, datetime) else None
        await self.async_new_todo(
            subject=item.summary,
            description=item.description,
            due=item.due,
            reminder=reminder,
        )

    async def async_new_todo(
        self, subject, description=None, due=None, reminder=None
    ) -> ServiceResponse:
        """Create a new task for this task list."""
        self._validate_task_permissions()

        new_ms365_todo = await self.hass.async_add_executor_job(self.todolist.new_task)
        await self._async_save_todo(new_ms365_todo, subject, description, due, reminder)
        self._raise_event(
            EVENT_NEW_TODO, new_ms365_todo.task_id, new_ms365_todo.subject
        )
        self.todo_last_created = new_ms365_todo.created
        await self.coordinator.async_refresh()
        return {ATTR_TODO_ID: new_ms365_todo.task_id}

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Add an item to the To Do list."""
        ms365_todo = await self.hass.async_add_executor_job(
            self.todolist.get_task, item.uid
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
                return

        if (
            item.summary != ms365_todo.subject
            or item.description != ms365_todo.body
            or (item.due and item.due != ms365_todo.due)
            or (not item.due and (ms365_todo.due or ms365_todo.reminder))
        ):
            reminder = item.due if isinstance(item.due, datetime) else None
            await self.async_update_todo(
                todo_id=item.uid,
                subject=item.summary,
                description=item.description,
                due=item.due,
                remove_due=not bool(item.due),
                reminder=reminder,
                remove_reminder=not bool(item.due),
                ms365_todo=ms365_todo,
                hatodo=True,
            )

    async def async_update_todo(
        self,
        todo_id,
        subject=None,
        description=None,
        due=None,
        remove_due=None,
        reminder=None,
        remove_reminder=None,
        ms365_todo=None,
        hatodo=False,
    ):
        """Update a task for this task list."""
        self._validate_task_permissions()

        if not ms365_todo:
            ms365_todo = await self.hass.async_add_executor_job(
                self.todolist.get_task, todo_id
            )
        if response := await self._async_save_todo(
            ms365_todo,
            subject,
            description,
            due,
            reminder,
            hatodo,
            remove_due,
            remove_reminder,
        ):
            self._raise_event(EVENT_UPDATE_TODO, todo_id)
            await self.coordinator.async_refresh()
        return response

    async def async_delete_todo_items(self, uids: list[str]) -> None:
        """Delete items from the To Do list."""
        for todo_id in uids:
            await self.async_delete_todo(todo_id)

    async def async_delete_todo(self, todo_id):
        """Delete task for this task list."""
        self._validate_task_permissions()

        ms365_todo = await self.hass.async_add_executor_job(
            self.todolist.get_task, todo_id
        )
        await self.hass.async_add_executor_job(ms365_todo.delete)
        self._raise_event(EVENT_DELETE_TODO, todo_id)
        await self.coordinator.async_refresh()
        return True

    async def async_complete_todo(self, todo_id, completed, ms365_todo=None):
        """Complete task for this task list."""
        self._validate_task_permissions()

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
        await self.hass.async_add_executor_job(ms365_todo.mark_completed)
        await self.hass.async_add_executor_job(ms365_todo.save)
        self._raise_event(EVENT_COMPLETED_TODO, todo_id)
        self.todo_last_completed = dt_util.utcnow()

    async def _async_uncomplete_task(self, ms365_todo, todo_id):
        if not ms365_todo.completed:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="todo_not_completed",
            )
        await self.hass.async_add_executor_job(ms365_todo.mark_uncompleted)
        await self.hass.async_add_executor_job(ms365_todo.save)
        self._raise_event(EVENT_UNCOMPLETED_TODO, todo_id)

    async def _async_save_todo(
        self,
        ms365_todo,
        subject,
        description,
        due,
        reminder,
        hatodo=False,
        remove_due=None,
        remove_reminder=None,
    ):
        # sourcery skip: raise-from-previous-error
        if subject or hatodo:
            ms365_todo.subject = subject
        if description or hatodo:
            ms365_todo.body = description

        if due:
            ms365_todo.due = self._add_timezone(due)
        if remove_due:
            ms365_todo.due = None

        if reminder:
            ms365_todo.reminder = self._add_timezone(reminder)
        if remove_reminder:
            ms365_todo.reminder = None

        return await self.hass.async_add_executor_job(ms365_todo.save)

    def _add_timezone(self, value):
        if isinstance(value, datetime) and not value.tzinfo:
            return value.replace(tzinfo=self._ha_timezone)
        return value

    async def async_new_todo_checklist_item(self, todo_id, name) -> ServiceResponse:
        """Create a new task checklist_item for this task."""
        ms365_todo = await self._async_get_todo_for_checklist_item(todo_id)

        new_ms365_todo_checklist_item = await self.hass.async_add_executor_job(
            ms365_todo.new_checklist_item, name
        )
        await self.hass.async_add_executor_job(new_ms365_todo_checklist_item.save)
        await self.coordinator.async_refresh()
        return {ATTR_CHECKLIST_ITEM_ID: new_ms365_todo_checklist_item.item_id}

    async def async_update_todo_checklist_item(
        self, todo_id, checklist_item_id, status
    ):
        """Update a task checklist_item for this task."""

        ms365_todo = await self._async_get_todo_for_checklist_item(todo_id)

        ms365_todo_checklist_item = await self.hass.async_add_executor_job(
            ms365_todo.get_checklist_item, checklist_item_id
        )
        if status == TodoItemStatus.COMPLETED:
            await self.hass.async_add_executor_job(
                ms365_todo_checklist_item.mark_checked
            )
        else:
            await self.hass.async_add_executor_job(
                ms365_todo_checklist_item.mark_unchecked
            )

        if response := await self.hass.async_add_executor_job(
            ms365_todo_checklist_item.save
        ):
            await self.coordinator.async_refresh()
        return response

    async def async_delete_todo_checklist_item(self, todo_id, checklist_item_id):
        """Delete a task checklist_item for this task."""
        ms365_todo = await self._async_get_todo_for_checklist_item(todo_id)

        ms365_todo_checklist_item = await self.hass.async_add_executor_job(
            ms365_todo.get_checklist_item, checklist_item_id
        )

        if response := await self.hass.async_add_executor_job(
            ms365_todo_checklist_item.delete
        ):
            await self.coordinator.async_refresh()
        return response

    async def _async_get_todo_for_checklist_item(self, todo_id):
        self._validate_task_permissions()

        try:
            return await self.hass.async_add_executor_job(
                self.todolist.get_task, todo_id
            )
        except HTTPError as err:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="todo_not_retrieved",
            ) from err

    def _raise_event(self, event_type, todo_id, subject=None):
        event_message = {ATTR_TODO_ID: todo_id, EVENT_HA_EVENT: True}
        if subject:
            event_message[ATTR_SUBJECT] = subject

        self.hass.bus.fire(
            f"{DOMAIN}_{event_type}",
            event_message,
        )
        _LOGGER.debug("%s - %s", event_type, todo_id)

    def _validate_task_permissions(self):
        return self._validate_permissions(
            PERM_TASKS_READWRITE,
            f"Not authorised to edit To Dos - requires permission: {PERM_TASKS_READWRITE}",
        )


def _raise_event_external(
    hass, event_type, todo_id, time_type, task_datetime, subject=None
):
    event_message = {
        ATTR_TODO_ID: todo_id,
        time_type: task_datetime,
        EVENT_HA_EVENT: False,
    }
    if subject:
        event_message[ATTR_SUBJECT] = subject

    hass.bus.fire(
        f"{DOMAIN}_{event_type}",
        event_message,
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


async def async_scan_for_todo_lists(hass, account, entry):
    """Scan for new task lists."""

    todos = await hass.async_add_executor_job(account.tasks)

    todolists = await hass.async_add_executor_job(todos.list_folders_delta)
    track = entry.options.get(CONF_TRACK_NEW, True)
    for todo in todolists:
        await async_update_todo_list_file(
            entry,
            todo,
            hass,
            track,
        )
    return await async_check_for_deleted_todos(entry, todolists, hass)
