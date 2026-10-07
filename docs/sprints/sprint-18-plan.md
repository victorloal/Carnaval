# Sprint 18 — v2/v3 close-out, part 1: the gallery and submission integrity

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** the public gallery renders a published image with its **citation**, and the
  integrity rules carried from v2 and v3 — duplicate bytes, a lying content type, deletion on
  rejection and a non-cacheable personal response — are enforced in code and tested.
- **Starts:** after the public site pages landed (2026-10-07); nominal 1 week.
- **WIP limit:** 2 items (ADR 0001)
- **Status:** delivered; CI green on `4a08742` and the follow-up commit.

> Off the version roadmap on purpose: the four backends are built, so this is the
> close-out of what the v2/v3 retros carried for lack of an environment — the parts that
> need no bucket and no browser.

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | Gallery page; a published image shows its citation, author, year and licence | FR-E-06, LEG-03 | component | Done |
| 2 | Identical image bytes are refused re-publication (`content_hash`, partial unique constraint) | FR-E-07 | test (DB) | Done |
| 3 | A duplicate submission is flagged for the reviewer, not silently accepted | FR-F-21 | test | Done |
| 4 | A declared image type that contradicts the bytes is refused; aliases and generic types pass | FR-F-04, SEC-19 | test | Done |
| 5 | Rejecting a submission deletes its quarantined files (ADR 0006) | FR-C-10 | test | Done |
| 6 | A personal submission response is `Cache-Control: private, no-store` | PRV-09 | test | Done |

### The citation is the point of the gallery

An old photo is not free of rights (AGENTS.md). The gallery renders only `published` rows —
`rights_status = unknown` cannot reach it — and every card carries the citation that makes the
image lawfully showable. The image **bytes** are a storage concern the deployment owns; the
card is correct without them, and it says so rather than showing a broken `<img>`.

### A declared type is a claim; the bytes are the fact

`validate_image` already decided the format from the bytes. `declared_mime_conflicts` only
rejects a *concrete* `image/*` declaration that contradicts that decision; an empty header, a
generic `application/octet-stream`, or the historical `image/jpg` spelling is allowed, because
browsers send imperfect content types and a rule that reddens on that would be turned off.

## What must be true when it ends

1. A published image cannot appear without its citation; a duplicative one cannot be stored.
2. A submission whose header lies about its type is refused; a duplicate is flagged.
3. A rejected upload leaves no bytes in quarantine.
4. `ruff`/`mypy`/`pytest`/`makemigrations --check`/`check --deploy` green; no OpenAPI drift.
5. The frontend `tsc`/eslint/vitest/build green; the translation-key check passes.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | Each rule has a dedicated test; the gallery has a component test |
| Documentation updated | `CHANGELOG.md`, `MEMORY.md`, the matrix, this plan, the v2/v3 plans |
| CI green | A new migration is checked by `makemigrations --check`; both CI jobs run |
| Linked in the matrix | FR-C-10, FR-E-06/07, FR-F-04/21, LEG-03, PRV-09 → Done |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| The gallery `<img>` and the quarantine → public move | Object storage; ADR 0015 is Proposed |
| The news transform (FR-E-02/03) | Needs a chosen news source |
| Per-locale slugs (FR-H-07/09), verbatim citations with a translation | Its own unit |
| PII purge (PRV-03/07) | Needs the retention window PRV-06 blocks |
| The submission form | v3 legal gate (ADR 0008 vs 0016), still undecided |
| Browser E2E, Lighthouse, axe | Need a browser environment |

## Risks

1. **A unique constraint can be added but not un-violated** — the migration is a partial
   unique index (`condition`), so the empty "no hash recorded" case is untouched; reviewed.
2. **Deleting on rejection must not delete the register** — the `Submission` row stays
   `rejected` with its reason; only the private bytes and their rows go.
