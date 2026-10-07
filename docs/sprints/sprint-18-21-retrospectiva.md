# Sprints 18–21 retrospective — the public close-out

- **Date:** 2026-10-07
- **Sprint:** 18, 19, 20 and 21, delivered together as one block after the v3 backend.
- **Method:** Start / Stop / Continue, plus what actually happened versus what was planned.
- **Why one retrospective:** the four sprints share one purpose — finish what the v2/v3
  retrospectives carried for lack of an environment, and expose the built backend to the
  public. Sprints 11–13 and 15–16 were already merged the same way.

## What was planned versus what happened

Planned across the four: complete the public site (gallery, submission form), enforce the
retention the privacy policy names, and give content a slug per locale.

What happened: **all four landed, CI green on `c31c97a`, `876e7ae`, `a2b9769` and `38753f0`.**
The suite went from **127 to 143 backend** and **12 to 33 frontend** tests; the matrix moved
from **108 to 136 Done** (sprints 18–21 alone moved 12 rows). Along the way a real
documentation drift was found: the matrix summary still read "1 Done / 167 Open".

Delivered:

- **Sprint 18** — a public **gallery** (citation text, year, author, licence; only `published`
  rows), duplicate refusal on `MediaAsset.content_hash` (FR-E-07), duplicate **submission**
  flagging (FR-F-21), the declared/detected MIME mismatch rule (FR-F-04), deletion of a
  quarantined file on rejection (FR-C-10) and `no-store` on personal responses (PRV-09).
- **Sprint 19** — the anonymous **submission form** (image or video link), with blocking rights
  and consent declarations whose copy says the accepted text is an unreviewed draft, a
  honeypot, and status lookup by token. It also fixed a real gap: `POST /api/submissions/`
  ignored `year` and `place` (FR-F-13).
- **Sprint 20** — `carnaval.privacy.purge_personal_data`, which **enforces** the ADR 0018
  retention periods rather than only naming them (PRV-03, PRV-07).
- **Sprint 21** — **per-locale slugs** (`slug_es` / `slug_en`) on `Edition` and `Day`, matching
  what `modelo-datos.md` had specified (FR-H-07).

Also settled between them: **ADR 0018**, which resolved the v3 legal gate that had been open
since ADR 0016, amending ADR 0008 and setting the maintainer's operational retention and
takedown defaults.

## Start

- **A carried item gets an owner or it disappears.** The gallery was named in Sprint 12's goal
  and Sprint 14's release, and built in neither; Sprint 18 gave it an owning sprint. The same
  pattern caught the submission form, whose gate was resolved before the form was written.
- **Enforce the number, do not publish it.** The privacy policy named retention periods in
  Sprint 18; Sprint 20 wrote the job that makes them true. A period without a mechanism is a
  promise, and the two sprints were deliberately kept apart so the second is real.
- **Dependent work waits for its input.** The submission form (19) was sequenced after the
  legal gate (ADR 0018) and before the retention job (20), not the other way round.
- **Migrate, do not drop.** The per-locale slug change **renames** `slug` to `slug_es`; existing
  rows keep their slug. A `RenameField` was chosen over remove-and-add deliberately.

## Stop

- **The frontend inherited two bugs from the test setup.** React Testing Library could not
  auto-clean between tests (vitest runs without `globals`), which only surfaced once a file
  rendered twice — fixed in `vitest.setup.ts`, and it was making one new test pass that should
  have failed.
- **A test asserted order over a random key.** `order_by("id")` on a UUID primary key is not
  insertion order; the duplicate-submission test was rewritten to identify the original through
  the foreign key instead of a position.
- **The matrix summary had been wrong for four sprints.** Nothing regenerated it, so the
  prose fell behind the rows. It is now checked by hand in the sweep; the count is the math of
  the rows, not a remembered figure.
- **Pre-existing "Done" rows were not re-verified here.** FR-F-01/02 were already Done without
  a form; this block built the form rather than reopening rows it did not touch.

## Continue

- **Validate at the edge and again at the core.** The MIME rule rejects a lying declaration but
  tolerates the aliases and generic types browsers actually send, because a rule that reddens
  on real traffic is a rule that gets turned off.
- **Personal data answers `no-store`; public data answers `public, max-age`.** The two caching
  decisions are deliberate opposites, and both are tested.
- **Keep the sweep honest.** When a summary disagrees with its rows, the summary is wrong.

## What the block proved about the project

The built backend became a **usable site**: a stranger can read the programme, the news, the
gallery and search, submit a photo or a video with real consent, and check its status — and
none of it can be seen until a human approves it. Two v2/v3 guarantees that had only existed
structurally became enforced: byte-duplicates are refused at the database, and retention is a
job, not a sentence.

## Concrete changes adopted

1. A feature in a release sprint's goal must have an owning sprint.
2. Naming a policy value and enforcing it are separate, sequenced pieces of work.
3. The matrix summary is re-counted in the documentation sweep, never trusted as remembered.
