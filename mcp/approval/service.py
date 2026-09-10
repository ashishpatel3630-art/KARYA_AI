from dataclasses import replace
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from mcp.approval.models import ApprovalRequest, ApprovalStatus
from mcp.approval.store import approval_store


APPROVAL_TTL_MINUTES = 10


class ApprovalService:
    def create_request(
        self,
        user_id: str,
        approver_role: str,
        work_id: str,
        task_id: str,
        server: str,
        tool: str,
        arguments: dict,
        risk_score: int,
        risk_level: str,
    ) -> ApprovalRequest:
        now = datetime.now(timezone.utc)

        expires_at = now + timedelta(
            minutes=APPROVAL_TTL_MINUTES
        )

        request = ApprovalRequest(
            approval_id=str(uuid4()),
            user_id=user_id,
            approver_role=approver_role,
            approved_by_id=None,
            work_id=work_id,
            task_id=task_id,
            server=server,
            tool=tool,
            arguments=dict(arguments),
            risk_score=risk_score,
            risk_level=risk_level,
            status=ApprovalStatus.PENDING,
            expires_at=expires_at,
            created_at=now,
            approved_at=None,
            rejected_at=None,
            executed_at=None,
        )

        approval_store.create(request)

        return request

    def get_request(
        self,
        approval_id: str,
    ) -> ApprovalRequest | None:
        return approval_store.get(approval_id)

    def list_pending(self) -> list[ApprovalRequest]:
        return approval_store.list_pending()

    def approve(
        self,
        approval_id: str,
        approver_id: str,
    ) -> ApprovalRequest:
        request = approval_store.get(approval_id)

        if request is None:
            raise KeyError(
                "Approval request not found"
            )

        if request.status == ApprovalStatus.EXPIRED:
            raise ValueError(
                "Approval request has expired"
            )

        if request.status != ApprovalStatus.PENDING:
            raise ValueError(
                "Approval request cannot be approved from status "
                f"'{request.status.value}'"
            )

        # -----------------------------------------------------
        # REQUESTER ≠ APPROVER
        # -----------------------------------------------------
        if request.user_id == approver_id:
            raise ValueError(
                "Requester cannot approve their own action"
            )

        now = datetime.now(timezone.utc)

        if request.expires_at is not None:
            expires_at = request.expires_at

            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(
                    tzinfo=timezone.utc
                )

            if now >= expires_at:
                expired = replace(
                    request,
                    status=ApprovalStatus.EXPIRED,
                )

                approval_store.update(expired)

                raise ValueError(
                    "Approval request has expired"
                )

        updated = replace(
            request,
            status=ApprovalStatus.APPROVED,
            approved_by_id=approver_id,
            approved_at=now,
        )

        approval_store.update(updated)

        return updated

    def reject(
        self,
        approval_id: str,
        approver_id: str | None = None,
    ) -> ApprovalRequest:
        request = approval_store.get(approval_id)

        if request is None:
            raise KeyError(
                "Approval request not found"
            )

        if request.status == ApprovalStatus.EXPIRED:
            raise ValueError(
                "Approval request has expired"
            )

        if request.status != ApprovalStatus.PENDING:
            raise ValueError(
                "Approval request cannot be rejected from status "
                f"'{request.status.value}'"
            )

        # A requester cannot reject their own request either.
        if approver_id is not None and request.user_id == approver_id:
            raise ValueError(
                "Requester cannot reject their own action"
            )

        now = datetime.now(timezone.utc)

        updated = replace(
            request,
            status=ApprovalStatus.REJECTED,
            rejected_at=now,
        )

        approval_store.update(updated)

        return updated

    def mark_executed(
        self,
        approval_id: str,
    ) -> ApprovalRequest:
        request = approval_store.get(approval_id)

        if request is None:
            raise KeyError(
                "Approval request not found"
            )

        if request.status == ApprovalStatus.EXPIRED:
            raise ValueError(
                "Approval request has expired"
            )

        if request.status != ApprovalStatus.APPROVED:
            raise ValueError(
                "Approval request cannot be executed from status "
                f"'{request.status.value}'"
            )

        now = datetime.now(timezone.utc)

        updated = replace(
            request,
            status=ApprovalStatus.EXECUTED,
            executed_at=now,
        )

        approval_store.update(updated)

        return updated


approval_service = ApprovalService()