---
title: Debug Calendar
type: context_template
scope: project
project: fitness-app
problem_types:
  - calendar
  - completion
  - meal-completion
keywords:
  - calendar
  - meals
  - exercises
  - completion
  - meal_key
  - logs
applies_to:
  - calendar
  - meals
  - state-management
related_distilled:
  - calendar
  - meals
related_paths:
  - projects/gym-trainer/docs/14-distilled-context/calendar.md
  - projects/gym-trainer/docs/14-distilled-context/meals.md
priority: 4
---

# Debug Calendar

## Problem Type

Use this context when the gym-trainer calendar shows the wrong completion state, misses planned items, or diverges from the underlying workout or meal logs.

## Comparison Strategy

- Compare the rendered day status against the raw logs for the same day.
- Compare workout completion and meal completion paths for symmetry.
- Compare normalized client-side date keys against backend log dates.
- Compare week-scoped caches versus full-history data when the UI renders multi-week ranges.

## Investigation Checklist

- Read the project distilled contexts for `calendar` and any affected module such as `meals`.
- Inspect the frontend calendar component and the parent view that supplies its props.
- Trace the store getters/actions that provide workout logs and meal logs.
- Verify whether completion is derived from the same identifier on both planning and logging sides.
- Check for differences between daily, weekly, and full-history loaders.
- Review existing debugging notes for calendar and nutrition completion regressions.

## Validation Strategy

- Validate a day with completed workouts and completed meals.
- Validate a day with planned items but no logs.
- Validate a multi-week range where the visible calendar extends beyond the current week cache.
- Validate that creating a new log updates the calendar without requiring a full page refresh.
