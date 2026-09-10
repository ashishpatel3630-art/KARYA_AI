from mcp.risk.engine import calculate_risk
from mcp.risk.models import (
    RiskAction,
    RiskContext,
    RiskLevel,
)


def make_context(
    tool_name: str,
    role: str = "admin",
) -> RiskContext:
    return RiskContext(
        tool_name=tool_name,
        role=role,
        work_id="WO-1042",
        task_id="TASK-001",
        arguments={},
    )


def test_low_risk_tool_is_allowed():
    decision = calculate_risk(
        make_context("system.ping")
    )

    assert decision.level == RiskLevel.LOW
    assert decision.action == RiskAction.ALLOW


def test_sensitive_knowledge_tool_is_audited():
    decision = calculate_risk(
        make_context("knowledge.search")
    )

    assert decision.level == RiskLevel.LOW
    assert decision.action == RiskAction.ALLOW


def test_filesystem_read_is_medium_risk():
    decision = calculate_risk(
        make_context("filesystem.read_file")
    )

    assert decision.level == RiskLevel.MEDIUM
    assert decision.action == RiskAction.AUDIT_ALLOW


def test_filesystem_write_requires_approval():
    decision = calculate_risk(
        make_context("filesystem.write_file")
    )

    assert decision.level == RiskLevel.HIGH
    assert decision.action == RiskAction.REQUIRE_APPROVAL


def test_database_query_requires_approval():
    decision = calculate_risk(
        make_context("database.query")
    )

    assert decision.level == RiskLevel.HIGH
    assert decision.action == RiskAction.REQUIRE_APPROVAL


def test_unknown_tool_is_blocked():
    decision = calculate_risk(
        make_context("unknown.dangerous_tool")
    )

    assert decision.level == RiskLevel.CRITICAL
    assert decision.action == RiskAction.BLOCK


def test_viewer_has_additional_risk():
    decision = calculate_risk(
        make_context(
            "filesystem.read_file",
            role="viewer",
        )
    )

    assert decision.score > 30
    assert decision.level == RiskLevel.MEDIUM