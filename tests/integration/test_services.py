# pylint: disable=unused-argument,line-too-long,wrong-import-order
"""Test service usage."""

from unittest.mock import patch

import probatio
import pytest
from requests.exceptions import HTTPError
from requests_mock import Mocker

from custom_components.ms365_todo.const import CONF_ENABLE_UPDATE
from homeassistant.components.todo import DOMAIN as TODO_DOMAIN, TodoServices
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError

from ..conftest import MS365MockConfigEntry
from ..helpers.utils import mock_call
from .const_integration import DOMAIN, URL
from .data_integration.state import TODO_GET_ITEMS, TODO_REMOVE_DUE_ARGS, TODO_UPDATE_ARGS
from .fixtures import ListenerSetupData


async def test_update_service_setup(
    hass: HomeAssistant,
    setup_update_integration,
    base_config_entry: MS365MockConfigEntry,
) -> None:
    """Test the reconfigure flow."""
    assert base_config_entry.data[CONF_ENABLE_UPDATE]
    assert hass.services.has_service(TODO_DOMAIN, TodoServices.ADD_ITEM)
    assert hass.services.has_service(TODO_DOMAIN, TodoServices.GET_ITEMS)
    assert hass.services.has_service(TODO_DOMAIN, TodoServices.REMOVE_COMPLETED_ITEMS)
    assert hass.services.has_service(TODO_DOMAIN, TodoServices.REMOVE_ITEM)
    assert hass.services.has_service(TODO_DOMAIN, TodoServices.UPDATE_ITEM)
    assert hass.services.has_service(DOMAIN, "complete_todo")
    assert hass.services.has_service(DOMAIN, "delete_todo")
    assert hass.services.has_service(DOMAIN, "new_todo")
    assert hass.services.has_service(DOMAIN, "update_todo")
    assert hass.services.has_service(DOMAIN, "new_todo_checklist_item")
    assert hass.services.has_service(DOMAIN, "update_todo_checklist_item")
    assert hass.services.has_service(DOMAIN, "delete_todo_checklist_item")


