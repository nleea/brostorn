from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from memory_core.context_pack_service import ContextPackService
from memory_core.context_packs import (
    GENERAL_PACK,
    ContextTemplateDescriptor,
    infer_context_pack,
    match_context_descriptors,
    match_context_paths,
)
from memory_core.note_writer import build_debug_note_markdown, build_session_summary_markdown, slugify
from memory_core.schemas import SearchResponse, SearchResultItem
from memory_core.workspace import MemoryWorkspace


def test_infer_auth_context_pack() -> None:
    pack, matched = infer_context_pack("arregla el logout login auth session router pinia")
    assert pack.name == "auth"
    assert "logout" in matched
    assert "router" in matched


def test_infer_deployment_context_pack() -> None:
    pack, matched = infer_context_pack("analiza docker deployment y cloudflare monitoring")
    assert pack.name == "deployment"
    assert "docker" in matched


def test_infer_general_context_pack_when_no_keywords() -> None:
    pack, matched = infer_context_pack("explora el contexto general del proyecto")
    assert pack == GENERAL_PACK
    assert matched == []


def test_infer_calendar_pack_for_calendar_meals_debug_task() -> None:
    pack, matched = infer_context_pack("debug why meals are not marked as completed in the calendar")
    assert pack.name == "calendar"
    assert "calendar" in matched


def test_match_context_paths_for_realistic_calendar_meals_task() -> None:
    matches = match_context_paths(
        "Debug why meals are not marked as completed in the calendar",
        [
            "contexts/debug-auth.md",
            "contexts/debug-calendar.md",
            "contexts/debug-state-management.md",
            "projects/gym-trainer/contexts/debug-calendar.md",
            "projects/gym-trainer/contexts/debug-meals.md",
        ],
        modules=["calendar", "meals"],
    )

    assert "contexts/debug-calendar.md" in matches
    assert "projects/gym-trainer/contexts/debug-calendar.md" in matches
    assert "projects/gym-trainer/contexts/debug-meals.md" in matches


def test_match_context_descriptors_prefers_metadata_ranked_contexts() -> None:
    matches = match_context_descriptors(
        "Debug why meals are not marked as completed in the calendar",
        [
            ContextTemplateDescriptor(
                path="contexts/debug-auth.md",
                metadata={"keywords": ["auth", "login"], "priority": 1},
            ),
            ContextTemplateDescriptor(
                path="contexts/debug-calendar.md",
                metadata={
                    "keywords": ["calendar", "completion", "meals"],
                    "applies_to": ["calendar", "meals"],
                    "related_distilled": ["calendar", "meals"],
                    "priority": 3,
                },
            ),
            ContextTemplateDescriptor(
                path="projects/gym-trainer/contexts/debug-meals.md",
                metadata={
                    "keywords": ["meals", "meal_key", "completion"],
                    "applies_to": ["meals", "calendar"],
                    "related_distilled": ["meals", "calendar"],
                    "priority": 4,
                },
            ),
        ],
        modules=["calendar", "meals"],
    )

    assert matches[0].path == "projects/gym-trainer/contexts/debug-meals.md"
    assert matches[1].path == "contexts/debug-calendar.md"


def test_slugify_normalizes_titles() -> None:
    assert slugify("Logout / Login Fix!!") == "logout-login-fix"


def test_build_debug_note_markdown_includes_expected_sections() -> None:
    markdown = build_debug_note_markdown(
        title="Logout Not Redirecting",
        summary="Resumen corto.",
        module="auth",
        symptom="Logout deja la sesion en estado inconsistente.",
        root_cause="Carrera entre logout y router.",
        solution="Limpiar sesion antes de navegar.",
        fix="Limpiar sesion antes de navegar.",
        files_changed=["04-frontend/logout-flow.md"],
        validation="Logout y login validados.",
        status="verified",
        validation_steps=["Logout", "Login"],
        validation_evidence=["La redireccion ocurre despues del logout."],
        follow_ups=["Agregar prueba de router guard."],
        updated_at="2026-03-11",
        project="fitness-app",
        tags=["fitness-app", "debugging"],
        related_paths=["04-frontend/logout-flow.md"],
    )

    assert "type: bug_fix" in markdown
    assert "# Logout Not Redirecting" in markdown
    assert "## Root Cause" in markdown
    assert "[[04-frontend/logout-flow]]" in markdown


