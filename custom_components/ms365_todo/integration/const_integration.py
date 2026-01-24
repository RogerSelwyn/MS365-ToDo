"""ToDo constants."""

from homeassistant.const import Platform

PLATFORMS: list[Platform] = [Platform.TODO]
DOMAIN = "ms365_todo"

ATTR_ALL_TODOS = "all_todos"
ATTR_CHECKLIST_ITEMS = "checklist_items"
ATTR_CHECKLIST_ITEM_ID = "checklist_item_id"
ATTR_COMPLETED = "completed"
ATTR_CREATED = "created"
ATTR_DESCRIPTION = "description"
ATTR_DUE = "due"
ATTR_ID = "id"
ATTR_IS_CHECKED = "is_checked"
ATTR_NAME = "name"
ATTR_OVERDUE_TODOS = "overdue_todos"
ATTR_PERCENT_COMPLETE = "percent_complete"
ATTR_REMINDER = "reminder"
ATTR_REMOVE_DUE = "remove_due"
ATTR_REMOVE_REMINDER = "remove_reminder"
ATTR_STATUS = "status"
ATTR_SUBJECT = "subject"
ATTR_TITLE = "title"
ATTR_TODOS = "todos"
ATTR_TODO_ID = "todo_id"


CONF_DUE_HOURS_BACKWARD_TO_GET = "due_start_offset"
CONF_DUE_HOURS_FORWARD_TO_GET = "due_end_offset"
CONF_MAX_TODOS = "max_todos"
CONF_MAX_TODOS_DEFAULT = 100
CONF_MS365_TODO_FOLDER = "MS365_todo_folder"
CONF_PLANNER = "MS365_planner"
CONF_SHOW_COMPLETED = "show_completed"
CONF_TODO_LIST = "todo_list"
CONF_TODO_LIST_ID = "todo_list_id"
CONF_TRACK = "track"
CONF_TRACK_NEW = "track_new"

ENTITY_ID_FORMAT_TODO = "todo.{}"

EVENT_COMPLETED_PLANNER_TASK = "completed_planner_task"
EVENT_COMPLETED_TODO = "completed_todo"
EVENT_DELETE_TODO = "delete_todo"
EVENT_NEW_PLANNER_TASK = "new_planner_task"
EVENT_NEW_TODO = "new_todo"
EVENT_UNCOMPLETED_TODO = "uncompleted_todo"
EVENT_UPDATE_TODO = "update_todo"

PERM_TASKS_READ = "Tasks.Read"
PERM_TASKS_READWRITE = "Tasks.ReadWrite"

PLANNER_UNIQUE_ID = "planner"
PLANNER_NAME = "Planner"

TODO_ENTITY_ID_FORMAT = "todo.{}"
TODO_TODO = "todo"
TODO_PLANNER = "planner"

YAML_TODO_LISTS_FILENAME = "ms365_todos{0}.yaml"
