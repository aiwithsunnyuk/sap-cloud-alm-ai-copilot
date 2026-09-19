from app.models.copilot_approval import CopilotApprovalResult
from app.models.copilot_approval_audit import (
    CopilotApprovalAuditRecord,
    CopilotApprovalAuditSummary,
)


_AUDIT_RECORDS: list[CopilotApprovalAuditRecord] = []


def record_approval_audit(
    approval: CopilotApprovalResult,
) -> CopilotApprovalAuditRecord:
    audit_id = f"AUD-{len(_AUDIT_RECORDS) + 1:03d}"

    record = CopilotApprovalAuditRecord(
        audit_id=audit_id,
        decision_id=approval.decision_id,
        status=approval.status,
        approval_required=approval.approval_required,
        allowed_to_proceed=approval.allowed_to_proceed,
        approver=approval.approver,
        approval_comment=approval.approval_comment,
        rationale=approval.rationale,
        trace=[
            "Approval Result",
            "Audit Record Created",
        ],
    )

    _AUDIT_RECORDS.append(record)
    return record


def get_approval_audit_records() -> list[CopilotApprovalAuditRecord]:
    return list(_AUDIT_RECORDS)


def get_approval_audit_record(
    audit_id: str,
) -> CopilotApprovalAuditRecord | None:
    for record in _AUDIT_RECORDS:
        if record.audit_id == audit_id:
            return record
    return None


def get_approval_audit_summary() -> CopilotApprovalAuditSummary:
    pending = 0
    approved = 0
    rejected = 0

    for record in _AUDIT_RECORDS:
        if record.status.value == "pending":
            pending += 1
        elif record.status.value == "approved":
            approved += 1
        elif record.status.value == "rejected":
            rejected += 1

    return CopilotApprovalAuditSummary(
        total_records=len(_AUDIT_RECORDS),
        pending=pending,
        approved=approved,
        rejected=rejected,
    )


def clear_approval_audit() -> None:
    _AUDIT_RECORDS.clear()
