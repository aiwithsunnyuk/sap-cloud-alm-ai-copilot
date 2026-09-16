import json
from pathlib import Path

from app.models.deployments import (
    Deployment,
    DeploymentStatus,
    ValidationStatus,
)


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "deployments.json"
)


def load_deployments() -> list[Deployment]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    return [
        Deployment.model_validate(record)
        for record in records
    ]


def get_deployments() -> list[Deployment]:
    return load_deployments()


def get_deployment(deployment_id: str) -> Deployment | None:
    deployments = load_deployments()

    return next(
        (
            deployment
            for deployment in deployments
            if deployment.deployment_id == deployment_id
        ),
        None,
    )


def get_deployment_summary() -> dict:
    deployments = load_deployments()

    return {
        "total_deployments": len(deployments),
        "successful_deployments": sum(
            1
            for deployment in deployments
            if deployment.deployment_status
            == DeploymentStatus.SUCCESSFUL
        ),
        "failed_deployments": sum(
            1
            for deployment in deployments
            if deployment.deployment_status
            == DeploymentStatus.FAILED
        ),
        "rolled_back_deployments": sum(
            1
            for deployment in deployments
            if deployment.deployment_status
            == DeploymentStatus.ROLLED_BACK
        ),
        "passed_validations": sum(
            1
            for deployment in deployments
            if deployment.validation_status
            == ValidationStatus.PASSED
        ),
        "failed_validations": sum(
            1
            for deployment in deployments
            if deployment.validation_status
            == ValidationStatus.FAILED
        ),
        "rollback_required": sum(
            1
            for deployment in deployments
            if deployment.rollback_required
        ),
        "affected_environments": sorted(
            {
                deployment.environment
                for deployment in deployments
            }
        ),
    }
