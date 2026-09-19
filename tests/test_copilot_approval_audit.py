from app.models.copilot_approval import (
    CopilotApprovalResult,
    CopilotApprovalStatus,
)
from app.services.copilot_approval_audit import (
    clear_approval_audit,
    get_approval_audit_record,
    get_approval_audit_records,
    get_approval_audit_summary,
    record_approval_audit,
)


def setup_function():
    clear_approval_audit()


def _approval(
    *,
    decision_id="DEC-001",
    status=CopilotApprovalStatus.PENDING,
    approval_required=True,
    allowed_to_proceed=False,
    approver=None,
    approval_comment=None,
):
    return CopilotApprovalResult(
        decision_id=decision_id,
        status=status,
        allowed_to_proceed=allowed_to_proceed,
        approval_required=approval_required,
        approver=approver,
        approval_comment=approval_comment,
        rationale="Test approval result.",
        trace=["Approval Request", "Approval Policy Evaluation"],
    )


def test_pending_approval_creates_audit_record():
    record = record_approval_audit(
        _approval()
    )

    assert record.audit_id == "AUD-001"
    assert record.decision_id == "DEC-001"
    assert record.status == CopilotApprovalStatus.PENDING
    assert record.allowed_to_proceed is False
    assert record.approval_required is True
    assert record.trace == [
        "Approval Result",
        "Audit Record Created",
    ]


def test_approved_action_preserves_approver_and_comment():
    record = record_approval_audit(
        _approval(
            decision_id="DEC-002",
            status=CopilotApprovalStatus.APPROVED,
            allowed_to_proceed=True,
            approver="human-reviewer",
            approval_comment="Approved for controlled execution.",
        )
    )

    assert record.audit_id == "AUD-001"
    assert record.status == CopilotApprovalStatus.APPROVED
    assert record.allowed_to_proceed is True
    assert record.approver == "human-reviewer"
    assert record.approval_comment == (
        "Approved for controlled execution."
    )


def test_multiple_records_get_incremental_audit_ids():
    first = record_approval_audit(_approval(decision_id="DEC-001"))

    second = record_approval_audit(
        _approval(
            decision_id="DEC-002",
            status=CopilotApprovalStatus.REJECTED,
        )
    )

    assert first.audit_id == "AUD-001"
    assert second.audit_id == "AUD-002"

    records = get_approval_audit_records()

    assert len(records) == 2
    assert records[0].decision_id == "DEC-001"
    assert records[1].decision_id == "DEC-002"


def test_audit_record_can_be_retrieved_by_id():
    record = record_approval_audit(
        _approval(
            decision_id="DEC-003",
            status=CopilotApprovalStatus.REJECTED,
        )
    )

    found = get_approval_audit_record(record.audit_id)

    assert found is not None
    assert found.audit_id == record.audit_id
    assert found.decision_id == "DEC-003"
    assert found.status == CopilotApprovalStatus.REJECTED


def test_unknown_audit_id_returns_none():
    assert get_approval_audit_record("AUD-999") is None


def test_audit_summary_counts_statuses():
    record_approval_audit(
        _approval(
            decision_id="DEC-001",
            status=CopilotApprovalStatus.PENDING,
        )
    )

    record_approval_audit(
        _approval(
            decision_id="DEC-002",
            status=CopilotApprovalStatus.APPROVED,
            allowed_to_proceed=True,
        )
    )

    record_approval_audit(
        _approval(
            decision_id="DEC-003",
            status=CopilotApprovalStatus.REJECTED,
        )
    )

    summary = get_approval_audit_summary()

    assert summary.total_records == 3
    assert summary.pending == 1
    assert summary.approved == 1
    assert summary.rejected == 1


def test_clear_audit_removes_all_records():
    record_approval_audit(_approval())

    assert get_approval_audit_summary().total_records == 1

    clear_approval_audit()

    assert get_approval_audit_summary().total_records == 0
    assert get_approval_audit_records() == []
