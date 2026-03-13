from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from memory_core.models import Note, NoteTag, Tag
from memory_core.schemas import SearchRequest, SearchResponse, SearchResultItem
from memory_vectorstore.embeddings import EmbeddingProvider
from memory_vectorstore.repository import SearchRepository


class SearchService:
    def __init__(self, embedding_provider: EmbeddingProvider) -> None:
        self.repo = SearchRepository()
        self.embedding_provider = embedding_provider

    async def semantic(self, db: AsyncSession, request: SearchRequest) -> SearchResponse:
        query_embedding = self.embedding_provider.embed([request.query])[0]
        rows = await self.repo.semantic_search(
            db=db,
            query_embedding=query_embedding,
            query_text=request.query,
            limit=request.limit,
            project=request.project,
            note_type=request.note_type,
            tags=request.tags,
        )
        items = [
            SearchResultItem(
                note_id=row["note_id"],
                chunk_id=row["chunk_id"],
                path=row["path"],
                title=row["title"],
                project=row["project"],
                note_type=row["note_type"],
                tags=list(row["tags"]),
                content=row["content"],
                score=float(row["score"]),
            )
            for row in rows
        ]
        return SearchResponse(query=request.query, items=items)

    async def hybrid(self, db: AsyncSession, request: SearchRequest) -> SearchResponse:
        query_embedding = self.embedding_provider.embed([request.query])[0]
        rows = await self.repo.hybrid_search(
            db=db,
            query_embedding=query_embedding,
            query_text=request.query,
            limit=request.limit,
            project=request.project,
            note_type=request.note_type,
            tags=request.tags,
        )
        items = [
            SearchResultItem(
                note_id=row["note_id"],
                chunk_id=row["chunk_id"],
                path=row["path"],
                title=row["title"],
                project=row["project"],
                note_type=row["note_type"],
                tags=list(row["tags"]),
                content=row["content"],
                score=float(row["score"]),
            )
            for row in rows
        ]
        return SearchResponse(query=request.query, items=items)


async def build_note_payload(note: Note, db: AsyncSession) -> dict:
    result = await db.execute(
        select(Tag.name)
        .join(NoteTag, NoteTag.tag_id == Tag.id)
        .where(NoteTag.note_id == note.id)
    )
    tags = list(result.scalars().all())
    return {
        "id": note.id,
        "path": note.path,
        "title": note.title,
        "project": note.project,
        "note_type": note.note_type,
        "tags": tags,
        "content": note.content,
        "metadata": note.metadata_json,
        "indexed_at": note.indexed_at,
    }
