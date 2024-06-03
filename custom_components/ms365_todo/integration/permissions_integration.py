"""Permissions processes for todo."""

from ..classes.permissions import BasePermissions
from ..const import (
    CONF_ENABLE_UPDATE,
    PERM_OFFLINE_ACCESS,
    PERM_USER_READ,
)
from .const_integration import PERM_TASKS_READ, PERM_TASKS_READWRITE


class Permissions(BasePermissions):
    """Class in support of building permission sets."""

    def __init__(self, hass, config):
        """Initialise the class."""
        super().__init__(hass, config)

        self._enable_update = self._config.get(CONF_ENABLE_UPDATE, False)

    @property
    def requested_permissions(self):
        """Return the required scope."""
        if not self._requested_permissions:
            self._requested_permissions = [PERM_OFFLINE_ACCESS, PERM_USER_READ]
            self._build_todo_permissions()

        return self._requested_permissions

    def _build_todo_permissions(self):
        if self._enable_update:
            self._requested_permissions.append(PERM_TASKS_READWRITE)
        else:
            self._requested_permissions.append(PERM_TASKS_READ)
