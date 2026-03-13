---
title: Debug Workflow
type: workflow
---

# Debug

## Goal

Resolve a bug without bypassing root cause analysis or memory capture.

## Workflow

1. Load context with `get_context_pack(task=..., project=...)`.
2. Check `search_bug_fixes` and `search_notes` for similar incidents.
3. Read the relevant architecture and module notes before changing code.
4. Inspect the implementation paths implicated by the context pack.
5. Form a root cause hypothesis before patching.
6. Implement the smallest coherent fix in the existing architecture.
7. Validate with targeted tests or manual verification.
8. Save a bug note with `save_debug_note(...)`.
9. If behavior or architecture changed, update the relevant vault note.

## Output Checklist

- Root cause identified
- Files changed listed
- Validation recorded
- Debug note written
