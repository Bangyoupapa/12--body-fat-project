# ADR-0003: Single Table for InBody and Manual Weight Entries

## Status
Accepted

## Context
The bot records two types of body composition data:
- **InBody scan** — from a photo, includes body fat %, muscle mass, weight, BMI
- **Manual weight** — user types their weight; BMI is calculated if height is provided

Options:
- **Two separate tables** (`inbody_entries`, `weight_entries`) — cleaner schema, each row is self-describing
- **Single table** (`composition_entries`) with a `source` column (`'inbody'` or `'manual'`) — simpler queries when tracking weight trend over time

## Decision
Single `composition_entries` table with a `source` field. InBody rows populate all columns; manual weight rows leave `body_fat_pct` and `muscle_mass_kg` as NULL.

## Consequences
- Weight trend queries span both sources in one `SELECT` — simpler for the coaching layer
- Some rows will have NULL columns by design — acceptable given the single-user scope
- Adding a new source (e.g. Apple Watch body composition) is a new `source` value, not a new table
