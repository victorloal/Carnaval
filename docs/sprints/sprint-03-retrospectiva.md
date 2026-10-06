# Sprint 03 retrospective — the extractor, part 1

- **Date:** 2026-10-06
- **Sprint:** 03 — The extractor, part 1: fetch, raw store and the breaker
- **Method:** Start / Stop / Continue, plus what actually happened versus what was planned.

## What was planned versus what happened

Planned: the HTTP layer (robots, rate limit, User-Agent, retry), the raw store, run
bookkeeping, the circuit breaker, the `ingest_source` and `prune_raw_documents` commands, and
fixtures — with no test touching the network. It stops at RAW STORE; nothing is transformed,
staged or published.

What happened: all eight backlog items landed and **CI is green on `b54f858`**. The suite grew
from 25 to **43 tests**; `ruff` (52 files), `mypy` (52 source files), `makemigrations --check`,
`check --deploy` and the OpenAPI drift check are all clean, and the diagram validator passes.
`SEC-37`/`38`/`39`/`41`/`42` now have executable tests. The matrix moved **FR-B-02, 03, 08,
09, 10, 13, 14 and 16 to Done**; FR-B-04 (needs staging), FR-B-17 (needs the Actions cron),
FR-B-18 (needs the v1 admin action) and FR-B-19 (SEC-35) stay Open on purpose.

## Start

- **Mock the network with the tool already present.** `httpx.MockTransport` intercepts every
  call without adding a dependency, and the session-wide egress guard fails a forgotten mock
  for an infrastructure reason (NFR-16). A test can never reach a live source by accident.
- **One module per concern.** `robots`, `http`, `storage`, `raw_store`, `runs`, `breaker`,
  `pipeline`: each is small enough to reason about, and `pipeline.run_source` is the only
  place that ties them together.
- **Fixtures with their computed hash.** A fixture is a directory with the body and a
  `meta.json` holding the URL, status, content type and the SHA-256 the pipeline should
  produce; the test asserts the pipeline computes it. They are reduced with `_fields=` so no
  third-party article text is committed (LEG-05).
- **The breaker is state, not code.** `consecutive_failures`, `last_error` and `is_active` on
  `scrape_sources`; a human re-enables a disabled source.

## Stop

- **A test slept for real.** The default `rate_limit_seconds = 60` compounded with the retry
  backoff across attempts, so one failing-source test took ~115 s and the suite 122 s. The
  fix: inject the clock and the sleep, and zero the retry backoff in tests. The suite is now
  ~1 s. **A rate limiter is a clock; nothing time-based may run against the real clock in a
  test.**
- **`--due` does not match cron yet.** Per-source `schedule_cron` is applied by the GitHub
  Actions cron; `--due` selects active sources. This is the open dispatch item in
  `flujo-datos.md` §11, stated in the command's help rather than left implicit.
- **Retention cannot exempt "live" payloads yet.** The design exempts a payload referenced by
  a live record, but nothing links a content row to its raw payload until staging. The command
  deletes strictly by age and size, and says so.
- **A stale local database hid nothing, but confused a smoke.** The first `ingest_source`
  smoke failed with `no such table: ingestion_scrapesource` because the dev `db.sqlite3`
  predated the ingestion migrations; the test database is created fresh, so only the manual
  smoke noticed. Run `migrate` before a manual smoke.

## Continue

- **Verify against the CLI and the filesystem**, not the completion report.
- **Keep the write surface tiny.** The pipeline writes only `raw_documents`, `ingestion_runs`
  and the breaker columns on `scrape_sources`; that is what makes "a failed run never touches
  `published`" (FR-B-09, SEC-38) mechanical rather than a promise.
- **Hand an explicit interface to the next sprint.** `FetchedPayload` and the hash are what
  Sprint 04's transform consumes; the boundary is a dataclass, not a shared global.

## What the sprint proved about the project

Idempotence is structural: the unique `content_hash` gates the raw store, so re-running a
source cannot duplicate anything, and the `IntegrityError` path is a skip rather than a crash.
The "never touch published" rule holds because the pipeline's write surface is small enough to
audit by reading one module. Both are the properties the brief's top risk depends on.

## Concrete changes adopted

1. Anything time-based injects its clock and sleep; no test sleeps against the real clock.
2. A deferred mechanism (`--due` cron matching, the retention exemption) is written in the
   command's help and in the docs, never left as an unnamed gap.
3. `migrate` the local database before any manual command smoke.
4. `FetchedPayload` and `CandidateRecord` stay the explicit interface between fetch and
   transform.
