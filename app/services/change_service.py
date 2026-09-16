import json
from pathlib import Path

from app.models.changes import ChangeRequest, ChangeStatus


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "changes.json"
)


def load_changes() -> list[ChangeRequest]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    return [
        ChangeRequest.model_validate(record)
        for record in records
    ]


def get_changes() -> list[ChangeRequest]:
    return load_changes()


def get_change(change_id: str) -> ChangeRequest | None:
    changes = load_changes()

    return next(
        (
            change
            for change in changes
            if change.change_id == change_id
        ),
        None,
    )


def get_change_summary() -> dict:
    changes = load_changes()

    active_changes = [
        change
        for change in changes
        if change.status not in {
            ChangeStatus.COMPLETED,
            ChangeStatus.REJECTED,
        }
    ]

    pending_approval = sum(
        1
        for change in active_changes
        if change.status == ChangeStatus.PENDING_APPROVAL
    )

    implementing = sum(
        1
        for change in active_changes
        if change.status == ChangeStatus.IMPLEMENTING
    )

    validation = sum(
        1
        for change in active_changes
        if change.status == ChangeStatus.VALIDATING
    )

    if any(change.priority.value == "P1" for change in active_changes):
        operational_status = "Critical"
    elif any(change.priority.value == "P2" for change in active_changes):
        operational_status = "High"
    elif active_changes:
        operational_status = "Medium"
    else:
        operational_status = "Green"

    return {
        "operational_status": operational_status,
        "total_changes": len(changes),
        "active_changes": len(active_changes),
        "pending_approval": pending_approval,
        "implementing": implementing,
        "validation": validation,
        "completed_changes": sum(
            1
            for change in changes
            if change.status == ChangeStatus.COMPLETED
        ),
        "approval_required": sum(
            1
            for change in changes
            if change.approval_required
        ),
        "affected_workstreams": sorted(
            {
                change.affected_workstream
                for change in active_changes
                if change.affected_workstream
            }
        ),
    }
