---
title: To Do Configuration
nav_order: 7
---

# To Do configuration
The integration uses an external `ms365_todos_<account_name>.yaml` file which is stored in the `ms365_storage` directory.
## Example To Do tasks YAML:
```yaml

- name: Tasks
  todo_list_id: xxxx
  track: false

- name: HASS
  todo_list_id: xxxx
  track: true
```

### To Do task YAML configuration variables

Key | Type | Required | Description
-- | -- | -- | --
`todo_list_id` | `string` | `True` | Microsoft To Do generated unique ID for the task list, DO NOT CHANGE
`name` | `string` | `True` | The name of your sensor that you’ll see in the frontend.
`track` | `boolean` | `False` | **True**=Create sensor entity. False=Don't create entity.
`show_completed` | `boolean` | `False` | True=Show completed items. **False**=Don't show completed items.
`due_start_offset` | `integer` | `False` | Number of hours to offset the due time for Microsoft To Do to retrieve (negative numbers to offset into the past).
`due_end_offset` | `integer` | `False` | Number of hours to offset the due time for Microsoft To Do to retrieve (negative numbers to offset into the past).
