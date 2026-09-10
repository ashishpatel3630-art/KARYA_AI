
from inspect import isawaitable

from fastapi import HTTPException

from mcp.approval.service import approval_service
from mcp.gateway.registry import registry
from mcp.risk.engine import calculate_risk
from mcp.risk.models import RiskAction, RiskContext
from mcp.security.audit import audit_log
from mcp.security.permissions import has_permission
from mcp.security.policies import get_policy
from mcp.work.context import WorkContext
from mcp.work.policies import check_work_tool_access


class MCPRouter:
    async def execute(
        self,
        server: str,
        tool: str,
        arguments: dict,
        user_id: str,
        role: str,
        work_id: str | None = None,
        task_id: str | None = None,
    ):
        tool_name = f"{server}.{tool}"

        # ---------------------------------------------------------
        # 1. ROLE PERMISSION
        # ---------------------------------------------------------
        if not has_permission(role, server):
            audit_log(
                user_id=user_id,
                action="mcp.permission_denied",
                details={
                    "server": server,
                    "tool": tool,
                    "role": role,
                },
            )

            raise HTTPException(
                status_code=403,
                detail=f"Role '{role}' cannot access server '{server}'",
            )

        # ---------------------------------------------------------
        # 2. TOOL EXISTS
        # ---------------------------------------------------------
        definition = registry.get(server, tool)

        if definition is None:
            audit_log(
                user_id=user_id,
                action="mcp.tool_not_found",
                details={
                    "server": server,
                    "tool": tool,
                },
            )

            raise HTTPException(
                status_code=404,
                detail=f"Tool '{tool_name}' not found",
            )

        # ---------------------------------------------------------
        # 3. TOOL POLICY
        # ---------------------------------------------------------
        policy = get_policy(server, tool)

        if policy is None:
            audit_log(
                user_id=user_id,
                action="mcp.policy_denied",
                details={
                    "server": server,
                    "tool": tool,
                    "reason": "missing_tool_policy",
                },
            )

            raise HTTPException(
                status_code=403,
                detail=f"No policy configured for tool '{tool_name}'",
            )

        # ---------------------------------------------------------
        # 4. WORK CONTEXT
        # ---------------------------------------------------------
        if work_id is None:
            audit_log(
                user_id=user_id,
                action="mcp.work_context_missing",
                details={
                    "server": server,
                    "tool": tool,
                },
            )

            raise HTTPException(
                status_code=400,
                detail="work_id is required for MCP tool execution",
            )

        if task_id is None:
            audit_log(
                user_id=user_id,
                action="mcp.task_context_missing",
                details={
                    "server": server,
                    "tool": tool,
                    "work_id": work_id,
                },
            )

            raise HTTPException(
                status_code=400,
                detail="task_id is required for MCP tool execution",
            )

        work_context = WorkContext(
            work_id=work_id,
            task_id=task_id,
            user_id=user_id,
            role=role,
        )

        # ---------------------------------------------------------
        # 5. WORK POLICY
        # ---------------------------------------------------------
        allowed = check_work_tool_access(
            work_id=work_context.work_id,
            server=server,
            tool=tool,
        )

        if not allowed:
            audit_log(
                user_id=user_id,
                action="mcp.work_policy_denied",
                details={
                    "work_id": work_context.work_id,
                    "task_id": work_context.task_id,
                    "server": server,
                    "tool": tool,
                    "role": role,
                },
            )

            raise HTTPException(
                status_code=403,
                detail=(
                    f"Work '{work_context.work_id}' does not allow "
                    f"tool '{tool_name}'"
                ),
            )

        # ---------------------------------------------------------
        # 6. RISK ENGINE
        # ---------------------------------------------------------
        risk_context = RiskContext(
            tool_name=tool_name,
            role=role,
            work_id=work_context.work_id,
            task_id=work_context.task_id,
            arguments=arguments,
        )

        risk_decision = calculate_risk(risk_context)

        audit_log(
            user_id=user_id,
            action="mcp.risk_evaluated",
            details={
                "work_id": work_context.work_id,
                "task_id": work_context.task_id,
                "server": server,
                "tool": tool,
                "risk_level": risk_decision.level.value,
                "risk_score": risk_decision.score,
                "risk_action": risk_decision.action.value,
                "reasons": list(risk_decision.reasons),
            },
        )

        # ---------------------------------------------------------
        # 7. CRITICAL RISK -> BLOCK
        # ---------------------------------------------------------
        if risk_decision.action == RiskAction.BLOCK:
            audit_log(
                user_id=user_id,
                action="mcp.risk_blocked",
                details={
                    "work_id": work_context.work_id,
                    "task_id": work_context.task_id,
                    "server": server,
                    "tool": tool,
                    "risk_level": risk_decision.level.value,
                    "risk_score": risk_decision.score,
                },
            )

            raise HTTPException(
                status_code=403,
                detail=(
                    f"Tool '{tool_name}' blocked by risk engine "
                    f"(risk={risk_decision.level.value}, "
                    f"score={risk_decision.score})"
                ),
            )

        # ---------------------------------------------------------
        # 8. HIGH RISK -> CREATE APPROVAL REQUEST
        # ---------------------------------------------------------
        if risk_decision.action == RiskAction.REQUIRE_APPROVAL:
            approval = approval_service.create_request(
                user_id=user_id,
                approver_role="admin",
                work_id=work_context.work_id,
                task_id=work_context.task_id,
                server=server,
                tool=tool,
                arguments=arguments,
                risk_score=risk_decision.score,
                risk_level=risk_decision.level.value,
            )

            audit_log(
                user_id=user_id,
                action="mcp.approval_requested",
                details={
                    "approval_id": approval.approval_id,
                    "work_id": work_context.work_id,
                    "task_id": work_context.task_id,
                    "server": server,
                    "tool": tool,
                    "risk_level": risk_decision.level.value,
                    "risk_score": risk_decision.score,
                    "status": approval.status.value,
                },
            )

            return {
                "success": False,
                "status": "approval_required",
                "approval_id": approval.approval_id,
                "message": (
                    f"Approval required before executing "
                    f"'{tool_name}'"
                ),
                "approval": {
                    "approval_id": approval.approval_id,
                    "status": approval.status.value,
                    "work_id": approval.work_id,
                    "task_id": approval.task_id,
                    "server": approval.server,
                    "tool": approval.tool,
                    "risk_level": approval.risk_level,
                    "risk_score": approval.risk_score,
                },
            }

        # ---------------------------------------------------------
        # 9. LEGACY CONFIRMATION
        # ---------------------------------------------------------
        if policy.requires_confirmation:
            audit_log(
                user_id=user_id,
                action="mcp.confirmation_required",
                details={
                    "work_id": work_context.work_id,
                    "task_id": work_context.task_id,
                    "server": server,
                    "tool": tool,
                },
            )

            raise HTTPException(
                status_code=409,
                detail=f"Tool '{tool_name}' requires confirmation",
            )

        # ---------------------------------------------------------
        # 10. EXECUTE LOW / MEDIUM RISK TOOL
        # ---------------------------------------------------------
        try:
            result = definition.handler(**arguments)

            if isawaitable(result):
                result = await result

        except HTTPException:
            raise

        except Exception as exc:
            audit_log(
                user_id=user_id,
                action="mcp.execution_failed",
                details={
                    "work_id": work_context.work_id,
                    "task_id": work_context.task_id,
                    "server": server,
                    "tool": tool,
                    "error": str(exc),
                },
            )

            raise HTTPException(
                status_code=500,
                detail=f"Tool execution failed: {str(exc)}",
            ) from exc

        # ---------------------------------------------------------
        # 11. AUDIT SUCCESSFUL EXECUTION
        # ---------------------------------------------------------
        audit_log(
            user_id=user_id,
            action="mcp.tool_executed",
            details={
                "work_id": work_context.work_id,
                "task_id": work_context.task_id,
                "server": server,
                "tool": tool,
                "risk_level": risk_decision.level.value,
                "risk_score": risk_decision.score,
            },
        )

        return result


router = MCPRouter()
