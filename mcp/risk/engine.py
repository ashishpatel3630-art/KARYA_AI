from mcp.risk.decisions import action_for_risk
from mcp.risk.models import (
    RiskContext,
    RiskDecision,
    RiskLevel,
)
from mcp.risk.rules import get_risk_rule


def _level_from_score(score: int) -> RiskLevel:
    if score >= 95:
        return RiskLevel.CRITICAL

    if score >= 60:
        return RiskLevel.HIGH

    if score >= 30:
        return RiskLevel.MEDIUM

    return RiskLevel.LOW


def calculate_risk(context: RiskContext) -> RiskDecision:
    rule = get_risk_rule(context.tool_name)

    if rule is None:
        return RiskDecision(
            level=RiskLevel.CRITICAL,
            action=action_for_risk(RiskLevel.CRITICAL),
            score=100,
            reasons=("No risk policy exists for this tool",),
        )

    score = rule.base_score
    reasons: list[str] = []

    reasons.append(
        f"Base tool risk score: {rule.base_score}"
    )

    if rule.destructive:
        score += 15
        reasons.append("Tool has destructive capabilities")

    if rule.sensitive_data:
        score += 10
        reasons.append("Tool may access sensitive data")

    if context.role.lower() == "viewer":
        score += 5
        reasons.append("Viewer role increases execution risk")

    score = min(score, 100)

    level = _level_from_score(score)
    action = action_for_risk(level)

    return RiskDecision(
        level=level,
        action=action,
        score=score,
        reasons=tuple(reasons),
    )