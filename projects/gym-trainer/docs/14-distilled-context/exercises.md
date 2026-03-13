---
type: distilled-context
module: exercises
project: fitness-app
status: active
updated: 2026-03-11
tags:
  - exercises
  - workouts
  - logs
  - completion
---

# Exercises Distilled Context

## Purpose
The exercises module tracks workout execution and day-level completion state.

## Core Flow
- Training plans define expected workouts.
- The user records workout/exercise logs.
- The frontend maps logs into completion state for progress views and calendar rendering.
- Exercise completion currently appears to be the working reference implementation for day-level completion.

## Source of Truth
- Workout/exercise log store
- Workout-related API responses
- Calendar completion mapping logic

## Key Contracts
- A valid workout/exercise log should mark the corresponding day as completed when rules are satisfied.
- Exercise completion should update the UI reactively.
- Exercise completion logic can be used as a reference when debugging other domains.

## Known Pitfalls
- Inconsistent date normalization between views
- Derived completion logic hidden in computed properties
- Day-level status built differently than meal-level status

## Relevant Files
- `src/stores/...exercise...`
- `src/views/...workout...`
- `src/components/...calendar...`

## Related Notes
- [[04-frontend/exercise-logs]]
- [[04-frontend/calendar]]
- [[11-debugging/calendar-meals-not-marked-completed]]