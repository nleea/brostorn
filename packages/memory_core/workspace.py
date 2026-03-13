from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _validate_portable_relative_path(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} paths must not be empty")
    if Path(normalized).is_absolute():
        raise ValueError(f"{field_name} paths must be relative, not absolute")
    return normalized


class ProjectRules(BaseModel):
    model_config = ConfigDict(extra="allow")

    load_distilled_context_first: bool | None = None
    require_debug_documentation: bool | None = None
    save_session_memory: bool | None = None


class ProjectConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_name: str
    note_project: str | None = None
    description: str | None = None
    workspace: dict[str, str] = Field(default_factory=dict)
    memory: dict[str, str] = Field(default_factory=dict)
    modules: list[str] = Field(default_factory=list)
    tech_stack: dict[str, Any] = Field(default_factory=dict)
    entry_points: dict[str, str] = Field(default_factory=dict)
    rules: ProjectRules = Field(default_factory=ProjectRules)

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("project_name must not be empty")
        return normalized

    @field_validator("note_project")
    @classmethod
    def validate_note_project(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("note_project must not be empty when provided")
        return normalized

    @field_validator("workspace", "memory", "entry_points")
    @classmethod
    def validate_path_maps(cls, value: dict[str, str], info) -> dict[str, str]:
        cleaned: dict[str, str] = {}
        for key, item in value.items():
            normalized_key = key.strip()
            if not normalized_key:
                raise ValueError(f"{info.field_name} keys must not be empty")
            cleaned[normalized_key] = _validate_portable_relative_path(item, field_name=info.field_name)
        return cleaned

    @field_validator("modules")
    @classmethod
    def validate_modules(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in value:
            normalized = item.strip()
            if not normalized:
                raise ValueError("modules must not contain empty values")
            if normalized not in cleaned:
                cleaned.append(normalized)
        return cleaned


@dataclass(frozen=True)
class ResolvedProject:
    slug: str
    config: ProjectConfig
    project_dir: Path
    docs_dir: Path

    @property
    def note_project(self) -> str:
        return self.config.note_project or self.config.project_name


@dataclass
class MemoryWorkspace:
    root_path: Path
    legacy_vault_path: Path | None = None
    active_project_name: str | None = None

    def __post_init__(self) -> None:
        self.root_path = self.root_path.resolve()
        if self.legacy_vault_path is not None:
            self.legacy_vault_path = self.legacy_vault_path.resolve()

    @property
    def system_dir(self) -> Path:
        return self.root_path / "system"

    @property
    def projects_dir(self) -> Path:
        return self.root_path / "projects"

    @property
    def global_contexts_dir(self) -> Path:
        return self.root_path / "contexts"

    def iter_index_roots(self) -> list[Path]:
        roots: list[Path] = []
        if self.system_dir.exists():
            roots.append(self.system_dir)
        if self.global_contexts_dir.exists():
            roots.append(self.global_contexts_dir)

        for project in self.list_projects():
            if project.docs_dir.exists():
                roots.append(project.docs_dir)
            project_contexts_dir = project.project_dir / "contexts"
            if project_contexts_dir.exists():
                roots.append(project_contexts_dir)

        if self.legacy_vault_path and self.legacy_vault_path.exists():
            roots.append(self.legacy_vault_path)

        unique_roots: list[Path] = []
        seen: set[Path] = set()
        for root in roots:
            if root in seen:
                continue
            unique_roots.append(root)
            seen.add(root)
        return unique_roots

    def list_projects(self) -> list[ResolvedProject]:
        if not self.projects_dir.exists():
            return []

        projects: list[ResolvedProject] = []
        for config_path in sorted(self.projects_dir.glob("*/project.config.json")):
            project = self._load_project_from_config(config_path)
            if project is not None:
                projects.append(project)
        return projects

    def resolve_active_project(self, project: str | None = None, cwd: Path | None = None) -> ResolvedProject | None:
        if project:
            return self.get_project(project)

        if self.active_project_name:
            resolved = self.get_project(self.active_project_name)
            if resolved is not None:
                return resolved

        inferred = self._infer_from_cwd((cwd or Path.cwd()).resolve())
        if inferred is not None:
            return inferred

        projects = self.list_projects()
        if len(projects) == 1:
            return projects[0]

        return None

    def get_project(self, project: str) -> ResolvedProject | None:
        normalized = project.strip().lower()
        for item in self.list_projects():
            aliases = {
                item.slug.lower(),
                item.config.project_name.lower(),
                item.note_project.lower(),
            }
            if normalized in aliases:
                return item
        return None

    def resolve_project_query_name(self, project: str | None = None, cwd: Path | None = None) -> str | None:
        resolved = self.resolve_active_project(project=project, cwd=cwd)
        if resolved is not None:
            return resolved.note_project
        return project

    def system_guidance_paths(self) -> list[str]:
        candidates = (
            "system/AGENT_GUIDE.md",
            "system/00-index/system-index.md",
            "system/00-index/engineering-brain-index.md",
        )
        return [path for path in candidates if (self.root_path / path).exists()]

    def global_context_paths(self) -> list[str]:
        if not self.global_contexts_dir.exists():
            return []
        return [
            self.to_relative(path)
            for path in sorted(self.global_contexts_dir.glob("*.md"))
            if path.is_file() and path.name.lower() != "readme.md"
        ]

    def project_context_paths(self, project: ResolvedProject | None) -> list[str]:
        if project is None:
            return []

        contexts_dir = project.project_dir / "contexts"
        if not contexts_dir.exists():
            return []

        return [
            self.to_relative(path)
            for path in sorted(contexts_dir.glob("*.md"))
            if path.is_file() and path.name.lower() != "readme.md"
        ]

    def project_index_paths(self, project: ResolvedProject | None) -> list[str]:
        if project is None:
            return []

        candidates = [
            self.to_relative(project.docs_dir / "AGENT_GUIDE.md"),
            self.to_relative(project.docs_dir / "00-index" / "index.md"),
            self.to_relative(project.docs_dir / "00-index" / "memory-system-index.md"),
        ]
        return [path for path in candidates if (self.root_path / path).exists()]

    def resolve_pack_priority_paths(self, project: ResolvedProject | None, paths: tuple[str, ...]) -> list[str]:
        if project is None:
            return [path for path in paths if (self.root_path / path).exists()]
        return [self.to_relative(project.docs_dir / path) for path in paths if (project.docs_dir / path).exists()]

    def resolve_distilled_path(self, project: ResolvedProject | None, default_relative_path: str | None) -> str | None:
        if default_relative_path is None:
            return None

        if project is None:
            candidate = self.root_path / default_relative_path
            return default_relative_path if candidate.exists() else None

        distilled_dir = self.resolve_project_memory_dir(project, "distilled_context")
        candidate = distilled_dir / Path(default_relative_path).name
        if candidate.exists():
            return self.to_relative(candidate)
        return None

    def resolve_project_memory_dir(self, project: ResolvedProject, key: str) -> Path:
        configured = project.config.memory.get(key)
        if configured:
            return (project.project_dir / configured).resolve()

        defaults = {
            "docs_path": project.project_dir / "docs",
            "debugging_notes": project.docs_dir / "11-debugging",
            "session_memory": project.docs_dir / "21-session-memory",
            "distilled_context": project.docs_dir / "20-distilled-context",
        }
        fallback = defaults.get(key, project.docs_dir)
        return fallback.resolve()

    def resolve_write_directory(
        self,
        *,
        project: str | None,
        note_kind: str,
        relative_dir: str,
        cwd: Path | None = None,
    ) -> tuple[Path, str | None]:
        resolved_project = self.resolve_active_project(project=project, cwd=cwd)
        if relative_dir.startswith(("system/", "projects/", "knowledge/")):
            return (self.root_path / relative_dir).resolve(), resolved_project.note_project if resolved_project else project

        if resolved_project is not None:
            if note_kind == "debug":
                base_dir = self.resolve_project_memory_dir(resolved_project, "debugging_notes")
            elif note_kind == "session":
                base_dir = self.resolve_project_memory_dir(resolved_project, "session_memory")
            elif note_kind == "distilled":
                base_dir = resolved_project.docs_dir / "14-distilled-context"
            else:
                base_dir = self.resolve_project_memory_dir(resolved_project, "docs_path")

            target_dir = base_dir if relative_dir in {"", ".", "11-debugging", "21-session-memory", "14-distilled-context"} else (resolved_project.docs_dir / relative_dir)
            return target_dir.resolve(), resolved_project.note_project

        if self.legacy_vault_path is not None:
            return (self.legacy_vault_path / relative_dir).resolve(), project

        return (self.root_path / relative_dir).resolve(), project

    def load_project_config_note(self, project: ResolvedProject | None) -> dict | None:
        if project is None:
            return None

        config_path = project.project_dir / "project.config.json"
        data = json.loads(config_path.read_text(encoding="utf-8"))

        content_lines = [
            f"Project: {project.config.project_name}",
            f"Docs: {self.to_relative(project.docs_dir)}",
        ]
        if project.config.modules:
            content_lines.append(f"Modules: {', '.join(project.config.modules)}")
        if project.config.tech_stack:
            stack_summary = ", ".join(f"{key}={value}" for key, value in project.config.tech_stack.items())
            content_lines.append(f"Tech stack: {stack_summary}")
        if project.config.entry_points:
            entry_summary = ", ".join(f"{key}={value}" for key, value in project.config.entry_points.items())
            content_lines.append(f"Entry points: {entry_summary}")

        return {
            "id": None,
            "path": self.to_relative(config_path),
            "title": f"{project.config.project_name} project config",
            "project": project.note_project,
            "note_type": "project_config",
            "tags": [project.slug, "project-config"],
            "content": "\n".join(content_lines),
            "metadata": data,
            "indexed_at": None,
            "score": None,
            "source_layer": "project-config",
        }

    def to_relative(self, path: Path) -> str:
        return str(path.resolve().relative_to(self.root_path))

    def _load_project_from_config(self, config_path: Path) -> ResolvedProject | None:
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            config = ProjectConfig.model_validate(data)
        except Exception:
            return None

        project_dir = config_path.parent
        docs_config = config.memory.get("docs_path", "./docs")
        docs_dir = (project_dir / docs_config).resolve()
        return ResolvedProject(
            slug=project_dir.name,
            config=config,
            project_dir=project_dir.resolve(),
            docs_dir=docs_dir,
        )

    def _infer_from_cwd(self, cwd: Path) -> ResolvedProject | None:
        for project in self.list_projects():
            for relative_path in project.config.workspace.values():
                workspace_path = (project.project_dir / relative_path).resolve()
                if cwd == workspace_path or workspace_path in cwd.parents:
                    return project
        return None
