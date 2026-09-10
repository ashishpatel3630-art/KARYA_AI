from mcp.work.service import is_tool_allowed_for_work


def check_work_tool_access(
    work_id: str,
    server: str,
    tool: str,
) -> bool:
    tool_name = f"{server}.{tool}"

    return is_tool_allowed_for_work(
        work_id=work_id,
        tool_name=tool_name,
    )