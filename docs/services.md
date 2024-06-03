---
title: Services
nav_order: 15
---

# Services

These MS365 services must be targeted at a `todo` sensor. Alternatively the core To Do services (e.g.`todo.add_item`) can be used. The core services do not support reminder date/time setting. 
The intention is to phase out the MS365 services once the core services provide full functionality.

### ms365.new_todo
Create a new To Do - All parameters are shown in the available parameter list on the Developer Tools/Services tab.
### ms365.update_todo
Update a To Do - All parameters are shown in the available parameter list on the Developer Tools/Services tab.
### ms365.delete_todo
Delete a To Do - All parameters are shown in the available parameter list on the Developer Tools/Services tab.
### ms365.complete_todo
(Un)complete a To Do - All parameters are shown in the available parameter list on the Developer Tools/Services tab.
### ms365.scan_for_todo_lists
Scan for new for To Do lists and add to ms365_todos.yaml - No parameters.

#### Example create To Do service call

```yaml
service: ms365.new_todo
target:
  entity_id: todo.hass_primary
data:
  subject: Pick up the mail
  description: Walk to the post box and collect the mail
  due: "2023-01-01"     # Note that due only takes a date, not a datetime
  reminder: 2023-01-01T12:00:00+0000
```


