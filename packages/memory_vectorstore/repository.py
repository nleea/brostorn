from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Integer, String, bindparam, delete, select, text
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from sqlalchemy.ext.asyncio import AsyncSession

from memory_core.models import Note, NoteChunk, NoteLink, NoteTag, Tag
from memory_parsers.types import Chunk, ParsedNote


class NoteRepository:
    async def get_by_path(self, db: AsyncSession, relative_path: str) -> Note | None:
        result = await db.execute(select(Note).where(Note.path == relative_path))
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, note_id: str) -> Note | None:
        result = await db.execute(select(Note).where(Note.id == note_id))
        return result.scalar_one_or_none()

    async def upsert_note(self, db: AsyncSession, parsed: ParsedNote) -> Note:
        note = await self.get_by_path(db, parsed.relative_path)
        if note is None:
            note = Note(
                path=parsed.relative_path,
                title=parsed.title,
                project=parsed.metadata.get("project"),
                note_type=parsed.metadata.get("type"),
                content=parsed.body_content,
                frontmatter=parsed.frontmatter,
                metadata_json=parsed.metadata,
                file_hash=parsed.file_hash,
                file_mtime=parsed.file_mtime,
                indexing_status="indexed",
            )
            db.add(note)
            await db.flush()
        else:
            note.title = parsed.title
            note.project = parsed.metadata.get("project")
            note.note_type = parsed.metadata.get("type")
            note.content = parsed.body_content
            note.frontmatter = parsed.frontmatter
            note.metadata_json = parsed.metadata
            note.file_hash = parsed.file_hash
            note.file_mtime = parsed.file_mtime
            note.indexing_status = "indexed"
        return note

    async def replace_chunks(
        self,
        db: AsyncSession,
        note_id: str,
        chunks: Sequence[Chunk],
        embeddings: Sequence[list[float]],
    ) -> None:
        await db.execute(delete(NoteChunk).where(NoteChunk.note_id == note_id))
        for item, vector in zip(chunks, embeddings, strict=True):
            db.add(
                NoteChunk(
                    note_id=note_id,
                    chunk_index=item.index,
                    content=item.content,
                    content_hash=item.content_hash,
                    token_estimate=item.token_estimate,
                    metadata_json=item.metadata,
                    embedding=vector,
                )
            )

    async def replace_tags(self, db: AsyncSession, note: Note, tags: list[str]) -> None:
        await db.execute(delete(NoteTag).where(NoteTag.note_id == note.id))
        for tag_name in tags:
            result = await db.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            if tag is None:
                tag = Tag(name=tag_name)
                db.add(tag)
                await db.flush()
            db.add(NoteTag(note_id=note.id, tag_id=tag.id))

    async def replace_links(self, db: AsyncSession, note: Note, links: list[str]) -> None:
        await db.execute(delete(NoteLink).where(NoteLink.source_note_id == note.id))
        for link in links:
            target = f"{link}.md" if not link.endswith(".md") else link
            db.add(NoteLink(source_note_id=note.id, target_path=target, link_text=link))

    async def delete_note_by_path(self, db: AsyncSession, relative_path: str) -> int:
        note = await self.get_by_path(db, relative_path)
        if note is None:
            return 0
        await db.delete(note)
        return 1


