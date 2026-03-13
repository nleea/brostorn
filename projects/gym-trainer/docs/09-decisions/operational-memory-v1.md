---
title: Operational Memory V1
project: memory-system
type: decision
tags: [memory-system, decision, context-packs, session-memory]
---

# Operational Memory V1

## Decision

Extend the existing memory-system architecture with:

- distilled module summaries in `20-distilled-context/`
- session summaries in `21-session-memory/`
- repo-level workflow templates in `commands/`
- repo-level guardrails in `rules/`

## Rationale

- Agents need smaller, more operational context for debugging and refactoring.
- The current MCP/API/indexing flow already supports additive context assembly and controlled vault writes.
- Reusing the existing `ContextPackService` and `NoteWriterService` avoids a parallel implementation.

## Consequences

- `get_context_pack(...)` should read a distilled note first when present.
- Supporting notes should remain intentionally small for token efficiency.
- Session memory is persisted through the same write-and-reindex path as debug notes.
- Existing MCP tools and vault structure remain compatible.
