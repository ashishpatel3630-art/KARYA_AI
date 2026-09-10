from mcp.work.models import WorkPolicy


WORK_POLICIES = {
    "WO-1042": WorkPolicy(
        work_id="WO-1042",
        allowed_tools={
            "knowledge.search",
            "knowledge.get_document",
            "industrial.get_asset",
            "industrial.list_assets",
            "industrial.get_asset_status",
            "analytics.calculate",
            "system.ping",
            "system.status",
        },
        denied_tools={
            "filesystem.write_file",
            "database.query",
        },
    ),

    # Dedicated controlled work order for testing
    # high-risk actions through the approval engine.
    "WO-APPROVAL-001": WorkPolicy(
        work_id="WO-APPROVAL-001",
        allowed_tools={
            "filesystem.write_file",
        },
    ),
}


def get_work_policy(work_id: str) -> WorkPolicy | None:
    return WORK_POLICIES.get(work_id)


def is_tool_allowed_for_work(work_id: str, tool_name: str) -> bool:
    policy = get_work_policy(work_id)

    if policy is None:
        return False

    return policy.is_tool_allowed(tool_name)