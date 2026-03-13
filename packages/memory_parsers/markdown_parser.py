from __future__ import annotations

import hashlib
import re
from datetime import date, datetime, time, timezone
from pathlib import Path

import frontmatter

from memory_parsers.types import ParsedNote

WIKI_LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
TAG_RE = re.compile(r"(?<!\w)#([a-zA-Z0-9_\-/]+)")


class MarkdownParser:
    def parse(self, absolute_path: Path, vault_root: Path) -> ParsedNote:
        raw = absolute_path.read_text(encoding="utf-8")
        post = frontmatter.loads(raw)
        body = post.content.strip()
        frontmatter_data = self._to_json_safe(dict(post.metadata))

        fm_tags = frontmatter_data.get("tags", [])
        if isinstance(fm_tags, str):
            fm_tags = [fm_tags]

        inline_tags = TAG_RE.findall(body)
        tags = sorted({str(tag).strip().lstrip("#") for tag in [*fm_tags, *inline_tags] if str(tag).strip()})
        wiki_links = [match.strip() for match in WIKI_LINK_RE.findall(body)]

        title = frontmatter_data.get("title")
        if not title:
            first_heading = next((ln[2:].strip() for ln in body.splitlines() if ln.startswith("# ")), None)
            title = first_heading or absolute_path.stem

        sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        stat = absolute_path.stat()

        metadata = {
            "project": frontmatter_data.get("project"),
            "type": frontmatter_data.get("type"),
            "tags": tags,
            "has_links": bool(wiki_links),
        }

        return ParsedNote(
            path=absolute_path,
            relative_path=str(absolute_path.relative_to(vault_root)),
            title=str(title),
            raw_content=raw,
            body_content=body,
            frontmatter=frontmatter_data,
            tags=tags,
            wiki_links=wiki_links,
            metadata=metadata,
            file_hash=sha,
            file_mtime=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
        )

    def _to_json_safe(self, value):
        if isinstance(value, dict):
            return {str(key): self._to_json_safe(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._to_json_safe(item) for item in value]
        if isinstance(value, tuple):
            return [self._to_json_safe(item) for item in value]
        if isinstance(value, (datetime, date, time)):
            return value.isoformat()
        return value
