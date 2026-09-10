from mcp.gateway.registry import registry


def query(sql: str) -> dict:
    """
    Read-only database interface.

    IMPORTANT:
    Production version should use a SQL parser / allow-list
    instead of executing arbitrary SQL.
    """

    normalized = sql.strip().lower()

    if not normalized.startswith("select"):
        raise PermissionError(
            "Only SELECT queries are allowed."
        )

    return {
        "sql": sql,
        "rows": [],
        "source": "karya-database",
    }


registry.register(
    name="query",
    server="database",
    description="Execute a read-only database query",
    handler=query,
)