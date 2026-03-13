from __future__ import annotations

import sys
from pathlib import Path
from uuid import UUID
from typing import Literal

from mcp.server.fastmcp import FastMCP
from sqlalchemy import select

ROOT_DIR = Path(__file__).resolve().parents[2]
PACKAGES_DIR = ROOT_DIR / "packages"
if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from memory_config.settings import get_settings
from memory_core.db import SessionLocal
from memory_core.context_pack_service import ContextPackService
from memory_core.indexer import VaultIndexer
from memory_core.models import Note, SearchAudit
from memory_core.note_writer import NoteWriterService
from memory_core.schemas import ContextPackResponse, SearchRequest
from memory_core.schemas import ContextTemplateRankResponse
from memory_core.search_service import SearchService, build_note_payload
from memory_core.workspace import MemoryWorkspace
from memory_vectorstore.embeddings import build_embedding_provider
from memory_vectorstore.repository import SearchRepository

settings = get_settings()
embedding_provider = build_embedding_provider()
search_service = SearchService(embedding_provider)
search_repo = SearchRepository()
indexer = VaultIndexer(settings=settings, embedding_provider=embedding_provider)
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

mcp = FastMCP(settings.mcp_server_name)


# ── helpers ──────────────────────────────────────────────────────────────────

async def _semantic_search(
    query: str,
    limit: int,
    project: str | None,
    note_type: str | None,
    tags: list[str] | None,
) -> list[dict]:
    async with SessionLocal() as db:
        result = await search_service.semantic(
            db,
            SearchRequest(
                query=query,
                limit=limit,
                project=workspace.resolve_project_query_name(project=project),
                note_type=note_type,
                tags=tags,
            ),
        )
        items = [item.model_dump() for item in result.items]

    try:
        async with SessionLocal() as audit_db:
            audit_db.add(SearchAudit(
                query=query,
                search_type=note_type or "note",
                top_score=result.items[0].score if result.items else None,
                metadata_json={
                    "result_paths": [item.path for item in result.items[:10]],
                    "note_type": note_type,
                    "project": project,
                },
            ))
            await audit_db.commit()
    except Exception:
        pass

    return items


def _filter_context_template_items(items: list[dict], project: str | None) -> list[dict]:
    if project is None:
        return [item for item in items if item["path"].startswith("contexts/")]

    resolved_project = workspace.resolve_active_project(project=project)
    if resolved_project is None:
        return items

    project_prefix = f"projects/{resolved_project.slug}/contexts/"
    return [
        item
        for item in items
        if item["path"].startswith("contexts/") or item["path"].startswith(project_prefix)
    ]


# ── TOOL 1: search_memory ─────────────────────────────────────────────────────

@mcp.tool()
async def search_memory(
    query: str,
    type: Literal["bug_fix", "decision", "context_template", "note"] | None = None,
    project: str | None = None,
    tags: list[str] | None = None,
    limit: int = 8,
) -> list[dict]:
    """
    Semantic search across memory notes.
    Use `type` to narrow the search:
      - "bug_fix"          → past bug fixes and debugging notes
      - "decision"         → architectural and design decisions
      - "context_template" → reusable context templates for tasks
      - "note"             → general notes (default when type is None)
    Leave `type` as None to search across all types.
    """
    items = await _semantic_search(
        query=query,
        limit=max(limit * 2, limit, 1) if type == "context_template" else limit,
        project=None if type == "context_template" else project,
        note_type=type,
        tags=tags,
    )

    if type == "context_template":
        items = _filter_context_template_items(items, project)
        return items[:limit]

    return items


# ── TOOL 2: get_context ───────────────────────────────────────────────────────

@mcp.tool()
async def get_context(
    task: str,
    project: str | None = None,
    mode: Literal["pack", "rank"] = "pack",
    limit: int = 8,
) -> dict:
    """
    Retrieve structured context for a task.
      - mode="pack"  → full context pack ready to use (default)
      - mode="rank"  → ranked list of relevant context templates with scores
    Use "pack" when starting work on a task.
    Use "rank" to explore which templates are most relevant before committing.
    """
    async with SessionLocal() as db:
        if mode == "rank":
            payload = await context_pack_service.rank_context_templates(
                db, task=task, project=project, limit=limit
            )
            return ContextTemplateRankResponse(**payload).model_dump(mode="json")

        payload = await context_pack_service.get_context_pack(
            db, task=task, project=project, limit=limit
        )
        return ContextPackResponse(**payload).model_dump(mode="json")


