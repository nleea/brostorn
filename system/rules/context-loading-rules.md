# Context Loading Rules

1. Classify the task first (SIMPLE / FAMILIAR / COMPLEX) before loading anything.
2. For SIMPLE tasks, act directly — no context loading needed.
3. For FAMILIAR tasks, use `search_notes(...)` only if uncertain.
4. For COMPLEX tasks, start with `get_context_pack(...)`.
5. Read the distilled note first when it exists.
6. Use only a small number of supporting notes unless deeper retrieval is necessary.
7. Fall back gracefully when a distilled note does not exist.
8. Avoid loading broad project context when a module-specific pack is sufficient.
