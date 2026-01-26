---
title: Events
nav_order: 16
---

# Events

The attribute `ha_event` shows whether the event is triggered by an HA initiated action

##  To Do Events

Events will be raised for the following items.

- ms365_todo_new_todo - New To Do task created either by the MS365 integration or via some external app
- ms365_todo_update_todo - Update of a To Do task via the MS365 integration
- ms365_todo_delete_todo - Deletion of a To Do task via the MS365 integration
- ms365_todo_completed_todo - To Do task marked complete either by the MS365 integration or via some external app (`show_completed` must be enabled for To Do list in `ms365_todos_xxxx.yaml`)
- ms365_todo_uncompleted_todo - To Do task marked incomplete via the MS365 integration

It should be noted that actions occurring external to HA are identified via a 30-second poll, so will very likely be delayed by up to that time. Any new or completed To Do task occurring within 5 minutes before HA restart will very likely have a new event sent after the restart.

The events have the following general structure. A `created` or `completed` attribute will be included where the action happened outside HA:

```yaml
event_type: ms365_todo_new_todo
data:
  todo_id: >-
    AAMkAGQwYzQ5ZjZjLTQyYmItNDJmNy04NDNjLTJjYWY3NzMyMDBGAAAAAAC9VxHxYFTdSrdCHSJkXtJ-BwCoiRErLbiNRJDCFyMjq4khAAbWN3xqAACoiRErLbiNRJDCFyMjq4khAAcZSXKvAAA=
  created: "2023-02-19T15:36:05.436266+00:00"
  ha_event: false
  subject: Go to post office
origin: LOCAL
time_fired: "2023-02-19T15:36:14.679300+00:00"
context:
  id: 01GSN5332Q90ZKVEX0CZQNND73
  parent_id: null
  user_id: null
```

