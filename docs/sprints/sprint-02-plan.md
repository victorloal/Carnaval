# Sprint 02 — The schema the pipeline needs

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** Complete the **MVP data model**. When this sprint ends, every table the
  ingestion pipeline and the public read API depend on exists, is migrated, and is tested:
  `events`, `scrape_sources`, `raw_documents`, `ingestion_runs`, plus the `ingestion_run`
  link on the moderation mixin. No extractor, no API endpoints, no admin screens.
- **Starts:** 2026-10-07 (planned)
- **WIP limit:** 2 items (ADR 0001)

> This is deliberately a **data-model** sprint. The extractor (Sprint 03) and the public API
> (Sprint 04) both depend on these tables; building either first would mean writing against a
> schema that does not exist. Sprint 01 delivered the machinery; this sprint delivers the
> shape of the data.

## Sprint backlog

Ordered; with a WIP limit of 2, items are taken top-down.

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | New Django app `carnaval.ingestion` (skeleton, `apps.py`, migrations package, registered in `INSTALLED_APPS`) | NFR-13 | `manage.py check` | Open |
| 2 | `Event` in `programme`: FK `day`, nullable FK `venue`, nullable `starts_at`/`ends_at`, `title_es`/`title_en`, nullable `description_es`/`description_en` (**own words only**), `sort_order`, moderation mixin, `source_url` | FR-A-03, FR-A-04, FR-A-12 | tests + migration review | Open |
| 3 | `ScrapeSource`: `name`, `url`, `source_type` (`wp_api`/`html`/`pdf`), `wp_object_type`/`wp_object_id`, `selectors` (JSON), `is_active`, `rate_limit_seconds`, `schedule_cron`, `consecutive_failures`, `last_success_at`/`last_failure_at`, `last_error`, `user_agent` | FR-B-12, FR-B-10 | tests + matrix | Open |
| 4 | `RawDocument`: FK `scrape_source`, `url`, `http_status`, `content_type`, **`content_hash` unique (SHA-256)**, `byte_size`, `storage_key`, `fetched_at` | FR-B-02, FR-B-03, FR-B-19 | test: re-fetch of the same hash is a no-op | Open |
| 5 | `IngestionRun`: nullable FK `scrape_source`, `trigger` (`cron`/`manual`/`admin`), `status` (`running`/`succeeded`/`failed`/`skipped`), `started_at`/`finished_at`, `stats` (JSON), `error_message` | FR-B-08 | tests | Open |
| 6 | Un-defer `ingestion_run` FK on `ModeratedModel` now that `ingestion_runs` exists | FR-B-06 | migration `programme/0004` | Open |
| 7 | `seed_demo` management command: idempotent, dev-only, creates the canonical 2026 edition, its five day rows and sample events as `published` | FR-A-04, FR-A-10 (demo) | test: running it twice creates no duplicates | Open |
| 8 | Confirm **no new model is registered in `/admin/`** (a fresh install must not expose `pending` content) | FR-D-03 | inspection | Open |
| 9 | Reconcile `modelo-datos.md` §2/§3.1/§3.4 and `estados.md` with the shipped mixin | ADR 0001 DoD 2 | inspection | Open |
| 10 | Matrix rows for items 2–5 moved from `Open` to their real status | ADR 0001 DoD 4 | inspection | Open |

### Why `events` and the ingestion tables in the same sprint

`FR-A-03` (events) is the last piece of the public catalogue the MVP API needs, and
`scrape_sources`, `raw_documents` and `ingestion_runs` are what the extractor writes to.
They are independent of each other and can be taken in any order under the WIP limit of 2.
If the week runs short, **items 3–5 come first**: the ingestion tables are on the critical
path for Sprint 03, while `events` only blocks Sprint 04.

## Decisions carried into this plan

Two points were decided while planning. They are recorded here because they change the
design documents, not just the code.

### 1. `events` links to its source with `source_url` for MVP

`FR-A-12` (MVP) requires the public site to link each programme entry to its source. The
design's citation registry `sources` (`modelo-datos.md` §4.3) belongs to the editorial
version (v2, FR-E). For the MVP, `Event` carries a plain `source_url`; the `sources` registry
replaces it in v2. `modelo-datos.md` §3.4 gains the `source_url` row.

### 2. The moderation mixin stays on the spine