def test_build_session_summary_markdown_includes_expected_sections() -> None:
    markdown = build_session_summary_markdown(
        task="Implement distilled context support",
        project="memory-system",
        tags=["memory-system", "session-memory"],
        context_pack="database",
        context_note_paths=["20-distilled-context/database.md", "05-database/schema.md"],
        findings=["Distilled notes should come from the vault first."],
        files_modified=["packages/memory_core/context_pack_service.py"],
        validation="pytest -q",
        follow_ups=["Add more distilled modules as the vault grows."],
        session_date="2026-03-11",
    )

    assert "type: session_summary" in markdown
    assert "## Context Loaded" in markdown
    assert "`database`" in markdown
    assert "[[20-distilled-context/database]]" in markdown
    assert "## Files Modified" in markdown
    assert "context_note_paths:" in markdown


def test_workspace_discovers_global_and_project_context_paths(tmp_path: Path) -> None:
    (tmp_path / "contexts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "contexts" / "debug-auth.md").write_text("# Debug Auth\n", encoding="utf-8")
    project_dir = tmp_path / "projects" / "gym-trainer"
    (project_dir / "docs").mkdir(parents=True, exist_ok=True)
    (project_dir / "contexts").mkdir(parents=True, exist_ok=True)
    (project_dir / "contexts" / "debug-calendar.md").write_text("# Debug Calendar\n", encoding="utf-8")
    (project_dir / "project.config.json").write_text(
        """
        {
          "project_name": "gym-trainer",
          "note_project": "fitness-app",
          "workspace": {"frontend_path": "../client"},
          "memory": {"docs_path": "./docs"}
        }
        """.strip(),
        encoding="utf-8",
    )

    workspace = MemoryWorkspace(root_path=tmp_path, active_project_name="gym-trainer")
    project = workspace.resolve_active_project()

    assert workspace.global_context_paths() == ["contexts/debug-auth.md"]
    assert workspace.project_context_paths(project) == ["projects/gym-trainer/contexts/debug-calendar.md"]


def test_workspace_handles_missing_project_context_directory(tmp_path: Path) -> None:
    project_dir = tmp_path / "projects" / "gym-trainer"
    (project_dir / "docs").mkdir(parents=True, exist_ok=True)
    (project_dir / "project.config.json").write_text(
        """
        {
          "project_name": "gym-trainer",
          "note_project": "fitness-app",
          "workspace": {"frontend_path": "../client"},
          "memory": {"docs_path": "./docs"}
        }
        """.strip(),
        encoding="utf-8",
    )

    workspace = MemoryWorkspace(root_path=tmp_path, active_project_name="gym-trainer")
    project = workspace.resolve_active_project()

    assert project is not None
    assert workspace.project_context_paths(project) == []


class DummySearchRepo:
    def __init__(
        self,
        notes_by_path: dict[str, SimpleNamespace],
        notes_by_id: dict[str, SimpleNamespace],
        recent_by_type: dict[str, list[SimpleNamespace]] | None = None,
    ) -> None:
        self.notes_by_path = notes_by_path
        self.notes_by_id = notes_by_id
        self.recent_by_type = recent_by_type or {}

    async def get_notes_by_paths(self, db, paths: list[str], project: str | None = None) -> list[SimpleNamespace]:
        return [self.notes_by_path[path] for path in paths if path in self.notes_by_path]

    async def get_note_by_id(self, db, note_id: str) -> SimpleNamespace | None:
        return self.notes_by_id.get(note_id)

    async def list_recent_by_type(self, db, note_type: str, limit: int = 10, project: str | None = None) -> list[SimpleNamespace]:
        notes = self.recent_by_type.get(note_type, [])
        if project is not None:
            notes = [note for note in notes if getattr(note, "project", None) == project]
        return notes[:limit]


class DummySearchService:
    def __init__(self, response: SearchResponse | dict[str | None, SearchResponse]) -> None:
        self.response = response

    async def hybrid(self, db, request) -> SearchResponse:
        if isinstance(self.response, dict):
            return self.response.get(request.note_type, self.response.get(None))  # type: ignore[arg-type]
        return self.response


@pytest.mark.asyncio
async def test_get_context_pack_prefers_distilled_note_and_limits_supporting_notes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "system" / "00-index").mkdir(parents=True, exist_ok=True)
    (tmp_path / "system" / "AGENT_GUIDE.md").write_text("# Guide\n", encoding="utf-8")
    (tmp_path / "system" / "00-index" / "system-index.md").write_text("# Index\n", encoding="utf-8")
    (tmp_path / "system" / "00-index" / "engineering-brain-index.md").write_text("# Brain\n", encoding="utf-8")

    project_dir = tmp_path / "projects" / "gym-trainer"
    (project_dir / "docs" / "14-distilled-context").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "AGENT_GUIDE.md").write_text("# Project Guide\n", encoding="utf-8")
    (project_dir / "docs" / "00-index").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "00-index" / "index.md").write_text("# Project Index\n", encoding="utf-8")
    (project_dir / "docs" / "00-index" / "memory-system-index.md").write_text("# Memory Index\n", encoding="utf-8")
    (project_dir / "docs" / "02-architecture").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "02-architecture" / "auth-flow.md").write_text("# Auth Flow\n", encoding="utf-8")
    (project_dir / "docs" / "04-frontend").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "04-frontend" / "router.md").write_text("# Router\n", encoding="utf-8")
    (project_dir / "project.config.json").write_text(
        """
        {
          "project_name": "gym-trainer",
          "note_project": "fitness-app",
          "workspace": {"frontend_path": "../client"},
          "memory": {
            "docs_path": "./docs",
            "distilled_context": "./docs/14-distilled-context",
            "debugging_notes": "./docs/11-debugging",
            "session_memory": "./docs/15-session-memory"
          },
          "modules": ["auth"]
        }
        """.strip(),
        encoding="utf-8",
    )

    distilled_path = project_dir / "docs" / "14-distilled-context" / "auth.md"
    distilled_path.parent.mkdir(parents=True, exist_ok=True)
    distilled_path.write_text(
        "---\nproject: fitness-app\ntype: distilled_context\ntags: [auth]\n---\n\n# Auth\n\nCompact auth summary.\n",
        encoding="utf-8",
    )

    note_one = SimpleNamespace(
        id=uuid4(),
        path="projects/gym-trainer/docs/02-architecture/auth-flow.md",
        title="Auth Flow",
        project="fitness-app",
        note_type="architecture",
        content="Auth flow details",
        metadata_json={},
        indexed_at=None,
    )
    note_two = SimpleNamespace(
        id=uuid4(),
        path="projects/gym-trainer/docs/04-frontend/router.md",
        title="Router",
        project="fitness-app",
        note_type="frontend",
        content="Router details",
        metadata_json={},
        indexed_at=None,
    )

    search_item = SearchResultItem(
        note_id=note_two.id,
        chunk_id=uuid4(),
        path=note_two.path,
        title=note_two.title,
        project=note_two.project,
        note_type=note_two.note_type,
        tags=[],
        content=note_two.content,
        score=0.9,
    )

    repo = DummySearchRepo(
        notes_by_path={note_one.path: note_one},
        notes_by_id={str(note_two.id): note_two},
    )
    service = ContextPackService(
        search_service=DummySearchService(SearchResponse(query="auth", items=[search_item])),
        search_repo=repo,
        workspace=MemoryWorkspace(root_path=tmp_path, active_project_name="gym-trainer"),
    )

    async def fake_build_note_payload(note, db):
        return {
            "id": note.id,
            "path": note.path,
            "title": note.title,
            "project": note.project,
            "note_type": note.note_type,
            "tags": [],
            "content": note.content,
            "metadata": note.metadata_json,
            "indexed_at": note.indexed_at,
        }

    monkeypatch.setattr("memory_core.context_pack_service.build_note_payload", fake_build_note_payload)

    payload = await service.get_context_pack(db=None, task="debug auth router login", project=None, limit=8)

    assert payload["active_project"] == "gym-trainer"
    assert payload["project_key"] == "fitness-app"
    assert payload["system_notes"][0]["path"] == "system/AGENT_GUIDE.md"
    assert payload["project_config_note"]["path"] == "projects/gym-trainer/project.config.json"
    assert payload["distilled_note"]["path"] == "projects/gym-trainer/docs/14-distilled-context/auth.md"
    assert len(payload["supporting_notes"]) == 2
    assert all(note["source_layer"] == "supporting" for note in payload["supporting_notes"])


