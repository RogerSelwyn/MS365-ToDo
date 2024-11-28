# pylint: disable=line-too-long
"""Tests for MS365 ToDo."""

import datetime

import zoneinfo

BASE_TODO_LIST_1 = [
    {
        "subject": "Task 1",
        "todo_id": "list1task1",
        "status": "notStarted",
        "description": "Task 1 body",
        "due": datetime.date(2021, 12, 31),
        "reminder": datetime.datetime(
            2021, 12, 31, 16, 0, tzinfo=zoneinfo.ZoneInfo(key="UTC")
        ),
    },
    {
        "subject": "Task 2",
        "todo_id": "list1task2",
        "status": "notStarted",
        "description": "Task 2 body",
    },
]
OVERDUE_TODO_LIST_1 = [
    {
        "subject": "Task 1",
        "todo_id": "list1task1",
        "due": datetime.date(2021, 12, 31),
        "reminder": datetime.datetime(
            2021, 12, 31, 16, 0, tzinfo=zoneinfo.ZoneInfo(key="UTC")
        ),
    }
]
BASE_TODO_LIST_2 = [
    {
        "subject": "Task 1",
        "todo_id": "list2task1",
        "status": "notStarted",
        "description": "Task 1 body",
        "due": datetime.date(2021, 12, 31),
    },
    {
        "subject": "Task 2",
        "todo_id": "list2task2",
        "status": "notStarted",
        "description": "Task 2 body",
        "due": datetime.date(2021, 12, 31),
    },
]
OVERDUE_TODO_LIST_2 = [
    {"subject": "Task 1", "todo_id": "list2task1", "due": datetime.date(2021, 12, 31)},
    {"subject": "Task 2", "todo_id": "list2task2", "due": datetime.date(2021, 12, 31)},
]

TODO_LIST_1_COMPLETED = [
    {
        "subject": "Task 1",
        "todo_id": "list1task1",
        "status": "notStarted",
        "description": "Task 1 body",
        "completed": False,
        "due": datetime.date(2021, 12, 31),
        "reminder": datetime.datetime(
            2021, 12, 31, 16, 0, tzinfo=zoneinfo.ZoneInfo(key="UTC")
        ),
    },
    {
        "subject": "Task 2",
        "todo_id": "list1task2",
        "status": "completed",
        "description": "Task 2 body",
        "completed": "2050-12-01T00:00:00+0000",
    },
]

BASE_TODO_1 = {"all_todos": BASE_TODO_LIST_1, "overdue_todos": OVERDUE_TODO_LIST_1}
BASE_TODO_2 = {"all_todos": BASE_TODO_LIST_2, "overdue_todos": OVERDUE_TODO_LIST_2}
TODO_COMPLETED = {"all_todos": TODO_LIST_1_COMPLETED}

TODO_GET_ITEMS = [
    {
        "summary": "Task 1",
        "uid": "list2task1",
        "status": "needs_action",
        "due": "2021-12-31",
        "description": "Task 1 body",
    },
    {
        "summary": "Task 2",
        "uid": "list2task2",
        "status": "needs_action",
        "due": "2021-12-31",
        "description": "Task 2 body",
    },
]
