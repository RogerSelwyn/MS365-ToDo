"""Permissions processes for todo."""

from copy import deepcopy

from ..classes.permissions import BasePermissions
from ..const import (
    CONF_ENABLE_UPDATE,
    PERM_BASE_PERMISSIONS,
)
from .const_integration import PERM_TASKS_READ, PERM_TASKS_READWRITE


class Permissions(BasePermissions):
    """Class in support of building permission sets."""

    def __init__(self, hass, config, token_backend):
        """Initialise the class."""
        super().__init__(hass, config, token_backend)

        self._enable_update = self._config.get(CONF_ENABLE_UPDATE, False)

    @property
    def requested_permissions(self):
        """Return the required scope."""
        if not self._requested_permissions:
            self._requested_permissions = deepcopy(PERM_BASE_PERMISSIONS)
            self._build_todo_permissions()

        return self._requested_permissions

    def _build_todo_permissions(self):
        if self._enable_update:
            self._requested_permissions.append(PERM_TASKS_READWRITE)
        else:
            self._requested_permissions.append(PERM_TASKS_READ)
