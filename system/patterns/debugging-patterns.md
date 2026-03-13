# Debugging Patterns

## Goal

Provide reusable debugging strategies that apply across projects.

## Standard Debugging Pattern

1. Define expected behavior
2. Observe actual behavior
3. Compare working vs non-working paths
4. Identify root cause
5. Fix in the correct layer
6. Validate with realistic scenarios
7. Document the fix

## Common High-Value Comparisons

When one flow works and another does not, compare:

- data shape
- state updates
- date normalization
- computed mapping
- API response structure
- naming conventions
- async timing
- routing behavior

## Common Root Cause Categories

- stale reactive state
- inconsistent date formats
- duplicated logic
- missing mapper or computed property
- persistence not cleared or updated
- store not synchronized with UI
- wrong source of truth