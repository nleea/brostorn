
These files contain concise knowledge about module behavior, contracts, and pitfalls.

Distilled context should always be loaded before deeper documentation.

---

# Step 4 — Load Supporting Notes

If additional context is needed, load notes from:

- architecture
- frontend
- backend
- debugging history
- architecture decisions

Avoid loading excessive context.

Focus only on relevant notes.

---

# Step 5 — Inspect Real Code

Documentation may be incomplete or outdated.

Always verify behavior by inspecting the real code paths.

Do not assume documentation is fully correct.

---

# Step 6 — Analyze the Problem

If the task involves debugging:

1. Identify expected behavior
2. Identify actual behavior
3. Determine the root cause

Avoid quick patches that hide the real issue.

---

# Step 7 — Implement the Change

Apply fixes or improvements aligned with the architecture.

Prefer consistent patterns over introducing new structures.

Do not mix refactor and feature work unless requested.

---

# Step 8 — Validate the Result

Verify the change using realistic scenarios.

Examples:

- UI behavior is correct
- state updates reactively
- no regressions occur

Validation should reflect how the feature is actually used.

---

# Step 9 — Document the Fix

If the task involved debugging or behavior changes:

Create or update a debugging note in:
[[11-debugging/index|index]]