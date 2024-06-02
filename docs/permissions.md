---
title: Permissions
nav_order: 3
---

# Permissions

Under "API Permissions" click Add a permission, then Microsoft Graph, then Delegated permission, and add the permissions as detailed in the list and table below:

   | Feature  | Permissions                | Update | MS Graph Description                                           | Notes |
   |----------|----------------------------|:------:|----------------------------------------------------------------|-------|
   | All      | offline_access             |        | *Maintain access to data you have given it access to*          |       |
   | All      | User.Read                  |        | *Sign in and read user profile*                                |       |
   | ToDo     | Tasks.Read                 |        | *Read user's tasks and task lists*                             | Not for shared mailboxes |
   | ToDo     | Tasks.ReadWrite            | Y      | *Create, read, update, and delete user’s tasks and task lists* | Not for shared mailboxes |
   

## Changing Features and Permissions
If you decide to enable new features in the integration, or decide to change from read only to read/write, you will very likely get a warning message similar to the following in your logs.

`Minimum required permissions not granted: ['Tasks.Read', ['Tasks.ReadWrite']]`

You will need to delete as detailed on the [token page](./token.md)