async def test_todo_services_ha(
    hass: HomeAssistant,
    setup_update_integration,
    listener_setup: ListenerSetupData,
    requests_mock: Mocker,
) -> None:
    """Test HA Services."""

    list_name = "todo.test_todo_list_2"
    mock_call(requests_mock, URL.TODO_SAVE, "todo_save", method="post")
    mock_call(requests_mock, URL.TODO_GET_1, "todo_get_1")
    mock_call(requests_mock, URL.TODO_GET_2, "todo_get_2")
    result = await hass.services.async_call(
        TODO_DOMAIN,
        TodoServices.GET_ITEMS,
        {
            "entity_id": list_name,
            "status": ["needs_action"],
        },
        blocking=True,
        return_response=True,
    )

    assert list_name in result
    assert "items" in result[list_name]
    assert result[list_name]["items"] == TODO_GET_ITEMS

    list_name = "todo.test_todo_list_1"
    await hass.services.async_call(
        TODO_DOMAIN,
        TodoServices.ADD_ITEM,
        {
            "entity_id": list_name,
            "item": "Test item",
            "due_date": "2023-11-17",
            "description": "Test description",
        },
        blocking=True,
        return_response=False,
    )
    await hass.async_block_till_done()
    listener = 1
    assert len(listener_setup.events) == listener
    assert [x for x in listener_setup.events if x.event_type == f"{DOMAIN}_new_todo"]

    list_name = "todo.test_todo_list_1"
    await hass.services.async_call(
        TODO_DOMAIN,
        TodoServices.ADD_ITEM,
        {
            "entity_id": list_name,
            "item": "Test item",
            "due_datetime": "2023-11-17T13:30:00.000Z",
            "description": "Test description",
        },
        blocking=True,
        return_response=False,
    )
    await hass.async_block_till_done()
    listener += 1
    assert len(listener_setup.events) == listener
    assert [x for x in listener_setup.events if x.event_type == f"{DOMAIN}_new_todo"]

    with patch("O365.tasks.Task.save") as mock_save:
        await hass.services.async_call(
            TODO_DOMAIN,
            TodoServices.UPDATE_ITEM,
            {
                "entity_id": list_name,
                "item": "Task 1",
                "due_date": "2099-01-01",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_save.called
    listener += 1
    assert len(listener_setup.events) == listener
    assert [x for x in listener_setup.events if x.event_type == f"{DOMAIN}_update_todo"]

    with patch("custom_components.ms365_todo.integration.todo_integration.MS365TodoList._async_save_todo") as mock_save:
        await hass.services.async_call(
            TODO_DOMAIN,
            TodoServices.UPDATE_ITEM,
            {
                "entity_id": list_name,
                "item": "Task 1",
                "due_datetime": "2023-11-17T13:30:00.000Z",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_save.called
    listener += 1
    assert len(listener_setup.events) == listener
    assert [x for x in listener_setup.events if x.event_type == f"{DOMAIN}_update_todo"]
    assert str(mock_save.call_args) == TODO_UPDATE_ARGS

    with patch("custom_components.ms365_todo.integration.todo_integration.MS365TodoList._async_save_todo") as mock_save:
        await hass.services.async_call(
            TODO_DOMAIN,
            TodoServices.UPDATE_ITEM,
            {
                "entity_id": list_name,
                "item": "Task 1",
                "due_datetime": None,
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_save.called
    listener += 1
    assert len(listener_setup.events) == listener
    assert [x for x in listener_setup.events if x.event_type == f"{DOMAIN}_update_todo"]
    assert str(mock_save.call_args) == TODO_REMOVE_DUE_ARGS

    with patch("O365.tasks.Task.save") as mock_save:
        await hass.services.async_call(
            TODO_DOMAIN,
            TodoServices.UPDATE_ITEM,
            {
                "entity_id": list_name,
                "item": "Task 1",
                "due_datetime": None,
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_save.called
    listener += 1
    assert len(listener_setup.events) == listener
    assert [x for x in listener_setup.events if x.event_type == f"{DOMAIN}_update_todo"]

    with patch("O365.tasks.Task.save") as mock_save:
        await hass.services.async_call(
            TODO_DOMAIN,
            TodoServices.UPDATE_ITEM,
            {
                "entity_id": list_name,
                "item": "Task 1",
                "status": "completed",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_save.called
    listener += 1
    assert len(listener_setup.events) == listener
    assert [x for x in listener_setup.events if x.event_type == f"{DOMAIN}_completed_todo"]

    mock_call(requests_mock, URL.TODO_LIST_1_TASKS, "todo_list_1_tasks_completed2")
    with patch("O365.tasks.Task.save") as mock_save:
        await hass.services.async_call(
            TODO_DOMAIN,
            TodoServices.UPDATE_ITEM,
            {
                "entity_id": list_name,
                "item": "Task 2",
                "status": "needs_action",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_save.called
    assert len(listener_setup.events) == listener

    with patch("O365.tasks.Task.delete") as mock_delete:
        await hass.services.async_call(
            TODO_DOMAIN,
            TodoServices.REMOVE_ITEM,
            {
                "entity_id": list_name,
                "item": "Task 2",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_delete.called
    listener += 1
    assert len(listener_setup.events) == listener
    assert [x for x in listener_setup.events if x.event_type == f"{DOMAIN}_delete_todo"]


async def test_todo_services_ms365(
    hass: HomeAssistant,
    setup_update_integration,
    listener_setup: ListenerSetupData,
    requests_mock: Mocker,
) -> None:
    """Test HA Services."""
    list_name = "todo.test_todo_list_1"
    mock_call(requests_mock, URL.TODO_SAVE, "todo_save", method="post")
    mock_call(requests_mock, URL.TODO_GET_1, "todo_get_1")
    mock_call(requests_mock, URL.TODO_GET_2, "todo_get_2")
    await hass.services.async_call(
        DOMAIN,
        "new_todo",
        {
            "entity_id": list_name,
            "subject": "Test item",
            "due": "2023-11-17",
            "description": "Test description",
        },
        blocking=True,
        return_response=False,
    )
    await hass.async_block_till_done()
    listener = 1
    assert len(listener_setup.events) == listener
    assert [x for x in listener_setup.events if x.event_type == f"{DOMAIN}_new_todo"]

    with patch("O365.tasks.Task.save") as mock_save:
        await hass.services.async_call(
            DOMAIN,
            "update_todo",
            {
                "entity_id": list_name,
                "todo_id": "list1task1",
                "due": "2099-01-01",
                "reminder": "2025-01-01T12:00:00",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_save.called
    listener += 1
    assert len(listener_setup.events) == listener
    assert [x for x in listener_setup.events if x.event_type == f"{DOMAIN}_update_todo"]

    with patch("O365.tasks.Task.save") as mock_save:
        await hass.services.async_call(
            DOMAIN,
            "complete_todo",
            {
                "entity_id": list_name,
                "todo_id": "list1task1",
                "completed": True,
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_save.called
    listener += 1
    assert len(listener_setup.events) == listener
    assert [x for x in listener_setup.events if x.event_type == f"{DOMAIN}_completed_todo"]

    mock_call(requests_mock, URL.TODO_LIST_1_TASKS, "todo_list_1_tasks_completed2")
    with patch("O365.tasks.Task.save") as mock_save:
        await hass.services.async_call(
            DOMAIN,
            "complete_todo",
            {
                "entity_id": list_name,
                "todo_id": "list1task2",
                "completed": False,
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_save.called
    assert len(listener_setup.events) == listener

    with patch("O365.tasks.Task.delete") as mock_delete:
        await hass.services.async_call(
            DOMAIN,
            "delete_todo",
            {
                "entity_id": list_name,
                "todo_id": "list1task2",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_delete.called
    listener += 1
    assert len(listener_setup.events) == listener
    assert [x for x in listener_setup.events if x.event_type == f"{DOMAIN}_delete_todo"]

    requests_mock.get(URL.TODO_GET_1.value, status_code=404, json={"error": {"code": "Client Error"}})
    with pytest.raises(ServiceValidationError) as exc_info:
        await hass.services.async_call(
            DOMAIN,
            "delete_todo",
            {
                "entity_id": list_name,
                "todo_id": "list1task1",
            },
            blocking=True,
            return_response=False,
        )

    await hass.async_block_till_done()
    assert "To Do was not found" in str(exc_info.value)


async def test_todo_checklist_item_services_ms365(
    hass: HomeAssistant,
    setup_update_integration,
    listener_setup: ListenerSetupData,
    requests_mock: Mocker,
) -> None:
    """Test HA Services."""
    list_name = "todo.test_todo_list_1"
    mock_call(requests_mock, URL.TODO_GET_1, "todo_get_1")
    mock_call(requests_mock, URL.TODO_GET_CHECKLIST_ITEM_1, "todo_get_checklist_item_1")

    with patch("O365.tasks.ChecklistItem.save") as mock_save:
        await hass.services.async_call(
            DOMAIN,
            "new_todo_checklist_item",
            {
                "entity_id": list_name,
                "todo_id": "list1task1",
                "name": "Test step",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_save.called

    with patch("O365.tasks.ChecklistItem.save") as mock_save:
        await hass.services.async_call(
            DOMAIN,
            "update_todo_checklist_item",
            {
                "entity_id": list_name,
                "todo_id": "list1task1",
                "checklist_item_id": "list1task1step1",
                "status": "completed",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_save.called

    with patch("O365.tasks.ChecklistItem.save") as mock_save:
        await hass.services.async_call(
            DOMAIN,
            "update_todo_checklist_item",
            {
                "entity_id": list_name,
                "todo_id": "list1task1",
                "checklist_item_id": "list1task1step1",
                "status": "needs_action",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_save.called

    with patch("O365.tasks.ChecklistItem.delete") as mock_delete:
        await hass.services.async_call(
            DOMAIN,
            "delete_todo_checklist_item",
            {
                "entity_id": list_name,
                "todo_id": "list1task1",
                "checklist_item_id": "list1task1step1",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_delete.called


@pytest.mark.parametrize("is_checked", [False, True])
@pytest.mark.parametrize(
    ("changes", "payload"),
    [
        ({"name": "Renamed step"}, {"displayName": "Renamed step"}),
        (
            {"name": "Renamed step", "status": "completed"},
            {"displayName": "Renamed step", "isChecked": True},
        ),
        (
            {"name": "Renamed step", "status": "needs_action"},
            {"displayName": "Renamed step", "isChecked": False},
        ),
        ({"status": "completed"}, {"isChecked": True}),
        ({"status": "needs_action"}, {"isChecked": False}),
    ],
)
async def test_update_checklist_item_payload(
    hass: HomeAssistant,
    setup_update_integration,
    requests_mock: Mocker,
    changes,
    payload,
    is_checked,
) -> None:
    """Persist only requested checklist changes through Microsoft Graph."""
    mock_call(requests_mock, URL.TODO_GET_1, "todo_get_1")
    item = {
        "id": "list1task1step1",
        "displayName": "Original step",
        "isChecked": is_checked,
    }
    requests_mock.get(URL.TODO_GET_CHECKLIST_ITEM_1.value, json=item)
    update = requests_mock.patch(
        URL.TODO_GET_CHECKLIST_ITEM_1.value, json={**item, **payload}
    )

    with patch(
        "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh"
    ) as mock_refresh:
        await hass.services.async_call(
            DOMAIN,
            "update_todo_checklist_item",
            {
                "entity_id": "todo.test_todo_list_1",
                "todo_id": "list1task1",
                "checklist_item_id": "list1task1step1",
                **changes,
            },
            blocking=True,
        )

    assert update.call_count == 1
    assert update.last_request.json() == payload
    mock_refresh.assert_awaited_once()


@pytest.mark.parametrize(
    "changes", [{}, {"name": ""}, {"name": None}, {"status": "invalid"}]
)
async def test_update_checklist_item_invalid_changes(
    hass: HomeAssistant, setup_update_integration, changes
) -> None:
    """Reject missing changes, empty names, and invalid completion states."""
    with pytest.raises(probatio.Invalid):
        await hass.services.async_call(
            DOMAIN,
            "update_todo_checklist_item",
            {
                "entity_id": "todo.test_todo_list_1",
                "todo_id": "list1task1",
                "checklist_item_id": "list1task1step1",
                **changes,
            },
            blocking=True,
        )


@pytest.mark.parametrize("changes", [{"name": "Renamed step"}, {"status": "completed"}])
async def test_update_checklist_item_failed_save(
    hass: HomeAssistant,
    setup_update_integration,
    requests_mock: Mocker,
    changes,
) -> None:
    """Report a failed Graph update without refreshing as if it succeeded."""
    mock_call(requests_mock, URL.TODO_GET_1, "todo_get_1")
    mock_call(requests_mock, URL.TODO_GET_CHECKLIST_ITEM_1, "todo_get_checklist_item_1")
    with (
        patch("O365.connection.Connection.patch", return_value=False),
        patch(
            "homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh"
        ) as mock_refresh,
        pytest.raises(ServiceValidationError, match="could not be updated"),
    ):
        await hass.services.async_call(
            DOMAIN,
            "update_todo_checklist_item",
            {
                "entity_id": "todo.test_todo_list_1",
                "todo_id": "list1task1",
                "checklist_item_id": "list1task1step1",
                **changes,
            },
            blocking=True,
        )
    mock_refresh.assert_not_awaited()


async def test_failed_permission(
    hass: HomeAssistant,
    setup_update_integration,
    requests_mock: Mocker,
) -> None:
    """Test notify - HA Service."""
    list_name = "todo.test_todo_list_1"
    failed_perm = "todo.failed_perm"
    mock_call(requests_mock, URL.TODO_GET_1, "todo_get_1")
    mock_call(requests_mock, URL.TODO_GET_2, "todo_get_2")
    with (
        patch(
            f"custom_components.{DOMAIN}.integration.todo_integration.PERM_TASKS_READWRITE",
            failed_perm,
        ),
        pytest.raises(ServiceValidationError) as exc_info,
    ):
        await hass.services.async_call(
            TODO_DOMAIN,
            TodoServices.ADD_ITEM,
            {
                "entity_id": list_name,
                "item": "Test item",
                "due_date": "2023-11-17",
                "description": "Test description",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert f"Not authorised to edit To Dos - requires permission: {failed_perm}" in str(exc_info.value)

    with (
        patch(
            f"custom_components.{DOMAIN}.integration.todo_integration.PERM_TASKS_READWRITE",
            failed_perm,
        ),
        pytest.raises(ServiceValidationError) as exc_info,
    ):
        await hass.services.async_call(
            TODO_DOMAIN,
            TodoServices.UPDATE_ITEM,
            {
                "entity_id": list_name,
                "item": "Task 1",
                "due_date": "2099-01-01",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert f"Not authorised to edit To Dos - requires permission: {failed_perm}" in str(exc_info.value)

    with (
        patch(
            f"custom_components.{DOMAIN}.integration.todo_integration.PERM_TASKS_READWRITE",
            failed_perm,
        ),
        pytest.raises(ServiceValidationError) as exc_info,
    ):
        await hass.services.async_call(
            TODO_DOMAIN,
            TodoServices.UPDATE_ITEM,
            {
                "entity_id": list_name,
                "item": "Task 1",
                "status": "completed",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert f"Not authorised to edit To Dos - requires permission: {failed_perm}" in str(exc_info.value)

    with (
        patch(
            f"custom_components.{DOMAIN}.integration.todo_integration.PERM_TASKS_READWRITE",
            failed_perm,
        ),
        pytest.raises(ServiceValidationError) as exc_info,
    ):
        await hass.services.async_call(
            TODO_DOMAIN,
            TodoServices.REMOVE_ITEM,
            {
                "entity_id": list_name,
                "item": "Task 2",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert f"Not authorised to edit To Dos - requires permission: {failed_perm}" in str(exc_info.value)


async def test_todo_services_ms365_errors(
    hass: HomeAssistant,
    setup_update_integration,
    listener_setup: ListenerSetupData,
    requests_mock: Mocker,
) -> None:
    """Test HA Services."""
    list_name = "todo.test_todo_list_1"
    mock_call(requests_mock, URL.TODO_GET_1, "todo_get_1")
    mock_call(requests_mock, URL.TODO_GET_2, "todo_get_2")
    with pytest.raises(ServiceValidationError) as exc_info:
        await hass.services.async_call(
            DOMAIN,
            "complete_todo",
            {
                "entity_id": list_name,
                "todo_id": "list1task2",
                "completed": True,
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert "To Do is already complete" in str(exc_info.value)

    with pytest.raises(ServiceValidationError) as exc_info:
        await hass.services.async_call(
            DOMAIN,
            "complete_todo",
            {
                "entity_id": list_name,
                "todo_id": "list1task1",
                "completed": False,
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert "To Do is already incomplete" in str(exc_info.value)

    with (
        pytest.raises(ServiceValidationError) as exc_info,
        patch(
            "O365.tasks.Folder.get_task",
            side_effect=HTTPError(),
        ),
    ):
        await hass.services.async_call(
            DOMAIN,
            "update_todo_checklist_item",
            {
                "entity_id": list_name,
                "todo_id": "list1task1",
                "checklist_item_id": "list1task1step1",
                "status": "needs_action",
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert "To Do has not been retrieved successfully, Action unsuccessful" in str(exc_info.value)


async def test_remove_items_already_deleted(
    hass: HomeAssistant,
    setup_update_integration,
    listener_setup: ListenerSetupData,
    requests_mock: Mocker,
) -> None:
    """Test removing multiple items where one has already been deleted."""
    list_name = "todo.test_todo_list_1"
    requests_mock.get(URL.TODO_GET_1.value, status_code=404, json={"error": {"code": "Client Error"}})
    mock_call(requests_mock, URL.TODO_GET_2, "todo_get_2")

    with (
        patch("O365.tasks.Task.delete") as mock_delete,
        patch("homeassistant.helpers.update_coordinator.DataUpdateCoordinator.async_refresh") as mock_refresh,
    ):
        await hass.services.async_call(
            TODO_DOMAIN,
            TodoServices.REMOVE_ITEM,
            {
                "entity_id": list_name,
                "item": ["list1task1", "list1task2"],
            },
            blocking=True,
            return_response=False,
        )
    await hass.async_block_till_done()
    assert mock_delete.call_count == 1
    assert mock_refresh.call_count == 1
    assert len([x for x in listener_setup.events if x.event_type == f"{DOMAIN}_delete_todo"]) == 1

    requests_mock.get(URL.TODO_GET_1.value, status_code=403, json={"error": {"code": "AccessDenied"}})
    with pytest.raises(HTTPError):
        await hass.services.async_call(
            TODO_DOMAIN,
            TodoServices.REMOVE_ITEM,
            {
                "entity_id": list_name,
                "item": ["list1task1"],
            },
            blocking=True,
            return_response=False,
        )


async def test_remove_items_delete_not_found(
    hass: HomeAssistant,
    setup_update_integration,
    listener_setup: ListenerSetupData,
    requests_mock: Mocker,
) -> None:
    """Test removing multiple items where the delete of one returns not found."""
    list_name = "todo.test_todo_list_1"
    mock_call(requests_mock, URL.TODO_GET_1, "todo_get_1")
    mock_call(requests_mock, URL.TODO_GET_2, "todo_get_2")
    requests_mock.delete(URL.TODO_GET_1.value, status_code=404, json={"error": {"code": "Client Error"}})
    requests_mock.delete(URL.TODO_GET_2.value, status_code=204)

    await hass.services.async_call(
        TODO_DOMAIN,
        TodoServices.REMOVE_ITEM,
        {
            "entity_id": list_name,
            "item": ["list1task1", "list1task2"],
        },
        blocking=True,
        return_response=False,
    )
    await hass.async_block_till_done()
    assert [x.url for x in requests_mock.request_history if x.method == "DELETE"] == [
        URL.TODO_GET_1.value,
        URL.TODO_GET_2.value,
    ]
    assert len([x for x in listener_setup.events if x.event_type == f"{DOMAIN}_delete_todo"]) == 1


async def test_remove_single_item_delete_not_found(
    hass: HomeAssistant,
    setup_update_integration,
    listener_setup: ListenerSetupData,
    requests_mock: Mocker,
) -> None:
    """Test removing sinngle where the delete returns not found."""
    list_name = "todo.test_todo_list_1"
    mock_call(requests_mock, URL.TODO_GET_1, "todo_get_1")
    requests_mock.delete(URL.TODO_GET_1.value, status_code=404, json={"error": {"code": "Client Error"}})

    with pytest.raises(ServiceValidationError) as exc_info:
        await hass.services.async_call(
            DOMAIN,
            "delete_todo",
            {
                "entity_id": list_name,
                "todo_id": "list1task1",
            },
            blocking=True,
            return_response=False,
        )

    await hass.async_block_till_done()
    assert "To Do was not found when deleting" in str(exc_info.value)