@pytest.mark.asyncio
async def test_get_context_pack_handles_missing_distilled_note(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    project_dir = tmp_path / "projects" / "gym-trainer"
    (project_dir / "docs").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "05-database").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "05-database" / "schema.md").write_text("# Schema\n", encoding="utf-8")
    (project_dir / "project.config.json").write_text(
        """
        {
          "project_name": "gym-trainer",
          "note_project": "fitness-app",
          "workspace": {"backend_path": "../backend"},
          "memory": {"docs_path": "./docs"}
        }
        """.strip(),
        encoding="utf-8",
    )
    note_one = SimpleNamespace(
        id=uuid4(),
        path="projects/gym-trainer/docs/05-database/schema.md",
        title="Schema",
        project="fitness-app",
        note_type="database",
        content="Schema details",
        metadata_json={},
        indexed_at=None,
    )

    repo = DummySearchRepo(notes_by_path={note_one.path: note_one}, notes_by_id={})
    service = ContextPackService(
        search_service=DummySearchService(SearchResponse(query="db", items=[])),
        search_repo=repo,
        workspace=MemoryWorkspace(root_path=tmp_path, active_project_name="gym-trainer"),
    )

    async def fake_build_note_payload(note, db):
        return {
            "id": note.id,
            "path": note.path,
            "title": note.title,
            "project": note.project,
            "note_type": note.note_type,
            "tags": [],
            "content": note.content,
            "metadata": note.metadata_json,
            "indexed_at": note.indexed_at,
        }

    monkeypatch.setattr("memory_core.context_pack_service.build_note_payload", fake_build_note_payload)

    payload = await service.get_context_pack(db=None, task="inspect database migrations", project=None, limit=2)

    assert payload["distilled_note"] is None
    assert payload["supporting_notes"][0]["path"] == "projects/gym-trainer/docs/05-database/schema.md"


