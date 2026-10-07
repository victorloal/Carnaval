# Sprint 10 retrospective — v1 completion and release (not run)

- **Date:** 2026-10-06 (recorded 2026-10-07)
- **Sprint:** 10 — v1 completion and release
- **Method:** Start / Stop / Continue, plus what actually happened versus what was planned.
- **Verdict:** **the sprint was never executed.** There is no deployment, so a sprint whose
  whole purpose is "make the previous two sprints true on the deployed system" had nothing to
  run against. This retrospective records that, rather than inventing a green.

## What was planned versus what happened

Planned: prove a backup/restore on the deployed database, verify the admin is HTTPS-only and
`noindex` **in production**, confirm no raw IP in any table or log, confirm the admin is
Spanish-only, schedule the raw-document pruning, run the pipeline on the deployed scheduler,
re-verify the roles matrix against the deployed admin, sweep the docs, and close v1.

What happened: **none of the deployment-dependent items ran**, because the MVP itself was
never deployed (Sprint 07 carried it for lack of the maintainer's accounts). The v1 **backend**
— roles, TOTP, audit, the review queue, `staged_changes`, the permission matrix — was delivered
in Sprints 08a/08b/09 (`ffcc353`) and its retrospective exists (`sprint-09-retrospectiva.md`).

The half that does not need a deployment was closed later, at the application layer, and is
marked Done in the matrix with its real verification:

| Item | State |
|---|---|
| No raw IP anywhere | **PRV-01 Done** — salted-hash tests, not an inspection of a running log |
| Admin Spanish-only | **FR-H-08 Done** — the middleware is tested |
| `noindex` on the admin | **NFR-21 Done (partial)** — the header is tested; **HTTPS at the deployment is carried** |
| Raw-document retention | **FR-B-16 Done** — `prune_raw_documents` enforces the window and byte cap |
| Circuit breaker observable | **FR-B-10 Done** — the breaker is tested |

Carried, and it is the whole point of the sprint: the **backup/restore rehearsal** (NFR-20),
the **scheduler** (FR-B-17), **HTTPS in production** (NFR-07), and the deployed re-verification
of the roles matrix (SEC-13).

## Stop

- **A "release" sprint cannot be run without a release.** Treating these items as done because
  the code that *would* satisfy them exists is exactly the false green the project keeps
  guarding against. They stay Open with the reason "needs a deployment".
- **Do not mark the version released.** v1's backend is built; v1 is not released. The version
  table in `README.md` says so.

## Continue

- **Separate "built" from "released" everywhere.** The matrix tracks requirements, not
  deployments; where a requirement's verification is a demonstration on a running system, it
  cannot be closed from a unit test.

## What this sprint recorded about the project

The project has a recurring shape: **its code runs ahead of its environment.** v1's backend was
finished in three sprints while the deployment that would prove it was deferred, and the honest
response was to leave the release open rather than to call it done. That shape repeats in
Sprints 14 and 17.

## Concrete changes adopted

1. Release/verification sprints (10, 14, 17) are recorded as **carried**, not as retrospectives
   describing delivered work.
2. The matrix keeps "needs a deployment" as the reason on every row that requires one.
