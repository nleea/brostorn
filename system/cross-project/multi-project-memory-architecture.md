# Multi-Project Memory Architecture

## Decision

Treat the `memory-system` repository root as the portable memory workspace.

## Layers

- `system/` for reusable engineering knowledge
- `projects/<project>/docs/` for project-specific memory
- `knowledge/obsidian-vault/` only as a legacy compatibility source

## Operational Rules

- Resolve the active project through explicit parameters, environment, or workspace-path inference.
- Use `project.config.json` to map project slugs to docs paths, workspace paths, and note project keys.
- Keep MCP tools compatible by resolving project scope internally instead of replacing tool names.
