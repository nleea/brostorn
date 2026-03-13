from __future__ import annotations

import hashlib
from dataclasses import dataclass

from memory_parsers.types import Chunk, ParsedNote


@dataclass(slots=True)
class ChunkingConfig:
    max_chars: int = 1200
    overlap_chars: int = 200


class MarkdownChunker:
    def __init__(self, config: ChunkingConfig) -> None:
        self._config = config

    def chunk(self, note: ParsedNote) -> list[Chunk]:
        lines = note.body_content.splitlines()
        blocks: list[str] = []
        current: list[str] = []

        for line in lines:
            if line.startswith("#") and current:
                blocks.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)

        if current:
            blocks.append("\n".join(current).strip())

        chunks: list[Chunk] = []
        idx = 0

        for block in blocks:
            if len(block) <= self._config.max_chars:
                chunks.append(self._build_chunk(idx, block, note))
                idx += 1
                continue

            start = 0
            while start < len(block):
                end = start + self._config.max_chars
                piece = block[start:end]
                chunks.append(self._build_chunk(idx, piece, note))
                idx += 1
                if end >= len(block):
                    break
                start = max(end - self._config.overlap_chars, start + 1)

        return chunks

    def _build_chunk(self, index: int, content: str, note: ParsedNote) -> Chunk:
        normalized = content.strip()
        est_tokens = max(1, len(normalized) // 4)
        return Chunk(
            index=index,
            content=normalized,
            metadata={
                "path": note.relative_path,
                "project": note.metadata.get("project"),
                "type": note.metadata.get("type"),
                "tags": note.tags,
            },
            token_estimate=est_tokens,
            content_hash=hashlib.sha256(normalized.encode("utf-8")).hexdigest(),
        )
