from .user import (
    create_users,
    update_users,
    delete_users,
)
from .axe import (
    create_axes,
    update_axes,
    delete_axes,
)
# Projects functions as aliases to axes functions
from .axe import (
    create_axes as create_projects,
    update_axes as update_projects,
    delete_axes as delete_projects,
)

__all__ = [
    # users
    "create_users",
    "update_users",
    "delete_users",
    # generic axes
    "create_axes",
    "update_axes",
    "delete_axes",
    # projects
    "create_projects",
    "update_projects",
    "delete_projects",
]