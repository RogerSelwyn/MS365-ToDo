"""Sensor processing."""

import functools as ft
import logging
from datetime import MAXYEAR, datetime, timedelta, timezone

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from requests.exceptions import HTTPError

from O365.utils.query import (  # pylint: disable=no-name-in-module, import-error
    QueryBuilder,
)

from ..const import (
    ATTR_DATA,
    ATTR_ERROR,
    ATTR_STATE,
    CONF_ENTITY_KEY,
    CONF_ENTITY_NAME,
    CONF_ENTITY_TYPE,
)
from ..helpers.utils import build_entity_id
from .const_integration import (
    ATTR_TODOS,
    CONF_MAX_TODOS,
    CONF_MAX_TODOS_DEFAULT,
    CONF_MS365_TODO_FOLDER,
    # CONF_PLANNER,
    CONF_TODO_LIST,
    CONF_TODO_LIST_ID,
    CONF_TRACK,
    ENTITY_ID_FORMAT_TODO,
    # PLANNER_NAME,
    # PLANNER_UNIQUE_ID,
    # TODO_PLANNER,
    TODO_TODO,
    YAML_TODO_LISTS_FILENAME,
)
from .filemgmt_integration import (
    build_yaml_file_path,
    build_yaml_filename,
    load_yaml_file,
)
from .schema_integration import YAML_TODO_LIST_SCHEMA
from .todo_integration import async_scan_for_todo_lists, build_todo_query
from .utils_integration import async_delete_todo

MAXDATETIME = datetime(MAXYEAR, 1, 1, tzinfo=timezone.utc)
_LOGGER = logging.getLogger(__name__)


