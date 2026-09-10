from mcp.approval.models import ApprovalStatus
from mcp.approval.service import ApprovalService


def test_create_approval_request():
    service = ApprovalService()

    request = service.create_request(
        user_id="test",
        approver_role="admin",
        work_id="WO-1042",
        task_id="TASK-001",
        server="filesystem",
        tool="write_file",
        arguments={
            "path": "test.txt",
            "content": "hello",
        },
        risk_score=90,
        risk_level="high",
    )

    assert request.status == ApprovalStatus.PENDING
    assert request.work_id == "WO-1042"
    assert request.tool == "write_file"


def test_approve_request():
    service = ApprovalService()

    request = service.create_request(
        user_id="test",
        approver_role="admin",
        work_id="WO-1042",
        task_id="TASK-002",
        server="filesystem",
        tool="write_file",
        arguments={},
        risk_score=90,
        risk_level="high",
    )

    approved = service.approve(request.approval_id)

    assert approved.status == ApprovalStatus.APPROVED


def test_reject_request():
    service = ApprovalService()

    request = service.create_request(
        user_id="test",
        approver_role="admin",
        work_id="WO-1042",
        task_id="TASK-003",
        server="database",
        tool="query",
        arguments={},
        risk_score=80,
        risk_level="high",
    )

    rejected = service.reject(request.approval_id)

    assert rejected.status == ApprovalStatus.REJECTED