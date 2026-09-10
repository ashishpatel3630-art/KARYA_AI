from dataclasses import asdict
from datetime import datetime
from inspect import isawaitable

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from mcp.approval.models import ApprovalStatus
from mcp.approval.service import approval_service
from mcp.gateway.registry import registry
from mcp.security.audit import audit_log


router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


class ApprovalActionRequest(BaseModel):
    approver_id: str = Field(
        min_length=1,
        max_length=128,
    )

    approver_role: str = Field(
        min_length=1,
        max_length=50,
    )


class ApprovalExecuteRequest(BaseModel):
    executor_id: str = Field(
        min_length=1,
        max_length=128,
    )

    executor_role: str = Field(
        min_length=1,
        max_length=50,
    )


def serialize(request):
    data = asdict(request)

    data["status"] = request.status.value

    for field_name in (
        "expires_at",
        "created_at",
        "approved_at",
        "rejected_at",
        "executed_at",
    ):
        value = data.get(field_name)

        if isinstance(value, datetime):
            data[field_name] = value.isoformat()

    return data


@router.get("")
async def list_approvals():
    requests = approval_service.list_pending()

    return {
        "success": True,
        "approvals": [
            serialize(request)
            for request in requests
        ],
    }


@router.get("/{approval_id}")
async def get_approval(
    approval_id: str,
):
    request = approval_service.get_request(
        approval_id
    )

    if request is None:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found",
        )

    return {
        "success": True,
        "approval": serialize(request),
    }


