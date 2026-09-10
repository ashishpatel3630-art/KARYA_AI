from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    ENGINEER = "engineer"
    OPERATOR = "operator"
    ANALYST = "analyst"
    VIEWER = "viewer"


PERMISSIONS = {
    Role.ADMIN: {
        "knowledge",
        "database",
        "filesystem",
        "industrial",
        "analytics",
        "system",
    },

    Role.ENGINEER: {
        "knowledge",
        "filesystem",
        "industrial",
        "analytics",
    },

    Role.OPERATOR: {
        "knowledge",
        "industrial",
    },

    Role.ANALYST: {
        "knowledge",
        "analytics",
        "database",
    },

    Role.VIEWER: {
        "knowledge",
    },
}


def has_permission(role: str, server_name: str) -> bool:
    try:
        role_enum = Role(role)
    except ValueError:
        return False

    return server_name in PERMISSIONS.get(role_enum, set())