# ── TOOL 3: fetch_notes ───────────────────────────────────────────────────────

@mcp.tool()
async def fetch_notes(
    by: Literal["id", "project", "recent"],
    value: str | None = None,
    limit: int = 20,
) -> list[dict] | dict:
    """
    Fetch notes by a specific strategy:
      - by="id"      → fetch a single note by its UUID (requires `value`)
      - by="project" → fetch all context notes for a project (requires `value`)
      - by="recent"  → fetch the most recently updated notes
    """
    async with SessionLocal() as db:
        if by == "id":
            if not value:
                return {"error": "value (note_id) is required when by='id'"}
            result = await db.execute(select(Note).where(Note.id == UUID(value)))
            note = result.scalar_one_or_none()
            if not note:
                return {"error": "Note not found"}
            return await build_note_payload(note, db)

        if by == "project":
            if not value:
                return {"error": "value (project name) is required when by='project'"}
            resolved = workspace.resolve_project_query_name(project=value)
            notes = await search_repo.project_context(db, project=resolved or value, limit=limit)
            return [await build_note_payload(note, db) for note in notes]

        # by == "recent"
        result = await db.execute(
            select(Note).order_by(Note.updated_at.desc()).limit(limit)
        )
        notes = list(result.scalars().all())
        return [await build_note_payload(note, db) for note in notes]


# ── TOOL 4: save_note ────────────────────────────────────────────────────────

@mcp.tool()
async def save_note(
    type: Literal["bug_fix", "session", "learning", "distilled"],
    # ── shared fields ──
    title: str | None = None,
    summary: str | None = None,
    project: str | None = None,
    tags: list[str] | None = None,
    slug: str | None = None,
    # ── bug_fix fields ──
    module: str | None = None,
    symptom: str | None = None,
    root_cause: str | None = None,
    solution: str | None = None,
    fix: str | None = None,
    files_changed: list[str] | None = None,
    validation: str | None = None,
    status: str = "open",
    validation_steps: list[str] | None = None,
    validation_evidence: list[str] | None = None,
    related_paths: list[str] | None = None,
    follow_ups: list[str] | None = None,
    updated_at: str | None = None,
    # ── session fields ──
    task: str | None = None,
    context_pack: str | None = None,
    context_note_paths: list[str] | None = None,
    findings: list[str] | None = None,
    files_modified: list[str] | None = None,
    session_date: str | None = None,
    # ── learning fields ──
    category: str = "reusable-solutions",
    lesson: str | None = None,
    applicability: str | None = None,
    source_paths: list[str] | None = None,
    # ── cross-type optional ──
    refs: list[dict] | None = None,
    ref_id: str | None = None,
    # ── distilled fields ──
    purpose: str | None = None,
    core_flow: list[str] | None = None,
    source_of_truth: list[str] | None = None,
    key_contracts: list[str] | None = None,
    known_pitfalls: list[str] | None = None,
    relevant_files: list[str] | None = None,
    related_notes: list[str] | None = None,
) -> dict:
    """
    Save a NEW memory note. To update an existing note use update_note instead.
      - type="bug_fix"   → debugging note with symptom, root_cause, fix, files_changed
      - type="session"   → session summary with task, findings, files_modified
      - type="learning"  → reusable cross-project learning with lesson, applicability
      - type="distilled" → distilled context for a module (requires `module`)
    Only fill the fields relevant to the type — unused fields are ignored.
    """
    async with SessionLocal() as db:
        if type == "bug_fix":
            return await note_writer_service.save_debug_note(
                db,
                title=title or "",
                summary=summary or "",
                project=project,
                module=module,
                symptom=symptom,
                tags=tags,
                root_cause=root_cause,
                solution=solution,
                fix=fix,
                files_changed=files_changed,
                validation=validation,
                status=status,
                validation_steps=validation_steps,
                validation_evidence=validation_evidence,
                related_paths=related_paths,
                follow_ups=follow_ups,
                updated_at=updated_at,
                relative_dir="debugging",
                slug=slug,
                refs=refs,
                note_id=ref_id,
            )

        if type == "session":
            return await note_writer_service.save_session_summary(
                db,
                task=task or title or "",
                project=project,
                tags=tags,
                context_pack=context_pack,
                context_note_paths=context_note_paths,
                findings=findings,
                files_modified=files_modified,
                validation=validation,
                follow_ups=follow_ups,
                session_date=session_date,
                relative_dir="sessions",
                slug=slug,
                refs=refs,
                note_id=ref_id,
            )

        if type == "distilled":
            return await note_writer_service.save_distilled_context(
                db,
                module=module or title or "",
                project=project,
                tags=tags,
                purpose=purpose,
                core_flow=core_flow,
                source_of_truth=source_of_truth,
                key_contracts=key_contracts,
                known_pitfalls=known_pitfalls,
                relevant_files=relevant_files,
                related_notes=related_notes,
                slug=slug or module or None,
                refs=refs,
                note_id=ref_id,
            )

        # type == "learning"
        return await note_writer_service.save_reusable_learning(
            db,
            title=title or "",
            summary=summary or "",
            project=project,
            tags=tags,
            category=category,
            lesson=lesson,
            applicability=applicability,
            source_paths=source_paths,
            validation=validation,
            relative_dir="system/cross-project",
            slug=slug,
            refs=refs,
            note_id=ref_id,
        )


