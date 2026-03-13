# Agent Operating Instructions

This repository contains a multi-project engineering workspace supported by a persistent MCP-based memory system.

Agents must use the memory system before making architectural decisions.

## Required reading on session start

Read these files before doing any work:

- `docs/AGENT_GUIDE.md` — full agent workflow, MCP usage, documentation structure
- `memory-system/system/AGENT_GUIDE.md` — global engineering brain, cross-project rules

---

# Task Classification — do this first

Classify the task before deciding what to load. Only escalate to MCP if the task is FAMILIAR or COMPLEX.

**SIMPLE — act directly, no MCP needed:**
- Add/modify a field in an existing model or schema
- Fix a typo, label, or static text
- Adjust CSS, spacing, or layout details
- Change a config value or constant
- Read or explain code already visible in context
- Rename a variable or function within a single file

**FAMILIAR — `search_notes()` only if uncertain:**
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

# Core Principle

Do not reason from scratch.

For FAMILIAR and COMPLEX tasks, load context from the memory system first.

---

# Memory System Structure

memory-system/

Contains:

system/        global reusable knowledge
contexts/      reusable reasoning templates
projects/      project-specific memory

---

# Global Contexts

memory-system/contexts/

Examples:

debug-auth
debug-api-endpoint
debug-state-management
analyze-data-flow

These contexts apply across multiple projects.

---

# Project Contexts

memory-system/projects/<project>/contexts/

Examples:

debug-calendar
debug-meals
debug-quote-engine

These contexts apply only to a specific project domain.

---

# Project Documentation

Each project contains:

memory-system/projects/<project>/docs/

Important sections:

architecture
backend
frontend
database
debugging
distilled
sessions

---

# Context Pack Workflow

Use the lightest tool that gives enough context. Escalate only if needed.

```
1. rank_context_templates(task, project)
   → identifies relevant context template without loading it

2. search_bug_fixes(query, project)
   → check if the problem was already solved

3. search_notes(query, project)
   → load only relevant note chunks, ranked by similarity

4. get_note(note_id)
   → load one specific note in full

5. get_context_pack(task, project)
   → loads contexts + distilled notes + supporting docs in bulk
   → WARNING: ~15k tokens, fills context quickly
   → use only when module is unfamiliar or steps 1–4 are insufficient
```

Then inspect relevant code and begin reasoning.

---

# Debugging Process

Use structured debugging.

Always determine:

expected behavior
actual behavior
difference
root cause

Never apply blind fixes.

---

# Memory Updates

When solving a bug:

update:

projects/<project>/docs/debugging/

When finishing complex work:

update:

projects/<project>/docs/sessions/

When discovering reusable lessons:

update:

system/cross-project/

---

# Context Usage Rules

Contexts are not documentation.

They are reasoning workflows.

Use them to guide investigation.

Do not copy them into documentation.

---

# Project Detection

Projects are defined in:

memory-system/projects/

Each project has:

project.config.json

Use this configuration to understand:

- workspace paths
- modules
- entry points

---

# Implementation Guidelines

Agents should:

prefer minimal safe changes
avoid architecture rewrites
reuse existing patterns
respect project boundaries

---

## save_debug_note — required fields

```
title       : short slug (e.g. "training-log-store-not-updated-after-upsert")
summary     : one-line description of the bug (required — tool fails without it)
content     : full markdown body
project     : e.g. "fitness-app"
relative_dir: always "debugging" for bug notes
```

## save_session_summary — required fields

```
title   : descriptive session title
task    : one-line description of what was worked on (required — tool fails without it)
content : full markdown body
project : e.g. "fitness-app"
```

Notes are saved with an auto-generated `id` in frontmatter (e.g., `bf-2026-03-13-001`).
Use the `refs` frontmatter field to cross-reference related notes by ID.

# Goal

The goal of this system is to build a persistent engineering brain that improves with every solved problem.

Agents must contribute to this knowledge system as they work.