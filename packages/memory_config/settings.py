from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(alias="DATABASE_URL")
    sync_database_url: str = Field(alias="SYNC_DATABASE_URL")

    memory_root_path: Path = Field(default=Path(__file__).resolve().parents[2], alias="MEMORY_ROOT_PATH")
    obsidian_vault_path: Path | None = Field(default=None, alias="OBSIDIAN_VAULT_PATH")
    active_project_name: str | None = Field(default=None, alias="MEMORY_ACTIVE_PROJECT")

    embedding_provider: str = Field(default="local", alias="EMBEDDING_PROVIDER")
    embedding_dimension: int = Field(default=384, alias="EMBEDDING_DIMENSION")
    embedding_model: str = Field(default="text-embedding-3-small", alias="EMBEDDING_MODEL")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")

    indexer_poll_seconds: float = Field(default=1.0, alias="INDEXER_POLL_SECONDS")
    chunk_max_chars: int = Field(default=1200, alias="CHUNK_MAX_CHARS")
    chunk_overlap_chars: int = Field(default=200, alias="CHUNK_OVERLAP_CHARS")

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8080, alias="API_PORT")
    mcp_server_name: str = Field(default="memory-mcp", alias="MCP_SERVER_NAME")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
