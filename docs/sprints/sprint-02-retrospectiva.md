# Sprint 02 retrospective — the schema the pipeline needs

- **Date:** 2026-10-06
- **Sprint:** 02 — The schema the pipeline needs (the MVP data model)
- **Method:** Start / Stop / Continue, plus what actually happened versus what was planned.

## What was planned versus what happened

Planned: complete the MVP data model — `events` (FR-A-03/04), the three ingestion tables
(`scrape_sources`, `raw_documents`, `ingestion_runs`), the `ingestion_run` link on the
moderation mixin, and a `seed_demo` command so the MVP has published content without an admin.

What happened: all ten backlog items landed and CI is green on both Sprint 02 commits
(`c8e985b`, `624f62f`). The verification, run locally and in CI:

- `pytest`: **25 passed** (from 15).
- `ruff check` / `ruff format --check`: clean, 34 files formatted.
- `mypy backend`: no issues in 34 source files.
- `makemigrations --check --dry-run`: no changes; migrations `ingestion/0001` and
  `programme/0004` reviewed.
- `manage.py check --deploy` with `DEBUG=0`: no warnings; no OpenAPI drift.

Two decisions were made while planning and are now in the code and the design docs: `events`
links to its source with a plain `source_url` for the MVP (the `sources` registry waits for
v2), and the moderation mixin stays on the programme spine rather than only on the four
content tables the design had named.

The plan's own risk — four models plus a seed command in one part-time week — did not
materialise into a slip, but the maintainer split the delivery into a `feat` commit and a
`docs` commit, which is a better shape than the single sprint-sized change the plan implied.

## Start

- **Plan the whole road before the sprint.** Writing the roadmap and the forward plans first
  is what exposed the design drift and the dependency order (`events` and the ingestion
  tables before the extractor, the extractor before the API).
- **Treat "no admin until v1" as a first-class decision.** It forced the `seed_demo` path to be
  explicit, idempotent and guarded instead of a quiet fixture.
- **Keep schema and behaviour in separate sprints.** Tables and the mixin landed with tests and
  a green CI; the extractor gets a stable foundation instead of a moving one.
- **Assert both halves of a private invariant.** `RawDocument.content_hash` is unique at the
  database level; the test proves a duplicate raises rather than trusting the field.

## Stop

- **Letting code and a design document disagree for a whole sprint.** The Sprint 01 review
  fixes applied the moderation mixin to `editions`/`days`/`venues` and removed the stored
  `is_published`, but `modelo-datos.md` §2/§3.1 still described four content tables and a
  stored flag. It was found only while planning Sprint 02. A design doc a code change
  contradicts is updated or reverted **in the same change**, not later.
- **Marking plan items `Done` before the gate.** The sprint table read `Done` while the CI run
  was still queued; the honest status at that moment was "implemented, pending CI". The
  project's recurring false-`Done` pattern is not only a delegated-report problem — the
  author's own status column can carry it too.
- **Discovering an abstract-model gotcha by accident.** `Meta.constraints` is not inherited
  from an abstract base, so the rejection-reason `CHECK` had to be composed per model. It cost
  a regenerate and is now recorded in `AGENTS.md`.

## Continue

- **Verify every claim against the filesystem.** Every `Done` was checked against disk before
  it was trusted.
- **One concern per migration.** `ingestion/0001` and `programme/0004` are separately
  reviewable; the next schema change should stay small for the same reason.
- **Reconcile the docs in the same change as the code** — this sprint did it for
  `modelo-datos.md` §2/§3.1/§3.4 and `estados.md` §1, and the traceability matrix moved only
  the rows whose requirements were actually met (FR-A-03/04), leaving the FR-B rows `Open`
  because their behaviour does not exist yet.
- **Guard the demo path.** `seed_demo` is idempotent, never creates a user, and refuses to run
  with `DEBUG` off unless forced. It is retired as a public-content path in v1.

## What the sprint proved about the project

The schema-now/behaviour-later split works: four models and the mixin landed, tested, with a
green pipeline, and the extractor has a foundation it can rely on. It also proved that the
highest-risk pattern in this repository — a status that says `Done` when the gate has not run —
applies to the maintainer's own planning, not only to delegated work.

## Concrete changes adopted

1. A design document that a code change contradicts is fixed in the same commit; "later" is
   how the Sprint 01/02 drift happened.
2. A sprint plan marks an item `Done` only after CI is green; until then it says
   "implemented, pending CI".
3. `AGENTS.md` records that `Meta.constraints` is not inherited from an abstract base and that
   content tables inherit `ModeratedModel` with a derived `is_published`.
4. `seed_demo` is documented as the MVP's only publishing path and is retired in v1.
