# Sprint 07 retrospective — hardening, and the MVP's open edge

- **Date:** 2026-10-06
- **Sprint:** 07 — MVP hardening, deployment and release (partially delivered)
- **Method:** Start / Stop / Continue, plus what actually happened versus what was planned.

## What was planned versus what happened

Planned: security headers and CORS, the complete `plan-pruebas.md` §7 stages, a PostgreSQL
service in CI, the SEC-46 secret scan, a coverage gate, ADR 0015 and the deployment, a backup
and restore procedure, log hygiene, and the no-source-available guarantee.

What happened: **the half that can be verified in this environment landed, and the half that
needs accounts, a Docker daemon or a browser is carried — named, not hidden.** Delivered and
green: strict CSP, `Referrer-Policy`, `X-Content-Type-Options`, CORS, the SEC-46 secret scan
(closing **NFR-09**), the coverage gate (**NFR-15**, measured 93 % of ingestion + API), the
frontend CI stages, the console `LOGGING` config (**NFR-19**), and **ADR 0015 (Proposed)**.
The suite is at **77 backend tests** and **12 frontend tests**; the matrix moved NFR-06/08/09,
NFR-15, NFR-19 and SEC-15 to Done.

Carried, with a reason:

- **The deployment** (item 7) needs the maintainer's accounts; ADR 0015 is Proposed, not
  Accepted.
- **The PostgreSQL CI service** (item 4) and **the browser stages** — `docker compose` +
  Playwright, Lighthouse, axe, dependency audit (part of item 3) — could not be verified: the
  Docker daemon is not running here and no browser is provisioned. They are not wired, so a
  half-written E2E job never reddens `main`.
- **The backup rehearsal** (item 8): the procedure is documented; rehearsing it needs the
  deployed database.
- **Dependency-vulnerability triage** (item 11): Dependabot is on; the triage process is not
  written.

## Start

- **Scope the header to where it is safe.** A strict CSP with no `unsafe-inline` is applied to
  everything except `/admin/`, because Django admin uses inline scripts; a broken console is
  worse than no header, and the admin's own CSP is a v1 concern. The public surface gets the
  policy, with a test.
- **Scan the tracked tree, not the working copy.** `scripts/check_secrets.py` reads
  `git ls-files`, so a gitignored `.env` is ignored by construction rather than by a rule
  someone must remember.
- **Put the coverage gate where the requirement is.** NFR-15 names the ingestion pipeline and
  the public API, so the gate is `--cov=carnaval.ingestion --cov=carnaval.api
  --cov-fail-under=80`, not a whole-project number that a well-covered module could inflate.
- **Wire the frontend into the pipeline at last.** `tsc`, eslint, vitest and build run in CI;
  the gap Sprint 06 named is closed for the unit half.

## Stop

- **Do not wire what cannot be verified.** A PostgreSQL job, an E2E job or a Lighthouse job
  that has never run is a green that proves nothing, and it turns the pipeline red for a
  reason no one can reproduce. They stay off the main path until the environment exists.
- **ADR 0015 is Proposed, not Accepted.** Writing it as Accepted would claim a platform
  decision that requires accounts; it compares the candidates and recommends one, and the
  acceptance is the maintainer's act.
- **NFR-07 stays Open.** The headers are in place, but "all traffic over HTTPS" is a
  deployment fact, and there is no deployment yet.
- **The E2E stage is the plan's own named risk** — "the one most likely to fail on free-tier
  minutes" — and it is exactly the one not done. That is not a surprise; it is the sprint's
  stated shape.

## Continue

- **Name carried items in the plan's Status column and here**, so the next sprint starts from
  truth rather than from a Done that is not.
- **Prefer a scoped guard over a broad claim**: the CSP test reads the real header, the secret
  scan reads the real index, the coverage gate reads the real modules.
- **Keep the deployment a human act.** Nothing in this sprint pretends a host was chosen.

## What the sprint proved about the project

The security posture and the pipeline can be enforced without a deployment: headers, CORS, a
secret scan and a coverage gate are all testable today. What remains is not code but access —
a host, a database, a bucket and a browser — and the honest deliverable is a Proposed ADR and
a list of carried items, not a released MVP.

## Concrete changes adopted

1. Nothing runs in CI that has not been run by a human first; the E2E/Postgres/Lighthouse jobs
   wait for an environment that can execute them.
2. ADR 0015 stays Proposed until the accounts exist.
3. The MVP's release checklist in this plan is the next sprint's first item.
