from __future__ import annotations

from memory_core.note_writer import build_session_summary_markdown
from memory_core.schemas import SessionSummarySaveRequest


def test_session_summary_accepts_stable_fields() -> None:
    payload = SessionSummarySaveRequest.model_validate(
        {
            "task": "Debug calendar meals",
            "project": "fitness-app",
            "context_pack": "calendar",
            "context_note_paths": ["contexts/debug-calendar.md"],
            "findings": ["UI used stale meal completion state."],
            "files_modified": ["packages/memory_core/context_pack_service.py"],
            "validation": "pytest",
            "follow_ups": ["Add regression test"],
            "session_date": "2026-03-11",
        }
    )

    assert payload.session_date == "2026-03-11"


def test_session_summary_markdown_keeps_required_sections() -> None:
    markdown = build_session_summary_markdown(
        task="Debug calendar meals",
        project="fitness-app",
        tags=["fitness-app", "session-memory"],
        context_pack="calendar",
        context_note_paths=["contexts/debug-calendar.md"],
        findings=["UI used stale meal completion state."],
        files_modified=["packages/memory_core/context_pack_service.py"],
        validation="pytest",
        follow_ups=["Add regression test"],
        session_date="2026-03-11",
    )

    assert "## Task" in markdown
    assert "## Context Loaded" in markdown
    assert "## Findings" in markdown
    assert "## Files Modified" in markdown
    assert "## Validation" in markdown
    assert "## Follow Ups" in markdown
