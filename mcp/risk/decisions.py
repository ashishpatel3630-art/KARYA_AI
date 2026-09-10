from mcp.risk.models import RiskAction, RiskLevel


def action_for_risk(level: RiskLevel) -> RiskAction:
    if level == RiskLevel.LOW:
        return RiskAction.ALLOW

    if level == RiskLevel.MEDIUM:
        return RiskAction.AUDIT_ALLOW

    if level == RiskLevel.HIGH:
        return RiskAction.REQUIRE_APPROVAL

    return RiskAction.BLOCK