"""Mock setup."""

from ...helpers.utils import mock_call
from ..const_integration import URL


class MS365Mocks:
    """Standard mocks."""

    def standard_mocks(self, requests_mock):
        """Setup the standard mocks."""
        mock_call(requests_mock, URL.OPENID, "openid")
        mock_call(requests_mock, URL.ME, "me")
        mock_call(requests_mock, URL.TODO_LISTS, "todo_lists")
        mock_call(requests_mock, URL.TODO_LIST_1, "todo_list_1")
        mock_call(requests_mock, URL.TODO_LIST_2, "todo_list_2")
        mock_call(requests_mock, URL.TODO_LIST_1_TASKS, "todo_list_1_tasks")
        mock_call(requests_mock, URL.TODO_LIST_2_TASKS, "todo_list_2_tasks")


MS365MOCKS = MS365Mocks()
