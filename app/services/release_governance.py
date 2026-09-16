from app.models.changes import ChangeStatus
from app.models.releases import ReleaseStatus
from app.services.change_service import get_change
from app.services.release_service import get_release


def validate_release_governance(release_id: str) -> dict:
    release = get_release(release_id)

    if release is None:
        return {
            "release_id": release_id,
            "eligible": False,
            "reason": f"Release not found: {release_id}",
            "change_status": None,
            "release_status": None,
        }

    change = get_change(release.change_id)

    if change is None:
        return {
            "release_id": release_id,
            "eligible": False,
            "reason": (
                f"Associated change not found: {release.change_id}"
            ),
            "change_status": None,
            "release_status": release.status.value,
        }

    change_status = change.status
    release_status = release.status

    if release_status in {
        ReleaseStatus.COMPLETED,
        ReleaseStatus.FAILED,
        ReleaseStatus.ROLLED_BACK,
    }:
        if (
            release_status == ReleaseStatus.COMPLETED
            and change_status == ChangeStatus.COMPLETED
        ):
            return {
                "release_id": release_id,
                "eligible": True,
                "reason": "Release and associated change are completed.",
                "change_status": change_status.value,
                "release_status": release_status.value,
            }

        if release_status == ReleaseStatus.ROLLED_BACK:
            return {
                "release_id": release_id,
                "eligible": False,
                "reason": "Release has been rolled back.",
                "change_status": change_status.value,
                "release_status": release_status.value,
            }

        return {
            "release_id": release_id,
            "eligible": False,
            "reason": (
                "Release is in a terminal state that does not permit "
                "new implementation activity."
            ),
            "change_status": change_status.value,
            "release_status": release_status.value,
        }

    if change_status != ChangeStatus.APPROVED:
        return {
            "release_id": release_id,
            "eligible": False,
            "reason": (
                f"Associated change {change.change_id} is "
                f"{change_status.value}. "
                "Release implementation requires an approved change."
            ),
            "change_status": change_status.value,
            "release_status": release_status.value,
        }

    return {
        "release_id": release_id,
        "eligible": True,
        "reason": (
            f"Associated change {change.change_id} is approved "
            "and the release is eligible to proceed."
        ),
        "change_status": change_status.value,
        "release_status": release_status.value,
    }
