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
        "due": datetime.datetime(
            2021, 12, 31, 0, 0, tzinfo=zoneinfo.ZoneInfo(key="UTC")
        ),
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
        "due": datetime.datetime(
            2021, 12, 31, 0, 0, tzinfo=zoneinfo.ZoneInfo(key="UTC")
        ),
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
        "due": datetime.datetime(
            2021, 12, 30, 22, 0, tzinfo=zoneinfo.ZoneInfo(key="UTC")
        ),
    },
    {
        "subject": "Task 2",
        "todo_id": "list2task2",
        "status": "notStarted",
        "description": "Task 2 body",
        "due": datetime.datetime(
            2021, 12, 31, 12, 0, tzinfo=zoneinfo.ZoneInfo(key="UTC")
        ),
    },
]
OVERDUE_TODO_LIST_2 = [
    {
        "subject": "Task 1",
        "todo_id": "list2task1",
        "due": datetime.datetime(
            2021, 12, 30, 22, 0, tzinfo=zoneinfo.ZoneInfo(key="UTC")
        ),
    },
    {
        "subject": "Task 2",
        "todo_id": "list2task2",
        "due": datetime.datetime(
            2021, 12, 31, 12, 0, tzinfo=zoneinfo.ZoneInfo(key="UTC")
        ),
    },
]

TODO_LIST_1_COMPLETED = [
    {
        "subject": "Task 1",
        "todo_id": "list1task1",
        "status": "notStarted",
        "description": "Task 1 body",
        "completed": False,
        "due": datetime.datetime(
            2021, 12, 31, 0, 0, tzinfo=zoneinfo.ZoneInfo(key="UTC")
        ),
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
        "due": "2021-12-30T22:00:00+00:00",
        "description": "Task 1 body",
    },
    {
        "summary": "Task 2",
        "uid": "list2task2",
        "status": "needs_action",
        "due": "2021-12-31T12:00:00+00:00",
        "description": "Task 2 body",
    },
]

TODO_UPDATE_ARGS = "call(Task: (o) Task 1 (due: 2099-01-01 at 00:00:00)  , 'Task 1', 'Task 1 body', datetime.datetime(2023, 11, 17, 5, 30, tzinfo=zoneinfo.ZoneInfo(key='US/Pacific')), datetime.datetime(2023, 11, 17, 5, 30, tzinfo=zoneinfo.ZoneInfo(key='US/Pacific')), True)"
