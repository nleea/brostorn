---
type: system-index
project: gym-trainer
status: active
updated: 2026-03-11
tags: [memory-system, index, vault-structure]
---

# Memory System Index

This vault contains the **engineering memory system** for the project.

It is used by developers and AI agents (Codex, Claude, etc.) to understand the architecture, investigate bugs, and document engineering decisions.

The memory system prioritizes **structured knowledge retrieval** over ad-hoc searching.

Agents should always start by reading this index before loading additional context.

---

# Vault Structure

## 00-index
High-level navigation for the memory system.

Contains:
- system overview
- vault structure
- workflow specifications

---

## 01-project
Project-level documentation.

Contains:
- product overview
- goals
- constraints
- core value proposition

---

## 02-architecture
System architecture documentation.

Contains:
- module design
- system flows
- architectural boundaries

---

## 03-backend
Backend architecture and implementation details.

Contains:
- API structure
- services
- background jobs
- data processing

---

## 04-frontend
Frontend architecture and state management.

Contains:
- UI flows
- store architecture
- rendering logic
- feature-specific behavior

---

## 05-database
Database design and persistence layer.

Contains:
- schema overview
- migrations
- data modeling decisions

---

## 09-decisions
Architecture Decision Records (ADR).

Documents important engineering decisions and trade-offs.

---

## 11-debugging
Bug reports and debugging notes.

Contains:
- bug descriptions
- root cause analysis
- fixes implemented
- validation results

---

## 12-skills
Reusable engineering knowledge and workflows.

Contains:
- debugging strategies
- architectural patterns
- development workflows

---

## 14-distilled-context
Concise summaries of key modules.

Used by context packs to reduce token usage and provide high-signal context.

Examples:
- auth
- calendar
- meals
- exercises
- deployment
- database

---

## 21-session-memory
Summaries of development sessions.

Each session note records:
- task worked on
- context loaded
- findings
- code changes
- validation
- follow-ups

---

# Rules for Agents

Agents interacting with this system must follow these rules:

1. Start by reading the **Memory System Index**.
2. Identify the relevant module.
3. Load the **distilled context** for that module.
4. Load supporting notes only if needed.
5. Inspect real code to verify documentation.
6. When fixing bugs, record root cause and validation.
7. Always update the memory system after significant work.

---

# Memory System Philosophy

This system is designed to provide:

- structured engineering memory
- reliable debugging knowledge
- architecture continuity
- reduced token usage through distilled context
