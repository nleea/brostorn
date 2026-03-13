# Promotion Workflow

Use cross-project memory when a lesson should outlive one project.

## Promote When

- the same bug shape can recur in multiple projects
- the fix encodes a reusable pattern
- the issue reveals an anti-pattern worth warning against
- the work changes how engineering decisions should be made

## Write Paths

- `recurring-bugs`
- `reusable-solutions`
- `anti-patterns`
- `architecture-lessons`

## Tooling

- `save_reusable_learning(...)` writes into `system/05-cross-project-memory/`
- `hooks/session_end.py` suggests promotion when a session ends with verified learnings
