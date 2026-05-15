# ADR-0001: Dependency Injection for Handler Testability

## Status
Accepted

## Context
Handlers call external services (OpenAI) and a database (Supabase). Testing handlers without hitting these systems requires some form of isolation. Options considered:
- **Module-level mocking** (`unittest.mock.patch`) — patches internals, breaks when functions are renamed or moved
- **Dependency injection** — pass `analyse_fn`, `save_fn` as optional parameters with production defaults

## Decision
Each handler accepts injectable callables for its AI service and storage calls (e.g. `analyse_fn=None`, `save_fn=None`). Production defaults are set inside the handler if not provided. Tests inject fakes directly.

## Consequences
- Handler tests do not touch OpenAI or Supabase
- Tests are coupled to the handler's public signature, not its internals — survive refactors
- Every handler has slightly more boilerplate (`if fn is None: fn = default`)
- Adding a new handler dependency requires adding a new parameter
