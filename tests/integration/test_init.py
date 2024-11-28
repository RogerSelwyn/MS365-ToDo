# pylint: disable=line-too-long, unused-argument
"""Test the setup."""

from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from requests.exceptions import HTTPError
from requests_mock import Mocker

from custom_components.ms365_todo.integration.const_integration import (
    CONF_DUE_HOURS_BACKWARD_TO_GET,
    CONF_DUE_HOURS_FORWARD_TO_GET,
    CONF_SHOW_COMPLETED,
    CONF_TODO_LIST,
    CONF_TRACK_NEW,
)

from ..helpers.mock_config_entry import MS365MockConfigEntry
from .const_integration import UPDATE_TODO_LIST
from .helpers_integration.mocks import MS365MOCKS


async def test_reload(
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

    with patch(
        "homeassistant.config_entries.ConfigEntries.async_reload"
    ) as mock_async_reload:
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={
                CONF_DUE_HOURS_FORWARD_TO_GET: 48,
                CONF_DUE_HOURS_BACKWARD_TO_GET: -48,
                CONF_SHOW_COMPLETED: True,
            },
        )
    assert mock_async_reload.called


async def test_httperror(
    hass: HomeAssistant,
    requests_mock: Mocker,
    base_token,
    base_config_entry: MS365MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Fixture for setting up the component."""

    MS365MOCKS.standard_mocks(requests_mock)

    base_config_entry.add_to_hass(hass)
    with patch(
        "O365.tasks_graph.ToDo.get_folder",
        side_effect=HTTPError(),
    ):
        await hass.config_entries.async_setup(base_config_entry.entry_id)
    await hass.async_block_till_done()
    assert (
        "MS365 To Do list not found for: test ToDo List 1 - Please remove from MS365_todo_test.yaml"
        in caplog.text
    )
