import json
from pathlib import Path

from app.models.problems import Problem, ProblemStatus


DATA_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "problems.json"
)


def load_problems() -> list[Problem]:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    return [
        Problem.model_validate(record)
        for record in records
    ]


def get_problems() -> list[Problem]:
    return load_problems()


def get_problem(problem_id: str) -> Problem | None:
    problems = load_problems()

    return next(
        (
            problem
            for problem in problems
            if problem.problem_id == problem_id
        ),
        None,
    )


def get_problem_summary() -> dict:
    problems = load_problems()

    active_problems = [
        problem
        for problem in problems
        if problem.status not in {
            ProblemStatus.RESOLVED,
            ProblemStatus.CLOSED,
        }
    ]

    root_cause_identified = sum(
        1
        for problem in problems
        if problem.root_cause
    )

    unresolved_root_causes = sum(
        1
        for problem in active_problems
        if not problem.root_cause
    )

    if any(
        problem.priority.value == "P1"
        for problem in active_problems
    ):
        operational_status = "Critical"
    elif any(
        problem.priority.value == "P2"
        for problem in active_problems
    ):
        operational_status = "High"
    elif active_problems:
        operational_status = "Medium"
    else:
        operational_status = "Green"

    return {
        "operational_status": operational_status,
        "total_problems": len(problems),
        "active_problems": len(active_problems),
        "root_cause_identified": root_cause_identified,
        "unresolved_root_causes": unresolved_root_causes,
        "resolved_problems": sum(
            1
            for problem in problems
            if problem.status == ProblemStatus.RESOLVED
        ),
        "affected_workstreams": sorted(
            {
                problem.affected_workstream
                for problem in active_problems
                if problem.affected_workstream
            }
        ),
    }
