# Sprint 12 retrospective — media gallery and rights

- **Date:** 2026-10-06
- **Sprint:** 12 — Media gallery and rights
- **Method:** Start / Stop / Continue.
- **Note:** delivered with Sprints 11 and 13 as the v2 backend (`5e73a4f`); see also
  `sprint-13-retrospectiva.md`.

## What was planned versus what happened

Planned: a historical image gallery in which **every published image is lawfully publishable** —
author, source, licence and citation present, `rights_status` not `unknown`, EXIF stripped,
duplicates refused, minors gated — enforced on **every** path, not only the form.

What happened: **the highest-risk table and its gate landed; the UI did not.** The v2 backend is
`5e73a4f` (**111 backend tests**). The matrix moved **FR-E-04, FR-E-05, FR-E-08, FR-E-09 and
LEG-02, LEG-09 to Done.**

Delivered: `MediaAsset` with the rights fields, `exif_stripped`, `featured`, `minor_subject` and
`guardian_consent_on_file`; the publish gate as **two database `CHECK` constraints** plus a
`publish_blockers()` hook the moderation service consults; EXIF required at approval; the
minor-subject gate; and the `editor`'s feature toggle.

Carried, and named: the **gallery UI** (FR-E-06, LEG-03) and **duplicate refusal** (FR-E-07) —
both landed later, in **Sprint 18** — and the **quarantine-key guarantee** (FR-F-08/09), which
needs object storage and is still carried.

## Start

- **The gate is data, not a form.** `rights_status = unknown`, a missing author, source or
  citation, an un-stripped EXIF tag, or a minor without guardian consent each block publication
  **at the database**; `publish_blockers()` gives the reviewer the reason. A bulk action or a
  future pipeline cannot bypass a `CHECK`.
- **Old photos are not free of rights.** `unknown` is the default and is never auto-filled; the
  requirement is that the project cannot publish what it cannot justify.
- **EXIF is re-verified, not assumed.** Approval requires `exif_stripped` to be true, and a
  re-injected tag is a test case.

## Stop

- **I forgot the UUID primary key.** `MediaAsset` and `NewsItem` inherited an auto-increment PK
  instead of the UUID every other table uses; a test caught it only because it compared a string
  id to an int. Fixed with a field and a regenerated migration.
- **A test built data the gate forbids.** A factory created a `published` `MediaAsset` with the
  default `unknown` rights, which the `CHECK` refuses — the **test was wrong, not the code**.
  Test data must be as lawful as the gate demands.
- **The gallery was in the goal and in nobody's backlog.** The UI the model was built for was
  not built here; it fell between this sprint and Sprint 14's release and was only found in the
  Sprint 18 sweep.

## Continue

- **Keep the gate at the database.** A `CHECK` is the difference between a rule and a hope.
- **Do not weaken the gate for tests or for convenience.**
- **Name every carried item** in the plan's Status column.

## What the sprint proved about the project

The riskiest object in the schema — an image — became publishable only when it is lawfully
publishable, and the rule is enforced **below** the application. Sprint 18 later rendered the
fields, and could not render an unlawful image, because the model never allowed one to exist in
`published`.

## Concrete changes adopted

1. Every table gets a UUID primary key; the design says so and the code follows.
2. Factories produce data that satisfies the constraints — the gate is never relaxed for tests.
3. A feature named in a goal must have an owning sprint (the gallery lesson).
