# Sprint 04 retrospective — the extractor, part 2

- **Date:** 2026-10-06
- **Sprint:** 04 — The extractor, part 2: transform, sanity gate and staging
- **Method:** Start / Stop / Continue, plus what actually happened versus what was planned.

## What was planned versus what happened

Planned: the `wp_api` transform, schema validation, the sanity gate, staging as `pending`,
`Event.source_record_key`, and end-to-end run statistics. It stops at STAGING; nothing is
published.

What happened: all seven backlog items landed and **CI is green on `383af93`**. The suite grew
from 43 to **63 tests**; `ruff` (61 files), `mypy` (61 source files), `makemigrations --check`,
`check --deploy` and the OpenAPI drift check are clean, and the diagram validator passes.
**SEC-40** now has an executable test and **SEC-37 closes end to end**: two runs over one
payload produce zero duplicates. The matrix moved **FR-B-04, 05, 06, 11 and 15 to Done**;
FR-B-01 stays Open because the chain still ends at STAGING (review and load are v1), FR-B-07
because the load path is v1, and FR-A-12 because the source link is only rendered by the site
(Sprint 06).

## Start

- **Reconcile two contradictory source signals.** The spike warned that slugs and dates
  disagree and that day labels carry no year, so the transform takes the **day from the
  category name** and the **year from the post date**. Neither signal is trusted alone.
- **Collect days by name pattern, not hierarchy.** The `6 de enero` category is a root
  category, so "children of `DIAS`" would drop the Day of Whites; a test asserts it is present.
- **A pure sanity gate.** `sanity.check(report, history, target_year)` reads a
  `TransformReport` and returns reasons; it needs no database and no network, so every branch
  is a unit test.
- **Staging with a guard, not a convention.** Editions and days use `get_or_create` and are
  never modified; an event is written only when it is new or an existing `pending` row the
  pipeline itself created (`origin = scraped`). A `published` or human-authored row is skipped.
- **Reduced fixtures.** The `wp_posts` fixture carries only id, date, slug, link, title and the
  embedded terms, so no third-party article text is committed (LEG-05).

## Stop

- **A previously passing test encoded the old pipeline.** The Sprint 03 fetch-and-store test
  used a body of `b"data"`; once the transform landed, that is not JSON, so the run failed. The
  assumption "store and stop" was correct for one sprint and wrong for the next. **When a
  sprint adds a stage, revisit the tests of the stage before it**, not just extend them.
- **The edition-alignment guard was off by default.** `_target_year` first read only a setting,
  which would leave the spike's top risk unguarded unless an operator remembered to configure
  it. It now falls back to the newest edition, so the guard is on without configuration, and a
  test pins that.
- **§5.1 is still decided by not deciding.** The pipeline refuses to overwrite a published row
  and counts it as skipped; the mechanism to *propose* a change still waits for its ADR
  (Sprint 09). That is named here rather than left as an implicit behaviour.

## Continue

- **Keep the gate pure and the interfaces explicit.** `EventCandidate` and `TransformReport`
  are the boundary between fetch and stage; the gate and the staging are testable in isolation
  because of it.
- **Verify against the filesystem and the CLI.** Running the command, not just the unit tests,
  is what exposed the stale local database in Sprint 03 and the changed test here.
- **Move only the requirements that are actually met.** FR-A-12 and FR-B-07 stayed Open because
  their behaviour does not exist yet, even though adjacent code landed.

## What the sprint proved about the project

The brief's top risk — the source changes and the extractor "succeeds" with nothing — is now a
mechanism, not a hope: an empty payload, a drop, a spike, a missing required field or a
wrong-year import each raise an alarm, and the pipeline cannot overwrite public content even
when the source lies. The moderation gate stays human because the pipeline's write surface is
limited to `pending` rows it owns.

## Concrete changes adopted

1. When a stage is added, revisit the tests of the previous stage; an assumption can expire.
2. A guard that exists because a spike proved a real risk is on by default, with a test.
3. The pipeline proposes nothing it cannot own: published and human-authored rows are read-only
   to it until §5.1 has its ADR.
4. Fixtures stay reduced to the fields the pipeline consumes.
