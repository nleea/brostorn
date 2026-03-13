from __future__ import annotations

from memory_core.schemas import ContextPackResponse


def test_context_pack_response_shape_is_stable() -> None:
    payload = ContextPackResponse.model_validate(
        {
            "task": "debug calendar meals",
            "pack_name": "calendar",
            "description": "Calendar debugging",
            "matched_keywords": ["calendar", "meals"],
            "project": "gym-trainer",
            "project_key": "fitness-app",
            "active_project": "gym-trainer",
            "system_notes": [],
            "project_config_note": None,
            "project_index_notes": [],
            "global_contexts": [],
            "project_contexts": [],
            "distilled_note": None,
            "supporting_notes": [],
            "notes": [],
            "fallback_used": False,
        }
    )

    assert payload.pack_name == "calendar"
    assert payload.global_contexts == []
    assert payload.project_contexts == []
