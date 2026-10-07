# Sprint 05 — The public read API

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** The published catalogue is readable over HTTP as JSON — editions, days,
  events and venues — read-only, filtered to `status = published`, filterable by edition and
  date range, rate-limited per IP, against a committed and drift-checked OpenAPI contract,
  with a `/health` probe.
- **Starts:** after Sprint 04 closes; nominal 1 week.
- **WIP limit:** 2 items (ADR 0001)
- **Status:** implemented and verified locally; `Done` is set once CI is green (ADR 0001).

> The anonymous surface is **read-only** (NFR-18). There is no write endpoint, no admin API
> and no token; the only mutation paths are the pipeline and, later, the admin.

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | New `carnaval.api` app; read-only serializers for editions, days, events, venues | FR-A-07 | tests | Implemented |
| 2 | A shared published-only queryset mixin; every endpoint starts filtered to `status = published` | FR-A-06 | SEC-47 | Implemented |
| 3 | Filtering by edition and date range; pagination | FR-A-11 | tests | Implemented |
| 4 | Per-IP throttling; anonymous read-only, no non-GET route reachable | NFR-17, NFR-18 | tests | Implemented |
| 5 | `/health` reporting application and database reachability, disclosing no configuration | FR-D-11 | test | Implemented |
| 6 | OpenAPI regenerated and committed; `--fail-on-warn` clean; drift fails CI | NFR-12 | CI | Implemented |
| 7 | Response caching policy for public reads | NFR-02 | analysis | Implemented |

## What must be true when it ends

1. A `pending` or `rejected` row returns 404 on every endpoint, never a redacted 200.
2. No non-GET method is routed for an anonymous caller.
3. Filters (edition, date range) and pagination behave; `/health` reflects database state.
4. `openapi.yaml` is regenerated in the same commit; the drift check passes.
5. `ruff`, `mypy`, `pytest` and `check --deploy` green.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | Every endpoint has a visibility test and a filter test |
| Documentation updated | `openapi.yaml` (generated), `arquitectura-c4.md` container notes, `CHANGELOG.md` |
| CI green | The schema stages 7–8 already exist from Sprint 01 |
| Linked in the matrix | FR-A-06, FR-A-07, FR-A-11, FR-D-11, NFR-17, NFR-18 |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| The React public site | Sprint 06 |
| CORS origins, CSP, deployment | Sprint 07 |
| Search | v2 (PostgreSQL full-text, ADR 0013) |
| Any write endpoint or submission endpoint | v1 / v3 |

## Risks

1. **Forgetting the published filter** is the one mistake that leaks unreviewed content; the
   mixin plus a per-endpoint test is the guard.
2. **Schema drift** — every view changes `openapi.yaml`; regenerate in the same commit, never
   by hand (ADR 0011).
3. **Test throttling** — the default client must not trip the limiter; an over-limit test uses
   an isolated cache.

## Carried into the next sprint

1. The React + TypeScript public site consuming this API, with bilingual routing (Sprint 06).
