from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml
from sqlalchemy.ext.asyncio import AsyncSession

from memory_core.indexer import VaultIndexer
from memory_core.workspace import MemoryWorkspace


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return normalized or "note"


def build_frontmatter(metadata: dict) -> str:
    yaml_text = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=False).strip()
    return f"---\n{yaml_text}\n---\n\n"


def build_debug_note_markdown(
    *,
    title: str,
    summary: str,
    module: str | None,
    symptom: str | None,
    root_cause: str | None,
    solution: str | None,
    fix: str | None,
    files_changed: list[str],
    validation: str | None,
    status: str,
    validation_steps: list[str],
    validation_evidence: list[str],
    follow_ups: list[str],
    updated_at: str,
    project: str,
    tags: list[str],
    related_paths: list[str],
) -> str:
    metadata = {
        "title": title,
        "project": project,
        "type": "bug_fix",
        "status": status,
        "module": module,
        "updated_at": updated_at,
        "files_changed": files_changed,
        "follow_ups": follow_ups,
        "tags": tags,
    }

    lines = [build_frontmatter(metadata), f"# {title}", "", "## Summary", summary.strip()]
    lines.extend(["", "## Status", status])

    if module:
        lines.extend(["", "## Module", module.strip()])

    if symptom:
        lines.extend(["", "## Symptom", symptom.strip()])

    if related_paths:
        lines.extend(["", "## Related Notes"])
        lines.extend([f"- [[{path.removesuffix('.md')}]]" for path in related_paths])

    if root_cause:
        lines.extend(["", "## Root Cause", root_cause.strip()])

    effective_solution = solution or fix
    if effective_solution:
        lines.extend(["", "## Solution", effective_solution.strip()])

    if files_changed:
        lines.extend(["", "## Files Changed"])
        lines.extend([f"- `{path}`" for path in files_changed])

    if validation_steps:
        lines.extend(["", "## Validation Steps"])
        lines.extend([f"- {step}" for step in validation_steps])

    if validation:
        lines.extend(["", "## Validation", validation.strip()])

    if validation_evidence:
        lines.extend(["", "## Validation Evidence"])
        lines.extend([f"- {item}" for item in validation_evidence])

    if follow_ups:
        lines.extend(["", "## Follow Ups"])
        lines.extend([f"- {item}" for item in follow_ups])

    return "\n".join(lines).strip() + "\n"


def build_session_summary_markdown(
    *,
    task: str,
    project: str,
    tags: list[str],
    context_pack: str | None,
    context_note_paths: list[str],
    findings: list[str],
    files_modified: list[str],
    validation: str | None,
    follow_ups: list[str],
    session_date: str,
) -> str:
    metadata = {
        "title": task,
        "project": project,
        "type": "session_summary",
        "session_date": session_date,
        "tags": tags,
        "context_pack": context_pack,
        "context_note_paths": context_note_paths,
    }

    lines = [build_frontmatter(metadata), f"# {task}", "", "## Task", task.strip()]

    lines.extend(["", "## Context Loaded"])
    if context_pack:
        lines.append(f"- Context pack: `{context_pack}`")
    if context_note_paths:
        lines.extend([f"- [[{path.removesuffix('.md')}]]" for path in context_note_paths])
    if not context_pack and not context_note_paths:
        lines.append("- No explicit context pack recorded.")

    lines.extend(["", "## Findings"])
    lines.extend([f"- {item}" for item in findings] or ["- None recorded."])

    lines.extend(["", "## Files Modified"])
    lines.extend([f"- `{path}`" for path in files_modified] or ["- None recorded."])

    lines.extend(["", "## Validation", (validation or "Not recorded.").strip()])

    lines.extend(["", "## Follow Ups"])
    lines.extend([f"- {item}" for item in follow_ups] or ["- None recorded."])

    return "\n".join(lines).strip() + "\n"


def build_distilled_context_markdown(
    *,
    module: str,
    project: str,
    tags: list[str],
    purpose: str | None,
    core_flow: list[str],
    source_of_truth: list[str],
    key_contracts: list[str],
    known_pitfalls: list[str],
    relevant_files: list[str],
    related_notes: list[str],
    updated: str,
) -> str:
    metadata = {
        "type": "distilled-context",
        "module": module,
        "project": project,
        "status": "active",
        "updated": updated,
        "tags": tags,
    }

    lines = [build_frontmatter(metadata), f"# {module.capitalize()} — Distilled Context"]

    if purpose:
        lines.extend(["", "## Purpose", purpose.strip()])

    if core_flow:
        lines.extend(["", "## Core Flow"])
        lines.extend([f"- {step}" for step in core_flow])

    if source_of_truth:
        lines.extend(["", "## Source of Truth"])
        lines.extend([f"- {item}" for item in source_of_truth])

    if key_contracts:
        lines.extend(["", "## Key Contracts"])
        lines.extend([f"- {item}" for item in key_contracts])

    if known_pitfalls:
        lines.extend(["", "## Known Pitfalls"])
        lines.extend([f"- {item}" for item in known_pitfalls])

    if relevant_files:
        lines.extend(["", "## Relevant Files"])
        lines.extend([f"- `{path}`" for path in relevant_files])

    if related_notes:
        lines.extend(["", "## Related Notes"])
        lines.extend([f"- [[{path.removesuffix('.md')}]]" for path in related_notes])

    return "\n".join(lines).strip() + "\n"


