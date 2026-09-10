from mcp.security.permissions import has_permission


def test_admin_access():

    assert has_permission(
        "admin",
        "system",
    )


def test_viewer_knowledge_access():

    assert has_permission(
        "viewer",
        "knowledge",
    )


def test_viewer_system_denied():

    assert not has_permission(
        "viewer",
        "system",
    )


def test_operator_database_denied():

    assert not has_permission(
        "operator",
        "database",
    )