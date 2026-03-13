from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from memory_config.settings import Settings
from memory_core.models import IndexingRun, Note, NoteLink
from memory_core.workspace import MemoryWorkspace
from memory_parsers.chunker import ChunkingConfig, MarkdownChunker
from memory_parsers.markdown_parser import MarkdownParser
from memory_vectorstore.embeddings import EmbeddingProvider
from memory_vectorstore.repository import NoteRepository

logger = logging.getLogger(__name__)


class VaultIndexer:
    def __init__(self, settings: Settings, embedding_provider: EmbeddingProvider) -> None:
        self.settings = settings
        self.workspace = MemoryWorkspace(
            root_path=settings.memory_root_path,
            legacy_vault_path=settings.obsidian_vault_path,
            active_project_name=settings.active_project_name,
        )
        self.vault_path = self.workspace.root_path
        self.parser = MarkdownParser()
        self.chunker = MarkdownChunker(
            ChunkingConfig(max_chars=settings.chunk_max_chars, overlap_chars=settings.chunk_overlap_chars)
        )
        self.embedder = embedding_provider
        self.repo = NoteRepository()

    async def rebuild(self, db: AsyncSession) -> tuple[int, int]:
        run = IndexingRun(status="running")
        db.add(run)
        await db.flush()

        indexed = 0
        scanned = 0
        try:
            known_paths = set()
            for file_path in self._iter_markdown_files(self.workspace.iter_index_roots()):
                scanned += 1
                known_paths.add(str(file_path.relative_to(self.vault_path)))
                indexed += await self.index_file(db, file_path)

            result = await db.execute(select(Note.path))
            current_paths = set(result.scalars().all())
            deleted = 0
            for missing in current_paths - known_paths:
                deleted += await self.repo.delete_note_by_path(db, missing)

            await self._resolve_links(db)

            run.status = "completed"
            run.finished_at = datetime.now(tz=timezone.utc)
            run.notes_scanned = scanned
            run.notes_indexed = indexed
            run.notes_deleted = deleted
            await db.commit()
            logger.info("Rebuild completed: scanned=%s indexed=%s deleted=%s", scanned, indexed, deleted)
            return indexed, deleted
        except Exception as exc:
            await db.rollback()
            run.status = "failed"
            run.finished_at = datetime.now(tz=timezone.utc)
            run.error_message = str(exc)
            db.add(run)
            await db.commit()
            logger.exception("Index rebuild failed")
            raise

    async def index_relative_path(self, db: AsyncSession, relative_path: str) -> bool:
        absolute = (self.vault_path / relative_path).resolve()
        if not absolute.exists():
            deleted = await self.repo.delete_note_by_path(db, relative_path)
            await db.commit()
            return bool(deleted)
        changed = await self.index_file(db, absolute)
        await self._resolve_links(db)
        await db.commit()
        return bool(changed)

    async def index_file(self, db: AsyncSession, file_path: Path) -> int:
        if file_path.suffix.lower() != ".md":
            return 0

        parsed = self.parser.parse(file_path, self.vault_path)
        existing = await self.repo.get_by_path(db, parsed.relative_path)
        if existing and existing.file_hash == parsed.file_hash:
            return 0

        note = await self.repo.upsert_note(db, parsed)
        chunks = self.chunker.chunk(parsed)
        vectors = self.embedder.embed([chunk.content for chunk in chunks]) if chunks else []

        await self.repo.replace_chunks(db, str(note.id), chunks, vectors)
        await self.repo.replace_tags(db, note, parsed.tags)
        await self.repo.replace_links(db, note, parsed.wiki_links)
        note.indexed_at = datetime.now(tz=timezone.utc)

        logger.info("Indexed note path=%s chunks=%s", parsed.relative_path, len(chunks))
        return 1

    async def _resolve_links(self, db: AsyncSession) -> None:
        result = await db.execute(select(Note))
        notes = list(result.scalars().all())
        path_map = {note.path: note.id for note in notes}

        result_links = await db.execute(select(NoteLink))
        for link in result_links.scalars().all():
            link.target_note_id = path_map.get(link.target_path)

    @staticmethod
    def _iter_markdown_files(roots: list[Path]):
        for root in roots:
            for path in root.rglob("*.md"):
                if path.is_file() and not any(part.startswith(".") for part in path.parts):
                    yield path
