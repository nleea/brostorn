# Debug Command

Use this workflow to investigate and fix a bug without bypassing root cause analysis.

## Steps

1. Classify the task. If SIMPLE, skip steps 2–5.
2. Load context: `get_context_pack(task=..., project=...)`.
3. Check `search_bug_fixes` and `search_notes` for similar prior incidents.
4. Read architecture and module notes before touching code.
5. Inspect the implementation paths implicated by the context pack.
6. Form a root cause hypothesis before patching.
7. Implement the smallest coherent fix within the existing architecture.
8. Validate with targeted tests or manual verification.
9. Save a debug note: `save_debug_note(...)`.
10. If the learning is reusable across projects, update `system/05-cross-project-memory/`.

## Output Checklist

- Root cause identified
- Files changed listed
- Validation recorded
- Debug note written
