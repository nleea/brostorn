from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class ParsedNote:
    path: Path
    relative_path: str
    title: str
    raw_content: str
    body_content: str
    frontmatter: dict
    tags: list[str] = field(default_factory=list)
    wiki_links: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    file_hash: str = ""
    file_mtime: datetime | None = None


@dataclass(slots=True)
class Chunk:
    index: int
    content: str
    metadata: dict
    token_estimate: int
    content_hash: str
