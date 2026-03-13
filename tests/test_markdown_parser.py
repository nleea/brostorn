from pathlib import Path

from memory_parsers.markdown_parser import MarkdownParser


def test_parse_markdown_extracts_frontmatter_tags_and_links(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    note = vault / "architecture.md"
    note.write_text(
        """---
project: atlas
type: decision
tags:
  - backend
  - pgvector
---
# Architecture
Use [[ADR-001]] and [[Indexing|Indexer]].
Inline #fastapi tag.
""",
        encoding="utf-8",
    )

    parsed = MarkdownParser().parse(note, vault)

    assert parsed.title == "Architecture"
    assert parsed.metadata["project"] == "atlas"
    assert parsed.metadata["type"] == "decision"
    assert "backend" in parsed.tags
    assert "fastapi" in parsed.tags
    assert "ADR-001" in parsed.wiki_links


def test_parse_markdown_normalizes_date_frontmatter_for_json_storage(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    note = vault / "dated-note.md"
    note.write_text(
        """---
title: Dated Note
updated: 2026-03-11
tags:
  - docs
---
# Dated Note
""",
        encoding="utf-8",
    )

    parsed = MarkdownParser().parse(note, vault)

    assert parsed.frontmatter["updated"] == "2026-03-11"


def test_parse_markdown_context_template_keeps_structured_metadata(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    note = vault / "debug-calendar.md"
    note.write_text(
        """---
title: Debug Calendar
type: context_template
scope: project
project: fitness-app
problem_types:
  - calendar
  - completion
keywords:
  - calendar
  - meals
applies_to:
  - calendar
  - meals
related_distilled:
  - calendar
priority: 4
---
# Debug Calendar
""",
        encoding="utf-8",
    )

    parsed = MarkdownParser().parse(note, vault)

    assert parsed.metadata["type"] == "context_template"
    assert parsed.frontmatter["scope"] == "project"
    assert parsed.frontmatter["problem_types"] == ["calendar", "completion"]
    assert parsed.frontmatter["priority"] == 4
