from dataclasses import dataclass

from mcp.risk.models import RiskLevel


@dataclass(frozen=True)
class RiskRule:
    base_score: int
    level: RiskLevel
    destructive: bool = False
    sensitive_data: bool = False


TOOL_RISK_RULES: dict[str, RiskRule] = {
    "knowledge.search": RiskRule(
        base_score=10,
        level=RiskLevel.LOW,
        sensitive_data=True,
    ),
    "knowledge.get_document": RiskRule(
        base_score=15,
        level=RiskLevel.LOW,
        sensitive_data=True,
    ),
    "industrial.get_asset": RiskRule(
        base_score=10,
        level=RiskLevel.LOW,
    ),
    "industrial.list_assets": RiskRule(
        base_score=5,
        level=RiskLevel.LOW,
    ),
    "industrial.get_asset_status": RiskRule(
        base_score=10,
        level=RiskLevel.LOW,
    ),
    "analytics.calculate": RiskRule(
        base_score=10,
        level=RiskLevel.LOW,
    ),
    "system.status": RiskRule(
        base_score=5,
        level=RiskLevel.LOW,
    ),
    "system.ping": RiskRule(
        base_score=1,
        level=RiskLevel.LOW,
    ),
    "filesystem.read_file": RiskRule(
        base_score=30,
        level=RiskLevel.MEDIUM,
        sensitive_data=True,
    ),
    "filesystem.write_file": RiskRule(
        base_score=75,
        level=RiskLevel.HIGH,
        destructive=True,
    ),
    "database.query": RiskRule(
        base_score=70,
        level=RiskLevel.HIGH,
        sensitive_data=True,
    ),
}


def get_risk_rule(tool_name: str) -> RiskRule | None:
    return TOOL_RISK_RULES.get(tool_name)