from datetime import datetime, timezone

from mcp.approval.models import ApprovalRequest, ApprovalStatus


class ApprovalStore:
    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}

    def create(
        self,
        request: ApprovalRequest,
    ) -> ApprovalRequest:
        self._requests[request.approval_id] = request
        return request

    def get(
        self,
        approval_id: str,
    ) -> ApprovalRequest | None:
        request = self._requests.get(approval_id)

        if request is None:
            return None

        return self._expire_if_needed(request)

    def list_pending(self) -> list[ApprovalRequest]:
        pending: list[ApprovalRequest] = []

        for request in list(self._requests.values()):
            request = self._expire_if_needed(request)

            if request.status == ApprovalStatus.PENDING:
                pending.append(request)

        return pending

    def update(
        self,
        request: ApprovalRequest,
    ) -> ApprovalRequest:
        if request.approval_id not in self._requests:
            raise KeyError(
                f"Approval '{request.approval_id}' not found"
            )

        self._requests[request.approval_id] = request
        return request

    def _expire_if_needed(
        self,
        request: ApprovalRequest,
    ) -> ApprovalRequest:
        if request.status != ApprovalStatus.PENDING:
            return request

        if request.expires_at is None:
            return request

        now = datetime.now(timezone.utc)

        expires_at = request.expires_at

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        if now < expires_at:
            return request

        expired = request.__class__(
            approval_id=request.approval_id,
            user_id=request.user_id,
            approver_role=request.approver_role,
            approved_by_id=request.approved_by_id,
            work_id=request.work_id,
            task_id=request.task_id,
            server=request.server,
            tool=request.tool,
            arguments=request.arguments,
            risk_score=request.risk_score,
            risk_level=request.risk_level,
            status=ApprovalStatus.EXPIRED,
            expires_at=request.expires_at,
            created_at=request.created_at,
            approved_at=request.approved_at,
            rejected_at=request.rejected_at,
            executed_at=request.executed_at,
        )

        self._requests[request.approval_id] = expired

        return expired


approval_store = ApprovalStore()