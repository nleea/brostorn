---
type: distilled-context
module: calendar
project: fitness-app
status: active
updated: 2026-03-11
tags:
  - calendar
  - completion
  - meals
  - exercises
  - tracking
---


## Purpose
The calendar provides a day-level visual summary of user activity and completion state across tracked domains such as workouts and meals.

## Core Flow
- Raw logs are loaded from stores or API-backed state.
- The calendar transforms logs into date-based completion indicators.
- A day is marked based on normalized date keys and module-specific completion rules.
- The same calendar UI may depend on different stores for exercises and meals.

## Source of Truth
- Calendar rendering component(s)
- Exercise log store
- Meal log store
- Date normalization helpers
- Completion/computed mapping logic

## Key Contracts
- Day-level completion should be consistent across tracked domains.
- Completion logic must use normalized dates.
- UI should not depend on page refresh to reflect new logs.
- Empty days must render safely without errors.

## Known Pitfalls
- Mismatch between date formats
- Timezone-related day shifts
- Different completion rules for exercises vs meals
- Missing mapper/computed logic for one domain
- Store updates not reflected reactively in the calendar

## Relevant Files
- `src/components/...calendar...`
- `src/stores/...exercise...`
- `src/stores/...meal...`

## Related Notes
- [[04-frontend/calendar]]
- [[04-frontend/meal-logs]]
- [[04-frontend/exercise-logs]]
- [[11-debugging/calendar-meals-not-marked-completed]]