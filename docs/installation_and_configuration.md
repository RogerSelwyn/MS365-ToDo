---
title: Installation and Configuration
nav_order: 4
---

# Installation and Configuration
This page details the configuration details for this integration. General instructions can be found on the MS365 Home Assistant [Installation and Configuration](https://rogerselwyn.github.io/MS365-HomeAssistant/installation_and_configuration.html) page.

### Configuration variables

Key | Type | Required | Description
-- | -- | -- | --
`account_name` | `string` | `True` | Uniquely identifying name for the account. To Do entity names will be suffixed with this. `todo.todo_account1`. Do not use email address or spaces.
`client_id` | `string` | `True` | Client ID from your Entra ID App Registration.
`client_secret` | `string` | `True` | Client Secret from your Entra ID App Registration.
`alt_auth_method` | `boolean` | `False` | If False (default), authentication is not dependent on internet access to your HA instance. [See Authentication](./authentication.md)
`enable_update` | `boolean` | `False` | If True (**default is False**), this will enable the various services that allow the creation and update of To Do list items

#### Advanced API Options

These options will only be relevant for users in very specific circumstances.

Key | Type | Required | Description
-- | -- | -- | --
`country` | `string` | `True` | Selection of an alternate country specific API. Currently only 21Vianet from China.
`tenant_id` | `string` | `False` | Azure tenant ID for single-tenant app registrations. Leave blank for multi-tenant apps.

### Options variables

Key | Type | Required | Description
-- | -- | -- | --
`track_new` | `boolean` | `False` | If True (default), will automatically generate a todo_entity when a new To Do list is detected. The system scans for new lists only on startup or reconfiguration/reload.
`max_todos` | `int` | `False` | Maximum of To Dos to be retrieved. Default: 100

## Note
If you are using Due Dates on your To Dos and create them outside Home Assistant, it is recommended that the time zone on your Home Assistant instance is set the same as the time zone you habitually use on the device you create To Dos from. This is due to the way the To Do information is returned to the integration, it needs to be corrected for the time zone difference it was saved in, however unfortunately MS do not make this time zone information available via it's api. Due Dates are always set midnight (Reminders are time specific).

Example of the problem:
* A To Do with a Due Date created in a -1000 time zone for 2024/10/24 returns data as below:
```json
    "dueDateTime": {
        "dateTime": "2024-10-24T10:00:00.0000000",
        "timeZone": "UTC"
    }
```
* A To Do with a Due Date created in a +1400 time zone for 2024/10/24 returns data as below:
```json
    "dueDateTime": {
        "dateTime": "2024-10-23T10:00:00.0000000",
        "timeZone": "UTC"
    }
```
* A To Do created by HA, will have data that returns as below:
```json
    "dueDateTime": {
        "dateTime": "2024-10-24T00:00:00.0000000",
        "timeZone": "UTC"
    }
```

As can be seen there it is not possible for the integration to know, just by looking at this data, what the correct date should be. Therefore, it will correct by the HA time zone if time on the due date is something other than 0.