# ── TOOL 5: update_note ───────────────────────────────────────────────────────

@mcp.tool()
async def update_note(
    note_id: str,
    # ── lifecycle ──
    status: Literal["open", "resolved", "failed", "wont_fix"] | None = None,
    # ── bug_fix resolution fields ──
    root_cause: str | None = None,
    fix: str | None = None,
    solution: str | None = None,
    files_changed: list[str] | None = None,
    validation: str | None = None,
    validation_steps: list[str] | None = None,
    validation_evidence: list[str] | None = None,
    follow_ups: list[str] | None = None,
    # ── generic fields ──
    summary: str | None = None,
    tags: list[str] | None = None,
    findings: list[str] | None = None,
    files_modified: list[str] | None = None,
) -> dict:
    """
    Update an existing note in place — avoids creating duplicate noise.

    Primary use cases:
      1. Close a bug: status="resolved" + root_cause + fix + files_changed
      2. Mark failed attempt: status="failed" + fix (what was tried)
      3. Add findings to a session note
      4. Append follow_ups after new info is discovered

    Workflow:
      1. Call search_memory or fetch_notes to get the note_id
      2. Call update_note with only the fields that changed
      → Everything else stays intact, no duplicate note is created.

    Only non-None fields are written — passing None leaves the field unchanged.
    """
    async with SessionLocal() as db:
        result = await db.execute(select(Note).where(Note.id == UUID(note_id)))
        note = result.scalar_one_or_none()

        if not note:
            return {"error": f"Note {note_id} not found"}

        # Build patch — only non-None values
        patch: dict = {}

        if status is not None:
            patch["status"] = status
        if root_cause is not None:
            patch["root_cause"] = root_cause
        if fix is not None:
            patch["fix"] = fix
        if solution is not None:
            patch["solution"] = solution
        if files_changed is not None:
            patch["files_changed"] = files_changed
        if validation is not None:
            patch["validation"] = validation
        if validation_steps is not None:
            patch["validation_steps"] = validation_steps
        if validation_evidence is not None:
            patch["validation_evidence"] = validation_evidence
        if follow_ups is not None:
            patch["follow_ups"] = follow_ups
        if summary is not None:
            patch["summary"] = summary
        if tags is not None:
            patch["tags"] = tags
        if findings is not None:
            patch["findings"] = findings
        if files_modified is not None:
            patch["files_modified"] = files_modified

        if not patch:
            return {"error": "No fields to update — provide at least one field"}

        return await note_writer_service.patch_note(db, note=note, patch=patch)


if __name__ == "__main__":
    mcp.run()