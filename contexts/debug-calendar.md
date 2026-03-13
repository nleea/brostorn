---
title: Debug Calendar
type: context_template
scope: global
problem_types:
  - calendar
  - scheduling
  - completion
  - timezone
keywords:
  - calendar
  - schedule
  - date
  - timezone
  - completion
  - completed
  - meals
  - exercises
applies_to:
  - calendar
  - meals
  - exercises
  - state-management
  - ui-rendering
related_distilled:
  - calendar
  - meals
priority: 3
---

# Debug Calendar

Use this context when scheduling, calendar completion state, recurring events, or date-bound workflows behave incorrectly.

## Compare

- Persisted schedule data versus rendered calendar state
- User timezone/date boundaries versus backend stored timestamps
- Completion logic versus displayed progress state
- Recurring-event rules versus generated occurrences

## Inspect

- Project calendar distilled context first
- Data-flow and architecture notes touching scheduling
- Backend services/repositories that shape calendar payloads
- Frontend views or stores that aggregate daily/weekly status

## Validate

- Same-day create/update flow
- Cross-day boundary behavior
- Completion toggles and refresh behavior
- Any timezone-sensitive path explicitly

## Documentation Trigger

If the issue reveals a reusable date/time anti-pattern, capture it in cross-project memory.
