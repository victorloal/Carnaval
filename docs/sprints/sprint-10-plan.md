# Sprint 10 — v1 completion and release

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** v1 is releasable — backups are proven, the console is hardened, no raw IP
  exists anywhere, and the documentation reflects a version a human can actually run. Close
  v1 with a retrospective.
- **Starts:** after Sprint 09 closes; nominal 1 week.
- **WIP limit:** 2 items (ADR 0001)

> This is a completion sprint. No new features; it makes the previous two sprints true on the
> deployed system.

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | Backup and restore procedure documented and exercised on the deployed database | NFR-20 | demonstration | Open |
| 2 | Admin reachable only over HTTPS; `noindex` verified in production | NFR-21 | inspection | Open |
| 3 | No raw IP in any table, log or analytics record | PRV-01 | inspection + test | Open |
| 4 | Admin Spanish-only confirmed end to end | FR-H-08 | inspection | Open |
| 5 | `raw_documents` retention/pruning scheduled (ADR 0013: 30 days + byte cap) | FR-B-16 | inspection | Open |
| 6 | Pipeline runs on the deployed scheduler; a breaker trip is observable | FR-B-10, FR-B-17 | demonstration | Open |
| 7 | Roles/permissions matrix re-verified against the deployed admin | SEC-13 | demonstration | Open |
| 8 | Documentation sweep: `README`, `CHANGELOG`, `docs/sprints`, matrix | ADR 0001 | inspection | Open |
| 9 | **Retrospective** for v1 | ADR 0001 | inspection | Open |

## What must be true when it ends

1. A restore reproduces the reviewed/published catalogue.
2. Production admin is HTTPS-only, `noindex` and Spanish-only.
3. `PRV-01` verified: no raw IP anywhere, including logs.
4. The scheduler runs ingestion and a failure surfaces.
5. CI green; matrix complete for v1; retrospective written; v1 declared.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | No new code except retention scheduling; the rest is verification |
| Documentation updated | `README.md`, `CHANGELOG.md`, `despliegue.md`, this plan's retrospective |
| CI green | Unchanged pipeline, green on `main` |
| Linked in the matrix | NFR-20, NFR-21, PRV-01, FR-H-08, FR-B-10/16/17 |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| News, media, settings, search | v2 |
| Public submissions | v3 |

## Risks

1. **Backup/restore is the classic "documented but never tested"** — exercise it here or it
   does not exist.
2. **Production admin exposure** — check HTTPS and `noindex` on the deployed host, not from
   settings alone.

## Carried into the next sprint

1. v2 begins: the `sources` citation registry and `news_items` (Sprint 11).