@pytest.mark.asyncio
async def test_get_context_pack_includes_global_and_project_contexts_for_calendar_meals_task(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "system" / "00-index").mkdir(parents=True, exist_ok=True)
    (tmp_path / "system" / "AGENT_GUIDE.md").write_text("# Guide\n", encoding="utf-8")
    (tmp_path / "system" / "00-index" / "system-index.md").write_text("# Index\n", encoding="utf-8")
    (tmp_path / "system" / "00-index" / "engineering-brain-index.md").write_text("# Brain\n", encoding="utf-8")
    (tmp_path / "contexts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "contexts" / "debug-calendar.md").write_text(
        "---\nkeywords: [calendar, meals, completion]\npriority: 3\n---\n\n# Debug Calendar\n",
        encoding="utf-8",
    )
    (tmp_path / "contexts" / "debug-state-management.md").write_text(
        "---\nkeywords: [state, cache, meals]\npriority: 2\n---\n\n# Debug State Management\n",
        encoding="utf-8",
    )
    (tmp_path / "contexts" / "debug-ui-rendering.md").write_text(
        "---\nkeywords: [rendering, marked, calendar]\npriority: 1\n---\n\n# Debug UI Rendering\n",
        encoding="utf-8",
    )

    project_dir = tmp_path / "projects" / "gym-trainer"
    (project_dir / "docs" / "14-distilled-context").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "00-index").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "00-index" / "index.md").write_text("# Project Index\n", encoding="utf-8")
    (project_dir / "docs" / "00-index" / "memory-system-index.md").write_text("# Memory Index\n", encoding="utf-8")
    (project_dir / "docs" / "AGENT_GUIDE.md").write_text("# Project Guide\n", encoding="utf-8")
    (project_dir / "docs" / "02-architecture").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "02-architecture" / "data-flow.md").write_text("# Data Flow\n", encoding="utf-8")
    (project_dir / "docs" / "04-frontend").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "04-frontend" / "vue-architecture.md").write_text("# Vue Architecture\n", encoding="utf-8")
    (project_dir / "docs" / "07-patterns").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "07-patterns" / "frontend-patterns.md").write_text("# Frontend Patterns\n", encoding="utf-8")
    (project_dir / "docs" / "07-patterns" / "debugging-patterns.md").write_text("# Debugging Patterns\n", encoding="utf-8")
    (project_dir / "docs" / "11-debugging").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "11-debugging" / "calendar-meals-not-completed.md").write_text("# Calendar Meals\n", encoding="utf-8")
    (project_dir / "contexts").mkdir(parents=True, exist_ok=True)
    (project_dir / "contexts" / "debug-calendar.md").write_text(
        "---\nkeywords: [calendar, completion, meals]\npriority: 4\n---\n\n# Project Debug Calendar\n",
        encoding="utf-8",
    )
    (project_dir / "contexts" / "debug-meals.md").write_text(
        "---\nkeywords: [meals, meal_key, completion]\npriority: 4\n---\n\n# Project Debug Meals\n",
        encoding="utf-8",
    )
    (project_dir / "project.config.json").write_text(
        """
        {
          "project_name": "gym-trainer",
          "note_project": "fitness-app",
          "workspace": {"frontend_path": "../client"},
          "memory": {
            "docs_path": "./docs",
            "distilled_context": "./docs/14-distilled-context"
          },
          "modules": ["calendar", "meals", "auth"]
        }
        """.strip(),
        encoding="utf-8",
    )
    (project_dir / "docs" / "14-distilled-context" / "calendar.md").write_text(
        "---\nproject: fitness-app\ntype: distilled_context\ntags: [calendar]\n---\n\n# Calendar\n\nCalendar summary.\n",
        encoding="utf-8",
    )

    note_one = SimpleNamespace(
        id=uuid4(),
        path="projects/gym-trainer/docs/11-debugging/calendar-meals-not-completed.md",
        title="Calendar Meals Not Completed",
        project="fitness-app",
        note_type="bug_fix",
        content="Calendar meal issue",
        metadata_json={},
        indexed_at=None,
    )

    search_item = SearchResultItem(
        note_id=note_one.id,
        chunk_id=uuid4(),
        path=note_one.path,
        title=note_one.title,
        project=note_one.project,
        note_type=note_one.note_type,
        tags=[],
        content=note_one.content,
        score=0.9,
    )

    repo = DummySearchRepo(
        notes_by_path={note_one.path: note_one},
        notes_by_id={str(note_one.id): note_one},
    )
    service = ContextPackService(
        search_service=DummySearchService(SearchResponse(query="calendar meals", items=[search_item])),
        search_repo=repo,
        workspace=MemoryWorkspace(root_path=tmp_path, active_project_name="gym-trainer"),
    )

    async def fake_build_note_payload(note, db):
        return {
            "id": note.id,
            "path": note.path,
            "title": note.title,
            "project": note.project,
            "note_type": note.note_type,
            "tags": [],
            "content": note.content,
            "metadata": note.metadata_json,
            "indexed_at": note.indexed_at,
        }

    monkeypatch.setattr("memory_core.context_pack_service.build_note_payload", fake_build_note_payload)

    payload = await service.get_context_pack(
        db=None,
        task="Debug why meals are not marked as completed in the calendar",
        project=None,
        limit=10,
    )

    assert payload["pack_name"] == "calendar"
    assert payload["fallback_used"] is False
    global_paths = [note["path"] for note in payload["global_contexts"]]
    assert global_paths[0] == "contexts/debug-calendar.md"
    assert set(global_paths[1:]) == {
        "contexts/debug-state-management.md",
        "contexts/debug-ui-rendering.md",
    }
    assert [note["path"] for note in payload["project_contexts"]] == [
        "projects/gym-trainer/contexts/debug-calendar.md",
        "projects/gym-trainer/contexts/debug-meals.md",
    ]
    assert payload["distilled_note"]["path"] == "projects/gym-trainer/docs/14-distilled-context/calendar.md"


