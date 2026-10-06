# Sprint 03 — The extractor, part 1: fetch, raw store and the breaker

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** `manage.py ingest_source` fetches a configured source and produces an
  immutable, idempotent record of exactly what the source said — a `raw_documents` row — plus
  an honest `ingestion_runs` entry and an up-to-date circuit breaker. **No test contacts the
  network.** It parses nothing and stages nothing.
- **Starts:** after Sprint 02 closes; nominal 1 week.
- **WIP limit:** 2 items (ADR 0001)

> This sprint turns the Sprint 02 tables into behaviour for the first time. It stops at
> **RAW STORE**: the payload is stored and recorded, and nothing becomes a record yet.
> Transform and staging are Sprint 04.

## Sprint backlog

Ordered; with a WIP limit of 2, items are taken top-down.

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | HTTP layer over `httpx`: `robots.txt` cached per host, per-source rate limit, identifiable User-Agent with contact, retry with backoff, 429 `Retry-After`, 4xx permanent | FR-B-13, FR-B-14 | SEC-41, SEC-42 | Open |
| 2 | Raw store: SHA-256, hash-gated no-op, payload written behind a storage abstraction, `raw_documents` insert, `IntegrityError` treated as a skip | FR-B-02, FR-B-03 | SEC-37 (raw layer) | Open |
| 3 | Run bookkeeping: open `ingestion_runs` `running`, per-stage `stats`, terminal status, `skipped` when a source is not due | FR-B-08 | tests | Open |
| 4 | Circuit breaker: increment/reset counters, `last_failure_at`/`last_error`, auto-disable at the threshold, alarm | FR-B-10 | SEC-39 | Open |
| 5 | `manage.py ingest_source --due \| --source \| --all` (and `--dry-run`) with trigger `cron`/`manual` | FR-B-17, FR-B-18 | tests | Open |
| 6 | A failed run never modifies, degrades or deletes a `published` row | FR-B-09 | SEC-38 | Open |
| 7 | Fixtures under `backend/tests/fixtures/<source>/<case>/` + `meta.json`; HTTP mocked with `httpx.MockTransport` | NFR-16 | plan-pruebas §1 | Open |
| 8 | Raw retention per ADR 0013 (30 days + per-source byte cap) via `prune_raw_documents` | FR-B-16 | test | Open |

### Why the raw store exists

Idempotency is not added at the end: `raw_documents` is why it exists. A fetch whose
SHA-256 already exists is a no-op — no transform, no queue entry — and the unique constraint
is the last line of defence, not application logic that can be skipped.

### Copyright and fixtures

`wp/v2` responses embed full article bodies, and the repository must never hold third-party
text (LEG-05). Fixtures are captured with `_fields=` limited to the fields the extractor
consumes, so a committed fixture contains no article body.

## What must be true when it ends

1. Fetching the same payload twice produces exactly one `raw_documents` row; the second run
   records a `skipped` (SEC-37 at the raw layer).
2. A source that fails N times is auto-disabled and makes no further request (SEC-39).
3. A failure leaves every `published` row byte-identical (SEC-38).
4. SEC-41 (rate limit) and SEC-42 (User-Agent) pass.
5. `ruff`, `ruff format --check`, `mypy`, `pytest` and `check --deploy` are green in CI, and
   `openapi.yaml` shows no drift (NFR-11, NFR-12, NFR-14).

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | The 8 items ship with the tests in the Sprint 03 deep plan; no network in any test |
| Documentation updated | `flujo-datos.md` stage-1/2 references, `CHANGELOG.md`, `.env.example`, this plan |
| CI green | The existing workflow runs the new tests; no live source |
| Linked in the matrix | FR-B-02, FR-B-03, FR-B-08, FR-B-13, FR-B-14; FR-B-09/10 only if their tests pass |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| Transform, schema validation, sanity gate, staging (`pending` rows) | Sprint 04 |
| `source_record_key` and the natural key for staging | Sprint 04 |
| Publishing, review queue, admin | Doesn't exist until v1 |
| The `sources` citation registry and news/media transforms | v2 |

## Risks

1. **Scope.** Fetch + robots + rate limit + retry + storage + runs + breaker + pruning is a
   full part-time week. If it slips, item 8 (retention) moves to Sprint 04 first.
2. **No `Crawl-delay`** on the source's `robots.txt`, so `rate_limit_seconds` is the only
   throttle; keep its default conservative.
3. **The suite must stay offline and fast** — injected clock, mocked transport, no waits.

## Carried into the next sprint

1. Transform for `wp_api` (preferred, FR-B-15), schema validation and the rights/attribution
   fields.
2. The sanity gate, including the target-edition date alignment (the spike found a plausible,
   six-year-old programme).
3. Staging as `pending` with `source_record_key`, and pipeline creation of missing
   `editions`/`days`.