def build_reusable_learning_markdown(
    *,
    title: str,
    summary: str,
    project: str,
    tags: list[str],
    category: str,
    lesson: str | None,
    applicability: str | None,
    source_paths: list[str],
    validation: str | None,
) -> str:
    metadata = {
        "title": title,
        "project": project,
        "type": "cross_project_learning",
        "category": category,
        "tags": tags,
    }

    lines = [build_frontmatter(metadata), f"# {title}", "", "## Summary", summary.strip()]
    lines.extend(["", "## Category", category])

    if lesson:
        lines.extend(["", "## Lesson", lesson.strip()])

    if applicability:
        lines.extend(["", "## Applicability", applicability.strip()])

    if source_paths:
        lines.extend(["", "## Source Notes"])
        lines.extend([f"- [[{path.removesuffix('.md')}]]" for path in source_paths])

    if validation:
        lines.extend(["", "## Validation", validation.strip()])

    return "\n".join(lines).strip() + "\n"


@dataclass
class NoteWriterService:
    workspace: MemoryWorkspace
    indexer: VaultIndexer

    async def save_debug_note(
        self,
        db: AsyncSession,
        *,
        title: str,
        summary: str,
        project: str | None = None,
        tags: list[str] | None = None,
        root_cause: str | None = None,
        module: str | None = None,
        symptom: str | None = None,
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
        relative_dir: str = "11-debugging",
        slug: str | None = None,
    ) -> dict:
        note_project, active_project = self._resolve_note_project(project)
        clean_tags = sorted(
            {
                "docs",
                "debugging",
                note_project,
                *(filter(None, [active_project])),
                *(tag for tag in (tags or []) if tag),
            }
        )
        clean_related = [path for path in (related_paths or []) if path]

        markdown = build_debug_note_markdown(
            title=title,
            summary=summary,
            module=module,
            symptom=symptom,
            root_cause=root_cause,
            solution=solution,
            fix=fix,
            files_changed=[path for path in (files_changed or []) if path],
            validation=validation,
            status=status,
            validation_steps=[step for step in (validation_steps or []) if step],
            validation_evidence=[item for item in (validation_evidence or []) if item],
            follow_ups=[item for item in (follow_ups or []) if item],
            updated_at=updated_at or datetime.now(tz=timezone.utc).date().isoformat(),
            project=note_project,
            tags=clean_tags,
            related_paths=clean_related,
        )

        return await self._write_markdown_note(
            db,
            title=title,
            project=project,
            tags=clean_tags,
            relative_dir=relative_dir,
            slug=slug,
            markdown=markdown,
            note_kind="debug",
            extra_response={"debug_status": status},
        )

    async def save_session_summary(
        self,
        db: AsyncSession,
        *,
        task: str,
        project: str | None = None,
        tags: list[str] | None = None,
        context_pack: str | None = None,
        context_note_paths: list[str] | None = None,
        findings: list[str] | None = None,
        files_modified: list[str] | None = None,
        validation: str | None = None,
        follow_ups: list[str] | None = None,
        session_date: str | None = None,
        relative_dir: str = "21-session-memory",
        slug: str | None = None,
    ) -> dict:
        note_project, active_project = self._resolve_note_project(project)
        clean_tags = sorted(
            {
                "docs",
                "session-memory",
                note_project,
                *(filter(None, [active_project])),
                *(tag for tag in (tags or []) if tag),
            }
        )
        markdown = build_session_summary_markdown(
            task=task,
            project=note_project,
            tags=clean_tags,
            context_pack=context_pack,
            context_note_paths=[path for path in (context_note_paths or []) if path],
            findings=[item for item in (findings or []) if item],
            files_modified=[path for path in (files_modified or []) if path],
            validation=validation,
            follow_ups=[item for item in (follow_ups or []) if item],
            session_date=session_date or datetime.now(tz=timezone.utc).date().isoformat(),
        )
        return await self._write_markdown_note(
            db,
            title=task,
            project=project,
            tags=clean_tags,
            relative_dir=relative_dir,
            slug=slug,
            markdown=markdown,
            note_kind="session",
        )

    async def save_distilled_context(
        self,
        db: AsyncSession,
        *,
        module: str,
        project: str | None = None,
        tags: list[str] | None = None,
        purpose: str | None = None,
        core_flow: list[str] | None = None,
        source_of_truth: list[str] | None = None,
        key_contracts: list[str] | None = None,
        known_pitfalls: list[str] | None = None,
        relevant_files: list[str] | None = None,
        related_notes: list[str] | None = None,
        slug: str | None = None,
    ) -> dict:
        note_project, active_project = self._resolve_note_project(project)
        clean_tags = sorted(
            {
                "distilled-context",
                "docs",
                module,
                note_project,
                *(filter(None, [active_project])),
                *(tag for tag in (tags or []) if tag),
            }
        )
        markdown = build_distilled_context_markdown(
            module=module,
            project=note_project,
            tags=clean_tags,
            purpose=purpose,
            core_flow=[s for s in (core_flow or []) if s],
            source_of_truth=[s for s in (source_of_truth or []) if s],
            key_contracts=[s for s in (key_contracts or []) if s],
            known_pitfalls=[s for s in (known_pitfalls or []) if s],
            relevant_files=[s for s in (relevant_files or []) if s],
            related_notes=[s for s in (related_notes or []) if s],
            updated=datetime.now(tz=timezone.utc).date().isoformat(),
        )
        return await self._write_markdown_note(
            db,
            title=f"{module} distilled context",
            project=project,
            tags=clean_tags,
            relative_dir="14-distilled-context",
            slug=slug or module,
            markdown=markdown,
            note_kind="distilled",
            extra_response={"module": module},
        )

    async def save_reusable_learning(
        self,
        db: AsyncSession,
        *,
        title: str,
        summary: str,
        project: str | None = None,
        tags: list[str] | None = None,
        category: str = "reusable-solutions",
        lesson: str | None = None,
        applicability: str | None = None,
        source_paths: list[str] | None = None,
        validation: str | None = None,
        relative_dir: str = "system/05-cross-project-memory",
        slug: str | None = None,
    ) -> dict:
        note_project, active_project = self._resolve_note_project(project)
        clean_tags = sorted(
            {
                "cross-project-memory",
                "docs",
                note_project,
                *(filter(None, [active_project])),
                *(tag for tag in (tags or []) if tag),
            }
        )
        markdown = build_reusable_learning_markdown(
            title=title,
            summary=summary,
            project=note_project,
            tags=clean_tags,
            category=category,
            lesson=lesson,
            applicability=applicability,
            source_paths=[path for path in (source_paths or []) if path],
            validation=validation,
        )
        return await self._write_markdown_note(
            db,
            title=title,
            project=project,
            tags=clean_tags,
            relative_dir=relative_dir,
            slug=slug,
            markdown=markdown,
            note_kind="system",
            extra_response={"category": category},
        )

    @staticmethod
    def _allocate_path(target_dir: Path, base_name: str) -> Path:
        candidate = target_dir / f"{base_name}.md"
        if not candidate.exists():
            return candidate

        suffix = 2
        while True:
            candidate = target_dir / f"{base_name}-{suffix}.md"
            if not candidate.exists():
                return candidate
            suffix += 1

    async def _write_markdown_note(
        self,
        db: AsyncSession,
        *,
        title: str,
        project: str | None,
        tags: list[str],
        relative_dir: str,
        slug: str | None,
        markdown: str,
        note_kind: str,
        extra_response: dict | None = None,
    ) -> dict:
        target_dir, note_project = self.workspace.resolve_write_directory(
            project=project,
            note_kind=note_kind,
            relative_dir=relative_dir,
        )
        target_dir.mkdir(parents=True, exist_ok=True)

        base_name = slugify(slug or title)
        file_path = self._allocate_path(target_dir, base_name)
        file_path.write_text(markdown, encoding="utf-8")

        relative_path = self.workspace.to_relative(file_path)
        await self.indexer.index_relative_path(db, relative_path)

        response = {
            "status": "ok",
            "path": relative_path,
            "title": title,
            "project": note_project,
            "tags": tags,
        }
        if extra_response:
            response.update(extra_response)
        return response

    def _resolve_note_project(self, project: str | None) -> tuple[str, str | None]:
        resolved_project = self.workspace.resolve_active_project(project=project)
        if resolved_project is not None:
            return resolved_project.note_project, resolved_project.slug
        return project or "memory-system", None
