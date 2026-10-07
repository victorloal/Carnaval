# Sprint 21 — Per-locale slugs

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** content has a **slug per locale** (FR-H-07), so a translated page has a
  translated URL and the source slug is the fallback rather than a shared identifier.
- **Starts:** after Sprint 20; nominal 1 week.
- **WIP limit:** 2 items (ADR 0001)
- **Status:** delivered.

> `modelo-datos.md` §3.1/§3.2 already specified `slug_es` / `slug_en`; the code carried a
> single `slug`. This sprint closes that drift.

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | `slug_es` + `slug_en` on `Edition` and `Day`, with `slug_es` as the fallback | FR-H-07 | migration review | Done |
| 2 | The English slug is unique when set, so two rows cannot share a translated URL | FR-H-07 | test (DB) | Done |
| 3 | `slug_for(locale)` resolves the slug with one-directional fallback | FR-H-06, FR-H-07 | unit | Done |
| 4 | The public API exposes both slugs; the admin searches both | FR-H-07 | schema + admin | Done |

### Fallback is one-directional

`slug_for("en")` returns `slug_en` when it exists and `slug_es` otherwise; there is no
`es ← en` path, for the same reason ADR 0012 gives for content: if the source is missing the
record is wrong, and substituting English would hide the defect. `Day` uniqueness stays per
edition, now applied to each locale.

## What must be true when it ends

1. Existing rows keep their slug as the Spanish one; the migration renames, it does not drop.
2. Two rows cannot share an English slug; empty English slugs are not "duplicates".
3. `ruff`/`mypy`/`pytest`/`makemigrations --check`/`check --deploy` green; the frontend
   `tsc`/eslint/vitest/build green; no OpenAPI drift.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | Fallback and the uniqueness constraints have tests |
| Documentation updated | `modelo-datos.md` §3.1/§3.2, `CHANGELOG.md`, `MEMORY.md`, the matrix |
| CI green | Both jobs; the regenerated `openapi.yaml` is committed |
| Linked in the matrix | FR-H-07 → Done |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| Locale-prefixed detail routes (`/es/ediciones/2026`) | There are no public detail pages yet; slugs are stored now so the routes are a rendering concern |
| Verbatim citations with a translation (FR-H-09) | Its own unit |