`modelo-datos.md` §2 and `estados.md` §1 describe the mixin on `events`, `news_items`,
`media_assets` and `submissions`, with `editions` using a stored `is_published`. Sprint 01
instead applied the mixin to `editions`, `days` and `venues` and made `is_published` derived.
This sprint **keeps the mixin on the spine** — it is the only way "every record keeps its
`origin`" holds for every record — and updates the two design documents to say so. `events`
gets the mixin as the first **content** table that needs review.

## What must be true when it ends

1. `manage.py makemigrations --check --dry-run` reports no changes, so **drift fails the
   build** (NFR-13).
2. `raw_documents.content_hash` is unique at the database level, and a second document with
   the same hash raises `IntegrityError` (FR-B-03).
3. `Event`, `ScrapeSource`, `RawDocument` and `IngestionRun` have factories and unit tests,
   and every migration is reviewed in the pull request (NFR-13).
4. `seed_demo` run twice leaves the same rows and no duplicates (idempotence).
5. No model added by this sprint appears in Django admin, so `/admin/` exposes no `pending`
   content (FR-D-03).
6. `ruff check`, `ruff format --check`, `mypy backend/`, `pytest` and `manage.py check
   --deploy` are all green, and the workflow runs them on the branch (NFR-11, NFR-14).

## Definition of Done

ADR 0001's four conditions, applied per backlog item:

| Condition | How it is met here |
|---|---|
| Code with tests | Each model ships with a factory and unit tests; the unique `content_hash` and `seed_demo` idempotence each get a dedicated test |
| Documentation updated | `modelo-datos.md` §2/§3.1/§3.4, `estados.md`, `CHANGELOG.md` and this plan's decision notes |
| CI green | The existing workflow covers migrations, lint, types and tests; it must run green on the branch |
| Linked in the matrix | Item 10; FR-A-03, FR-A-04, FR-A-12, FR-B-02, FR-B-03, FR-B-08, FR-B-12 gain their status |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| The extractor, rate limiting, circuit breaker (FR-B-01…FR-B-19 beyond the tables) | Sprint 03; it needs these tables to exist first |
| Public read API endpoints and `/health` (FR-A-06, FR-A-07, FR-A-11, FR-D-11) | Sprint 04; the API is built against a finished schema |
| Django admin screens, roles, review queue, audit log (FR-C, FR-D) | v1 (ADR 0008) |
| `sources` citation registry, `news_items`, `media_assets`, `site_settings` | v2 (FR-E) |
| `submissions`, files, consent (FR-F) | v3; deliberately last (ADR 0008) |
| Object storage wiring for `raw_documents.storage_key` | ADR 0015 is unwritten; the column stores the key, the provider is decided before any upload |
| `audit_logs` (FR-D-08) | v1; nothing in the MVP writes to it yet |

## Risks

1. **Four models plus a seed command in one part-time week is a lot.** The mitigation is the
   ordering above: the three ingestion tables are the critical path, `events` can slip to
   Sprint 03, and the WIP limit of 2 stays honest. Do not start the extractor before the
   tables are merged.
2. **`raw_documents.storage_key` presupposes storage that is not chosen yet.** Sprint 02
   only defines the column; nothing uploads a payload. ADR 0015 decides the provider before
   the extractor stores anything, or the first real run writes to a path that will move.
3. **`jsonb` fields on SQLite.** `ScrapeSource.selectors` and `IngestionRun.stats` use
   Django's `JSONField`, which works on SQLite for development but is only truly `jsonb` on
   PostgreSQL. Tests run on SQLite; the CI Postgres service is optional (carried from Sprint
   01) and should be added here so the production engine is exercised at least once.
4. **`seed_demo` is a deliberate review bypass.** It exists only because the MVP ships no
   admin (decision: publishing waits for v1). It must be idempotent, must never create a
   user, and must refuse to run with `DEBUG` off unless explicitly forced — otherwise it
   becomes a backdoor around FR-C-02.

## Carried into the next sprint

1. The extractor: WordPress REST API first, committed fixtures, `Crawl-delay`-aware
   politeness, retry with backoff and the circuit breaker (FR-B-01 … FR-B-19), per
   `fuentes-y-atribucion.md` §5.
2. Public read API endpoints for editions, days, events and venues, filtered to
   `status = published`, plus `/health` (FR-A-06, FR-A-07, FR-A-11, FR-D-11).
3. A PostgreSQL service in CI (carried from Sprint 01) so the schema is exercised on its
   production engine, not only SQLite.
4. `SEC-46`'s secret scan (NFR-09, still `Open`).
5. ADR 0015 (storage and egress) once the schema makes the provider decision concrete.
