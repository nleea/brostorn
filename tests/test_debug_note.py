from __future__ import annotations

import pytest

from memory_core.schemas import DebugNoteSaveRequest


def test_debug_note_accepts_validation_aware_statuses() -> None:
    payload = DebugNoteSaveRequest.model_validate(
        {
            "title": "Calendar Meals",
            "summary": "Meals not marked completed.",
            "project": "fitness-app",
            "status": "verified",
        }
    )

    assert payload.status == "verified"


def test_debug_note_rejects_invalid_status() -> None:
    with pytest.raises(Exception):
        DebugNoteSaveRequest.model_validate(
            {
                "title": "Calendar Meals",
                "summary": "Meals not marked completed.",
                "project": "fitness-app",
                "status": "done",
            }
        )


def test_debug_note_supports_extended_fields() -> None:
    payload = DebugNoteSaveRequest.model_validate(
        {
            "title": "Calendar Meals",
            "summary": "Meals not marked completed.",
            "project": "fitness-app",
            "module": "calendar",
            "symptom": "Meals stayed uncompleted in UI.",
            "solution": "Use meal_key and full history.",
            "files_changed": ["vue/views/client/TrainingView.vue"],
            "follow_ups": ["Add regression test"],
            "updated_at": "2026-03-11",
        }
    )

    assert payload.module == "calendar"
    assert payload.files_changed == ["vue/views/client/TrainingView.vue"]
