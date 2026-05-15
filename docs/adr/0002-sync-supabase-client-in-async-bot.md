# ADR-0002: Sync Supabase Client in Async Bot

## Status
Accepted

## Context
The Discord bot runs on an async event loop (discord.py). Supabase-py offers both a sync and an async client. Options:
- **Async client** (`AsyncClient`) — non-blocking, fits the async model, but API is less stable and more complex
- **Sync client** — simpler, well-documented, blocks the event loop during DB calls

## Decision
Use the sync Supabase client. Storage functions (`save_food_entry`, etc.) are plain synchronous functions called directly from async handlers.

## Consequences
- DB calls block the event loop briefly — acceptable for a single-user bot with low concurrency
- Storage layer is simpler to read and test (no `await` in db/storage.py)
- If the bot ever needs to handle concurrent users, storage calls should be moved to `asyncio.to_thread()`
