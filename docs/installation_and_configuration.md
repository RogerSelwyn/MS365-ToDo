---
title: Installation and Configuration
nav_order: 4
---

# Installation and Configuration
## Installation
1. Ensure you have followed the [prerequisites instructions](./prerequisites.md)
    * Ensure you have a copy of the Client ID and the Client Secret **Value** (not the ID)
1. Optionally you can set up the [permissions](./permissions.md), alternatively you will be requested to approve permissions when you authenticate to MS 365.
1. Install this integration:
    * Recommended - see below, or
    * Manually - Copy [these files](https://github.com/RogerSelwyn/MS365-ToDo/tree/main/custom_components/ms365_todo) to custom_components/ms365_todo/.
1. Restart your Home Assistant instance to enable the integration
1. Add the integration via the `Devices & Services` dialogue. Follow the instructions in the install process (or see [Authentication](./authentication.md)) to establish the link between this integration and the Entra ID App Registration
    * A persistent token will be created in the hidden directory config/ms365_storage/.MS365-token-cache
    * The `ms365_todos_<entity_name>.yaml` will be created under the config directory in the `ms365_storage` directory.
1. [Configure To Do](./todo_configuration.md)
1. Restart your Home Assistant instance.

**Note** If your installation does not complete authentication, or the sensors are not created, please go back and ensure you have accurately followed the steps detailed, also look in the logs to see if there are any errors. You can also look at the [errors page](./errors.md) for some other possibilities.

**Note** To configure a second account, add the integration again via the `Devices & Services` dialogue.

### HACS

1. Launch HACS
1. Search for "Microsoft 365 To Do"
1. Select "Download"
1. Restart Home Assistant
1. Go to the Home Assistant Devices configuration page
1. Click "Add Integration"
1. Search for "Microsoft 365 To Do"
1. Click on the result, and follow the prompts.


### Configuration variables

Key | Type | Required | Description
-- | -- | -- | --
`account_name` | `string` | `True` | Uniquely identifying name for the account. To Do entity names will be suffixed with this. `todo.todo_account1`. Do not use email address or spaces.
`client_id` | `string` | `True` | Client ID from your Entra ID App Registration.
`client_secret` | `string` | `True` | Client Secret from your Entra ID App Registration.
`alt_auth_method` | `boolean` | `False` | If False (default), authentication is not dependent on internet access to your HA instance. [See Authentication](./authentication.md)
`enable_update` | `boolean` | `False` | If True (**default is False**), this will enable the various services that allow the creation and update of To Do list items

### Options variables

Key | Type | Required | Description
-- | -- | -- | --
`track_new_` | `boolean` | `False` | If True (default), will automatically generate a todo_entity when a new To Do list is detected. The system scans for new lists only on startup or reconfiguration/reload.

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
