---
title: Debug Meals
type: context_template
scope: project
project: fitness-app
problem_types:
  - meals
  - nutrition
  - meal-completion
keywords:
  - meals
  - meal_key
  - nutrition
  - completion
  - logs
  - cache
applies_to:
  - meals
  - calendar
  - state-management
related_distilled:
  - meals
  - calendar
related_paths:
  - projects/gym-trainer/docs/14-distilled-context/meals.md
  - projects/gym-trainer/docs/14-distilled-context/calendar.md
priority: 4
---

# Debug Meals

## Problem Type

Use this context when meal or nutrition logs do not map correctly to completion state, daily summaries, or calendar indicators in gym-trainer.

## Comparison Strategy

- Compare planned meals for a date against the actual meal logs recorded for that date.
- Compare the identifier used in plan generation versus the identifier persisted in meal logs.
- Compare meal log loading strategy with workout log loading strategy to detect asymmetry.
- Compare API response shape with the frontend store shape used by computed completion logic.

## Investigation Checklist

- Read the distilled contexts for `meals` and `calendar`.
- Inspect the nutrition or training views where meal completion is computed.
- Inspect the meal log store, repo layer, and any cache invalidation paths.
- Verify whether the UI compares by `meal_key`, `type`, or another derived field.
- Check whether the component uses week cache only or full client history.
- Review debugging notes related to meal completion and calendar status.

## Validation Strategy

- Validate one meal per day and multiple meals of the same type on the same day.
- Validate completion after creating and deleting a meal log.
- Validate calendar state across 1-week, 2-week, and 4-week views.
- Validate that completion remains correct when API payloads use snake_case and UI state uses camelCase.
