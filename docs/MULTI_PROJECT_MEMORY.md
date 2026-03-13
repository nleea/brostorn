# Multi-Project Memory

## Layout

The runtime now treats the `memory-system` repository root as the memory workspace.

Indexed sources:

- `system/`
- `projects/<project>/docs/`
- `knowledge/obsidian-vault/` as a legacy fallback when present

## Active Project Resolution

Resolution order:

1. explicit MCP/API `project` parameter
2. `MEMORY_ACTIVE_PROJECT`
3. current working directory inferred from `project.config.json` workspace paths
4. the single configured project when only one project exists

If nothing resolves, project-filtered tools fall back to broad search.

## project.config.json

Each project lives under `projects/<project>/project.config.json`.

The runtime reads:

- `project_name`
- `note_project`
- `workspace`
- `memory`
- `modules`
- `tech_stack`
- `entry_points`
- `rules`

`note_project` lets the runtime map a stable project slug like `gym-trainer` to the existing frontmatter project key used in notes, such as `fitness-app`.

## Context Loading Order

`get_context_pack(...)` now assembles context in this order:

1. `system/` guidance notes
2. active project config
3. project index notes
4. project distilled context
5. supporting project notes from indexed search

The `notes` field remains for compatibility, while structured fields expose each layer separately.

## V1.5 Operational Layers

- `contexts/`: recurring task templates for targeted debugging and validation
- `hooks/`: lightweight session start/end helpers
- `schemas/`: JSON schemas for config and note contracts
- validation-aware debug notes with `open`, `fixed`, and `verified`
- reusable learning promotion into `system/05-cross-project-memory/`

## Write-Back Behavior

- `save_debug_note(...)` writes into the active project's configured debugging folder.
- `save_session_summary(...)` writes into the active project's configured session-memory folder.
- `save_reusable_learning(...)` writes into cross-project system memory.
- If no project resolves, writes fall back to the legacy vault when available.

## Adding a New Project

1. Create `projects/<project>/project.config.json`.
2. Create `projects/<project>/docs/`.
3. Add index, architecture, debugging, distilled-context, and session-memory docs as needed.
4. Set `note_project` if your existing markdown frontmatter uses a different project key.
5. Rebuild the index.
