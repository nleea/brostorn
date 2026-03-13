---
title: Debug Auth
type: context_template
scope: global
problem_types:
  - auth
  - login
  - logout
  - session
  - token
keywords:
  - auth
  - login
  - logout
  - session
  - token
  - refresh
  - router
  - guard
applies_to:
  - auth
  - routing
related_distilled:
  - auth
priority: 2
---

# Debug Auth

Use this context when authentication, session, login, logout, token refresh, or guarded-route behavior is failing.

## Compare

- Expected auth state transitions versus actual transitions
- Frontend store/session state versus backend/session token state
- Router guard expectations versus redirect behavior
- Login success path versus logout cleanup path

## Inspect

- Project auth distilled context first
- Auth flow architecture notes
- Auth store and router entry points from `project.config.json`
- Recent bug-fix notes related to auth, logout, refresh, or 401s

## Validate

- Fresh login from a logged-out state
- Logout from a logged-in state
- Token/session refresh or expiration path
- Protected route access before and after auth changes

## Documentation Trigger

If the bug root cause is reusable across projects, promote the lesson into `system/05-cross-project-memory/`.
