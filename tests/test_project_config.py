from __future__ import annotations

import pytest

from memory_core.workspace import ProjectConfig


def test_valid_project_config_loads_correctly() -> None:
    config = ProjectConfig.model_validate(
        {
            "project_name": "gym-trainer",
            "note_project": "fitness-app",
            "workspace": {"frontend_path": "../../gym-trainer-client"},
            "memory": {"docs_path": "./docs", "debugging_notes": "./docs/11-debugging"},
            "modules": ["auth", "calendar", "auth"],
            "entry_points": {"router": "gym-trainer-client/src/router/index.ts"},
            "rules": {"load_distilled_context_first": True},
        }
    )

    assert config.project_name == "gym-trainer"
    assert config.note_project == "fitness-app"
    assert config.modules == ["auth", "calendar"]
    assert config.rules.load_distilled_context_first is True


def test_missing_required_project_name_fails_clearly() -> None:
    with pytest.raises(Exception):
        ProjectConfig.model_validate({"workspace": {"frontend_path": "../../gym-trainer-client"}})


def test_optional_fields_are_tolerated() -> None:
    config = ProjectConfig.model_validate({"project_name": "memory-system"})
    assert config.workspace == {}
    assert config.memory == {}
    assert config.modules == []


def test_absolute_paths_are_rejected_for_portability() -> None:
    with pytest.raises(Exception):
        ProjectConfig.model_validate(
            {
                "project_name": "gym-trainer",
                "workspace": {"frontend_path": "/Users/foo/project"},
            }
        )
