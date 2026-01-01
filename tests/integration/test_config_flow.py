# pylint: disable=line-too-long, unused-argument
"""Test the config flow."""

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from requests_mock import Mocker

from custom_components.ms365_todo.integration.const_integration import (
    CONF_DUE_HOURS_BACKWARD_TO_GET,
    CONF_DUE_HOURS_FORWARD_TO_GET,
    CONF_SHOW_COMPLETED,
    CONF_TODO_LIST,
    CONF_MAX_TODOS,
    CONF_TRACK_NEW,
)

from ..helpers.mock_config_entry import MS365MockConfigEntry
from ..helpers.utils import get_schema_default
from .const_integration import UPDATE_TODO_LIST, UPDATE_MAX_TODOS
from .helpers_integration.mocks import MS365MOCKS
from .helpers_integration.utils_integration import check_yaml_file_contents, yaml_setup


async def test_options_flow(
    tmp_path,
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test the options flow"""

    result = await hass.config_entries.options.async_init(base_config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    schema = result["data_schema"].schema
    assert get_schema_default(schema, CONF_TRACK_NEW) is True
    assert get_schema_default(schema, CONF_TODO_LIST) == ["ToDo List 1", "ToDo List 2"]

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_TRACK_NEW: False,
            CONF_MAX_TODOS: UPDATE_MAX_TODOS,
            CONF_TODO_LIST: UPDATE_TODO_LIST,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "todo_config"
    assert result["last_step"] is True
    schema = result["data_schema"].schema
    assert get_schema_default(schema, CONF_DUE_HOURS_FORWARD_TO_GET) is None
    assert get_schema_default(schema, CONF_DUE_HOURS_BACKWARD_TO_GET) is None
    assert not get_schema_default(schema, CONF_SHOW_COMPLETED)

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_DUE_HOURS_FORWARD_TO_GET: 48,
            CONF_DUE_HOURS_BACKWARD_TO_GET: -48,
            CONF_SHOW_COMPLETED: True,
        },
    )
    assert result.get("type") is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_TRACK_NEW] is False
    assert result["data"][CONF_MAX_TODOS] == UPDATE_MAX_TODOS
    assert result["data"][CONF_TODO_LIST] == UPDATE_TODO_LIST
    check_yaml_file_contents(tmp_path, "ms365_todo_updated")


async def test_correct_file_update(
    tmp_path,
    hass: HomeAssistant,
    requests_mock: Mocker,
    base_token,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test for correct file update."""
    MS365MOCKS.standard_mocks(requests_mock)
    yaml_setup(tmp_path, "ms365_todo_updated")

    base_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(base_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(base_config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_TRACK_NEW: False,
            CONF_TODO_LIST: UPDATE_TODO_LIST,
        },
    )

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_SHOW_COMPLETED: True,
        },
    )

    check_yaml_file_contents(tmp_path, "ms365_todo_updated2")
