# Backend Patterns

## Goal

Provide reusable backend architecture patterns.

## Recommended Patterns

- Prefer router → service → repository separation.
- Keep business logic out of transport layers.
- Use explicit validation boundaries.
- Keep async behavior predictable and observable.
- Centralize cross-cutting concerns where possible.

## Common Pitfalls

- business logic inside route handlers
- duplicated persistence logic
- inconsistent transaction boundaries
- hidden side effects