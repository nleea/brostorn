---
title: Debug UI Rendering
type: context_template
scope: global
problem_types:
  - ui-rendering
  - display
  - synchronization
keywords:
  - ui
  - render
  - rendering
  - component
  - view
  - display
  - marked
  - visible
applies_to:
  - ui-rendering
  - calendar
  - meals
related_distilled:
  - calendar
priority: 1
---

# Debug UI Rendering

Use this context when the UI shows the wrong status even though the underlying data appears to exist.

## Compare

- Source data versus rendered component props
- Parent view computed state versus child component expectations
- Conditional rendering rules versus real runtime values
- Visual completion markers versus actual business-state booleans

## Inspect

- Parent-to-child prop wiring
- Computed helpers that translate data into UI state
- Component defaults and fallback behavior
- Any asymmetric rendering path between similar domains

## Validate

- Initial render
- Re-render after new data arrives
- Alternate view modes and tabs
- Empty, partial, and completed states
