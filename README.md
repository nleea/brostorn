# Memory System (Multi-Project Engineering Brain)

Sistema de memoria técnica local-first con indexado semántico en PostgreSQL + pgvector, API FastAPI y servidor MCP para agentes. El runtime ahora soporta una capa global `system/` y memoria por proyecto en `projects/<project>/docs/`, manteniendo compatibilidad con el vault legado.

## 1) Resumen de arquitectura

- `memory-system/` es la raíz portable del workspace de memoria.
- `system/` contiene conocimiento global reutilizable.
- `projects/<project>/docs/` contiene memoria específica por proyecto.
- `knowledge/obsidian-vault` sigue siendo un fallback legado compatible.
- `apps/indexer` sincroniza notas a Postgres en modo rebuild + incremental.
- `apps/api` expone indexación y búsqueda semántica/híbrida.
- `apps/mcp_server` expone herramientas MCP reutilizando el mismo backend.
- Proveedor de embeddings desacoplado (`local` por defecto, `openai` opcional).
- `commands/` y `rules/` añaden workflows operativos y guardrails para agentes sin cambiar el backend.

## 2) Estructura

```text
memory-system/
  apps/
    api/
    indexer/
    mcp_server/
  packages/
    config/
    core/
    parsers/
    vectorstore/
  migrations/
  scripts/
  tests/
  docs/
  system/
  projects/
  contexts/
  hooks/
  schemas/
  commands/
  rules/
  knowledge/obsidian-vault/
```

## 3) Requisitos

- Python 3.12
- Docker + Docker Compose

## 4) Arranque rápido

```bash
cd memory-system
cp .env.example .env
docker compose up -d db
pip install -e .[dev]
alembic upgrade head
make run-api
```

En otra terminal:

```bash
cd memory-system
make run-indexer
```

MCP server:

```bash
cd memory-system
make run-mcp
```

Registro de MCP en Codex (una vez):

```bash
cd memory-system
./scripts/register_codex_mcp.sh /RUTA/ABSOLUTA/TU/VAULT
```

También puedes fijar un proyecto activo:

```bash
cd memory-system
./scripts/register_codex_mcp.sh "$(pwd)" gym-trainer
```

## 5) Endpoints

- `GET /health`
- `POST /index/rebuild`
- `POST /index/file`
- `POST /search/semantic`
- `POST /search/hybrid`
- `GET /notes/{id}`
- `GET /projects/{project}/context`
- `GET /decisions/recent`

## 6) Esquema de datos

Tablas principales:

- `notes`
- `note_chunks`
- `tags`
- `note_tags`
- `note_links`
- `indexing_runs`
- `embedding_jobs`

Incluye hash de archivo, metadata JSONB, vector embedding, timestamps y estado de indexación.

## 7) MCP Tools

- `search_notes`
- `get_note`
- `get_project_context`
- `list_recent_notes`
- `search_decisions`
- `search_bug_fixes`
- `get_context_pack`
- `save_debug_note`
- `save_session_summary`

## 7.1) Context Packs

Context packs are lightweight heuristics on top of the existing search/index pipeline. They:

- infer the most probable module from a task string
- load `system/` guidance first
- load active project configuration
- load project index notes
- attempt to load the project distilled note
- prioritize canonical supporting notes for that area
- enrich the result with a small hybrid-search slice
- return a compact bundle for agents before code changes

First packs included:

- `auth`
- `deployment`
- `database`
- `backend-jobs`

Returned structure now includes:

- `system_notes`: global reusable guidance
- `project_config_note`: active `project.config.json` rendered as operational context
- `project_index_notes`: project guide/index notes
- `distilled_note`: the concise vault summary when it exists
- `supporting_notes`: a small set of indexed notes for depth
- `notes`: combined ordered list kept for compatibility

## 7.2) Active Project Resolution

Resolution order:

1. explicit tool parameter like `project="gym-trainer"`
2. `MEMORY_ACTIVE_PROJECT`
3. current working directory inference using `project.config.json`
4. the only configured project, if there is just one

The runtime maps a project slug to the indexed note project key through `project.config.json`.

## 7.3) Session Memory

Session summaries are markdown notes written into `21-session-memory/` through the same write + reindex flow used by debug notes.

Use them to capture:

- task worked on
- context pack and notes loaded
- key findings
- files modified
- validation performed
- follow-up items

## 7.4) Commands and Rules

- `commands/` contains reusable workflow templates for debugging, refactoring, flow analysis, and fix documentation.
- `rules/` contains lightweight guardrails for context loading, debugging discipline, and documentation updates.
- `contexts/` contains recurring task templates such as `debug-auth` and `debug-calendar`.
- `hooks/` contains session start/end helpers that reuse the workspace resolver and context-pack heuristics.
- `schemas/` contains JSON schema files documenting project config and note contracts.

These folders are repo guidance for agents. They do not replace the indexed vault or MCP tools.

## 7.5) Validation-Aware Debug Notes

`save_debug_note(...)` now supports a debug `status` of:

- `open`
- `fixed`
- `verified`

It also supports structured `validation_steps` and `validation_evidence` so bug notes can track whether a fix is only proposed, implemented, or actually confirmed.

## 7.6) Reusable Learning

Cross-project lessons can now be promoted into `system/05-cross-project-memory/`.

The write path is available through:

- `save_reusable_learning(...)` in MCP/API

Use it for recurring bugs, reusable solutions, anti-patterns, and architecture lessons.

## 8) Tests

```bash
cd memory-system
poetry run pytest -q
```

## 9) Notas de diseño

- `python-frontmatter` evita parser manual frágil para YAML.
- `watchdog` habilita indexación reactiva local.
- `hybrid search` mezcla score semántico y léxico con peso configurable.

## 10) TODO explícitos

- Añadir autenticación/autorización para API y MCP en entornos multiusuario.
- Mejorar parser de wikilinks para subcarpetas complejas y anchors avanzados.
- Añadir reintentos y cola persistente para `embedding_jobs`.
- Añadir evaluación de relevancia y observabilidad (métricas/tracing).

## 11) Uso desde Codex o Claude

Recommended flow:

1. Read the relevant file in `commands/`.
2. Load context with `get_context_pack(...)`.
3. Inspect supporting code and implement the change.
4. Save `save_debug_note(...)` or `save_session_summary(...)` when the work is complete.

See [docs/MULTI_PROJECT_MEMORY.md](/Users/nelsonborrego/Desktop/CO/ng2/memory-system/docs/MULTI_PROJECT_MEMORY.md) for the detailed multi-project model.
