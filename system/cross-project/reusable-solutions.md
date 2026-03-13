# Reusable Solutions

## Purpose

Store solution patterns that may help across projects.

## Solution Pattern: Fix stale session transitions

### Use Case
Logout or session invalidation does not fully update the UI.

### Typical Fix
- clear reactive auth state
- clear persisted session data
- force correct navigation
- ensure guards read current state

### Why It Works
It aligns session persistence, UI state, and navigation behavior.