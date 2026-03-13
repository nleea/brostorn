from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class IndexFileRequest(BaseModel):
    relative_path: str


class SearchRequest(BaseModel):
    query: str
    limit: int = Field(default=8, ge=1, le=50)
    project: str | None = None
    note_type: str | None = None
    tags: list[str] | None = None


class SearchResultItem(BaseModel):
    note_id: UUID
    chunk_id: UUID
    path: str
    title: str
    project: str | None
    note_type: str | None
    tags: list[str]
    content: str
    score: float


class SearchResponse(BaseModel):
    query: str
    items: list[SearchResultItem]


class NoteResponse(BaseModel):
    id: UUID
    path: str
    title: str
    project: str | None
    note_type: str | None
    tags: list[str]
    content: str
    metadata: dict
    indexed_at: datetime | None


class RebuildResponse(BaseModel):
    status: str
    indexed: int
    deleted: int


class ContextPackNote(BaseModel):
    id: UUID | None = None
    path: str
    title: str
    project: str | None
    note_type: str | None
    tags: list[str]
    content: str
    metadata: dict
    indexed_at: datetime | None
    score: float | None = None
    source_layer: str | None = None


class ContextPackResponse(BaseModel):
    task: str
    pack_name: str
    description: str
    matched_keywords: list[str]
    project: str | None
    project_key: str | None = None
    active_project: str | None = None
    system_notes: list[ContextPackNote] = Field(default_factory=list)
    project_config_note: ContextPackNote | None = None
    project_index_notes: list[ContextPackNote] = Field(default_factory=list)
    global_contexts: list[ContextPackNote] = Field(default_factory=list)
    project_contexts: list[ContextPackNote] = Field(default_factory=list)
    distilled_note: ContextPackNote | None = None
    supporting_notes: list[ContextPackNote] = Field(default_factory=list)
    notes: list[ContextPackNote]
    fallback_used: bool


class ContextTemplateRankItem(BaseModel):
    path: str
    title: str
    project: str | None = None
    scope: str
    metadata: dict = Field(default_factory=dict)
    local_score: int = 0
    semantic_score: float | None = None
    usage_count: int = 0
    evidence_score: float = 0.0
    combined_score: float
    source_layers: list[str] = Field(default_factory=list)


class ContextTemplateRankResponse(BaseModel):
    task: str
    project: str | None = None
    project_key: str | None = None
    active_project: str | None = None
    items: list[ContextTemplateRankItem] = Field(default_factory=list)


DebugStatus = Literal["open", "fixed", "verified"]


class DebugNoteSaveRequest(BaseModel):
    title: str
    summary: str
    project: str | None = None
    module: str | None = None
    symptom: str | None = None
    tags: list[str] | None = None
    root_cause: str | None = None
    solution: str | None = None
    fix: str | None = None
    files_changed: list[str] | None = None
    validation: str | None = None
    status: DebugStatus = "open"
    validation_steps: list[str] | None = None
    validation_evidence: list[str] | None = None
    related_paths: list[str] | None = None
    follow_ups: list[str] | None = None
    updated_at: str | None = None
    relative_dir: str = "11-debugging"
    slug: str | None = None


class SessionSummarySaveRequest(BaseModel):
    task: str
    project: str | None = None
    tags: list[str] | None = None
    context_pack: str | None = None
    context_note_paths: list[str] | None = None
    findings: list[str] | None = None
    files_modified: list[str] | None = None
    validation: str | None = None
    follow_ups: list[str] | None = None
    session_date: str | None = None
    relative_dir: str = "21-session-memory"
    slug: str | None = None


class ReusableLearningSaveRequest(BaseModel):
    title: str
    summary: str
    project: str | None = None
    tags: list[str] | None = None
    category: Literal["recurring-bugs", "reusable-solutions", "anti-patterns", "architecture-lessons"] = "reusable-solutions"
    lesson: str | None = None
    applicability: str | None = None
    source_paths: list[str] | None = None
    validation: str | None = None
    relative_dir: str = "system/05-cross-project-memory"
    slug: str | None = None
