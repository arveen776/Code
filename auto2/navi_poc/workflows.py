import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional

WORKFLOWS_PATH = Path(__file__).parent / "data" / "workflows.json"

Workflow = Dict[str, object]


def load_workflows() -> List[Workflow]:
    WORKFLOWS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not WORKFLOWS_PATH.exists():
        WORKFLOWS_PATH.write_text("[]", encoding="utf-8")

    try:
        return json.loads(WORKFLOWS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        backup = WORKFLOWS_PATH.with_suffix(".corrupt.json")
        WORKFLOWS_PATH.rename(backup)
        WORKFLOWS_PATH.write_text("[]", encoding="utf-8")
        print(f"Corrupt workflows file. Backup saved to {backup}")
        return []


def save_workflows(workflows: List[Workflow]) -> None:
    WORKFLOWS_PATH.write_text(json.dumps(workflows, indent=2), encoding="utf-8")


def add_workflow(name: str, description: str, events: List[dict]) -> Workflow:
    workflow = {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "description": description.strip(),
        "events": events,
    }
    workflows = load_workflows()
    workflows.append(workflow)
    save_workflows(workflows)
    return workflow


def find_best_workflow(command: str, workflows: List[Workflow]) -> Optional[Workflow]:
    command_words = _tokenize(command)
    best: Optional[Workflow] = None
    best_score = -1

    for workflow in workflows:
        description = workflow.get("description", "")
        desc_words = _tokenize(description)
        score = len(command_words & desc_words)
        if score > best_score:
            best_score = score
            best = workflow

    return best


def _tokenize(text: str) -> set[str]:
    return {word for word in text.lower().split() if word}

