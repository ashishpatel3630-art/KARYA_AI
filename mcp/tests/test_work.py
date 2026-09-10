from mcp.work.models import WorkPolicy
from mcp.work.service import is_tool_allowed_for_work


def test_work_allows_industrial_asset():
    assert is_tool_allowed_for_work(
        "WO-1042",
        "industrial.get_asset",
    ) is True


def test_work_allows_knowledge_search():
    assert is_tool_allowed_for_work(
        "WO-1042",
        "knowledge.search",
    ) is True


def test_work_denies_database():
    assert is_tool_allowed_for_work(
        "WO-1042",
        "database.query",
    ) is False


def test_work_denies_filesystem_write():
    assert is_tool_allowed_for_work(
        "WO-1042",
        "filesystem.write_file",
    ) is False


def test_unknown_work_denied():
    assert is_tool_allowed_for_work(
        "UNKNOWN-WORK",
        "industrial.get_asset",
    ) is False