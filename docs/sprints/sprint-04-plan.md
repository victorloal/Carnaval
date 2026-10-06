# Sprint 04 — The extractor, part 2: transform, sanity gate and staging

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** A stored payload becomes validated candidate records and is staged as
  `pending` with `origin = scraped` and its `ingestion_run` set. The sanity gate turns the
  brief's top risk — a clean-looking fetch that yields nothing — into an alarm instead of a
  green run.
- **Starts:** after Sprint 03 closes; nominal 1 week.
- **WIP limit:** 2 items (ADR 0001)
- **Status:** delivered; CI green on `383af93`.

> The pipeline reaches **STAGING** and stops. Nothing is published: publishing requires a
> human, and the admin does not exist until v1.

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | `Event.source_record_key` (migration `programme/0005`), unique per `(day, key)` on non-empty keys | FR-B-07 | migration review | Done |
| 2 | `wp_api` transform handler (preferred, FR-B-15); html/pdf handlers as interfaces only | FR-B-01, FR-B-15 | unit | Done |
| 3 | Schema validation; a failing record is counted in `stats.rejected` with a reason | FR-B-05 | unit | Done |
| 4 | Attribution fields on each candidate (source URL; the run is the provenance) | FR-A-12, FR-B-06 | unit | Done |
| 5 | Sanity gate: zero-yield stop, drop/spike ratios, selector hits, field completeness, **and target-edition date alignment** | FR-B-11 | SEC-40 | Done |
| 6 | Staging: upsert `pending` rows by `source_record_key`; create missing `editions`/`days` as `pending` | FR-B-06, FR-B-07 | SEC-37 | Done |
| 7 | `stats` end to end: extracted/inserted/updated/skipped/rejected | FR-B-08 | integration | Done |

### The trap this sprint must not fall into

The source spike found that **`6 de enero` is a root category, not a child of `DIAS`** — so
any logic that treats "children of `DIAS`" as the days silently drops the Day of Whites, the
single most important day. Days are collected by **name pattern**, and the expected set is
asserted to be complete.

The same spike found the source's programme is mostly six years old. "The fetch returned 42
records" is never evidence the fetch was correct: extracted dates are checked against the
target edition's window.

## What must be true when it ends

1. SEC-37 closes end to end: two runs over one fixture produce zero duplicates anywhere.
2. SEC-40 passes: zero extraction alarms, no silent success, no published row touched.
3. Days are complete (the `6 de enero` trap) and aligned to the target edition.
4. A changed payload updates the existing `pending` row rather than inserting a second.
5. `ruff`, `mypy`, `pytest`, `makemigrations --check` and `check --deploy` green; no drift.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | Transform, validation, sanity and staging each ship with tests |
| Documentation updated | `flujo-datos.md` §5/§7 references, `modelo-datos.md` §3.4 `source_record_key`, `CHANGELOG.md` |
| CI green | Fixture-driven, offline |
| Linked in the matrix | FR-B-01, FR-B-04, FR-B-05, FR-B-06, FR-B-11, FR-A-12; FR-B-07 stays Open until the load path exists |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| Publishing / the load path | v1 (no admin until then) |
| Proposing a change to already-published content (`flujo-datos.md` §5.1) | Its own ADR in Sprint 09; unreachable while nothing is published |
| News and media transforms, the `sources` registry | v2 |

## Risks

1. **Stale source data** is the shape the project's top risk takes: not zero records, but a
   silent success returning old data. Edition alignment is mandatory.
2. **Elementor/JetEngine markup** makes an HTML fallback hostile; `wp_api` stays first.
3. **Scope** — transform + sanity + staging is a full week.

## Carried into the next sprint

1. The public read API over the published catalogue (Sprint 05).
2. Public submissions are explicitly last (v3); do not start any intake work early.
