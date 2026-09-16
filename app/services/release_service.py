import json
from pathlib import Path

from app.models.releases import Release, ReleaseStatus


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "releases.json"
)


def load_releases() -> list[Release]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    return [
        Release.model_validate(record)
        for record in records
    ]


def get_releases() -> list[Release]:
    return load_releases()


def get_release(release_id: str) -> Release | None:
    releases = load_releases()

    return next(
        (
            release
            for release in releases
            if release.release_id == release_id
        ),
        None,
    )


def get_release_summary() -> dict:
    releases = load_releases()

    active_releases = [
        release
        for release in releases
        if release.status not in {
            ReleaseStatus.COMPLETED,
            ReleaseStatus.FAILED,
            ReleaseStatus.ROLLED_BACK,
        }
    ]

    return {
        "total_releases": len(releases),
        "active_releases": len(active_releases),
        "planned_releases": sum(
            1
            for release in active_releases
            if release.status == ReleaseStatus.PLANNED
        ),
        "ready_releases": sum(
            1
            for release in active_releases
            if release.status == ReleaseStatus.READY
        ),
        "deploying_releases": sum(
            1
            for release in active_releases
            if release.status == ReleaseStatus.DEPLOYING
        ),
        "validating_releases": sum(
            1
            for release in active_releases
            if release.status == ReleaseStatus.VALIDATING
        ),
        "completed_releases": sum(
            1
            for release in releases
            if release.status == ReleaseStatus.COMPLETED
        ),
        "successful_deployments": sum(
            1
            for release in releases
            if release.deployment_status.value == "Successful"
        ),
        "affected_environments": sorted(
            {
                release.environment
                for release in active_releases
            }
        ),
    }
