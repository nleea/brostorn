---
title: Debug State Management
type: context_template
scope: global
problem_types:
  - state-management
  - cache
  - reactivity
keywords:
  - state
  - store
  - stores
  - pinia
  - reactive
  - computed
  - cache
  - invalidate
  - sync
applies_to:
  - state-management
  - calendar
  - meals
related_distilled:
  - meals
  - calendar
priority: 2
---

# Debug State Management

Use this context when UI state diverges from source data because of stale stores, cache scope mistakes, missing invalidation, or incomplete derived state.

## Compare

- API payload shape versus normalized store shape
- Cached week or page scope versus the time range rendered by the UI
- Raw logs versus computed completion state
- Mutation/update path versus invalidation/reload path

## Inspect

- Project store architecture and state-management patterns
- Store getters/computed selectors that derive view state
- Cache keying strategy and invalidation triggers
- Places where one domain uses full history and another uses partial cache

## Validate

- Fresh load and immediate post-mutation state
- Cross-view consistency after create, update, and delete
- Multi-range or multi-tab scenarios when relevant
- Derived completion state after cache invalidation
