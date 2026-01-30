"""Mock setup."""

from ...helpers.utils import mock_call
from ..const_integration import CN21VURL, URL


class MS365Mocks:
    """Standard mocks."""

    def cn21v_mocks(self, requests_mock):
        """Setup the standard mocks."""
        mock_call(requests_mock, CN21VURL.DISCOVERY, "discovery")
        mock_call(requests_mock, CN21VURL.OPENID, "openid")
        mock_call(requests_mock, CN21VURL.ME, "me")
        mock_call(requests_mock, CN21VURL.TODO_LISTS_DELTA, "todo_lists")
        mock_call(requests_mock, CN21VURL.TODO_LIST_1, "todo_list_1")
        mock_call(requests_mock, CN21VURL.TODO_LIST_2, "todo_list_2")
        mock_call(requests_mock, CN21VURL.TODO_LIST_1_TASKS, "todo_list_1_tasks")
        mock_call(requests_mock, CN21VURL.TODO_LIST_2_TASKS, "todo_list_2_tasks")

    def standard_mocks(self, requests_mock):
        """Setup the standard mocks."""
        mock_call(requests_mock, URL.OPENID, "openid")
        mock_call(requests_mock, URL.ME, "me")
        mock_call(requests_mock, URL.TODO_LISTS_DELTA, "todo_lists")
        mock_call(requests_mock, URL.TODO_LIST_1, "todo_list_1")
        mock_call(requests_mock, URL.TODO_LIST_2, "todo_list_2")
        mock_call(requests_mock, URL.TODO_LIST_1_TASKS, "todo_list_1_tasks")
        mock_call(requests_mock, URL.TODO_LIST_2_TASKS, "todo_list_2_tasks")


MS365MOCKS = MS365Mocks()
