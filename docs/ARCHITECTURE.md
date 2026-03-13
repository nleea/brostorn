# Memory System Architecture

## Overview

This system is local-first and treats the `memory-system` repository as the portable memory workspace. Markdown files in `system/` and `projects/<project>/docs/` are parsed, chunked, embedded, and indexed into PostgreSQL + pgvector. The legacy `knowledge/obsidian-vault` directory remains a compatible fallback. FastAPI and MCP expose the same indexed context.

## Components

- `apps/indexer`: full rebuild + filesystem watch (watchdog) for incremental sync.
- `apps/api`: query and indexing endpoints for app integration.
- `apps/mcp_server`: MCP tools for agent access (Codex/Claude).
- `packages/memory_core/workspace.py`: project registry, active-project resolution, and path mapping.
- `packages/memory_core/context_packs.py`: pack definitions and inference heuristics.
- `packages/memory_core/context_pack_service.py`: context assembly across system guidance, project config, project docs, and supporting indexed notes.
- `packages/memory_core/note_writer.py`: controlled writes back into the active project's docs, system cross-project memory, or legacy fallback.
- `contexts/`: operational comparison/inspection templates for recurring task classes.
- `hooks/`: lightweight session start/end helpers.
- `schemas/`: explicit JSON-schema contract files.
- `packages/parsers`: markdown + frontmatter + wikilinks + tags parsing and chunking.
- `packages/vectorstore`: embedding providers and search repository.
- `packages/core`: DB models, indexer orchestration, search service.
- `packages/config`: typed runtime configuration.
- `commands/`: workflow templates for agent operations.
- `rules/`: guardrails for context loading and documentation discipline.

## Data Flow

1. Markdown note changes in `system/`, `projects/<project>/docs/`, or the legacy vault.
2. Indexer parses file and computes hash.
3. If hash changed: upsert note, replace chunks/tags/links, generate embeddings.
4. Resolve basic backlinks by matching link target path.
5. API/MCP search through semantic or hybrid retrieval.
6. Context packs load system guidance, project config, project indexes, distilled context, and then supporting indexed notes.
7. Debug notes, session summaries, and reusable learnings are written back into project/system memory and immediately reindexed.

## Why these libraries

- `python-frontmatter`: robust YAML frontmatter extraction with markdown body separation.
- `watchdog`: low-latency filesystem event stream for local-first workflows.
- `pgvector`: vector ops inside Postgres, enabling operational simplicity.
- `SQLAlchemy`: clean typed ORM + async support + migration compatibility.
- `FastMCP`: straightforward MCP tool surface for AI agents.

## Security and Boundaries

- Memory is read from the local filesystem only.
- Writes are limited to controlled note-writing helpers for debug-note and session-summary capture.
- Embeddings provider is abstracted; default local provider avoids external dependency.
- Future hardening: authn/z on API + MCP transport restrictions.