class SearchRepository:
    async def get_notes_by_paths(
        self,
        db: AsyncSession,
        paths: list[str],
        project: str | None = None,
    ) -> list[Note]:
        if not paths:
            return []

        query = select(Note).where(Note.path.in_(paths))
        if project is not None:
            query = query.where(Note.project == project)

        result = await db.execute(query)
        notes = list(result.scalars().all())
        notes_by_path = {note.path: note for note in notes}
        return [notes_by_path[path] for path in paths if path in notes_by_path]

    async def get_note_by_id(self, db: AsyncSession, note_id: str) -> Note | None:
        result = await db.execute(select(Note).where(Note.id == note_id))
        return result.scalar_one_or_none()

    @staticmethod
    def _search_query(sql: str):
        statement = text(sql)
        params = {
            "embedding": bindparam("embedding", type_=String()),
            "query_text": bindparam("query_text", type_=String()),
            "project": bindparam("project", type_=String()),
            "note_type": bindparam("note_type", type_=String()),
            "tags": bindparam("tags", type_=ARRAY(TEXT)),
            "tag_count": bindparam("tag_count", type_=Integer()),
            "limit": bindparam("limit", type_=Integer()),
        }
        active_params = [param for name, param in params.items() if f":{name}" in sql]
        return statement.bindparams(*active_params)

    async def semantic_search(
        self,
        db: AsyncSession,
        query_embedding: list[float],
        query_text: str,
        limit: int,
        project: str | None,
        note_type: str | None,
        tags: list[str] | None,
    ) -> list[dict]:
        sql = self._search_query(
            """
            SELECT
              n.id AS note_id,
              c.id AS chunk_id,
              n.path,
              n.title,
              n.project,
              n.note_type,
              c.content,
              (1 - (c.embedding <=> CAST(:embedding AS vector))) AS score,
              COALESCE(array_agg(t.name) FILTER (WHERE t.name IS NOT NULL), '{}') AS tags
            FROM note_chunks c
            JOIN notes n ON n.id = c.note_id
            LEFT JOIN note_tags nt ON nt.note_id = n.id
            LEFT JOIN tags t ON t.id = nt.tag_id
            WHERE (CAST(:project AS TEXT) IS NULL OR n.project = CAST(:project AS TEXT))
              AND (CAST(:note_type AS TEXT) IS NULL OR n.note_type = CAST(:note_type AS TEXT))
              AND (CAST(:tag_count AS INTEGER) = 0 OR EXISTS (
                   SELECT 1 FROM note_tags nt2
                   JOIN tags t2 ON t2.id = nt2.tag_id
                   WHERE nt2.note_id = n.id AND t2.name = ANY(CAST(:tags AS text[]))
              ))
            GROUP BY n.id, c.id
            ORDER BY c.embedding <=> CAST(:embedding AS vector)
            LIMIT CAST(:limit AS INTEGER)
            """
        )
        result = await db.execute(
            sql,
            {
                "embedding": str(query_embedding),
                "project": project,
                "note_type": note_type,
                "tags": tags or [],
                "tag_count": len(tags or []),
                "limit": limit,
                "query_text": query_text,
            },
        )
        return [dict(row._mapping) for row in result]

    async def hybrid_search(
        self,
        db: AsyncSession,
        query_embedding: list[float],
        query_text: str,
        limit: int,
        project: str | None,
        note_type: str | None,
        tags: list[str] | None,
    ) -> list[dict]:
        sql = self._search_query(
            """
            WITH ranked AS (
              SELECT
                n.id AS note_id,
                c.id AS chunk_id,
                n.path,
                n.title,
                n.project,
                n.note_type,
                c.content,
                (1 - (c.embedding <=> CAST(:embedding AS vector))) AS semantic_score,
                ts_rank_cd(to_tsvector('english', c.content), plainto_tsquery('english', :query_text)) AS lexical_score
              FROM note_chunks c
              JOIN notes n ON n.id = c.note_id
              WHERE (CAST(:project AS TEXT) IS NULL OR n.project = CAST(:project AS TEXT))
                AND (CAST(:note_type AS TEXT) IS NULL OR n.note_type = CAST(:note_type AS TEXT))
                AND (CAST(:tag_count AS INTEGER) = 0 OR EXISTS (
                     SELECT 1 FROM note_tags nt2
                     JOIN tags t2 ON t2.id = nt2.tag_id
                     WHERE nt2.note_id = n.id AND t2.name = ANY(CAST(:tags AS text[]))
                ))
            )
            SELECT
              r.note_id,
              r.chunk_id,
              r.path,
              r.title,
              r.project,
              r.note_type,
              r.content,
              (0.75 * r.semantic_score + 0.25 * r.lexical_score) AS score,
              COALESCE(array_agg(t.name) FILTER (WHERE t.name IS NOT NULL), '{}') AS tags
            FROM ranked r
            LEFT JOIN note_tags nt ON nt.note_id = r.note_id
            LEFT JOIN tags t ON t.id = nt.tag_id
            GROUP BY r.note_id, r.chunk_id, r.path, r.title, r.project, r.note_type, r.content, r.semantic_score, r.lexical_score
            ORDER BY score DESC
            LIMIT CAST(:limit AS INTEGER)
            """
        )
        result = await db.execute(
            sql,
            {
                "embedding": str(query_embedding),
                "query_text": query_text,
                "project": project,
                "note_type": note_type,
                "tags": tags or [],
                "tag_count": len(tags or []),
                "limit": limit,
            },
        )
        return [dict(row._mapping) for row in result]

    async def list_recent_by_type(
        self,
        db: AsyncSession,
        note_type: str,
        limit: int = 10,
        project: str | None = None,
    ) -> list[Note]:
        query = select(Note).where(Note.note_type == note_type)
        if project is not None:
            query = query.where(Note.project == project)
        result = await db.execute(query.order_by(Note.updated_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def project_context(self, db: AsyncSession, project: str, limit: int = 30) -> list[Note]:
        result = await db.execute(
            select(Note).where(Note.project == project).order_by(Note.updated_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