@pytest.mark.asyncio
async def test_get_context_pack_can_add_semantic_context_templates_not_matched_locally(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "system" / "00-index").mkdir(parents=True, exist_ok=True)
    (tmp_path / "system" / "AGENT_GUIDE.md").write_text("# Guide\n", encoding="utf-8")
    (tmp_path / "system" / "00-index" / "system-index.md").write_text("# Index\n", encoding="utf-8")
    (tmp_path / "system" / "00-index" / "engineering-brain-index.md").write_text("# Brain\n", encoding="utf-8")
    (tmp_path / "contexts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "contexts" / "debug-calendar.md").write_text(
        "---\nkeywords: [calendar, meals, completion]\npriority: 3\n---\n\n# Debug Calendar\n",
        encoding="utf-8",
    )
    (tmp_path / "contexts" / "debug-ui-rendering.md").write_text(
        "---\nkeywords: [widget, badge]\npriority: 1\n---\n\n# Debug UI Rendering\n",
        encoding="utf-8",
    )

    project_dir = tmp_path / "projects" / "gym-trainer"
    (project_dir / "docs" / "14-distilled-context").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "00-index").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "00-index" / "index.md").write_text("# Project Index\n", encoding="utf-8")
    (project_dir / "docs" / "00-index" / "memory-system-index.md").write_text("# Memory Index\n", encoding="utf-8")
    (project_dir / "docs" / "AGENT_GUIDE.md").write_text("# Project Guide\n", encoding="utf-8")
    (project_dir / "docs" / "02-architecture").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "02-architecture" / "data-flow.md").write_text("# Data Flow\n", encoding="utf-8")
    (project_dir / "docs" / "07-patterns").mkdir(parents=True, exist_ok=True)
    (project_dir / "docs" / "07-patterns" / "frontend-patterns.md").write_text("# Frontend Patterns\n", encoding="utf-8")
    (project_dir / "docs" / "07-patterns" / "debugging-patterns.md").write_text("# Debugging Patterns\n", encoding="utf-8")
    (project_dir / "project.config.json").write_text(
        """
        {
          "project_name": "gym-trainer",
          "note_project": "fitness-app",
          "workspace": {"frontend_path": "../client"},
          "memory": {"docs_path": "./docs", "distilled_context": "./docs/14-distilled-context"},
          "modules": ["calendar", "meals"]
        }
        """.strip(),
        encoding="utf-8",
    )
    (project_dir / "docs" / "14-distilled-context" / "calendar.md").write_text(
        "---\nproject: fitness-app\ntype: distilled_context\ntags: [calendar]\n---\n\n# Calendar\n\nCalendar summary.\n",
        encoding="utf-8",
    )

    semantic_context = SimpleNamespace(
        id=uuid4(),
        path="contexts/debug-ui-rendering.md",
        title="Debug UI Rendering",
        project=None,
        note_type="context_template",
        content="Rendered state versus source state",
        metadata_json={"type": "context_template", "scope": "global"},
        indexed_at=None,
    )
    search_item = SearchResultItem(
        note_id=semantic_context.id,
        chunk_id=uuid4(),
        path=semantic_context.path,
        title=semantic_context.title,
        project=semantic_context.project,
        note_type=semantic_context.note_type,
        tags=[],
        content=semantic_context.content,
        score=0.93,
    )

    repo = DummySearchRepo(
        notes_by_path={},
        notes_by_id={str(semantic_context.id): semantic_context},
    )
    service = ContextPackService(
        search_service=DummySearchService(
            {
                "context_template": SearchResponse(query="context", items=[search_item]),
                None: SearchResponse(query="supporting", items=[]),
            }
        ),
        search_repo=repo,
        workspace=MemoryWorkspace(root_path=tmp_path, active_project_name="gym-trainer"),
    )

    async def fake_build_note_payload(note, db):
        return {
            "id": note.id,
            "path": note.path,
            "title": note.title,
            "project": note.project,
            "note_type": note.note_type,
            "tags": [],
            "content": note.content,
            "metadata": note.metadata_json,
            "indexed_at": note.indexed_at,
        }

    monkeypatch.setattr("memory_core.context_pack_service.build_note_payload", fake_build_note_payload)

    payload = await service.get_context_pack(
        db=None,
        task="Debug why meals are not marked as completed in the calendar",
        project=None,
        limit=10,
    )

    global_paths = [note["path"] for note in payload["global_contexts"]]
    assert "contexts/debug-calendar.md" in global_paths
    assert "contexts/debug-ui-rendering.md" in global_paths


