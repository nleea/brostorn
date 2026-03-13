from __future__ import annotations

import json
from pathlib import Path

import pytest

from memory_core.note_writer import (
    NoteWriterService,
    build_debug_note_markdown,
    build_reusable_learning_markdown,
    build_session_summary_markdown,
)
from memory_core.workspace import MemoryWorkspace


class DummyIndexer:
    def __init__(self) -> None:
        self.indexed_paths: list[str] = []

    async def index_relative_path(self, db, relative_path: str) -> bool:
        self.indexed_paths.append(relative_path)
        return True


def _build_workspace(tmp_path: Path) -> MemoryWorkspace:
    project_dir = tmp_path / "projects" / "gym-trainer"
    (project_dir / "docs").mkdir(parents=True, exist_ok=True)
    (project_dir / "project.config.json").write_text(
        json.dumps(
            {
                "project_name": "gym-trainer",
                "note_project": "fitness-app",
                "workspace": {"backend_path": "../../trainerGM"},
                "memory": {
                    "docs_path": "./docs",
                    "debugging_notes": "./docs/11-debugging",
                    "session_memory": "./docs/15-session-memory",
                },
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "system" / "05-cross-project-memory").mkdir(parents=True, exist_ok=True)
    return MemoryWorkspace(root_path=tmp_path, active_project_name="gym-trainer")


def test_build_debug_note_markdown_tracks_validation_status() -> None:
    markdown = build_debug_note_markdown(
        title="Auth Regression",
        summary="Auth fails after refresh.",
        module="auth",
        symptom="Refresh deja auth inconsistente.",
        root_cause="Stale store state.",
        solution="Reset store on refresh.",
        fix="Reset store on refresh.",
        files_changed=["projects/gym-trainer/docs/04-frontend/router.md"],
        validation="Manual auth flow checks.",
        status="verified",
        validation_steps=["Login", "Refresh", "Protected route"],
        validation_evidence=["Observed correct redirect after refresh."],
        follow_ups=["Add auth refresh regression test."],
        updated_at="2026-03-11",
        project="fitness-app",
        tags=["fitness-app", "debugging"],
        related_paths=["projects/gym-trainer/docs/04-frontend/router.md"],
    )

    assert "status: verified" in markdown
    assert "## Status" in markdown
    assert "## Symptom" in markdown
    assert "## Solution" in markdown
    assert "## Files Changed" in markdown
    assert "## Validation Steps" in markdown
    assert "## Validation Evidence" in markdown


def test_build_reusable_learning_markdown_includes_cross_project_sections() -> None:
    markdown = build_reusable_learning_markdown(
        title="Avoid Stale Auth Caches",
        summary="Reset auth stores before redirecting.",
        project="fitness-app",
        tags=["cross-project-memory"],
        category="reusable-solutions",
        lesson="Store reset ordering matters.",
        applicability="Any client app with route guards.",
        source_paths=["projects/gym-trainer/docs/11-debugging/logout-not-redirecting.md"],
        validation="Verified on login and logout flows.",
    )

    assert "type: cross_project_learning" in markdown
    assert "## Applicability" in markdown
    assert "[[projects/gym-trainer/docs/11-debugging/logout-not-redirecting]]" in markdown


@pytest.mark.asyncio
async def test_save_debug_note_writes_project_scoped_file(tmp_path: Path) -> None:
    workspace = _build_workspace(tmp_path)
    indexer = DummyIndexer()
    writer = NoteWriterService(workspace=workspace, indexer=indexer)

    payload = await writer.save_debug_note(
        db=None,
        title="Auth Regression",
        summary="Auth fails after refresh.",
        project="gym-trainer",
        module="auth",
        symptom="Refresh deja auth inconsistente.",
        solution="Reset store on refresh.",
        files_changed=["packages/memory_core/note_writer.py"],
        status="fixed",
        validation_steps=["Login", "Refresh"],
        validation_evidence=["Refresh returned 200."],
        follow_ups=["Add auth regression test."],
        updated_at="2026-03-11",
    )

    output_path = tmp_path / payload["path"]
    assert payload["debug_status"] == "fixed"
    assert output_path.exists()
    assert "projects/gym-trainer/docs/11-debugging" in payload["path"]
    assert indexer.indexed_paths == [payload["path"]]
    content = output_path.read_text(encoding="utf-8")
    assert "status: fixed" in content
    assert "updated_at: '2026-03-11'" in content


@pytest.mark.asyncio
async def test_save_session_summary_writes_project_session_memory(tmp_path: Path) -> None:
    workspace = _build_workspace(tmp_path)
    indexer = DummyIndexer()
    writer = NoteWriterService(workspace=workspace, indexer=indexer)

    payload = await writer.save_session_summary(
        db=None,
        task="Trace auth refresh issue",
        project="gym-trainer",
        findings=["Refresh flow read stale auth state."],
        files_modified=["packages/memory_core/note_writer.py"],
        session_date="2026-03-11",
    )

    output_path = tmp_path / payload["path"]
    assert output_path.exists()
    assert "projects/gym-trainer/docs/15-session-memory" in payload["path"]
    content = output_path.read_text(encoding="utf-8")
    assert "session_date: '2026-03-11'" in content
    assert "## Findings" in content


@pytest.mark.asyncio
async def test_save_reusable_learning_writes_system_memory(tmp_path: Path) -> None:
    workspace = _build_workspace(tmp_path)
    indexer = DummyIndexer()
    writer = NoteWriterService(workspace=workspace, indexer=indexer)

    payload = await writer.save_reusable_learning(
        db=None,
        title="Auth Store Reset Ordering",
        summary="Reset auth state before navigation to avoid stale guard checks.",
        project="gym-trainer",
        category="architecture-lessons",
        source_paths=["projects/gym-trainer/docs/11-debugging/auth-regression.md"],
    )

    output_path = tmp_path / payload["path"]
    assert output_path.exists()
    assert payload["category"] == "architecture-lessons"
    assert payload["path"].startswith("system/05-cross-project-memory")
