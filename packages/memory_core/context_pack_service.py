from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from memory_core.models import SearchAudit
from memory_core.context_packs import (
    GENERAL_PACK,
    ContextTemplateDescriptor,
    rank_context_descriptors,
    infer_context_pack,
)
from memory_core.search_service import SearchService, build_note_payload
from memory_core.schemas import SearchRequest
from memory_core.workspace import MemoryWorkspace
from memory_parsers.markdown_parser import MarkdownParser
from memory_vectorstore.repository import SearchRepository


@dataclass
class ContextPackService:
    search_service: SearchService
    search_repo: SearchRepository
    workspace: MemoryWorkspace
    markdown_parser: MarkdownParser = field(default_factory=MarkdownParser)

    async def get_context_pack(
        self,
        db: AsyncSession,
        task: str,
        project: str | None = None,
        limit: int = 8,
    ) -> dict:
        pack, matched_keywords = infer_context_pack(task)
        active_project = self.workspace.resolve_active_project(project=project)
        effective_project = active_project.note_project if active_project is not None else project
        system_notes = self._load_filesystem_notes(self.workspace.system_guidance_paths(), source_layer="system")
        project_config_note = self.workspace.load_project_config_note(active_project)
        project_index_notes = self._load_filesystem_notes(
            self.workspace.project_index_paths(active_project),
            source_layer="project-index",
        )
        context_ranking = await self.rank_context_templates(db, task=task, project=project, limit=8)
        global_contexts = self._load_ranked_context_notes(context_ranking["items"], scope="global", source_layer="global-context")
        project_contexts = self._load_ranked_context_notes(context_ranking["items"], scope="project", source_layer="project-context")
        resolved_priority_paths = self.workspace.resolve_pack_priority_paths(active_project, pack.priority_paths)
        distilled_note = self._load_distilled_note(
            self.workspace.resolve_distilled_path(active_project, pack.distilled_path)
        )
        supporting_limit = self._resolve_supporting_limit(
            requested_limit=limit,
            has_distilled_note=distilled_note is not None,
            default_limit=pack.supporting_limit,
        )

        priority_notes = await self.search_repo.get_notes_by_paths(
            db,
            paths=resolved_priority_paths,
            project=effective_project,
        )

        if not priority_notes and effective_project is not None:
            priority_notes = await self.search_repo.get_notes_by_paths(
                db,
                paths=resolved_priority_paths,
                project=None,
            )

        search_query = self._build_search_query(task, pack.search_terms)
        search_response = await self.search_service.hybrid(
            db,
            SearchRequest(
                query=search_query,
                limit=max(supporting_limit * 2, supporting_limit, 1),
                project=effective_project,
            ),
        )

        if not search_response.items and effective_project is not None:
            search_response = await self.search_service.hybrid(
                db,
                SearchRequest(
                    query=search_query,
                    limit=max(supporting_limit * 2, supporting_limit, 1),
                    project=None,
                ),
            )

        notes_by_path: dict[str, dict] = {}

        for note in priority_notes:
            payload = await build_note_payload(note, db)
            payload["source_layer"] = "supporting"
            notes_by_path[payload["path"]] = payload

        for item in search_response.items:
            if item.path in notes_by_path:
                continue
            note = await self.search_repo.get_note_by_id(db, str(item.note_id))
            if note is None:
                continue
            payload = await build_note_payload(note, db)
            payload["score"] = item.score
            payload["source_layer"] = "supporting"
            notes_by_path[payload["path"]] = payload

        ordered_notes = self._order_notes(
            tuple(resolved_priority_paths),
            [note for note in notes_by_path.values() if note["path"] != (distilled_note or {}).get("path")],
        )
        supporting_notes = ordered_notes[:supporting_limit]
        notes = [
            *system_notes,
            *([project_config_note] if project_config_note else []),
            *project_index_notes,
            *global_contexts,
            *project_contexts,
            *([distilled_note] if distilled_note else []),
            *supporting_notes,
        ]

        return {
            "task": task,
            "pack_name": pack.name,
            "description": pack.description,
            "matched_keywords": matched_keywords,
            "project": active_project.slug if active_project is not None else project,
            "project_key": effective_project,
            "active_project": active_project.slug if active_project is not None else None,
            "system_notes": system_notes,
            "project_config_note": project_config_note,
            "project_index_notes": project_index_notes,
            "global_contexts": global_contexts,
            "project_contexts": project_contexts,
            "distilled_note": distilled_note,
            "supporting_notes": supporting_notes,
            "notes": notes[: max(limit, 1)],
            "fallback_used": pack.name == GENERAL_PACK.name,
        }

    async def rank_context_templates(
        self,
        db: AsyncSession,
        *,
        task: str,
        project: str | None = None,
        limit: int = 10,
    ) -> dict:
        pack, _ = infer_context_pack(task)
        active_project = self.workspace.resolve_active_project(project=project)
        effective_project = active_project.note_project if active_project is not None else project
        project_modules = active_project.config.modules if active_project is not None else []

        local_candidates = self._rank_local_contexts(task, active_project, project_modules)
        semantic_candidates = await self._search_context_templates(
            db=db,
            task=task,
            search_terms=pack.search_terms,
            active_project=active_project,
            limit=max(limit * 2, limit, 1),
        )
        items = self._merge_ranked_context_candidates(
            local_candidates=local_candidates,
            semantic_candidates=semantic_candidates,
        )
        usage_counts = await self._get_context_usage_counts(
            db=db,
            paths=[item["path"] for item in items],
            project=effective_project,
            limit=100,
        )
        for item in items:
            usage_count = usage_counts.get(item["path"], 0)
            evidence_score = float(usage_count * 2)
            item["usage_count"] = usage_count
            item["evidence_score"] = evidence_score
            item["combined_score"] = float(item["combined_score"]) + evidence_score
            if usage_count > 0 and "session-feedback" not in item["source_layers"]:
                item["source_layers"].append("session-feedback")

        items.sort(key=lambda item: (-float(item["combined_score"]), item["path"]))
        items = items[:limit]

        return {
            "task": task,
            "project": active_project.slug if active_project is not None else project,
            "project_key": effective_project,
            "active_project": active_project.slug if active_project is not None else None,
            "items": items,
        }

    def _load_context_descriptors(self, relative_paths: list[str]) -> list[ContextTemplateDescriptor]:
        descriptors: list[ContextTemplateDescriptor] = []
        for relative_path in relative_paths:
            absolute_path = (self.workspace.root_path / relative_path).resolve()
            if not absolute_path.exists() or not absolute_path.is_file():
                continue

            parsed = self.markdown_parser.parse(absolute_path, self.workspace.root_path)
            descriptors.append(
                ContextTemplateDescriptor(
                    path=parsed.relative_path,
                    title=parsed.title,
                    metadata=parsed.frontmatter,
                )
            )
        return descriptors

    async def _search_context_templates(
        self,
        *,
        db: AsyncSession,
        task: str,
        search_terms: tuple[str, ...],
        active_project,
        limit: int,
    ) -> dict[str, list[dict]]:
        response = await self.search_service.hybrid(
            db,
            SearchRequest(
                query=self._build_search_query(task, search_terms),
                limit=max(limit, 1),
                project=None,
                note_type="context_template",
            ),
        )

        global_notes: list[dict] = []
        project_notes: list[dict] = []
        project_prefix = f"projects/{active_project.slug}/contexts/" if active_project is not None else None

        for item in response.items:
            note = await self.search_repo.get_note_by_id(db, str(item.note_id))
            if note is None:
                continue

            payload = await build_note_payload(note, db)
            payload["score"] = item.score
            path = payload["path"]

            if path.startswith("contexts/"):
                global_notes.append(payload)
            elif project_prefix and path.startswith(project_prefix):
                project_notes.append(payload)

        global_notes.sort(key=lambda note: (-(float(note.get("score", 0.0))), note["path"]))
        project_notes.sort(key=lambda note: (-(float(note.get("score", 0.0))), note["path"]))
        return {"global": global_notes, "project": project_notes}

    async def _get_context_usage_counts(
        self,
        *,
        db: AsyncSession,
        paths: list[str],
        project: str | None,
        limit: int,
    ) -> dict[str, float]:
        if not paths:
            return {}

        wanted = set(paths)
        counts: dict[str, float] = {path: 0.0 for path in paths}

        # Signal 1: session summaries with explicit context_note_paths (high quality)
        notes = await self.search_repo.list_recent_by_type(
            db,
            note_type="session_summary",
            limit=limit,
            project=project,
        )
        for note in notes:
            frontmatter = note.frontmatter or {}
            context_paths = frontmatter.get("context_note_paths") or []
            if not isinstance(context_paths, list):
                continue
            for path in context_paths:
                if path in wanted:
                    counts[path] += 1.0

        # Signal 2: SearchAudit — paths that appeared in recent search results (lower weight)
        try:
            audit_result = await db.execute(
                select(SearchAudit)
                .order_by(SearchAudit.created_at.desc())
                .limit(limit * 3)
            )
            for row in audit_result.scalars().all():
                result_paths = (row.metadata_json or {}).get("result_paths") or []
                if not isinstance(result_paths, list):
                    continue
                for path in result_paths:
                    if path in wanted:
                        counts[path] += 0.5
        except Exception:
            pass

        return counts

    def _rank_local_contexts(self, task: str, active_project, project_modules: list[str]) -> dict[str, list[dict]]:
        global_descriptors = self._load_context_descriptors(self.workspace.global_context_paths())
        project_descriptors = self._load_context_descriptors(self.workspace.project_context_paths(active_project))

        global_ranked = rank_context_descriptors(task, global_descriptors, modules=project_modules)
        project_ranked = rank_context_descriptors(task, project_descriptors, modules=project_modules)

        def _serialize(matches: list) -> list[dict]:
            items: list[dict] = []
            for match in matches:
                items.append(
                    {
                        "path": match.descriptor.path,
                        "title": match.descriptor.title or Path(match.descriptor.path).stem,
                        "metadata": match.descriptor.metadata or {},
                        "local_score": match.score,
                    }
                )
            return items

        return {"global": _serialize(global_ranked), "project": _serialize(project_ranked)}

    def _merge_ranked_context_candidates(
        self,
        *,
        local_candidates: dict[str, list[dict]],
        semantic_candidates: dict[str, list[dict]],
    ) -> list[dict]:
        merged: dict[str, dict] = {}

        for scope in ("global", "project"):
            for item in local_candidates[scope]:
                merged[item["path"]] = {
                    "path": item["path"],
                    "title": item["title"],
                    "project": item["metadata"].get("project"),
                    "scope": scope,
                    "metadata": item["metadata"],
                    "local_score": int(item.get("local_score", 0)),
                    "semantic_score": None,
                    "usage_count": 0,
                    "evidence_score": 0.0,
                    "combined_score": float(item.get("local_score", 0) * 10),
                    "source_layers": ["local-match"],
                }

        for scope in ("global", "project"):
            for item in semantic_candidates[scope]:
                existing = merged.get(item["path"])
                semantic_score = float(item.get("score", 0.0))
                if existing is None:
                    merged[item["path"]] = {
                        "path": item["path"],
                        "title": item["title"],
                        "project": item.get("project"),
                        "scope": scope,
                        "metadata": item.get("metadata", {}),
                        "local_score": 0,
                        "semantic_score": semantic_score,
                        "usage_count": 0,
                        "evidence_score": 0.0,
                        "combined_score": semantic_score,
                        "source_layers": ["semantic-search"],
                    }
                    continue

                existing["semantic_score"] = semantic_score
                existing["combined_score"] = float(existing["local_score"] * 10) + semantic_score
                if "semantic-search" not in existing["source_layers"]:
                    existing["source_layers"].append("semantic-search")

        return sorted(
            merged.values(),
            key=lambda item: (-float(item["combined_score"]), item["path"]),
        )

    def _load_ranked_context_notes(self, items: list[dict], *, scope: str, source_layer: str) -> list[dict]:
        scoped_items = [item for item in items if item["scope"] == scope]
        loaded = {
            note["path"]: note
            for note in self._load_filesystem_notes([item["path"] for item in scoped_items], source_layer=source_layer)
        }

        notes: list[dict] = []
        for item in scoped_items:
            note = loaded.get(item["path"])
            if note is None:
                continue
            note["score"] = item.get("combined_score")
            notes.append(note)
        return notes

    @staticmethod
    def _build_search_query(task: str, search_terms: tuple[str, ...]) -> str:
        parts = [task.strip(), *[term.strip() for term in search_terms if term.strip()]]
        return " ".join(part for part in parts if part)

    @staticmethod
    def _order_notes(priority_paths: tuple[str, ...], notes: list[dict]) -> list[dict]:
        priority_index = {path: index for index, path in enumerate(priority_paths)}

        return sorted(
            notes,
            key=lambda note: (
                0 if note["path"] in priority_index else 1,
                priority_index.get(note["path"], 10_000),
                -(float(note.get("score", 0.0))),
                note["path"],
            ),
        )

    def _load_distilled_note(self, relative_path: str | None) -> dict | None:
        notes = self._load_filesystem_notes([relative_path] if relative_path else [], source_layer="distilled")
        return notes[0] if notes else None

    def _load_filesystem_notes(self, relative_paths: list[str], source_layer: str) -> list[dict]:
        notes: list[dict] = []
        for relative_path in relative_paths:
            if not relative_path:
                continue

            absolute_path = (self.workspace.root_path / relative_path).resolve()
            if not absolute_path.exists() or not absolute_path.is_file():
                continue

            parsed = self.markdown_parser.parse(absolute_path, self.workspace.root_path)
            notes.append(
                {
                    "id": None,
                    "path": parsed.relative_path,
                    "title": parsed.title,
                    "project": parsed.metadata.get("project"),
                    "note_type": parsed.metadata.get("type"),
                    "tags": parsed.tags,
                    "content": parsed.body_content,
                    "metadata": parsed.frontmatter,
                    "indexed_at": None,
                    "score": None,
                    "source_layer": source_layer,
                }
            )
        return notes

    @staticmethod
    def _resolve_supporting_limit(requested_limit: int, has_distilled_note: bool, default_limit: int) -> int:
        if requested_limit <= 0:
            return 0

        available_slots = requested_limit - 1 if has_distilled_note else requested_limit
        if available_slots <= 0:
            return 0
        return min(default_limit, available_slots)
