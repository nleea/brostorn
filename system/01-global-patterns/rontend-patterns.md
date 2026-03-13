# Frontend Patterns

## Goal

Provide reusable frontend engineering patterns across projects.

## Recommended Patterns

- Keep state ownership clear.
- Use stores as explicit sources of truth.
- Avoid duplicating derived UI logic in multiple components.
- Normalize dates before rendering or comparison.
- Centralize auth and session transitions.
- Use explicit flow documentation for complex UI behavior.

## Common Pitfalls

- stale store-derived state
- duplicated completion logic
- inconsistent naming
- view-specific workarounds that bypass architecture