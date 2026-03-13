# Context Loading Rules

1. Start with `get_context_pack(...)` before debugging, refactoring, or architecture changes.
2. Read the distilled note first when it exists.
3. Use only a small number of supporting notes unless deeper retrieval is necessary.
4. Fall back gracefully when a distilled note does not exist.
5. Avoid loading broad project context when a module-specific pack is sufficient.
