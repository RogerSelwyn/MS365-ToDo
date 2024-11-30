# pylint: disable=unused-import
"""Constants for todo integration."""

from copy import deepcopy
from enum import Enum

from custom_components.ms365_todo.const import (  # noqa: F401
    AUTH_CALLBACK_PATH_ALT,
    AUTH_CALLBACK_PATH_DEFAULT,
)
from custom_components.ms365_todo.integration.const_integration import (
    DOMAIN,  # noqa: F401
)

from ..const import CLIENT_ID, CLIENT_SECRET, ENTITY_NAME

BASE_CONFIG_ENTRY = {
    "entity_name": ENTITY_NAME,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "alt_auth_method": False,
    "enable_update": False,
}
BASE_TOKEN_PERMS = "Tasks.Read"
BASE_MISSING_PERMS = BASE_TOKEN_PERMS
UPDATE_TOKEN_PERMS = "Tasks.ReadWrite"
UPDATE_OPTIONS = {"enable_update": True}

ALT_CONFIG_ENTRY = deepcopy(BASE_CONFIG_ENTRY)
ALT_CONFIG_ENTRY["alt_auth_method"] = True

RECONFIGURE_CONFIG_ENTRY = deepcopy(BASE_CONFIG_ENTRY)
del RECONFIGURE_CONFIG_ENTRY["entity_name"]

MIGRATION_CONFIG_ENTRY = {
    "data": BASE_CONFIG_ENTRY,
    "options": {},
    "todos": {
        "todolist1": {
            "name": "ToDo List 1",
            "show_completed": False,
            "track": False,
            "todo_list_id": "todolist1",
        },
    },
}

DIAGNOSTIC_GRANTED_PERMISSIONS = [
    "Tasks.Read",
    "User.Read",
    "profile",
    "openid",
    "email",
]
DIAGNOSTIC_REQUESTED_PERMISSIONS = [
    "offline_access",
    "User.Read",
    "Tasks.Read",
]

FULL_INIT_ENTITY_NO = 2

UPDATE_TODO_LIST = ["ToDo List 1"]


class URL(Enum):
    """List of URLs"""

    ME = "https://graph.microsoft.com/v1.0/me"
    TODO_LISTS = "https://graph.microsoft.com/v1.0/me/todo/lists"
    TODO_LIST_1 = "https://graph.microsoft.com/v1.0/me/todo/lists/todolist1"
    TODO_LIST_2 = "https://graph.microsoft.com/v1.0/me/todo/lists/todolist2"
    TODO_LIST_1_TASKS = "https://graph.microsoft.com/v1.0/me/todo/lists/todolist1/tasks"
    TODO_LIST_2_TASKS = "https://graph.microsoft.com/v1.0/me/todo/lists/todolist2/tasks"
    TODO_SAVE = "https://graph.microsoft.com/v1.0/me/todo/lists/todolist1/tasks"
    TODO_GET_1 = (
        "https://graph.microsoft.com/v1.0/me/todo/lists/todolist1/tasks/list1task1"
    )
    TODO_GET_2 = (
        "https://graph.microsoft.com/v1.0/me/todo/lists/todolist1/tasks/list1task2"
    )
