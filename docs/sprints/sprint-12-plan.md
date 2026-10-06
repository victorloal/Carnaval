# Sprint 12 — Media gallery and rights

- **Sprint length:** 1–2 weeks (Scrumban, ADR 0001)
- **Sprint goal:** A historical image gallery in which **every published image is lawfully
  publishable** — author, source, licence and citation present, `rights_status` not `unknown`,
  EXIF stripped, duplicates refused, minors gated — enforced on **every** path, not only the
  form.
- **Starts:** after Sprint 11 closes; nominal 1–2 weeks.
- **WIP limit:** 2 items (ADR 0001)

> This is the highest-risk table in the schema. A bypass is a legal exposure, so the gate is
> repeated at every layer and tested at each one.

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | `MediaAsset` schema (rights fields, `exif_stripped`, `featured`, `minor_subject`, `guardian_consent_on_file`) | FR-E-04 | migration review | Open |
| 2 | The publish gate: `rights_status = unknown` blocks publication on every path | FR-E-05, LEG-02 | SEC test | Open |
| 3 | Citation text shown beside every published image | FR-E-06, LEG-03 | E2E | Open |
| 4 | Duplicate detection by `content_hash`; identical bytes refused re-publication | FR-E-07 | test | Open |
| 5 | EXIF stripped on ingest and **re-verified at approval** | FR-E-08, PRV-04 | test | Open |
| 6 | Minor-subject gate: `minor_subject` requires `guardian_consent_on_file` | LEG-09 | test | Open |
| 7 | `editor` can feature an approved asset | FR-E-09 | test | Open |
| 8 | Quarantine and public storage are separate keys; unapproved assets have no public key | ADR 0006 | test | Open |

### The gate is not the form

`rights_status = unknown` blocks publication in model validation, in the serializer, in the
admin form, and — where expressible — in a database constraint, so a pipeline or bulk
operation cannot bypass it. Old photos are not free of rights; `unknown` is the default and is
never "helpfully" filled in.

## What must be true when it ends

1. No path publishes an image with `rights_status = unknown` or a missing citation.
2. EXIF is stripped and verified; duplicates refused; minors gated.
3. The gallery renders citation text beside every image, in both locales.
4. `ruff`/`mypy`/`pytest`/`makemigrations --check`/`check --deploy` green; OpenAPI no drift.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | Each gate has a dedicated test, including a re-injected EXIF tag |
| Documentation updated | `modelo-datos.md` §4.2, `estados.md`, `CHANGELOG.md` |
| CI green | Fixture-driven; image fixtures generated locally, never committed binaries |
| Linked in the matrix | FR-E-04…09, LEG-02/03/09, PRV-04 |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| Site settings, translated slugs, search | Sprint 13 |
| Public submission of images and quarantine transfer | v3 |

## Risks

1. **This is the highest-risk table** — the gate is repeated at every layer and tested at each.
2. **Old photos are not free of rights** (AGENTS.md) — `unknown` must never be auto-filled.

## Carried into the next sprint

1. Typed `site_settings`, translated slugs, verbatim citations with translations, and search
   (`pg_trgm` + `unaccent`, ADR 0013).
