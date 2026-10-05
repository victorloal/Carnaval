# Sprint 01 — The repository that runs

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** Turn a documentation-only repository into one that builds. When this
  sprint ends, `manage.py check` passes, the first migrations apply, an `openapi.yaml`
  exists **and is enforced**, and the 14 CI stages in `plan-pruebas.md` §7 run green — with
  **no test ever touching the network**.
- **Starts:** 2026-10-05 (planned)
- **WIP limit:** 2 items (ADR 0001)

> This sprint does **not** deliver the data model, the scraper, the Django admin, the public
> site, or submissions. It delivers the machinery that makes the rest reviewable: linters,
> a migration path, a generated contract, and a CI pipeline that can refuse a bad change.
> Everything after this sprint is blocked on it.

## Sprint backlog

Ordered; with a WIP limit of 2, items are taken top-down.

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | Django project skeleton in `backend/`; `manage.py check` passes | NFR-14 | `ruff` + `mypy` clean | Done |
| 2 | Settings read **only** from environment variables; no secret in the tree | NFR-09 | **SEC-46** | Done |
| 3 | `ruff` and `mypy` configured, zero errors, no exceptions in the config | NFR-14 | CI stage 1–2 | Done |
| 4 | First migration set: moderation mixin + the programme spine (`editions`, `days`, `venues`) | NFR-13 | reviewed in the PR | Done |
| 5 | `drf-spectacular` wired; first `docs/02-diseno/openapi.yaml` **committed** | NFR-12, ADR 0011 | CI stages 7–8 | Done |
| 6 | GitHub Actions workflow running `plan-pruebas.md` §7 in the documented order | NFR-11 | pipeline green | Done |
| 7 | Mechanical **no-egress guard** on the test suite | NFR-16 | CI: no egress | Done |
| 8 | `backend/tests/fixtures/` convention + `factory_boy` factories | NFR-16, plan §5 | inspection | Done |
| 9 | `scripts/check-diagrams.cjs` wired into the lint stage | ADR 0014 | exits non-zero | Done |
| 10 | Dependabot configuration | NFR-10 | inspection | Done |
| 11 | Matrix rows for items 1–10 moved from `Open` to their real status | ADR 0001 DoD 4 | inspection | Done |

### Why item 7 is a guard and not a rule

`NFR-16` says *"No test shall contact a live external source"*, and its verification method in
the matrix is **`CI: no egress`** — a mechanism, not a convention. The implementation is a
session-scoped blocker on outbound sockets that permits **loopback only** (`localhost`,
`127.0.0.1`, `::1`, so PostgreSQL still connects) and refuses everything else. A test that
reaches for the network then fails for an infrastructure reason, which is the point: the
project's highest-risk failure mode is a suite that *happens* not to make live calls today,
and starts doing so the week someone is in a hurry.

Fixtures replayed from `backend/tests/fixtures/` are the positive half of the same
requirement. Sprint 01 delivers the **convention and the directory**; the first real payloads
arrive with the extractor, because a fixture with no code to consume it cannot be tested
against anything.

## What must be true when it ends

These are the exit criteria, and they are mechanical — each is a thing that either runs or
does not.

1. `git clone` + `pip install -r requirements.txt` + `python manage.py check` succeeds on a
   clean machine with only environment variables set.
2. `makemigrations --check --dry-run` finds nothing to do, so **drift fails the build**
   rather than being discovered at deploy time (NFR-13).
3. `spectacular --validate --fail-on-warn` passes, and regenerating the schema followed by
   `git diff --exit-code` on `docs/02-diseno/openapi.yaml` is clean (NFR-12, ADR 0011).
4. The workflow runs its stages **in the documented order** and a deliberately failing
   change blocks at the first broken stage, not the last (NFR-11).
5. A test that attempts an outbound connection fails the run (NFR-16).
6. `ruff check`, `ruff format --check` and `mypy backend/` report zero errors (NFR-14).
7. `node scripts/check-diagrams.cjs .` runs inside CI and would fail on a diagram regression
   (ADR 0014).

Item 7 deserves emphasis, because ADR 0014 deferred exactly this. Until it is wired, the
diagram check only exists for someone who happens to install `mermaid` and `jsdom` and run it
by hand — which is how the first false green survived long enough to be found.

## Definition of Done

ADR 0001's four conditions, applied per backlog item:

| Condition | How it is met here |
|---|---|
| Code with tests | Every item above that is code ships with a test; item 7 ships with a test that *proves egress is blocked* |
| Documentation updated | `CHANGELOG.md`, `README.md` status table, and the relevant design document |
| CI green | The workflow exists **and has run green on the branch** — a workflow file that has never executed is not CI |
| Linked in the matrix | Item 11; the seven NFR rows above already carry their verification methods and need only their status moved |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| The rest of the data model (editorial, security, submissions, legal tables) | Requires the migration-review path (item 4) to exist first, so that a large migration lands reviewed rather than as a first attempt |
| The scraper and any ingestion code | Needs fixtures, the rate limiter and the circuit breaker together; partial delivery would ship the failure mode without the protections |
| Django admin screens | Nothing exists to review until content tables land |
| Public submissions (v3) | ADR 0008 deliberately places submissions last |
| The React public site | The API contract (item 5) must exist before a client can be built against it |
| `docs/legal/` work | Unrelated to the build, and ADR 0016 settled its status: permanent drafts with a DRAFT notice, never reviewed |
| **ADR 0015** (egress cost) | Decides the storage provider, which is a deployment question — after the schema exists |

## Risks

1. **Stage 11 (`docker compose up` + Playwright) is the one most likely to fail on free-tier
   minutes.** It is also the only stage that cannot be reasoned about locally the way a
   linter can. If it blocks, the honest move is to keep it running on branches and `main`
   only, which `plan-pruebas.md` §7 already permits — not to delete it.

2. **The first migration is the one nobody reviews carefully**, because there is nothing yet
   to compare it against. Item 4 is deliberately *small* for that reason: a spine of four
   tables proves the review path on something tractable, so the big migration later is a
   second review rather than a first.

3. **`openapi.yaml` will not exist until item 5**, so stages 7–8 must not be marked passing
   before it is committed. Wiring the workflow in the order above makes this self-evident.

4. **A green pipeline on day one proves little.** It is worth deliberately breaking the
   build once — flip an assertion, commit, watch the stage fail, revert — to confirm the
   pipeline can actually refuse a change. A CI that has never failed has not been tested.

## Carried into the next sprint

1. The remainder of the data model, one package per migration, reviewed in the PR (NFR-13).
2. The extractor with its committed fixtures, rate limiting, `Crawl-delay`-aware politeness
   and the circuit breaker (FR-B-01 … FR-B-19) — after re-reading `robots.txt`, per
   `fuentes-y-atribucion.md` §5.
3. `estados.md` §7's remaining open items and `flujo-datos.md` §5.1, once content tables
   exist to change.
4. ADR 0015, when the schema makes the storage decision concrete.
5. Contact Corpocarnaval (brief §20), and the site's terms of use, which remain **not found**
   (`fuentes-y-atribucion.md` §9.5).
