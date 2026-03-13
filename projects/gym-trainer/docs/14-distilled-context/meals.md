---
type: distilled-context
module: meals
project: fitness-app
status: active
updated: 2026-03-11
tags:
  - meals
  - nutrition
  - logs
  - completion
---

## Purpose
The meals module tracks nutrition-related entries and their day-level completion state.

## Core Flow
- Meal plans or expected meal entries are assigned to the user.
- The user creates meal logs or completion records.
- Meal data is transformed into daily status for views such as logs, dashboards, or calendar.
- The frontend depends on consistent log shape and date normalization.

## Source of Truth
- Meal log store
- Nutrition/meal API responses
- Date normalization utilities
- Calendar/day summary mapping logic

## Key Contracts
- A valid meal log for a day should be eligible to mark that day as completed when business rules say so.
- The frontend must use a consistent completion rule for meal tracking.
- Meal completion must be reflected reactively after log creation or update.

## Known Pitfalls
- API shape differs from exercise log shape
- Date keys include time while calendar expects plain dates
- Missing mapping from meal logs to calendar completion state
- Store updates do not invalidate or recompute calendar data
- Completion property naming mismatch

## Relevant Files
- `src/stores/...meal...`
- `src/views/...nutrition...`
- `src/components/...calendar...`

## Related Notes
- [[06-features/authentication]]
- [[04-frontend/meal-logs]]
- [[11-debugging/calendar-meals-not-marked-completed]]