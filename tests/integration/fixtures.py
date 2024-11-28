# pylint: disable=redefined-outer-name, unused-argument
"""Fixtures specific to the integration."""

from dataclasses import dataclass
from unittest.mock import Mock, patch

import pytest
from aiohttp.test_utils import TestClient
from homeassistant.core import Event, HomeAssistant
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.ms365_todo.integration import filemgmt_integration

from ..const import STORAGE_LOCATION
from .const_integration import DOMAIN


@pytest.fixture(autouse=True)
def yaml_storage_path_setup(tmp_path):
    """Setup the storage paths."""
    yml_path = tmp_path / STORAGE_LOCATION / f"{DOMAIN}s_test.yaml"

    with patch.object(
        filemgmt_integration,
        "build_config_file_path",
        return_value=yml_path,
    ):
        yield


@dataclass
class ListenerSetupData:
    """A collection of data set up by the listener_setup fixture."""

    hass: HomeAssistant
    client: TestClient
    event_listener: Mock
    events: any


@pytest.fixture
async def listener_setup(
    hass: HomeAssistant,
    hass_client_no_auth: ClientSessionGenerator,
) -> ListenerSetupData:
    """Set up integration, client and webhook url."""

    client = await hass_client_no_auth()

    events = []

    async def event_listener(event: Event) -> None:
        events.append(event)

    hass.bus.async_listen(f"{DOMAIN}_completed_todo", event_listener)
    hass.bus.async_listen(f"{DOMAIN}_delete_todo", event_listener)
    hass.bus.async_listen(f"{DOMAIN}_new_todo", event_listener)
    hass.bus.async_listen(f"{DOMAIN}_uncompleted_todos", event_listener)
    hass.bus.async_listen(f"{DOMAIN}_update_todo", event_listener)

    return ListenerSetupData(hass, client, event_listener, events)
