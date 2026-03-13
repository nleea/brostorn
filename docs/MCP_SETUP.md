# MCP Setup

## Run MCP server

```bash
cd memory-system
make run-mcp
```

## Suggested tool exposure

The server exposes read-only tools:

- `search_notes`
- `get_note`
- `get_project_context`
- `list_recent_notes`
- `search_decisions`
- `search_bug_fixes`

## Claude Desktop config example

```json
{
  "mcpServers": {
    "memory-system": {
      "command": "python",
      "args": ["-m", "apps.mcp_server.main"],
      "cwd": "/absolute/path/to/memory-system",
      "env": {
        "DATABASE_URL": "postgresql+asyncpg://memory:memory@localhost:5434/memory_db",
        "SYNC_DATABASE_URL": "postgresql+psycopg://memory:memory@localhost:5434/memory_db",
        "MEMORY_ROOT_PATH": "/absolute/path/to/memory-system",
        "MEMORY_ACTIVE_PROJECT": "gym-trainer",
        "OBSIDIAN_VAULT_PATH": "/absolute/path/to/memory-system/knowledge/obsidian-vault"
      }
    }
  }
}
```

## Codex integration note

Use the same command and env in your Codex MCP configuration so both agents read identical indexed memory.

`MEMORY_ROOT_PATH` is the portable root used by the runtime. `OBSIDIAN_VAULT_PATH` is now legacy compatibility only.
