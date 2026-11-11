---
title: To Do Lists
nav_order: 9
---

# To Do Lists

One To Do task list entity is created for each to-do list on the user account. Each sensor shows the number of incomplete To Do task items as the status of the sensor. The `all_todos` attribute is an array of incomplete To Do tasks. The `overdue_todos` attribute shows any To Do tasks which have a due date and are overdue as an array.

Each task in `all_todos` and `overdue_todos` includes the `importance` value returned by Microsoft Graph: `low`, `normal`, or `high`. Microsoft To Do displays `high` as an Important star. Set any of the three values with the optional `importance` field on `ms365_todo.update_todo`; omitting the field preserves the current value. Checklist items (subtasks) do not have a separate importance value.

For example, select the important tasks with:

```jinja
{% raw %}{{ state_attr('todo.todos_sc_personal', 'all_todos')
   | selectattr('importance', 'eq', 'high') | list }}{% endraw %}
```

### Display
In order to show the To Do tasks in the front end either use the HA inbuilt "to-do list" panel or a markdown card can be used. The following is an example that allows you to display a bulleted list subject from the `all_todos` array of To Do tasks.

```yaml
type: markdown
title: Todos
content: |-
  {% raw %}{% for todo in state_attr('todo.todos_sc_personal', 'all_todos') -%}
  - {{ todo['subject'] }}
  {% endfor %}{% endraw %}
```
