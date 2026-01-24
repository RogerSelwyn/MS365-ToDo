---
title: Services
nav_order: 15
---

# Services

These MS365 services must be targeted at a `todo` sensor. Alternatively the core To Do services (e.g.`todo.add_item`) can be used. The core services do not support reminder date/time setting. 
The intention is to phase out the MS365 services once the core services provide full functionality.

### ms365_todo.new_todo
Create a new To Do task - All parameters are shown in the available parameter list on the Developer Tools/Services tab.
### ms365_todo.update_todo
Update a To Do task - All parameters are shown in the available parameter list on the Developer Tools/Services tab.
### ms365_todo.delete_todo
Delete a To Do task - All parameters are shown in the available parameter list on the Developer Tools/Services tab.
### ms365_todo.complete_todo
(Un)complete a To Do task - All parameters are shown in the available parameter list on the Developer Tools/Services tab.
### ms365_todo.new_todo_checklist_item
Create a new Checklist Item for an existing To Do task - All parameters are shown in the available parameter list on the Developer Tools/Services tab.
### ms365_todo.update_todo_checklist_item
Update a To Do Checklist Item to mark complete/incomplete - All parameters are shown in the available parameter list on the Developer Tools/Services tab.
### ms365_tododelete_todo_checklist_item
Delete a To Do Checklist Item - All parameters are shown in the available parameter list on the Developer Tools/Services tab.
### ms365_todo.scan_for_todo_lists
Scan for new for To Do lists and add to ms365_todos.yaml - No parameters.

#### Example create To Do service call

```yaml
service: ms365_todo.new_todo
target:
  entity_id: todo.hass_primary
data:
  subject: Pick up the mail
  description: Walk to the post box and collect the mail
  due: "2023-01-01"     # Note that due only takes a date, not a datetime
  reminder: 2023-01-01T12:00:00+0000
```

#### Example create To Do Check List Item service call

```yaml
service: ms365_todo.new_todo
target:
  entity_id: todo.hass_primary
data:
  subject: Pick up the mail
  description: Walk to the post box and collect the mail
  due: "2023-01-01"     # Note that due only takes a date, not a datetime
  reminder: 2023-01-01T12:00:00+0000
action: ms365_todo.new_todo_checklist_item
target:
  entity_id: todo.new_hass
data:
  todo_id: >-
    todo_guid
  name: Go to post office
```

Response - Note item id is shown as an attribute of the entity_id since multiple entities can potentially be actioned at the same time.

```yaml
todo.hass_primary:
  checklist_item_id: checklist_item_guid
```
