# Refactor Command

Use this workflow when improving internal structure without changing behavior.

## Steps

1. Classify the task. If SIMPLE, skip steps 2–3.
2. Load the nearest context pack and distilled note.
3. Read architecture or pattern notes related to the area.
4. Identify current responsibilities, boundaries, and call paths.
5. State the invariant behavior that must remain true.
6. Make incremental edits that preserve the existing architecture.
7. Run focused validation for the touched behavior.
8. Update notes if module structure or responsibilities changed.
9. Save a session summary: `save_session_summary(...)`.

## Output Checklist

- Behavior invariants captured
- Refactor scope bounded
- Validation completed
- Session summary written
