from __future__ import annotations

import sys
from pathlib import Path
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ROOT_DIR = Path(__file__).resolve().parents[2]
PACKAGES_DIR = ROOT_DIR / "packages"
if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from memory_config.logging import configure_logging
from memory_config.settings import get_settings
from memory_core.context_pack_service import ContextPackService
from memory_core.db import get_db_session
from memory_core.indexer import VaultIndexer
from memory_core.models import Note
from memory_core.note_writer import NoteWriterService
from memory_core.schemas import (
    ContextPackResponse,
    ContextTemplateRankResponse,
    DebugNoteSaveRequest,
    HealthResponse,
    IndexFileRequest,
    NoteResponse,
    RebuildResponse,
    ReusableLearningSaveRequest,
    SearchRequest,
    SearchResponse,
    SessionSummarySaveRequest,
)
from memory_core.search_service import SearchService, build_note_payload
from memory_core.workspace import MemoryWorkspace
from memory_vectorstore.embeddings import build_embedding_provider
from memory_vectorstore.repository import SearchRepository

settings = get_settings()
configure_logging(settings.log_level)

embedding_provider = build_embedding_provider()
indexer = VaultIndexer(settings=settings, embedding_provider=embedding_provider)
search_service = SearchService(embedding_provider=embedding_provider)
search_repo = SearchRepository()
workspace = MemoryWorkspace(
    root_path=settings.memory_root_path,
    legacy_vault_path=settings.obsidian_vault_path,
    active_project_name=settings.active_project_name,
)
context_pack_service = ContextPackService(
    search_service=search_service,
    search_repo=search_repo,
    workspace=workspace,
)
note_writer_service = NoteWriterService(workspace=workspace, indexer=indexer)


def _resolve_project_scope(project: str | None) -> str | None:
    return workspace.resolve_project_query_name(project=project)


def _filter_context_template_items(items: list[dict], project: str | None) -> list[dict]:
    if project is None:
        return [item for item in items if item.path.startswith("contexts/")]

    resolved_project = workspace.resolve_active_project(project=project)
    if resolved_project is None:
        return list(items)

    project_prefix = f"projects/{resolved_project.slug}/contexts/"
    return [
        item
        for item in items
        if item.path.startswith("contexts/") or item.path.startswith(project_prefix)
    ]

app = FastAPI(title="Memory System API", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/index/rebuild", response_model=RebuildResponse)
async def rebuild_index(db: AsyncSession = Depends(get_db_session)) -> RebuildResponse:
    indexed, deleted = await indexer.rebuild(db)
    return RebuildResponse(status="ok", indexed=indexed, deleted=deleted)


@app.post("/index/file")
async def index_file(payload: IndexFileRequest, db: AsyncSession = Depends(get_db_session)) -> dict:
    changed = await indexer.index_relative_path(db, payload.relative_path)
    return {"status": "ok", "changed": changed, "path": payload.relative_path}


@app.post("/search/semantic", response_model=SearchResponse)
async def semantic_search(payload: SearchRequest, db: AsyncSession = Depends(get_db_session)) -> SearchResponse:
    return await search_service.semantic(db, payload.model_copy(update={"project": _resolve_project_scope(payload.project)}))


@app.post("/search/hybrid", response_model=SearchResponse)
async def hybrid_search(payload: SearchRequest, db: AsyncSession = Depends(get_db_session)) -> SearchResponse:
    return await search_service.hybrid(db, payload.model_copy(update={"project": _resolve_project_scope(payload.project)}))


@app.get("/context-templates/search", response_model=SearchResponse)
async def search_context_templates(
    query: str,
    limit: int = 8,
    project: str | None = None,
    db: AsyncSession = Depends(get_db_session),
) -> SearchResponse:
    response = await search_service.semantic(
        db,
        SearchRequest(
            query=query,
            limit=max(limit * 2, limit, 1),
            project=None,
            note_type="context_template",
        ),
    )
    return SearchResponse(query=query, items=_filter_context_template_items(response.items, project)[:limit])


@app.get("/context-templates/rank", response_model=ContextTemplateRankResponse)
async def rank_context_templates(
    task: str,
    project: str | None = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db_session),
) -> ContextTemplateRankResponse:
    payload = await context_pack_service.rank_context_templates(db, task=task, project=project, limit=limit)
    return ContextTemplateRankResponse(**payload)


@app.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: UUID, db: AsyncSession = Depends(get_db_session)) -> NoteResponse:
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    payload = await build_note_payload(note, db)
    return NoteResponse(**payload)


@app.get("/projects/{project}/context")
async def get_project_context(project: str, db: AsyncSession = Depends(get_db_session)) -> dict:
    resolved_project = _resolve_project_scope(project)
    notes = await search_repo.project_context(db, project=resolved_project or project, limit=30)
    payload = [await build_note_payload(note, db) for note in notes]
    return {"project": project, "project_key": resolved_project or project, "count": len(payload), "items": payload}


@app.get("/decisions/recent")
async def get_recent_decisions(db: AsyncSession = Depends(get_db_session)) -> dict:
    notes = await search_repo.list_recent_by_type(db, note_type="decision", limit=20)
    payload = [await build_note_payload(note, db) for note in notes]
    return {"count": len(payload), "items": payload}


@app.get("/context-packs", response_model=ContextPackResponse)
async def get_context_pack(task: str, project: str | None = None, limit: int = 8, db: AsyncSession = Depends(get_db_session)) -> ContextPackResponse:
    payload = await context_pack_service.get_context_pack(db, task=task, project=project, limit=limit)
    return ContextPackResponse(**payload)


@app.post("/notes/debug")
async def save_debug_note(
    payload: DebugNoteSaveRequest,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    return await note_writer_service.save_debug_note(
        db,
        title=payload.title,
        summary=payload.summary,
        project=payload.project,
        module=payload.module,
        symptom=payload.symptom,
        tags=payload.tags,
        root_cause=payload.root_cause,
        solution=payload.solution,
        fix=payload.fix,
        files_changed=payload.files_changed,
        validation=payload.validation,
        status=payload.status,
        validation_steps=payload.validation_steps,
        validation_evidence=payload.validation_evidence,
        related_paths=payload.related_paths,
        follow_ups=payload.follow_ups,
        updated_at=payload.updated_at,
        relative_dir=payload.relative_dir,
        slug=payload.slug,
    )


@app.post("/notes/session-summary")
async def save_session_summary(
    payload: SessionSummarySaveRequest,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    return await note_writer_service.save_session_summary(
        db,
        task=payload.task,
        project=payload.project,
        tags=payload.tags,
        context_pack=payload.context_pack,
        context_note_paths=payload.context_note_paths,
        findings=payload.findings,
        files_modified=payload.files_modified,
        validation=payload.validation,
        follow_ups=payload.follow_ups,
        session_date=payload.session_date,
        relative_dir=payload.relative_dir,
        slug=payload.slug,
    )


@app.post("/notes/reusable-learning")
async def save_reusable_learning(
    payload: ReusableLearningSaveRequest,
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    return await note_writer_service.save_reusable_learning(
        db,
        title=payload.title,
        summary=payload.summary,
        project=payload.project,
        tags=payload.tags,
        category=payload.category,
        lesson=payload.lesson,
        applicability=payload.applicability,
        source_paths=payload.source_paths,
        validation=payload.validation,
        relative_dir=payload.relative_dir,
        slug=payload.slug,
    )
