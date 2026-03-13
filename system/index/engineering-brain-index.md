# Engineering Brain Index

The engineering brain has two layers:

## Layer 1 — Global Brain

Stored in:

`system/`

Contains knowledge shared across multiple projects:
- patterns
- skills
- commands
- rules
- reusable lessons

## Layer 2 — Project Brain

Stored in:

`projects/<project>/docs/`

Contains knowledge specific to one project:
- architecture
- debugging notes
- decisions
- distilled context
- session memory

## Workflow

When a task begins:

1. Load the global brain
2. Identify the project and load `projects/<project>/project.config.json`
3. Load the project brain
4. Use global workflows + project-specific context together

## Rule of Separation

Store knowledge in `system/` if it is reusable across projects.
Store knowledge in `projects/<project>/docs/` if it only applies to that project.
