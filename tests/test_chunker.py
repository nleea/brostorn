from pathlib import Path

from memory_parsers.chunker import ChunkingConfig, MarkdownChunker
from memory_parsers.types import ParsedNote


def test_chunker_splits_large_block() -> None:
    content = "# Section\n" + ("abcde" * 500)
    note = ParsedNote(
        path=Path("test.md"),
        relative_path="test.md",
        title="Test",
        raw_content=content,
        body_content=content,
        frontmatter={},
    )

    chunks = MarkdownChunker(ChunkingConfig(max_chars=500, overlap_chars=50)).chunk(note)

    assert len(chunks) >= 5
    assert chunks[0].index == 0
    assert all(chunk.content_hash for chunk in chunks)