@pytest.mark.asyncio
async def test_rank_context_templates_returns_scored_candidates(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "contexts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "contexts" / "debug-calendar.md").write_text(
        "---\nkeywords: [calendar, meals, completion]\npriority: 3\n---\n\n# Debug Calendar\n",
        encoding="utf-8",
    )
    project_dir = tmp_path / "projects" / "gym-trainer"
    (project_dir / "docs").mkdir(parents=True, exist_ok=True)
    (project_dir / "contexts").mkdir(parents=True, exist_ok=True)
    (project_dir / "contexts" / "debug-meals.md").write_text(
        "---\nkeywords: [meals, meal_key, completion]\npriority: 4\n---\n\n# Debug Meals\n",
        encoding="utf-8",
    )
    (project_dir / "project.config.json").write_text(
        """
        {
          "project_name": "gym-trainer",
          "note_project": "fitness-app",
          "workspace": {"frontend_path": "../client"},
          "memory": {"docs_path": "./docs"},
          "modules": ["calendar", "meals"]
        }
        """.strip(),
        encoding="utf-8",
    )

    semantic_context = SimpleNamespace(
        id=uuid4(),
        path="contexts/debug-calendar.md",
        title="Debug Calendar",
        project=None,
        note_type="context_template",
        content="Calendar context",
        metadata_json={"type": "context_template", "scope": "global"},
        indexed_at=None,
    )
    search_item = SearchResultItem(
        note_id=semantic_context.id,
        chunk_id=uuid4(),
        path=semantic_context.path,
        title=semantic_context.title,
        project=semantic_context.project,
        note_type=semantic_context.note_type,
        tags=[],
        content=semantic_context.content,
        score=0.91,
    )

    repo = DummySearchRepo(notes_by_path={}, notes_by_id={str(semantic_context.id): semantic_context})
    service = ContextPackService(
        search_service=DummySearchService(
            {
                "context_template": SearchResponse(query="context", items=[search_item]),
                None: SearchResponse(query="supporting", items=[]),
            }
        ),
        search_repo=repo,
        workspace=MemoryWorkspace(root_path=tmp_path, active_project_name="gym-trainer"),
    )

    async def fake_build_note_payload(note, db):
        return {
            "id": note.id,
            "path": note.path,
            "title": note.title,
            "project": note.project,
            "note_type": note.note_type,
            "tags": [],
            "content": note.content,
            "metadata": note.metadata_json,
            "indexed_at": note.indexed_at,
        }

    monkeypatch.setattr("memory_core.context_pack_service.build_note_payload", fake_build_note_payload)

    payload = await service.rank_context_templates(
        db=None,
        task="Debug why meals are not marked as completed in the calendar",
        project=None,
        limit=5,
    )

    assert payload["items"][0]["path"] == "contexts/debug-calendar.md"
    assert payload["items"][0]["local_score"] > 0
    assert payload["items"][0]["semantic_score"] == 0.91
    assert payload["items"][0]["combined_score"] > payload["items"][0]["semantic_score"]
    assert "local-match" in payload["items"][0]["source_layers"]
    assert "semantic-search" in payload["items"][0]["source_layers"]


