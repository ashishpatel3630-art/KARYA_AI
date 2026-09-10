from dataclasses import dataclass


@dataclass(frozen=True)
class ToolPolicy:
    server: str
    tool: str
    description: str
    requires_confirmation: bool = False


TOOL_POLICIES = {
    # =========================
    # KNOWLEDGE
    # =========================

    "knowledge.search": ToolPolicy(
        server="knowledge",
        tool="search",
        description="Search KARYA knowledge base",
    ),

    "knowledge.get_document": ToolPolicy(
        server="knowledge",
        tool="get_document",
        description="Retrieve a document from knowledge base",
    ),

    # =========================
    # DATABASE
    # =========================

    "database.query": ToolPolicy(
        server="database",
        tool="query",
        description="Execute a read-only database query",
        requires_confirmation=True,
    ),

    # =========================
    # FILESYSTEM
    # =========================

    "filesystem.read_file": ToolPolicy(
        server="filesystem",
        tool="read_file",
        description="Read an approved local file",
    ),

    "filesystem.write_file": ToolPolicy(
        server="filesystem",
        tool="write_file",
        description="Write to approved local storage",
        requires_confirmation=True,
    ),

    # =========================
    # INDUSTRIAL
    # =========================

    "industrial.get_asset": ToolPolicy(
        server="industrial",
        tool="get_asset",
        description="Retrieve industrial asset information",
    ),

    "industrial.list_assets": ToolPolicy(
        server="industrial",
        tool="list_assets",
        description="List registered industrial assets",
    ),

    "industrial.get_asset_status": ToolPolicy(
        server="industrial",
        tool="get_asset_status",
        description="Get industrial asset status",
    ),

    # =========================
    # ANALYTICS
    # =========================

    "analytics.calculate": ToolPolicy(
        server="analytics",
        tool="calculate",
        description="Run analytics calculation",
    ),

    # =========================
    # SYSTEM
    # =========================

    "system.status": ToolPolicy(
        server="system",
        tool="status",
        description="Retrieve KARYA system status",
    ),

    "system.ping": ToolPolicy(
        server="system",
        tool="ping",
        description="Ping KARYA system",
    ),
}


def get_policy(server: str, tool: str) -> ToolPolicy | None:
    return TOOL_POLICIES.get(f"{server}.{tool}")