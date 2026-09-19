from datetime import date
from typing import Any

from app.services.calm_task_adapter import map_sap_task_to_internal
from app.services.risk_engine import calculate_risk_score


def evaluate_sap_task_risk(
    sap_task: dict[str, Any],
    *,
    dependencies: list[dict[str, Any]] | None = None,
    risks: list[dict[str, Any]] | None = None,
    as_of_date: date | None = None,
    priority_map: dict[int, str] | None = None,
    status_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Map a SAP Cloud ALM task into the internal task contract,
    then evaluate it with the existing deterministic risk engine.
    """
    internal_task = map_sap_task_to_internal(
        sap_task,
        priority_map=priority_map,
        status_map=status_map,
    )

    assessment = calculate_risk_score(
        task=internal_task,
        dependencies=dependencies or [],
        risks=risks or [],
        as_of_date=as_of_date,
    )

    return {
        "source": "sap_cloud_alm",
        "task": internal_task,
        "risk": assessment,
    }
