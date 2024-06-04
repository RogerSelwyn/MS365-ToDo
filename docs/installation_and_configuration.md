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
    * The `ms365_todos_<account_name>.yaml` will be created under the config directory in the `ms365_storage` directory.
1. [Configure To Do](./todo_configuration.md)
1. Restart your Home Assistant instance.

**Note** If your installation does not complete authentication, or the sensors are not created, please go back and ensure you have accurately followed the steps detailed, also look in the logs to see if there are any errors. You can also look at the [errors page](./errors.md) for some other possibilities.

**Note** To configure a second account, add the integration again via the `Devices & Services` dialogue.

### HACS

1. Launch HACS
1. Navigate to the Integrations section
1. Add this repository as a Custom Repository (Integration) via the menu at top right.
1. Search for "Microsoft 365 To Do"
1. Select "Install this repository"
1. Restart Home Assistant


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
