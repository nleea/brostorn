# Agent Guide

This repository contains an **AI-assisted engineering memory system** designed to help developers and AI agents understand the project architecture, debug issues, and preserve technical knowledge over time.

Agents working in this repository must use the documentation system before performing development tasks.

This guide explains how to interact with the memory system correctly.

---

# Core Principle

Never start coding immediately.

Always load context from the engineering memory before making changes.

The documentation system acts as the **primary knowledge base for the project**.

---

# Documentation Structure

All engineering knowledge is stored under:

docs/

Key sections include:

## System Navigation

00-index

Contains the global entry points for the memory system.

Start here before loading additional context.

Important files:

- `memory-system-index.md`
- `index.md`

---

## Project Context

01-project

Contains high-level information about the project:

- goals
- constraints
- glossary
- overview

This section helps agents understand the broader purpose of the system.

---

## Architecture

02-architecture

Explains the system design and module boundaries.

Includes:

- auth flow
- service architecture
- integrations
- system overview

Agents should consult this section when analyzing system behavior.

---

## Backend Implementation

03-backend

Documents backend technologies and patterns.

Examples:

- FastAPI architecture
- Celery usage
- background jobs
- error handling
- API design patterns

---

## Frontend Architecture

04-frontend

Explains the frontend architecture and state management.

Includes:

- router behavior
- auth store
- logout flow
- UI architecture
- Vue patterns

---

## Database Layer

05-database

Documents database design and persistence logic.

Includes:

- schema overview
- migration strategy
- indexing strategy
- vector search integration

---

## Features

06-features

Feature-level documentation.

Examples:

- authentication
- quoting system
- inventory
- chatbot sales assistant

---

## Engineering Patterns

07-patterns

Reusable development patterns for the project.

Examples:

- backend patterns
- frontend patterns
- debugging patterns
- async patterns

---

## Roadmap

08-roadmap

Contains planning documents:

- short term goals
- mid term goals
- long term vision

---

## Architecture Decisions

09-decisions

Architecture Decision Records (ADR).

These documents explain why certain technical decisions were made.

Agents should consult ADRs before proposing major architectural changes.

---

## Deployment

10-deployment

Operational documentation.

Includes:

- docker configuration
- CI/CD
- monitoring
- cloudflare integration

---

# Operational Memory

The following sections transform the documentation into a **living engineering memory system**.

---

## Debugging Knowledge

11-debugging

Contains structured debugging notes.

Each debugging note documents:

- symptoms
- root cause
- solution
- files modified
- validation

Agents should search this section when investigating bugs.

---

## Skills

12-skills

Reusable engineering workflows and knowledge.

Important files include:

- `memory-system-skill.md`
- `memory-workflow-v1.md`

These files define how agents should interact with the memory system.

---

## Commands

13-commands

Standard workflows for common development tasks.

Examples:

- `debug.md`
- `refactor.md`
- `analyze-flow.md`
- `document-fix.md`

Agents should use these command workflows when performing tasks.

---

## Distilled Context

14-distilled-context

Concise module summaries used to reduce token usage.

Distilled context should always be loaded before deeper documentation.

Examples include:

- calendar
- meals
- exercises
- database
- deployment

---

## Session Memory

15-session-memory

Records development sessions.

Each session note captures:

- task worked on
- context loaded
- findings
- files modified
- validation
- follow-ups

This ensures that engineering knowledge accumulates over time.

---

# Standard Agent Workflow

Agents should follow this workflow when performing tasks:

Task  
↓  
Read memory system index  
↓  
Identify affected module  
↓  
Load distilled context  
↓  
Load supporting documentation if needed  
↓  
Inspect real code  
↓  
Analyze behavior  
↓  
Implement change  
↓  
Validate result  
↓  
Document debugging knowledge  
↓  
Save session summary

---

# Context Efficiency Rules

To reduce token usage, use the lightest MCP tool that gives enough context:

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
   → WARNING: ~15k tokens, fills context quickly
   → use only when module is unfamiliar or steps 1–4 are insufficient
```

Additional rules:

- always start with distilled context
- load only relevant notes
- avoid loading entire documentation sections
- verify documentation against real code

## save_debug_note — required fields

```
title       : short slug (e.g. "calendar-day-not-marked-complete")
summary     : one-line description of the bug (required — tool fails without it)
content     : full markdown body
project     : e.g. "fitness-app"
relative_dir: always "11-debugging" for bug notes
```

## save_session_summary — required fields

```
title   : descriptive session title
task    : one-line description of what was worked on (required — tool fails without it)
content : full markdown body
project : e.g. "fitness-app"
```

---

# Documentation Updates

Agents must update the memory system when:

- fixing bugs
- discovering root causes
- introducing architectural changes
- implementing new features
- identifying reusable patterns

---

# Expected Behavior

Agents interacting with this repository should:

- prioritize existing documentation
- avoid redundant investigation
- validate documentation against real code
- preserve knowledge for future tasks

By following these practices, the repository becomes a **self-improving engineering system** where each development session improves future productivity.