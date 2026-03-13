---
title: Document Fix Workflow
type: workflow
---

# Document Fix

## Goal

Capture the fix so future debugging starts from known context.

## Workflow

1. Gather the task summary, root cause, files changed, and validation evidence.
2. Save a debug note with `save_debug_note(...)`.
3. Save a session summary with `save_session_summary(...)` if the session included multiple changes or discoveries.
4. Update architecture or module notes when the expected system behavior changed.
5. Reindex the impacted notes if indexing is not already triggered automatically.

## Output Checklist

- Bug note saved
- Session summary saved when applicable
- Docs updated if behavior changed
