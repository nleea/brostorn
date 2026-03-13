# AGENTS Instructions - Memory System

## Task Classification — do this first

Classify the task before loading any context. Only use MCP for FAMILIAR or COMPLEX tasks.

**SIMPLE — act directly, no MCP needed:**
- Add/modify a field in an existing model or schema
- Fix a typo, label, or static text
- Adjust CSS, spacing, or layout details
- Change a config value or constant
- Read or explain code already visible in context

**FAMILIAR — `search_notes()` only if uncertain:**
- New route or endpoint following an existing pattern
- New method similar to existing methods in the same service
- Minor changes in a known module

**COMPLEX — full MCP protocol required:**
- Bug with no obvious cause
- New module or cross-cutting feature
- Changes to auth, sessions, DB schema, or core architecture
- Feature touching >3 files across different layers

---

## Priority Rules

1. Read architecture docs before changing backend structure (`docs/ARCHITECTURE.md`).
2. Query memory first (API or MCP) before changing business rules or decisions.
3. Do not invent architectural decisions when relevant notes exist.
4. Keep Obsidian vault as source of truth; generated indexes are derived state.
5. Preserve compatibility with local-first operation.

## Required Workflow for Backend Changes

1. Check existing notes via MCP tool `search_notes` for context.
2. If change affects rules/architecture, search `search_decisions` and `get_project_context`.
3. Update code and, if needed, add/update note in vault documenting decision.
4. Re-index impacted notes (`POST /index/file` or `POST /index/rebuild`).

## MCP Usage Expectations

Use the lightest tool that gives enough context. Escalate only if needed.

```
1. rank_context_templates(task, project)   → find relevant context without loading it
2. search_bug_fixes(query, project)        → check for prior solutions
3. search_notes(query, project)            → load relevant chunks by similarity
4. get_note(note_id)                       → load one specific note in full
5. get_context_pack(task, project)         → WARNING: ~15k tokens, use only when
                                             module is unfamiliar or 1–4 insufficient
```

- Use `list_recent_notes` to detect latest context changes.

## save_debug_note — required fields

```
title       : short slug (e.g. "auth-token-not-refreshed-on-401")
summary     : one-line description of the bug (required — tool fails without it)
content     : full markdown body
project     : e.g. "fitness-app"
relative_dir: always "11-debugging" for bug notes
```

## save_session_summary — required fields

```
title   : descriptive session title
task    : one-line description of what was worked on (required — tool fails without it)
content : full markdown body
project : e.g. "fitness-app"
```

---

## Coding Standards

- Keep strong typing.
- Keep layers isolated (`parsers`, `vectorstore`, `core`, `apps`).
- Add tests for parser/chunking/indexing behavior when logic changes.
- Prefer additive migrations.
