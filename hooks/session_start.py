from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
PACKAGES_DIR = ROOT_DIR / "packages"
if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from memory_core.context_packs import ContextTemplateDescriptor, infer_context_pack, match_context_descriptors
from memory_parsers.markdown_parser import MarkdownParser
from memory_core.workspace import MemoryWorkspace


def build_session_start_payload(
    *,
    workspace_root: Path,
    project: str | None = None,
    task: str | None = None,
    cwd: Path | None = None,
    legacy_vault_path: Path | None = None,
    active_project_name: str | None = None,
) -> dict:
    workspace = MemoryWorkspace(
        root_path=workspace_root,
        legacy_vault_path=legacy_vault_path,
        active_project_name=active_project_name,
    )
    resolved_project = workspace.resolve_active_project(project=project, cwd=cwd)
    pack, matched_keywords = infer_context_pack(task or "")
    project_modules = resolved_project.config.modules if resolved_project is not None else []
    parser = MarkdownParser()
    global_contexts = _load_context_descriptors(workspace, parser, workspace.global_context_paths())
    project_contexts = _load_context_descriptors(workspace, parser, workspace.project_context_paths(resolved_project))
    context_templates = [
        descriptor.path
        for descriptor in [
            *match_context_descriptors(task or "", global_contexts, modules=project_modules),
            *match_context_descriptors(task or "", project_contexts, modules=project_modules),
        ]
    ]

    return {
        "workspace_root": str(workspace.root_path),
        "active_project": resolved_project.slug if resolved_project else None,
        "project_key": resolved_project.note_project if resolved_project else project,
        "project_config_path": workspace.to_relative(resolved_project.project_dir / "project.config.json") if resolved_project else None,
        "system_guidance_paths": workspace.system_guidance_paths(),
        "project_index_paths": workspace.project_index_paths(resolved_project),
        "suggested_context_pack": pack.name,
        "matched_keywords": matched_keywords,
        "context_templates": context_templates,
    }


def _load_context_descriptors(
    workspace: MemoryWorkspace,
    parser: MarkdownParser,
    relative_paths: list[str],
) -> list[ContextTemplateDescriptor]:
    descriptors: list[ContextTemplateDescriptor] = []
    for relative_path in relative_paths:
        absolute_path = (workspace.root_path / relative_path).resolve()
        if not absolute_path.exists() or not absolute_path.is_file():
            continue
        parsed = parser.parse(absolute_path, workspace.root_path)
        descriptors.append(
            ContextTemplateDescriptor(
                path=parsed.relative_path,
                title=parsed.title,
                metadata=parsed.frontmatter,
            )
        )
    return descriptors


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize memory-system session context.")
    parser.add_argument("--workspace-root", default=str(ROOT_DIR))
    parser.add_argument("--project")
    parser.add_argument("--task")
    parser.add_argument("--cwd")
    parser.add_argument("--legacy-vault-path")
    parser.add_argument("--active-project-name")
    args = parser.parse_args()

    payload = build_session_start_payload(
        workspace_root=Path(args.workspace_root),
        project=args.project,
        task=args.task,
        cwd=Path(args.cwd).resolve() if args.cwd else None,
        legacy_vault_path=Path(args.legacy_vault_path).resolve() if args.legacy_vault_path else None,
        active_project_name=args.active_project_name,
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
