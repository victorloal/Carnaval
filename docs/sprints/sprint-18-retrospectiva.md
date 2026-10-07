# Sprint 18 retrospective — the gallery and submission integrity

- **Date:** 2026-10-07
- **Sprint:** 18 — v2/v3 close-out, part 1: the gallery and submission integrity
- **Method:** Start / Stop / Continue.
- **Note:** first of the four close-out sprints (18–21); see also
  `sprint-18-21-retrospectiva.md`.

## What was planned versus what happened

Planned: render a published image with its **citation** in the public gallery, and enforce the
integrity rules carried from v2/v3 — duplicate bytes, a lying content type, deletion on
rejection and a non-cacheable personal response.

What happened: **all six items landed and CI is green on `c31c97a`.** The suite reached **133
backend + 27 frontend tests.** The matrix moved **FR-C-10, FR-E-06, FR-E-07, FR-F-04, FR-F-21,
LEG-03 and PRV-09 to Done** — seven rows, several of them carried since Sprints 12 and 15.

Delivered: the gallery page (a `MediaList` showing title, year, author, licence and citation
text; only `published` rows), a partial unique constraint on `MediaAsset.content_hash`
(FR-E-07), `SubmissionFile.duplicate_of` set from a content-hash match (FR-F-21),
`declared_mime_conflicts` (FR-F-04), quarantine deletion on rejection (FR-C-10), and
`Cache-Control: private, no-store` on the submission endpoints (PRV-09).

## Start

- **The citation is the point of the gallery.** An old photo is not free of rights; the card
  carries what makes it lawfully showable, and only `published` rows reach it.
- **The gate below the application outlives the UI.** The rights `CHECK` had been correct since
  Sprint 12, so the gallery could not render an unlawful image — it only had to render fields.
- **A declared type is a claim; the bytes are the fact.** The mismatch rule rejects a **concrete**
  `image/*` declaration that contradicts the bytes and tolerates the aliases and generic types
  browsers actually send — a rule that reddens on real traffic is a rule that gets turned off.
- **Migrate, do not drop.** The duplicate constraint is a **partial** unique index
  (`condition`), so the empty "no hash recorded" case is untouched.

## Stop

- **The frontend test setup had two latent bugs.** React Testing Library could not auto-clean
  between tests (vitest runs without `globals`), which only surfaced once a file rendered twice —
  the same bug was making a test pass that should have failed. Fixed in `vitest.setup.ts`.
- **A test asserted order over a random key.** `order_by("id")` on a UUID primary key is not
  insertion order; the duplicate-submission test was rewritten to identify the original through
  the foreign key.
- **The gallery `<img>` is still missing.** The bytes need object storage (ADR 0015 is Proposed);
  the card is honest without them rather than showing a broken image.
- **`audit_logs` could not be given a retention period here** — it is append-only; the conflict
  was resolved by ADR 0018 in Sprint 20, not silently.

## Continue

- **Validate at the edge and again at the core.** The MIME rule and the re-encode both apply;
  neither trusts the other.
- **Personal data answers `no-store`; public data answers `public, max-age`.** Deliberate
  opposites, both tested.

## What the sprint proved about the project

The built backend became visibly usable: a stranger can read the gallery and the news, and the
two v2/v3 guarantees that had only existed structurally became enforced — byte-duplicates are
refused at the database, and a rejected upload leaves no bytes in quarantine.

## Concrete changes adopted

1. React trees are unmounted between vitest tests.
2. A test identifies a row by its foreign key, never by UUID order.
3. The gallery renders a citation card until object storage exists; no broken `<img>`.
