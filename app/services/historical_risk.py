import json
from datetime import date
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[2]
HISTORY_FILE = BASE_DIR / "data" / "risk_history.json"


def load_risk_history() -> list[dict[str, Any]]:
    """Load historical risk snapshots from the demo dataset."""
    with HISTORY_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_task_history(task_id: str) -> list[dict[str, Any]]:
    """Return chronological risk history for a task."""
    history = [
        snapshot
        for snapshot in load_risk_history()
        if snapshot["task_id"] == task_id
    ]

    return sorted(
        history,
        key=lambda snapshot: date.fromisoformat(snapshot["snapshot_date"]),
    )
