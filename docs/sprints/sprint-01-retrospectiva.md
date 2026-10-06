# Sprint 01 retrospective — the repository that runs

- **Date:** 2026-10-06
- **Sprint:** 01 — The repository that runs
- **Method:** Start / Stop / Continue, plus what actually happened versus what was planned.

## What was planned versus what happened

Planned: the seven exit criteria in `sprint-01-plan.md` — a Django skeleton whose
`manage.py check` passes, settings read from environment only, `ruff`/`mypy` clean, the first
migration set, a committed and drift-enforced `openapi.yaml`, the CI pipeline, and a
mechanical no-egress guard.

What happened: all eleven backlog items landed and were re-verified on 2026-10-06 — `pytest`
10 passed, `ruff check` and `ruff format --check` clean, `mypy` clean, `manage.py check` and
`makemigrations --check --dry-run` clean, and `spectacular --validate --fail-on-warn` clean.
The programme spine (`editions`, `days`, `venues`) and the `core` moderation enums are the
first migrations, and the no-egress guard is real, with tests proving both the block and the
loopback exception.

Two gaps remain, and they are not the same kind:

1. **The sprint goal named fourteen CI stages; only the backend/docs subset is wired.** Stages
   3–5 and 10–14 of `plan-pruebas.md` §7 (frontend `tsc`/eslint/vitest/build, docker-compose
   E2E, Lighthouse, axe, dependency audit) need a frontend and an E2E stack that do not exist
   yet. This is a goal that was unachievable by design, not a missed item: the plan listed the
   frontend as out of scope while the goal text still counted the frontend's stages.

2. **The final commit has never run in CI.** At the close of the sprint, local `main` was one
   commit ahead of `origin/main`: `5d08331`, the review-fix commit that made the egress guard
   real. The only green CI run on `main` is on `e3f5c52`, which is *before* those fixes. ADR
   0001's DoD says a workflow that has never executed is not CI; by the same argument, a fix
   commit that never ran is not verified. Pushing it is the first action of the next session.

Two items are open without blocking: `NFR-09` remains `Open` in `matriz-trazabilidad.md`
(its verification, `SEC-46`, is done, but the secret scan is not automated), and
`docs/02-diseno/openapi.yaml` is committed with `paths: {}` because no endpoint exists yet —
expected, not a defect.

## Start

- **Settings that fail loudly.** `SECRET_KEY` absent now raises `ImproperlyConfigured` and
  `DEBUG` defaults off (SEC-46). A default that silently works is a default that silently ships.
- **The no-egress guard as a mechanism, not a convention.** NFR-16 is enforced by a
  session-scoped blocker on outbound sockets, with proof tests, so a test that reaches the
  network fails for an infrastructure reason.
- **Committing the generated contract.** `openapi.yaml` is regenerated in CI and
  `git diff --exit-code` fails the build on drift (ADR 0011).
- **A deliberately small first migration.** Four tables prove the review path on something
  tractable, so the large migration later is a second review rather than a first.

## Stop

- **Marking items Done without a filesystem check.** The sprint carries its own lesson: the
  egress guard shipped as `assert True`, the factories did not exist, and the plan said Done
  (`MEMORY.md`, 2026-10-05). Both were caught only when someone looked.
- **Writing a goal whose verification counts components the sprint excludes.** The fourteen
  stages should have been quoted as "stages 1, 2, 6–9 and the docs check now; the rest when
  their components land".
- **Leaving the last commit unpushed.** The sprint closed with its most important change
  unvalidated. The machine that produced the fix should not be the only place it ran.
- **`AGENTS.md` drifting a whole sprint behind the repository.** It still described an
  empty `backend/`, no linter, no test runner and no CI while all four existed. A binding
  document that describes a repo that no longer exists is worse than no document; it was
  corrected on 2026-10-06.

## Continue

- **Verify against the filesystem, not the report.** Every "Done" in this sprint was checked
  against disk before it was trusted.
- **Let CI refuse a change.** Nine dependency-update pull requests did fail CI, which is
  evidence the pipeline can block — the sprint plan's own risk note asked for exactly that
  deliberate failure.
- **Update the traceability matrix in the same commit as the code** (items 11 and
  FR-A-01/FR-A-02), rather than in a follow-up.

## What the sprint proved about the project

The false-Done pattern is the project's recurring failure mode, and human review is the only
thing that has caught it. Sprint 01 delivered machinery whose whole purpose is to make that
pattern expensive: lint and type gates, a migration check, a schema-drift check, a diagram
check, and an egress guard. The honest reading is that the machinery works — and that the
repository still needed a person to notice that the plan was lying.

## Concrete changes adopted

1. Push `5d08331` and confirm CI is green on `HEAD` before the sprint is called closed.
2. Plan the remaining `plan-pruebas.md` §7 stages as their own items, each tied to the
   component that unblocks it, instead of as a single "finish CI" catch-all.
3. When a goal quotes a numbered list, name the in-scope subset explicitly.
4. Re-read `AGENTS.md` at the end of every sprint against the filesystem, alongside
   `MEMORY.md`.
