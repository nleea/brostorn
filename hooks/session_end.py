from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
PACKAGES_DIR = ROOT_DIR / "packages"
if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from memory_core.workspace import MemoryWorkspace


def build_session_end_payload(
    *,
    workspace_root: Path,
    task: str,
    project: str | None = None,
    debug_status: str = "open",
    validation_performed: bool = False,
    reusable_learning: bool = False,
    files_modified: list[str] | None = None,
    legacy_vault_path: Path | None = None,
    active_project_name: str | None = None,
) -> dict:
    workspace = MemoryWorkspace(
        root_path=workspace_root,
        legacy_vault_path=legacy_vault_path,
        active_project_name=active_project_name,
    )
    resolved_project = workspace.resolve_active_project(project=project)
    project_slug = resolved_project.slug if resolved_project else project

    should_save_debug_note = debug_status in {"fixed", "verified"} or validation_performed
    should_save_session_summary = bool(task.strip()) or bool(files_modified)
    should_promote_learning = reusable_learning or debug_status == "verified"

    return {
        "task": task,
        "active_project": project_slug,
        "project_key": resolved_project.note_project if resolved_project else project,
        "debug_status": debug_status,
        "should_save_debug_note": should_save_debug_note,
        "suggested_debug_status": "verified" if validation_performed and debug_status == "fixed" else debug_status,
        "should_save_session_summary": should_save_session_summary,
        "should_promote_learning": should_promote_learning,
        "suggested_cross_project_path": "system/cross-project",
        "files_modified": files_modified or [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize memory-system session outcomes.")
    parser.add_argument("--workspace-root", default=str(ROOT_DIR))
    parser.add_argument("--task", required=True)
    parser.add_argument("--project")
    parser.add_argument("--debug-status", default="open")
    parser.add_argument("--validation-performed", action="store_true")
    parser.add_argument("--reusable-learning", action="store_true")
    parser.add_argument("--file", action="append", dest="files_modified")
    parser.add_argument("--legacy-vault-path")
    parser.add_argument("--active-project-name")
    args = parser.parse_args()

    payload = build_session_end_payload(
        workspace_root=Path(args.workspace_root),
        task=args.task,
        project=args.project,
        debug_status=args.debug_status,
        validation_performed=args.validation_performed,
        reusable_learning=args.reusable_learning,
        files_modified=args.files_modified,
        legacy_vault_path=Path(args.legacy_vault_path).resolve() if args.legacy_vault_path else None,
        active_project_name=args.active_project_name,
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
