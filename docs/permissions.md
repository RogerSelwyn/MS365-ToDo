---
title: Permissions
nav_order: 3
---

# Permissions

This page details the permissions for this integration. General instructions can be found on the MS365 Home Assistant [Permissions](https://rogerselwyn.github.io/MS365-HomeAssistant/permissions.html) page.

   | Feature  | Permissions                | Update | MS Graph Description                                           | Notes |
   |----------|----------------------------|:------:|----------------------------------------------------------------|-------|
   | All      | offline_access             |        | *Maintain access to data you have given it access to*          |       |
   | All      | User.Read                  |        | *Sign in and read user profile*                                |       |
   | To Do     | Tasks.Read                 |        | *Read user's tasks and task lists*                             | Not for shared mailboxes |
   | To Do     | Tasks.ReadWrite            | Y      | *Create, read, update, and delete user’s tasks and task lists* | Not for shared mailboxes |
   