@router.post("/{approval_id}/approve")
async def approve_approval(
    approval_id: str,
    request: ApprovalActionRequest,
):
    # ---------------------------------------------------------
    # APPROVER ROLE
    # ---------------------------------------------------------
    if request.approver_role.lower() not in {
        "admin",
        "engineer",
    }:
        raise HTTPException(
            status_code=403,
            detail=(
                "User is not authorized to approve actions"
            ),
        )

    # ---------------------------------------------------------
    # APPROVE
    # ---------------------------------------------------------
    try:
        approval = approval_service.approve(
            approval_id=approval_id,
            approver_id=request.approver_id,
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        if "Requester cannot" in str(exc):
            audit_log(
                user_id=request.approver_id,
                action="mcp.self_approval_blocked",
                details={
                    "approval_id": approval_id,
                    "reason": str(exc),
                },
            )

            raise HTTPException(
                status_code=403,
                detail=str(exc),
            ) from exc

        audit_log(
            user_id=request.approver_id,
            action="mcp.approval_denied",
            details={
                "approval_id": approval_id,
                "reason": str(exc),
            },
        )

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    # ---------------------------------------------------------
    # AUDIT
    # ---------------------------------------------------------
    audit_log(
        user_id=request.approver_id,
        action="mcp.approval_approved",
        details={
            "approval_id": approval.approval_id,
            "requester_id": approval.user_id,
            "approver_id": approval.approved_by_id,
            "work_id": approval.work_id,
            "task_id": approval.task_id,
            "server": approval.server,
            "tool": approval.tool,
            "risk_level": approval.risk_level,
            "risk_score": approval.risk_score,
            "status": approval.status.value,
        },
    )

    return {
        "success": True,
        "message": "Approval granted",
        "approval": serialize(approval),
    }


@router.post("/{approval_id}/reject")
async def reject_approval(
    approval_id: str,
    request: ApprovalActionRequest,
):
    # ---------------------------------------------------------
    # APPROVER ROLE
    # ---------------------------------------------------------
    if request.approver_role.lower() not in {
        "admin",
        "engineer",
    }:
        raise HTTPException(
            status_code=403,
            detail=(
                "User is not authorized to reject actions"
            ),
        )

    # ---------------------------------------------------------
    # REJECT
    # ---------------------------------------------------------
    try:
        approval = approval_service.reject(
            approval_id=approval_id,
            approver_id=request.approver_id,
        )

    except KeyError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        if "Requester cannot" in str(exc):
            audit_log(
                user_id=request.approver_id,
                action="mcp.self_rejection_blocked",
                details={
                    "approval_id": approval_id,
                    "reason": str(exc),
                },
            )

            raise HTTPException(
                status_code=403,
                detail=str(exc),
            ) from exc

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    # ---------------------------------------------------------
    # AUDIT
    # ---------------------------------------------------------
    audit_log(
        user_id=request.approver_id,
        action="mcp.approval_rejected",
        details={
            "approval_id": approval.approval_id,
            "requester_id": approval.user_id,
            "approver_id": request.approver_id,
            "work_id": approval.work_id,
            "task_id": approval.task_id,
            "server": approval.server,
            "tool": approval.tool,
            "status": approval.status.value,
        },
    )

    return {
        "success": True,
        "message": "Approval rejected",
        "approval": serialize(approval),
    }


@router.post("/{approval_id}/execute")
async def execute_approved_action(
    approval_id: str,
    request: ApprovalExecuteRequest,
):
    # ---------------------------------------------------------
    # LOAD APPROVAL
    # ---------------------------------------------------------
    approval = approval_service.get_request(
        approval_id
    )

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found",
        )

    # ---------------------------------------------------------
    # EXPIRY CHECK
    # ---------------------------------------------------------
    if approval.status == ApprovalStatus.EXPIRED:
        audit_log(
            user_id=request.executor_id,
            action="mcp.approval_execution_expired",
            details={
                "approval_id": approval_id,
                "reason": "approval_expired",
            },
        )

        raise HTTPException(
            status_code=409,
            detail="Approval has expired",
        )

    # ---------------------------------------------------------
    # REPLAY PROTECTION
    # ---------------------------------------------------------
    if approval.status == ApprovalStatus.EXECUTED:
        audit_log(
            user_id=request.executor_id,
            action="mcp.approval_replay_blocked",
            details={
                "approval_id": approval_id,
                "reason": "approval_already_executed",
            },
        )

        raise HTTPException(
            status_code=409,
            detail="Approval has already been executed",
        )

    # ---------------------------------------------------------
    # APPROVAL STATUS
    # ---------------------------------------------------------
    if approval.status != ApprovalStatus.APPROVED:
        raise HTTPException(
            status_code=409,
            detail=(
                "Approval must be approved before execution. "
                f"Current status: '{approval.status.value}'"
            ),
        )

    # ---------------------------------------------------------
    # EXECUTOR AUTHORIZATION
    # ---------------------------------------------------------
    if request.executor_role.lower() not in {
        "admin",
        "engineer",
    }:
        audit_log(
            user_id=request.executor_id,
            action="mcp.approval_execution_denied",
            details={
                "approval_id": approval_id,
                "reason": "executor_not_authorized",
                "executor_role": request.executor_role,
            },
        )

        raise HTTPException(
            status_code=403,
            detail=(
                "User is not authorized to execute "
                "approved actions"
            ),
        )

    # ---------------------------------------------------------
    # TOOL LOOKUP
    # ---------------------------------------------------------
    definition = registry.get(
        approval.server,
        approval.tool,
    )

    if definition is None:
        audit_log(
            user_id=request.executor_id,
            action="mcp.approval_tool_missing",
            details={
                "approval_id": approval_id,
                "server": approval.server,
                "tool": approval.tool,
            },
        )

        raise HTTPException(
            status_code=404,
            detail=(
                f"Approved tool "
                f"'{approval.server}.{approval.tool}' "
                "no longer exists"
            ),
        )

    # ---------------------------------------------------------
    # EXECUTE EXACT APPROVED ARGUMENTS
    # ---------------------------------------------------------
    try:
        result = definition.handler(
            **approval.arguments
        )

        if isawaitable(result):
            result = await result

    except HTTPException:
        raise

    except Exception as exc:
        audit_log(
            user_id=request.executor_id,
            action="mcp.approval_execution_failed",
            details={
                "approval_id": approval_id,
                "server": approval.server,
                "tool": approval.tool,
                "error": str(exc),
            },
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Approved tool execution failed: {str(exc)}"
            ),
        ) from exc

    # ---------------------------------------------------------
    # MARK EXECUTED
    # ---------------------------------------------------------
    try:
        executed = approval_service.mark_executed(
            approval_id
        )

    except (KeyError, ValueError) as exc:
        audit_log(
            user_id=request.executor_id,
            action="mcp.approval_mark_execution_failed",
            details={
                "approval_id": approval_id,
                "error": str(exc),
            },
        )

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    # ---------------------------------------------------------
    # AUDIT SUCCESS
    # ---------------------------------------------------------
    audit_log(
        user_id=request.executor_id,
        action="mcp.approval_executed",
        details={
            "approval_id": approval_id,
            "requester_id": executed.user_id,
            "approver_id": executed.approved_by_id,
            "executor_id": request.executor_id,
            "work_id": executed.work_id,
            "task_id": executed.task_id,
            "server": executed.server,
            "tool": executed.tool,
            "risk_level": executed.risk_level,
            "risk_score": executed.risk_score,
            "status": executed.status.value,
        },
    )

    return {
        "success": True,
        "status": "executed",
        "approval_id": approval_id,
        "result": result,
        "approval": serialize(executed),
    }