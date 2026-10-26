# pylint: disable=unused-argument,line-too-long,wrong-import-order
"""Test file management."""

import pytest
from requests_mock import Mocker

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from ..helpers.mock_config_entry import MS365MockConfigEntry
from .const_integration import FULL_INIT_ENTITY_NO
from .helpers_integration.mocks import MS365MOCKS
from .helpers_integration.utils_integration import check_yaml_file_contents, yaml_setup


async def test_base_filemgmt(
    tmp_path,
    hass: HomeAssistant,
    setup_base_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test base file management."""

    check_yaml_file_contents(tmp_path, "ms365_todo_base")


async def test_empty_file(
    tmp_path,
    hass: HomeAssistant,
    requests_mock: Mocker,
    base_token,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test for an empty yaml file."""
    MS365MOCKS.standard_mocks(requests_mock)
    yaml_setup(tmp_path, "ms365_todo_empty")

    base_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(base_config_entry.entry_id)
    await hass.async_block_till_done()

    check_yaml_file_contents(tmp_path, "ms365_todo_base")


async def test_corrupt_file(
    tmp_path,
    hass: HomeAssistant,
    requests_mock: Mocker,
    base_token,
    base_config_entry: MS365MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test for corrupt yaml content (invalid 'todolistids')."""
    MS365MOCKS.standard_mocks(requests_mock)
    yaml_setup(tmp_path, "ms365_todo_corrupt")

    base_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(base_config_entry.entry_id)
    await hass.async_block_till_done()

    assert "Invalid Data - duplicate entries may be created in file" in caplog.text


async def test_corrupt_file2(
    tmp_path,
    hass: HomeAssistant,
    requests_mock: Mocker,
    base_token,
    base_config_entry: MS365MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test for corrupt yaml content (hanging hyphen)."""
    MS365MOCKS.standard_mocks(requests_mock)
    yaml_setup(tmp_path, "ms365_todo_corrupt2")

    base_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(base_config_entry.entry_id)
    await hass.async_block_till_done()

    assert "Invalid Data - duplicate entries may be created in file" in caplog.text

    entities = er.async_entries_for_config_entry(entity_registry, base_config_entry.entry_id)
    assert len(entities) == FULL_INIT_ENTITY_NO


async def test_corrupt_file3(
    tmp_path,
    hass: HomeAssistant,
    requests_mock: Mocker,
    base_token,
    base_config_entry: MS365MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test for corrupt yaml content (empty name)."""
    MS365MOCKS.standard_mocks(requests_mock)
    yaml_setup(tmp_path, "ms365_todo_corrupt3")

    base_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(base_config_entry.entry_id)
    await hass.async_block_till_done()

    assert "Invalid Data - duplicate entries may be created in file" in caplog.text

    entities = er.async_entries_for_config_entry(entity_registry, base_config_entry.entry_id)
    assert len(entities) == FULL_INIT_ENTITY_NO


async def test_deleted_file(
    tmp_path,
    hass: HomeAssistant,
    requests_mock: Mocker,
    base_token,
    base_config_entry: MS365MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test for corrupt yaml content."""
    MS365MOCKS.standard_mocks(requests_mock)
    yaml_setup(tmp_path, "ms365_todo_delete")

    base_config_entry.add_to_hass(hass)

    await hass.config_entries.async_setup(base_config_entry.entry_id)
    await hass.async_block_till_done()

    check_yaml_file_contents(tmp_path, "ms365_todo_base")

    assert "ToDo List deleted from" in caplog.text
