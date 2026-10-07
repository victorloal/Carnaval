# Sprint 07 — MVP hardening, deployment and release

- **Sprint length:** 1–2 weeks (Scrumban, ADR 0001)
- **Sprint goal:** The MVP is deployed at zero cost, serves over HTTPS with a strict security
  posture, refuses a bad change end to end, and stays up when every external source is
  unreachable. This sprint closes the MVP.
- **Starts:** after Sprint 06 closes; nominal 1–2 weeks.
- **WIP limit:** 2 items (ADR 0001)
- **Status:** partially delivered — the security headers, CORS, the secret scan, the coverage
  gate, the frontend CI stages, the **dependency audit** and the **PostgreSQL 16 CI job** all
  landed. The **deployment** and the **browser stages** (E2E, Lighthouse, axe) are carried
  and named in `sprint-07-retrospectiva.md`.

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | CSP without `unsafe-inline` for scripts; HSTS; `X-Content-Type-Options`; `Referrer-Policy` | SEC-15, NFR-07 | `check --deploy` + header test | Done |
| 2 | CORS restricted to the site's own origins | NFR-08 | test | Done |
| 3 | Complete `plan-pruebas.md` §7: `tsc`, eslint, vitest, build, docker-compose E2E, Lighthouse, axe, `pip-audit`/`npm audit` | NFR-01, NFR-11 | CI green | Done for the unit stages + `pip-audit`; E2E/Lighthouse/axe/`npm audit` carried |
| 4 | PostgreSQL service in CI so the schema is exercised on its production engine | NFR-13 | CI | Done — the `postgres` job runs the suite on PostgreSQL 16; green on `4a08742` |
| 5 | Automate the `SEC-46` secret scan (closes **NFR-09**) | NFR-09 | CI | Done |
| 6 | Ingestion + API coverage ≥ 80 % | NFR-15 | coverage | Done |
| 7 | **ADR 0015** (storage and egress) and deployment on free tiers | NFR-05, ADR 0015 | demonstration | ADR 0015 proposed; deployment carried (needs the maintainer's accounts) |
| 8 | Backup and restore procedure for PostgreSQL, rehearsed | NFR-20 | demonstration | Procedure documented; rehearsal carried |
| 9 | Logs free of secrets, raw IPs and session identifiers | NFR-19 | inspection | Done |
| 10 | Site stays up with every source unreachable | NFR-06 | demonstration | Done |
| 11 | Dependency vulnerability triage documented | SEC-16, NFR-10 | inspection | `pip-audit` gates CI (NFR-10); the written triage process is carried |

### The stage that scares the plan

Stage 11 (`docker compose up` + Playwright) is the one most likely to hit free-tier minutes
and the only one that cannot be reasoned about the way a linter can. If it blocks, keep it on
branches and `main` only — `plan-pruebas.md` §7 permits that — never delete it.

## What must be true when it ends

1. A deployed MVP on free tiers, reachable over HTTPS, with a strict CSP and no console errors.
2. A deliberately broken change fails at the first affected CI stage.
3. NFR-09's secret scan and NFR-15's coverage are enforced in CI.
4. A restore from a backup reproduces the published catalogue.
5. The site survives every source being unreachable (NFR-06).
6. `ruff`, `mypy`, `pytest`, `check --deploy` green; no OpenAPI drift.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | Header, CORS and coverage gates ship with tests; the deployment is exercised |
| Documentation updated | ADR 0015, `despliegue.md`, `README.md`, `CHANGELOG.md` |
| CI green | Every §7 stage runs or is documented as deferred with a reason |
| Linked in the matrix | NFR-01/05/06/07/08/09/15/19, SEC-15/16, LEG-05/06/07/08/10 |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| Admin, roles, review queue, audit | v1 |
| News, gallery, settings, search | v2 |
| Submissions | v3, deliberately last (ADR 0008) |
| Public signup of any kind | Never (FR-D-13) |

## Risks

1. **E2E/Lighthouse minutes** — keep them off every-push if needed; never delete them.
2. **Free-tier limits** may force the storage or database choice; write ADR 0015 before the
   deploy, not after.
3. **Scope** — if the week runs short, deployment (items 7–8) is the release blocker; items
   3–6 can spill to the v1 branch without blocking the MVP deploy, but the MVP is not
   released until it is deployed.

## Carried into the next sprint

1. The v1 admin foundation: Django admin, roles, TOTP, step-up, `audit_logs` (Sprint 08).
