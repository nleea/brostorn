# Agent Guide

This directory contains the **global engineering brain** shared across multiple projects.

It provides reusable patterns, rules, workflows, contexts, and cross-project memory.

Agents must use this system before working inside any specific project.

---

# Purpose

The `system/` directory stores knowledge that is reusable across projects.

It contains:

- global engineering workflows
- reusable debugging patterns
- architectural rules
- reasoning contexts
- documentation standards
- cross-project lessons and recurring problems

It should NOT contain:

- project-specific architecture
- repository-specific file paths
- debugging history tied to a single project

Project-specific knowledge must live under:

memory-system/projects/<project>/

---

# Memory System Architecture

The engineering brain is organized into three layers.

## Global Knowledge

memory-system/system/

Reusable knowledge across projects:

- debugging workflows
- architecture patterns
- documentation rules
- cross-project memory

---

## Reasoning Contexts

memory-system/contexts/

Contexts are **problem-solving templates** that guide investigation.

Examples:

- debug-auth
- debug-state-management
- debug-api-endpoint
- analyze-data-flow

Contexts are not documentation.

They help agents reason about common classes of problems.

---

## Project Memory

memory-system/projects/<project>/

Each project contains:

docs/
contexts/
project.config.json

Docs contain:

- architecture
- backend/frontend design
- database structure
- debugging history
- distilled context
- deployment knowledge

---

# Project Resolution

Projects are resolved through:

1. explicit MCP tool parameter
2. environment variable `MEMORY_ACTIVE_PROJECT`
3. workspace path resolution via `project.config.json`

Agents should always determine the active project before saving memory.

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

# Standard Usage Flow

When working on a task:

0. **Classify the task** (see above). Only continue below for FAMILIAR or COMPLEX tasks.

1. Read:

system/index/system-index.md
system/index/engineering-brain-index.md

2. Load relevant global rules and commands.

3. Identify the active project.

4. Load the project's configuration:

projects/<project>/project.config.json

5. Load reasoning contexts when relevant:

memory-system/contexts/

or

projects/<project>/contexts/

6. Load project distilled context:

projects/<project>/docs/distilled/

7. Inspect the real code.

8. Apply the debugging or implementation workflow.

9. Document learnings back into memory.

---

# Context Loading Order

When analyzing a task, context should be loaded in this order:

1. global contexts
2. project contexts
3. project distilled context
4. supporting architecture docs
5. codebase

This ensures reasoning starts from reusable patterns before inspecting implementation details.

---

# MCP Usage

The memory system is accessed through MCP tools.

Use the lightest tool that gives enough context. Escalate only if needed.

```
1. search_memory(query, type="context_template", project)
   → identifies relevant context templates without loading them

2. search_memory(query, type="bug_fix", project)
   → check if the problem was already solved

3. search_memory(query, project)
   → load only relevant note chunks, ranked by similarity

4. fetch_notes(by="id", value=note_id)
   → load one specific note in full

5. get_context(task, project, mode="pack")
   → loads contexts + distilled notes + supporting docs in bulk
   → WARNING: ~15k tokens, fills context quickly
   → use only when module is unfamiliar or steps 1–4 are insufficient

Use get_context(task, project, mode="rank") to explore relevant templates before committing to a full pack.
Use fetch_notes(by="project", value=project) or fetch_notes(by="recent") for broader browsing.
```

---

# Debugging Workflow

When debugging an issue:

1. load context pack
2. compare expected vs actual behavior
3. identify root cause
4. implement minimal fix
5. validate behavior
6. document the solution

Debugging notes must be saved in:

projects/<project>/docs/debugging/

Each note should include:

- symptom
- root cause
- solution
- files changed
- validation steps
- status

Bug status lifecycle:

open → fixed → verified

---

# Session Memory

At the end of complex work sessions, save a summary in:

projects/<project>/docs/sessions/

Include:

- task worked on
- contexts loaded
- key findings
- files modified
- validation results
- follow-up work

## save_note(type="bug_fix") — required fields

```
type        : "bug_fix"
title       : short slug (e.g. "auth-token-not-refreshed-on-401")
summary     : one-line description of the bug (required)
project     : e.g. "fitness-app"
symptom / root_cause / fix / files_changed / validation : optional structured fields
```

## save_note(type="session") — required fields

```
type    : "session"
task    : one-line description of what was worked on (required)
project : e.g. "fitness-app"
findings / files_modified / follow_ups : optional structured fields
```

## save_note(type="learning") — required fields

```
type          : "learning"
title         : short slug
summary       : one-line description (required)
lesson        : the reusable insight
applicability : when to apply it
project       : optional (cross-project learnings can omit it)
```

## Note ID and cross-referencing

Notes are saved with an auto-generated `id` in frontmatter (e.g., `bf-2026-03-13-001`).
Use the `refs` frontmatter field to cross-reference related notes by ID.

Example frontmatter:

```yaml
---
id: bf-2026-03-13-001
type: bug_fix
refs:
  - ss-2026-03-12-002
  - ln-2026-03-10-001
---
```

---

# Cross-Project Learning

If a solved problem represents reusable knowledge, promote it to:

memory-system/system/cross-project/

Examples:

- recurring bugs
- reusable solutions
- architecture lessons
- anti-patterns

This ensures the engineering brain improves across projects.

---

# Hooks

Session automation helpers live in:

memory-system/hooks/

Examples:

session_start.py  
session_end.py  

These assist with:

- context suggestions
- session initialization
- session summaries

Hooks assist the workflow but do not replace MCP context loading.

---

# Main Principle

Global knowledge lives in:

system/

Reusable reasoning templates live in:

contexts/

Project knowledge lives in:

projects/<project>/

Agents must keep these boundaries clean.

---

# Expected Agent Behavior

Agents working in this repository must:

1. load context before reasoning
2. inspect architecture documentation
3. implement minimal safe changes
4. validate behavior
5. document new knowledge

This ensures the engineering brain improves with every solved problem.