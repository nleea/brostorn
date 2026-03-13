from __future__ import annotations

import json
from pathlib import Path

from hooks.session_end import build_session_end_payload
from hooks.session_start import build_session_start_payload
from memory_core.workspace import MemoryWorkspace, ProjectConfig


def _project_fixture(tmp_path: Path) -> Path:
    project_dir = tmp_path / "projects" / "gym-trainer"
    (project_dir / "docs" / "00-index").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "00-index" / "index.md").write_text("# Index\n", encoding="utf-8")
    (project_dir / "docs" / "AGENT_GUIDE.md").write_text("# Guide\n", encoding="utf-8")
    (project_dir / "project.config.json").write_text(
        json.dumps(
            {
                "project_name": "gym-trainer",
                "note_project": "fitness-app",
                "workspace": {"frontend_path": "../../gym-trainer-client"},
                "memory": {
                    "docs_path": "./docs",
                    "distilled_context": "./docs/distilled",
                    "debugging_notes": "./docs/debugging",
                    "session_memory": "./docs/sessions"
                },
                "modules": ["auth", "calendar"],
            }
        ),
        encoding="utf-8",
    )
    return project_dir


def test_project_config_schema_files_exist_and_parse() -> None:
    schema_root = Path(__file__).resolve().parents[1] / "schemas"
    expected = {
        "project.config.schema.json",
        "debug-note.schema.json",
        "session-summary.schema.json",
        "distilled-context.schema.json",
        "context-pack.schema.json",
        "context-template.schema.json",
    }
    actual = {path.name for path in schema_root.glob("*.json")}
    assert expected.issubset(actual)
    for name in expected:
        parsed = json.loads((schema_root / name).read_text(encoding="utf-8"))
        assert parsed["$schema"].startswith("https://json-schema.org/")


def test_project_config_loading_uses_current_contract(tmp_path: Path) -> None:
    project_dir = _project_fixture(tmp_path)
    config = ProjectConfig.model_validate_json((project_dir / "project.config.json").read_text(encoding="utf-8"))
    assert config.project_name == "gym-trainer"
    assert config.note_project == "fitness-app"
    assert config.modules == ["auth", "calendar"]


def test_global_and_project_memory_stay_separate(tmp_path: Path) -> None:
    (tmp_path / "system" / "00-index").mkdir(parents=True, exist_ok=True)
    (tmp_path / "system" / "AGENT_GUIDE.md").write_text("# System\n", encoding="utf-8")
    (tmp_path / "contexts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "contexts" / "debug-auth.md").write_text("# Debug Auth\n", encoding="utf-8")
    _project_fixture(tmp_path)
    (tmp_path / "projects" / "gym-trainer" / "contexts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "projects" / "gym-trainer" / "contexts" / "debug-calendar.md").write_text(
        "# Project Debug Calendar\n",
        encoding="utf-8",
    )

    workspace = MemoryWorkspace(root_path=tmp_path, active_project_name="gym-trainer")
    roots = {workspace.to_relative(path) for path in workspace.iter_index_roots()}

    assert "system" in roots
    assert "contexts" in roots
    assert "projects/gym-trainer/docs" in roots
    assert "projects/gym-trainer/contexts" in roots
    assert "projects/gym-trainer" not in roots


def test_session_start_hook_suggests_project_and_contexts(tmp_path: Path) -> None:
    (tmp_path / "system" / "00-index").mkdir(parents=True, exist_ok=True)
    (tmp_path / "system" / "AGENT_GUIDE.md").write_text("# System\n", encoding="utf-8")
    (tmp_path / "system" / "00-index" / "system-index.md").write_text("# Index\n", encoding="utf-8")
    (tmp_path / "system" / "00-index" / "engineering-brain-index.md").write_text("# Brain\n", encoding="utf-8")
    (tmp_path / "contexts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "contexts" / "debug-auth.md").write_text(
        "---\nkeywords: [auth, login, redirect]\npriority: 2\n---\n\n# Debug Auth\n",
        encoding="utf-8",
    )
    project_dir = _project_fixture(tmp_path)

    payload = build_session_start_payload(
        workspace_root=tmp_path,
        task="debug auth redirect after login",
        cwd=(project_dir / "../../gym-trainer-client").resolve(),
    )

    assert payload["active_project"] == "gym-trainer"
    assert payload["project_key"] == "fitness-app"
    assert "contexts/debug-auth.md" in payload["context_templates"]


def test_session_start_hook_includes_project_contexts_when_available(tmp_path: Path) -> None:
    (tmp_path / "system" / "00-index").mkdir(parents=True, exist_ok=True)
    (tmp_path / "system" / "AGENT_GUIDE.md").write_text("# System\n", encoding="utf-8")
    (tmp_path / "system" / "00-index" / "system-index.md").write_text("# Index\n", encoding="utf-8")
    (tmp_path / "system" / "00-index" / "engineering-brain-index.md").write_text("# Brain\n", encoding="utf-8")
    (tmp_path / "contexts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "contexts" / "debug-calendar.md").write_text(
        "---\nkeywords: [calendar, meals, completion]\npriority: 3\n---\n\n# Debug Calendar\n",
        encoding="utf-8",
    )
    project_dir = _project_fixture(tmp_path)
    (project_dir / "contexts").mkdir(parents=True, exist_ok=True)
    (project_dir / "contexts" / "debug-calendar.md").write_text(
        "---\nkeywords: [calendar, completion]\npriority: 4\n---\n\n# Project Debug Calendar\n",
        encoding="utf-8",
    )
    (project_dir / "contexts" / "debug-meals.md").write_text(
        "---\nkeywords: [meals, meal_key, completion]\npriority: 4\n---\n\n# Project Debug Meals\n",
        encoding="utf-8",
    )

    payload = build_session_start_payload(
        workspace_root=tmp_path,
        task="debug why meals are not marked as completed in the calendar",
        cwd=(project_dir / "../../gym-trainer-client").resolve(),
    )

    assert "contexts/debug-calendar.md" in payload["context_templates"]
    assert "projects/gym-trainer/contexts/debug-calendar.md" in payload["context_templates"]
    assert "projects/gym-trainer/contexts/debug-meals.md" in payload["context_templates"]


def test_session_end_hook_flags_debug_and_learning_follow_ups(tmp_path: Path) -> None:
    _project_fixture(tmp_path)

    payload = build_session_end_payload(
        workspace_root=tmp_path,
        task="Fix auth redirect regression",
        project="gym-trainer",
        debug_status="verified",
        validation_performed=True,
        reusable_learning=False,
        files_modified=["apps/mcp_server/main.py"],
    )

    assert payload["should_save_debug_note"] is True
    assert payload["should_save_session_summary"] is True
    assert payload["should_promote_learning"] is True
    assert payload["suggested_cross_project_path"] == "system/cross-project"
