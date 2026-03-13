# Claude Operating Guide

This repository uses a **custom MCP-based memory system** designed to provide persistent engineering context across multiple projects.

Before performing any task, classify it first (see Task Classification below).
Only load context from the memory system if the task is FAMILIAR or COMPLEX.

## Required reading on session start

Read these files before doing any work:

- `docs/AGENT_GUIDE.md` — full agent workflow, MCP usage, documentation structure
- `memory-system/system/AGENT_GUIDE.md` — global engineering brain, cross-project rules

---

# Memory System Overview

The engineering memory system lives in:

memory-system/

It provides:

- global reusable knowledge
- project-specific memory
- debugging history
- distilled architecture context
- reasoning contexts
- operational commands

The memory system is accessed through MCP tools.

---

# Memory Architecture

The system is organized into three layers.

GLOBAL MEMORY

memory-system/system/

Contains reusable knowledge such as:

- debugging patterns
- architectural lessons
- cross-project bugs
- reusable solutions

---

PROJECT MEMORY

memory-system/projects/<project>/

Each project contains:

docs/
contexts/
project.config.json

Docs contain:

- architecture
- debugging notes
- distilled context
- decisions
- deployment knowledge

---

SESSION MEMORY

projects/<project>/docs/sessions/

Each significant work session should be summarized here.

---

# Context Layers

When solving a task you must load context in this order:

1. global contexts
2. project contexts
3. distilled module docs
4. supporting architecture notes

Contexts live in:

memory-system/contexts/

and optionally:

memory-system/projects/<project>/contexts/

Contexts are **reasoning templates**, not documentation.

They help guide debugging and investigation.

---

# Task Classification

Classify the task before loading any context.

**SIMPLE — act directly, no MCP needed:**
- Add/modify a field in an existing model or schema
- Fix a typo, label, or static text
- Adjust CSS, spacing, or layout details
- Change a config value or constant
- Read or explain code already visible in context
- Rename a variable or function within a single file

**FAMILIAR — `search_memory()` only if uncertain:**
- New route following an existing pattern in the same router
- New component mirroring an existing one
- New service method similar to existing methods
- Minor UI changes in a known view or component

**COMPLEX — full MCP protocol required:**
- Bug with no obvious cause
- New module or feature touching multiple layers
- Changes to auth, sessions, DB schema, or core architecture
- Feature touching >3 files across different layers
- Unexpected behavior in a module that should be working

---

# MCP Tools

The memory system is accessed via MCP.

## Preferred call order (least to most expensive)

Use the lightest tool that gives enough context. Only escalate if previous step is insufficient.

```
1. search_memory(query, type="context_template", project)
   → identifies the most relevant context templates without loading them
   → use first for any new investigation

2. search_memory(query, type="bug_fix", project)
   → check if the bug or pattern was already solved

3. search_memory(query, project)
   → load only relevant note chunks, ranked by similarity

4. fetch_notes(by="id", value=note_id)
   → load one specific note in full when you have the ID

5. get_context(task, project, mode="pack")
   → loads contexts + distilled notes + supporting docs in bulk
   → WARNING: returns ~15k tokens, fills context quickly
   → use only when starting work in an unfamiliar module
     or when steps 1–4 do not provide enough context
```

- Use `get_context(task, project, mode="rank")` to explore relevant templates before committing to a full pack.
- Use `fetch_notes(by="project", value=project)` or `fetch_notes(by="recent")` for broader browsing.

Always inspect the returned payload before modifying code.

---

# Debugging Workflow

When debugging:

1. load the context pack
2. compare expected vs actual behavior
3. identify the root cause
4. implement a minimal fix
5. validate the behavior
6. document the fix

If the issue represents a reusable lesson:

promote it to:

memory-system/system/cross-project/

---

# Documentation Rules

When a bug is solved:

create or update a debugging note in:

projects/<project>/docs/debugging/

Include:

- symptom
- root cause
- solution
- files changed
- validation steps

## save_note(type="bug_fix") — required fields

```
type        : "bug_fix"
title       : short slug (e.g. "training-log-store-not-updated-after-upsert")
summary     : one-line description of the bug (required)
project     : e.g. "fitness-app"
symptom / root_cause / fix / files_changed / validation : optional structured fields
```

Notes are saved with an auto-generated `id` in frontmatter (e.g., `bf-2026-03-13-001`).
Use the `refs` frontmatter field to cross-reference related notes by ID.

---

# Session Memory

At the end of complex work sessions:

save a summary in:

projects/<project>/docs/sessions/

Include:

- task worked on
- contexts loaded
- key findings
- files modified
- follow-up work

## save_note(type="session") — required fields

```
type    : "session"
task    : one-line description of what was worked on (required)
project : e.g. "gym-trainer"
findings / files_modified / follow_ups : optional structured fields
```

## save_note(type="learning") — required fields

```
type          : "learning"
title         : short slug
summary       : one-line description (required)
lesson        : the reusable insight
applicability : when to apply it
project       : optional
```

> Filename convention: `YYYY-MM-DD-short-title.md` (max 5 words after date). Never use the full task description as filename.

---

# Important Rules

Do not:

- invent architecture
- skip context loading
- modify system memory without reason

Always:

- inspect context first
- follow debugging workflows
- document fixes properly

---

# Project Awareness

This workspace may contain multiple projects.

Examples:

- gym-trainer
- wsquote
- ERP services

The memory system separates them under:

memory-system/projects/

Always identify the correct project before saving memory.

---

# Expected Agent Behavior

Agents working in this repository must:

1. load context before reasoning
2. inspect architecture documentation
3. implement minimal safe changes
4. document new knowledge

This ensures the engineering brain improves over time.