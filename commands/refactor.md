---
title: Refactor Workflow
type: workflow
---

# Refactor

## Goal

Improve structure or maintainability without changing behavior accidentally.

## Workflow

1. Load the nearest context pack and distilled note first.
2. Read architecture or pattern notes related to the area.
3. Identify current responsibilities, boundaries, and call paths.
4. State the invariant behavior that must remain true.
5. Make incremental edits that preserve the existing architecture.
6. Run focused validation for the touched behavior.
7. Update notes if module structure or responsibilities changed.
8. Save a session summary with `save_session_summary(...)`.

## Output Checklist

- Behavior invariants captured
- Refactor scope bounded
- Validation completed
- Session summary written
