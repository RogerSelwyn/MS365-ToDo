# pylint: disable=unused-argument,line-too-long,wrong-import-order
"""Test main sensors testing."""

from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from requests.exceptions import HTTPError
from requests_mock import Mocker

from custom_components.ms365_todo.integration.const_integration import (
    CONF_DUE_HOURS_BACKWARD_TO_GET,
    CONF_DUE_HOURS_FORWARD_TO_GET,
    CONF_SHOW_COMPLETED,
    CONF_TODO_LIST,
    CONF_TRACK_NEW,
    DOMAIN,
)

from ..helpers.mock_config_entry import MS365MockConfigEntry
from ..helpers.utils import check_entity_state, mock_call
from .const_integration import UPDATE_TODO_LIST, URL
from .data_integration.state import BASE_TODO_1, BASE_TODO_2, TODO_COMPLETED
from .fixtures import ListenerSetupData
from .helpers_integration.mocks import MS365MOCKS
from .helpers_integration.utils_integration import yaml_setup


async def test_get_data(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test get data."""
    entities = er.async_entries_for_config_entry(
        entity_registry, base_config_entry.entry_id
    )
    assert len(entities) == 2
    check_entity_state(
        hass,
        "todo.test_todo_list_1",
        "2",
        attributes=BASE_TODO_1,
    )
    check_entity_state(
        hass,
        "todo.test_todo_list_2",
        "2",
        attributes=BASE_TODO_2,
    )


async def test_show_completed(
    tmp_path,
    hass: HomeAssistant,
    requests_mock: Mocker,
    base_token,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test filtering of events."""
    MS365MOCKS.standard_mocks(requests_mock)
    mock_call(requests_mock, URL.TODO_LIST_1_TASKS, "todo_list_1_tasks_completed")
    yaml_setup(tmp_path, "ms365_todo_completed")

    base_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(base_config_entry.entry_id)
    await hass.async_block_till_done()

    check_entity_state(
        hass,
        "todo.test_todo_list_1",
        "1",
        attributes=TODO_COMPLETED,
    )


async def test_query(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test the options flow"""

    result = await hass.config_entries.options.async_init(base_config_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_TRACK_NEW: False,
            CONF_TODO_LIST: UPDATE_TODO_LIST,
        },
    )

    with patch("O365.tasks.Folder.get_tasks") as mock_get_tasks:
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={
                CONF_DUE_HOURS_FORWARD_TO_GET: 48,
                CONF_DUE_HOURS_BACKWARD_TO_GET: -48,
                CONF_SHOW_COMPLETED: False,
            },
        )
    assert mock_get_tasks.called
    assert "duedatetime/dateTime ge" in str(mock_get_tasks.call_args_list)
    assert "duedatetime/dateTime le" in str(mock_get_tasks.call_args_list)
    assert "status ne 'completed'" in str(mock_get_tasks.call_args_list)


async def test_base_events(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
    listener_setup: ListenerSetupData,
    requests_mock: Mocker,
) -> None:
    """Test events created from new/completed todos externally."""

    coordinator = base_config_entry.runtime_data.coordinator
    mock_call(requests_mock, URL.TODO_LIST_1_TASKS, "todo_list_1_tasks_updated")
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert len(listener_setup.events) == 2
    assert [
        x for x in listener_setup.events if x.event_type == f"{DOMAIN}_completed_todo"
    ]
    assert [x for x in listener_setup.events if x.event_type == f"{DOMAIN}_new_todo"]


async def test_fetch_error(
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test error fetching data."""
    coordinator = base_config_entry.runtime_data.coordinator
    with patch(
        "O365.tasks.Folder.get_tasks",
        side_effect=HTTPError(),
    ):
        await coordinator.async_refresh()
        await hass.async_block_till_done()
    assert (
        "MS365 To Do list not found for: test ToDo List 1 - Has it been deleted?"
        in caplog.text
    )

    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert "MS365 To Do list reconnected for: test ToDo List 1" in caplog.text
