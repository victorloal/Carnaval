# Sprint 13 — Settings, translated URLs and search

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** Typed site settings without secrets, translated slugs, verbatim citations
  with a Spanish translation alongside, and PostgreSQL full-text search over **published**
  events and news using `pg_trgm` + `unaccent`.
- **Starts:** after Sprint 12 closes; nominal 1 week.
- **WIP limit:** 2 items (ADR 0001)

> Search is a filter over the public catalogue, never a way around its visibility rules. No
> external search service is introduced (FR-I-03, NFR-05).

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | `SiteSetting` (`key`, `value` jsonb, `value_type`, `description`, `updated_by`, `updated_at`) with typed accessors | FR-E-10 | tests | Open |
| 2 | Every settings change written to `audit_logs` with before/after | FR-E-12 | test | Open |
| 3 | Secrets are never stored in `site_settings` (env only) | FR-E-11 | test | Open |
| 4 | Per-locale slugs with fallback and redirect | FR-H-07 | test | Open |
| 5 | Citations, source URLs and legal bodies reproduced verbatim with a translation alongside | FR-H-09 | test | Open |
| 6 | Full-text search over **published** events and news; `pg_trgm` + `unaccent` | FR-I-01/02/03 | tests | Open |

## What must be true when it ends

1. Settings are typed, audited and secret-free.
2. Search covers published events and news only, is accent-insensitive and uses no external
   service.
3. Translated slugs resolve; fallbacks redirect rather than 404.
4. The `pg_trgm`/`unaccent` extensions are created in a reviewed migration and exist in CI's
   PostgreSQL.
5. `ruff`/`mypy`/`pytest`/`check --deploy` green; matrix rows updated.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | Settings audit, secret refusal, search visibility and accent handling are tested |
| Documentation updated | `modelo-datos.md` §4.4, ADR 0013 references, `CHANGELOG.md` |
| CI green | Search tests require the PostgreSQL service |
| Linked in the matrix | FR-E-10/11/12, FR-H-07/09, FR-I-01/02/03 |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| Submissions and everything v3 | Sprint 15, deliberately last (ADR 0008) |
| A settings schema/enforcement | Not needed; typed accessors suffice (ADR 0013) |

## Risks

1. **SQLite cannot test search** — the PostgreSQL CI service is now load-bearing.
2. **Accent handling** — `unaccent` is installed in the migration, not assumed.
3. **Settings as a secret back door** — the accessor refuses secret-shaped keys.

## Carried into the next sprint

1. v2 hardening and release, including a rights-workflow rehearsal on real data.