class MS365SensorCordinator(DataUpdateCoordinator):
    """MS365 sensor data update coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, account):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            # Name of the data. For logging purposes.
            name="MS365 To Do",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
        )
        self._entry = entry
        self._account = account
        self._entity_name = entry.data[CONF_ENTITY_NAME]
        self._max_todos = entry.options.get(CONF_MAX_TODOS, CONF_MAX_TODOS_DEFAULT)
        self.keys = []
        self._data = {}
        self._builder = QueryBuilder(protocol=account.protocol)

    async def _async_setup(self):
        """Do the initial setup of the entities."""
        todo_keys = await self._async_todo_sensors()
        # planner_keys = []  # await self._async_planner_sensors()
        self.keys = todo_keys  # + planner_keys
        return self.keys

    async def _async_todo_sensors(self):
        deleted_todo_lists = await async_scan_for_todo_lists(
            self.hass, self._account, self._entry
        )
        await self._async_delete_todo_list_entities(deleted_todo_lists)

        yaml_filename = build_yaml_filename(self._entry, YAML_TODO_LISTS_FILENAME)
        yaml_filepath = build_yaml_file_path(self.hass, yaml_filename)
        ms365_task_dict = await self.hass.async_add_executor_job(
            load_yaml_file,
            yaml_filepath,
            CONF_TODO_LIST_ID,
            YAML_TODO_LIST_SCHEMA,
        )
        ms365_todo_lists = list(ms365_task_dict.values())
        return await self._async_todo_entities(ms365_todo_lists)

    async def _async_todo_entities(self, ms365_todo_lists):
        keys = []
        ms365_todos = await self.hass.async_add_executor_job(self._account.tasks)
        for ms365_todo_list in ms365_todo_lists:
            track = ms365_todo_list.get(CONF_TRACK)
            if not track:
                continue

            ms365_todo_list_id = ms365_todo_list.get(CONF_TODO_LIST_ID)
            name = f"{self._entity_name} {ms365_todo_list.get(CONF_NAME)}"

            try:
                ms365_todo = await self.hass.async_add_executor_job(  # pylint: disable=no-member
                    ft.partial(
                        ms365_todos.get_folder,
                        folder_id=ms365_todo_list_id,
                    )
                )
                unique_id = f"{self._entity_name}_{ms365_todo_list_id}"
                new_key = {
                    CONF_ENTITY_KEY: build_entity_id(
                        self.hass, ENTITY_ID_FORMAT_TODO, name
                    ),
                    CONF_UNIQUE_ID: unique_id,
                    CONF_MS365_TODO_FOLDER: ms365_todo,
                    CONF_NAME: name,
                    CONF_TODO_LIST: ms365_todo_list,
                    CONF_ENTITY_TYPE: TODO_TODO,
                }

                keys.append(new_key)

            except HTTPError:
                _LOGGER.warning(
                    "MS365 To Do list not found for: %s - Please remove from MS365_todo_%s.yaml",
                    name,
                    self._entity_name,
                )
        return keys

    async def _async_delete_todo_list_entities(self, deleted_todo_lists):
        for todo_list in deleted_todo_lists:
            await async_delete_todo(self.hass, self._entry, todo_list[CONF_NAME])

    # async def _async_planner_sensors(self):
    #     return await self._async_planner_entities()

    # async def _async_planner_entities(self):
    #     keys = []
    #     planner = await self.hass.async_add_executor_job(self._account.planner)
    #     name = f"{self._entity_name} {PLANNER_NAME}"
    #     unique_id = f"{self._entity_name}_{PLANNER_UNIQUE_ID}"
    #     new_key = {
    #         CONF_ENTITY_KEY: build_entity_id(self.hass, ENTITY_ID_FORMAT_TODO, name),
    #         CONF_UNIQUE_ID: unique_id,
    #         CONF_NAME: name,
    #         CONF_PLANNER: planner,
    #         CONF_ENTITY_TYPE: TODO_PLANNER,
    #     }

    #     keys.append(new_key)
    #     return keys

    async def _async_update_data(self):
        _LOGGER.debug(
            "Doing %s sensor update(s) for: %s", len(self.keys), self._entity_name
        )

        for key in self.keys:
            entity_type = key[CONF_ENTITY_TYPE]
            if entity_type == TODO_TODO:
                await self._async_todos_update(key)
            # if entity_type == TODO_PLANNER:
            #     await self._async_planner_update(key)

        return self._data

    async def _async_todos_update(self, key):
        """Update state."""
        entity_key = key[CONF_ENTITY_KEY]
        if entity_key in self._data:
            error = self._data[entity_key][ATTR_ERROR]
        else:
            self._data[entity_key] = {ATTR_TODOS: {}, ATTR_STATE: 0}
            error = False
        data, error = await self._async_todos_update_query(key, error)
        if not error:
            todos = await self.hass.async_add_executor_job(list, data)
            todossorted = sorted(
                todos,
                key=lambda x: ((x.due or MAXDATETIME), (x.reminder or MAXDATETIME)),
            )
            self._data[entity_key][ATTR_DATA] = todossorted

        self._data[entity_key][ATTR_ERROR] = error

    async def _async_todos_update_query(self, key, error):
        data = None
        ms365_todo = key[CONF_MS365_TODO_FOLDER]
        full_query = build_todo_query(
            self._builder,
            key,
        )
        name = key[CONF_NAME]

        try:
            data = await self.hass.async_add_executor_job(  # pylint: disable=no-member
                ft.partial(
                    ms365_todo.get_tasks, batch=self._max_todos, query=full_query
                )
            )
            if error:
                _LOGGER.info("MS365 To Do list reconnected for: %s", name)
                error = False
        except HTTPError:
            if not error:
                _LOGGER.error(
                    "MS365 To Do list not found for: %s - Has it been deleted?",
                    name,
                )
                error = True

        return data, error

    # async def _async_planner_update(self, key):
    #     """Update state."""
    #     entity_key = key[CONF_ENTITY_KEY]
    #     self._data[entity_key] = {ATTR_TODOS: {}, ATTR_STATE: 0}
    #     data = await self._async_planner_update_query(key)

    #     todos = await self.hass.async_add_executor_job(list, data)
    #     todossorted = sorted(
    #         todos,
    #         key=lambda x: (x.due_date_time or MAXDATETIME),
    #     )
    #     self._data[entity_key][ATTR_DATA] = todossorted

    # async def _async_planner_update_query(self, key):
    #     data = None
    #     planner = key[CONF_PLANNER]

    #     data = await self.hass.async_add_executor_job(  # pylint: disable=no-member
    #         planner.get_my_tasks
    #     )

    #     return data
