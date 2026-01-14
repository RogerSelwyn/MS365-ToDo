"""Configuration flow for the skyq platform."""

from copy import deepcopy

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import (
    config_entries,
)
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_NAME
from homeassistant.helpers.selector import BooleanSelector

from ..classes.config_entry import MS365ConfigEntry
from ..const import (
    CONF_ENABLE_UPDATE,
    CONF_ENTITY_NAME,
)
from ..helpers.utils import add_attribute_to_item
from .const_integration import (
    CONF_DUE_HOURS_BACKWARD_TO_GET,
    CONF_DUE_HOURS_FORWARD_TO_GET,
    CONF_MAX_TODOS,
    CONF_MAX_TODOS_DEFAULT,
    CONF_SHOW_COMPLETED,
    CONF_TODO_LIST,
    CONF_TRACK,
    CONF_TRACK_NEW,
    YAML_TODO_LISTS_FILENAME,
)
from .filemgmt_integration import (
    build_yaml_file_path,
    build_yaml_filename,
    read_todo_yaml_file,
    write_todo_yaml_file,
    write_yaml_file,
)
from .utils_integration import async_delete_todo

BOOLEAN_SELECTOR = BooleanSelector()


def integration_reconfigure_schema(entry_data):
    """Extend the schame with integration specific attributes."""
    return {
        vol.Optional(
            CONF_ENABLE_UPDATE, default=entry_data[CONF_ENABLE_UPDATE]
        ): cv.boolean,
    }


def integration_validate_schema(user_input):  # pylint: disable=unused-argument
    """Validate the user input."""
    return {}


async def async_integration_imports(hass, import_data):
    """Do the integration  level import tasks."""
    todo_lists = import_data["todos"]
    path = YAML_TODO_LISTS_FILENAME.format(
        f"_{import_data['data'].get(CONF_ENTITY_NAME)}"
    )
    yaml_filepath = build_yaml_file_path(hass, path)

    for todo_list in todo_lists.values():
        await hass.async_add_executor_job(write_yaml_file, yaml_filepath, todo_list)
    return


class MS365OptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options for MS365."""

    def __init__(self, entry: MS365ConfigEntry):
        """Initialize MS365 options flow."""

        self._track_new = entry.options.get(CONF_TRACK_NEW, True)
        self._max_todos = entry.options.get(CONF_MAX_TODOS, CONF_MAX_TODOS_DEFAULT)
        self._todos = []
        self._todo_list = []
        self._todo_list_selected = []
        self._todo_list_selected_original = []
        self._yaml_filename = build_yaml_filename(entry, YAML_TODO_LISTS_FILENAME)
        self._yaml_filepath = None
        self._todo_no = 0
        self._user_input = None

    async def async_step_init(
        self,
        user_input=None,  # pylint: disable=unused-argument
    ) -> ConfigFlowResult:
        """Set up the option flow."""

        self._yaml_filepath = build_yaml_file_path(self.hass, self._yaml_filename)
        self._todos = await self.hass.async_add_executor_job(
            read_todo_yaml_file,
            self._yaml_filepath,
        )

        for todo in self._todos:
            self._todo_list.append(todo[CONF_NAME])
            if todo[CONF_TRACK]:
                self._todo_list_selected.append(todo[CONF_NAME])

        self._todo_list_selected_original = deepcopy(self._todo_list_selected)
        return await self.async_step_user()

    async def async_step_user(self, user_input=None) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input:
            self._user_input = user_input
            self._track_new = user_input[CONF_TRACK_NEW]
            self._max_todos = user_input[CONF_MAX_TODOS]
            self._todo_list_selected = user_input[CONF_TODO_LIST]

            for todo in self._todos:
                todo[CONF_TRACK] = todo[CONF_NAME] in self._todo_list_selected

            return await self.async_step_todo_config()

        return self.async_show_form(
            step_id="user",
            description_placeholders={
                CONF_ENTITY_NAME: self.config_entry.data[CONF_ENTITY_NAME]
            },
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_TODO_LIST, default=self._todo_list_selected
                    ): cv.multi_select(self._todo_list),
                    vol.Optional(
                        CONF_TRACK_NEW,
                        default=self._track_new,
                    ): BOOLEAN_SELECTOR,
                    vol.Optional(
                        CONF_MAX_TODOS,
                        default=self._max_todos,
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=250)),
                }
            ),
            errors=errors,
            last_step=False,
        )

    async def async_step_todo_config(self, user_input=None) -> ConfigFlowResult:
        """Handle todo setup."""
        if user_input is not None:
            for todo in self._todos:
                if todo[CONF_NAME] == self._todo_list_selected[self._todo_no - 1]:
                    add_attribute_to_item(todo, user_input, CONF_SHOW_COMPLETED)
                    add_attribute_to_item(
                        todo, user_input, CONF_DUE_HOURS_BACKWARD_TO_GET
                    )
                    add_attribute_to_item(
                        todo, user_input, CONF_DUE_HOURS_FORWARD_TO_GET
                    )

                    return await self.async_step_todo_config()

        if self._todo_no == len(self._todo_list_selected):
            return await self._async_tidy_up(self._user_input)

        todo_item = self._get_todo_item()
        last_step = self._todo_no == len(self._todo_list_selected)
        return self.async_show_form(
            step_id="todo_config",
            description_placeholders={
                CONF_ENTITY_NAME: self.config_entry.data[CONF_ENTITY_NAME],
                CONF_NAME: todo_item[CONF_NAME],
            },
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SHOW_COMPLETED,
                        default=todo_item[CONF_SHOW_COMPLETED],
                    ): BOOLEAN_SELECTOR,
                    vol.Optional(
                        CONF_DUE_HOURS_BACKWARD_TO_GET,
                        description={
                            "suggested_value": todo_item.get(
                                CONF_DUE_HOURS_BACKWARD_TO_GET
                            )
                        },
                    ): int,
                    vol.Optional(
                        CONF_DUE_HOURS_FORWARD_TO_GET,
                        description={
                            "suggested_value": todo_item.get(
                                CONF_DUE_HOURS_FORWARD_TO_GET
                            )
                        },
                    ): int,
                }
            ),
            last_step=last_step,
        )

    def _get_todo_item(self):
        self._todo_no += 1
        for todo in self._todos:
            if todo[CONF_NAME] == self._todo_list_selected[self._todo_no - 1]:
                return todo

    async def _async_tidy_up(self, user_input):
        await self.hass.async_add_executor_job(
            write_todo_yaml_file, self._yaml_filepath, self._todos
        )
        for todo in self._todo_list_selected_original:
            if todo not in self._todo_list_selected:
                await async_delete_todo(self.hass, self.config_entry, todo)
        update = self.async_create_entry(title="", data=user_input)
        await self.hass.config_entries.async_reload(self._config_entry_id)
        return update
