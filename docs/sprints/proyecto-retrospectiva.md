# Project retrospective — the close

- **Date:** 2026-10-07
- **Scope:** the whole project, Phase 0 (documentation) through the v3 close-out (Sprints 00–21)
- **Method:** what was delivered, what was carried and why, what the project taught, and how it
  closes.
- **Status of the project:** **complete in code; not launched.** The deployment is the one
  thing left and it is a human act, not a sprint.

## What was delivered

Four versions, built in order, each on top of a working previous one (ADR 0008):

| Version | Backend | Public site |
|---|---|---|
| MVP | Ingestion pipeline (robots, rate-limit, raw store, hash idempotency, sanity gate, circuit breaker, staging), programme spine, published-only read API, `/health` | Programme grouped by day, two locales, disclaimer |
| v1 | Django admin behind a permission matrix, roles, TOTP, audit log, review queue, `staged_changes` proposals (ADR 0017) | — (the admin is Django's, Spanish only) |
| v2 | Citation registry, news, media with a database-level rights gate, typed settings, search | News list, gallery with citation, search |
| v3 | Anonymous submissions (magic-byte validation, re-encode, EXIF strip, quarantine, salted-IP quotas, honeypot), legal register, takedown with escalation | Submission form, status lookup |

Cross-cutting, built along the way: server-side sessions with no JWT (ADR 0005), generated
OpenAPI with a drift gate (ADR 0011), a real no-egress test guard, a dependency audit and a
PostgreSQL CI job, and `purge_personal_data` enforcing the retention periods (ADR 0018).

## The numbers at the close

| | |
|---|---|
| Requirements tracked | **170** — **136 Done, 33 Open, 0 blocked** (`matriz-trazabilidad.md`) |
| Backend tests | **143** (pytest), coverage gate ≥ 80 % on ingestion + API (measured 93 %) |
| Frontend tests | **33** (vitest + testing-library) |
| ADRs | **18** (0001–0018) |
| CI | two jobs — `ci` on SQLite, `postgres` on PostgreSQL 16 — green on `main` |
| Legal texts | four, permanently labelled drafts (ADR 0016), published under ADR 0018 |

## What was carried, and why

Everything still Open falls into four buckets, none of them "forgot to":

1. **Deployment** — backups (NFR-20), HTTPS in production (NFR-07), the scheduler (FR-B-17/18),
   the deployed security sweep, DNS and launch. Needs the maintainer's accounts and a host.
2. **Browser** — Lighthouse, axe, Playwright E2E (NFR-01/03/04, FR-A-13, FR-G-08). Needs a
   browser environment; a jsdom proxy would be a false green.
3. **Object storage** — the gallery `<img>`, the quarantine → public move, signed URLs
   (FR-F-08/09, SEC-13). ADR 0015 is Proposed because it needs accounts to accept.
4. **Smaller content work** — the news transform (needs a chosen source, FR-E-02/03) and
   verbatim citations with a translation (FR-H-09).

A fifth, smaller set is manual re-verification (SEC-05/09/10, FR-D-15) whose reason is recorded
in the matrix.

## What the project taught

- **Documentation drifts silently, and the sweep is the only cure.** The matrix summary read
  "1 Done / 167 Open" while the body carried 108 Done rows; `AGENTS.md` and `SECURITY.md` were
  both describing a project several sprints behind. Every one was found by comparing documents
  to the **filesystem**, never to each other.
- **A completion report is not evidence.** Repeatedly, "Done" was true of a plan and false of
  the repository — a no-op test, a missing factory, a form that ignored two fields. The habit
  that worked is a one-line check of the artefact before believing the claim.
- **Decisions belong in ADRs, not commit messages.** ADR 0018 turned a three-week open conflict
  into a buildable feature by making the choice explicit; ADR 0017 did the same for changes to
  published rows.
- **The gate below the application outlives the UI.** The media rights `CHECK` was correct
  before any gallery existed, so the gallery could not render an unlawful image even by
  mistake. Structural guarantees survive; conventions do not.
- **A policy value is not a policy.** Retention periods meant nothing until
  `purge_personal_data` ran; naming and enforcing were kept as separate, sequenced work.
- **Name the not-done.** Every carried item says why, which is what makes the matrix usable.

## Start / Stop / Continue, in one line each

- **Start** with the decision recorded, not with the code that needs it (the v3 gate).
- **Stop** treating a green check as a launch (nothing is live).
- **Continue** verifying claims against the filesystem and keeping the matrix the single source
  of truth.

## How the project closes

The project is **closed as an engineering deliverable**: four versions implemented, tested and
running in CI, with a bilingual public site and a moderated ingestion pipeline. It is **not
launched**, and it does not claim to be. The remaining work is the deployment, which needs the
maintainer's accounts and is the first thing the post-launch checklist (`despliegue.md` §10)
covers.

Nothing is hidden: the Open rows, the labelled-draft legal texts, the unanswered letter to
Corpocarnaval and the source's missing terms of use are all recorded where a reader will find
them. `matriz-trazabilidad.md` is the single source of truth for what was and was not done.
