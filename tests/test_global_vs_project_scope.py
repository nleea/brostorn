from __future__ import annotations

import json
from pathlib import Path

from memory_core.workspace import MemoryWorkspace


def test_global_and_project_memory_remain_separate(tmp_path: Path) -> None:
    (tmp_path / "system").mkdir(parents=True, exist_ok=True)
    (tmp_path / "contexts").mkdir(parents=True, exist_ok=True)
    project_dir = tmp_path / "projects" / "gym-trainer"
    (project_dir / "docs").mkdir(parents=True, exist_ok=True)
    (project_dir / "contexts").mkdir(parents=True, exist_ok=True)
    (project_dir / "project.config.json").write_text(
        json.dumps(
            {
                "project_name": "gym-trainer",
                "note_project": "fitness-app",
                "workspace": {"frontend_path": "../../gym-trainer-client"},
                "memory": {"docs_path": "./docs"},
            }
        ),
        encoding="utf-8",
    )

    workspace = MemoryWorkspace(root_path=tmp_path, active_project_name="gym-trainer")
    roots = {workspace.to_relative(path) for path in workspace.iter_index_roots()}

    assert "system" in roots
    assert "contexts" in roots
    assert "projects/gym-trainer/docs" in roots
    assert "projects/gym-trainer/contexts" in roots
    assert "projects/gym-trainer" not in roots