@pytest.mark.asyncio
async def test_rank_context_templates_uses_session_feedback_bonus(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "contexts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "contexts" / "debug-calendar.md").write_text(
        "---\nkeywords: [calendar, meals, completion]\npriority: 3\n---\n\n# Debug Calendar\n",
        encoding="utf-8",
    )
    (tmp_path / "contexts" / "debug-ui-rendering.md").write_text(
        "---\nkeywords: [calendar, marked]\npriority: 1\n---\n\n# Debug UI Rendering\n",
        encoding="utf-8",
    )
    project_dir = tmp_path / "projects" / "gym-trainer"
    (project_dir / "docs").mkdir(parents=True, exist_ok=True)
    (project_dir / "project.config.json").write_text(
        """
        {
          "project_name": "gym-trainer",
          "note_project": "fitness-app",
          "workspace": {"frontend_path": "../client"},
          "memory": {"docs_path": "./docs"},
          "modules": ["calendar", "meals"]
        }
        """.strip(),
        encoding="utf-8",
    )

    session_summary = SimpleNamespace(
        id=uuid4(),
        path="projects/gym-trainer/docs/15-session-memory/s1.md",
        title="Session 1",
        project="fitness-app",
        note_type="session_summary",
        content="Session summary",
        metadata_json={},
        frontmatter={"context_note_paths": ["contexts/debug-ui-rendering.md", "contexts/debug-ui-rendering.md"]},
        indexed_at=None,
    )

    repo = DummySearchRepo(
        notes_by_path={},
        notes_by_id={},
        recent_by_type={"session_summary": [session_summary]},
    )
    service = ContextPackService(
        search_service=DummySearchService(
            {
                "context_template": SearchResponse(query="context", items=[]),
                None: SearchResponse(query="supporting", items=[]),
            }
        ),
        search_repo=repo,
        workspace=MemoryWorkspace(root_path=tmp_path, active_project_name="gym-trainer"),
    )

    payload = await service.rank_context_templates(
        db=None,
        task="Debug why meals are not marked as completed in the calendar",
        project=None,
        limit=5,
    )

    by_path = {item["path"]: item for item in payload["items"]}
    assert by_path["contexts/debug-ui-rendering.md"]["usage_count"] == 2
    assert by_path["contexts/debug-ui-rendering.md"]["evidence_score"] == 4.0
    assert "session-feedback" in by_path["contexts/debug-ui-rendering.md"]["source_layers"]


def test_workspace_resolves_project_by_slug_alias_and_workspace_path(tmp_path: Path) -> None:
    project_dir = tmp_path / "projects" / "gym-trainer"
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "docs").mkdir(parents=True, exist_ok=True)
    (project_dir / "project.config.json").write_text(
        """
        {
          "project_name": "gym-trainer",
          "note_project": "fitness-app",
          "workspace": {
            "frontend_path": "../../gym-trainer-client",
            "backend_path": "../../trainerGM"
          },
          "memory": {"docs_path": "./docs"}
        }
        """.strip(),
        encoding="utf-8",
    )

    workspace = MemoryWorkspace(root_path=tmp_path)

    assert workspace.get_project("gym-trainer") is not None
    assert workspace.get_project("fitness-app") is not None
    inferred = workspace.resolve_active_project(cwd=(project_dir / "../../trainerGM").resolve())
    assert inferred is not None
    assert inferred.slug == "gym-trainer"
