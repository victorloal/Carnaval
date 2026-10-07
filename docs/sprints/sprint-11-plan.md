# Sprint 11 — News intake and the citation registry

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** The `sources` citation registry exists and the pipeline can bring in news
  as headline, link, outlet, date and a short **original** summary — never the article body
  or its images. News is moderated like everything else.
- **Starts:** after Sprint 10 closes; nominal 1 week.
- **WIP limit:** 2 items (ADR 0001)
- **Status:** backend delivered (models, admin, published-only API); the **news transform** is
  carried — news is entered by hand as `pending`.

> v2 opens. The first content type beyond the programme is the one with the most obvious
> copyright trap: a news item is a citation, never a copy.

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | `Source` registry (`name`, `kind`, `url`, `is_official`, `notes`) | `modelo-datos.md` §4.3 | tests | Done |
| 2 | `NewsItem` (`source`, `headline`, `url`, `outlet`, `published_on`, bilingual summary, mixin) | FR-E-01 | migration review | Done |
| 3 | News transform: store headline, link, outlet, date and an own-words summary only | FR-E-02, LEG-04 | unit | Open — carried |
| 4 | News enters `pending` with `origin = scraped` | FR-E-03 | test | Open — news pipeline carried |
| 5 | Published news exposed read-only on the public API, published-only | FR-E-01, FR-A-06 | test | Done |
| 6 | `is_official` drives the disclaimer wording | LEG-08 | test | Done |

### Never the article body

The transform keeps headline, canonical URL, outlet, date and a short **own-words** summary.
The response body is captured with `_fields=` limited to consumed fields (the Sprint 03
fixture rule), so no article text or image ever enters the database or the repository
(LEG-04, LEG-05).

## What must be true when it ends

1. `NewsItem.url` is the natural key; re-staging upserts, never duplicates.
2. No stored or committed news record contains article text or an article image.
3. News is invisible on the public API until `published`.
4. `ruff`/`mypy`/`pytest`/`makemigrations --check`/`check --deploy` green; OpenAPI no drift.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | The transform, the natural key and the visibility rule are tested |
| Documentation updated | `modelo-datos.md` §4.1/§4.3, `flujo-datos.md`, `CHANGELOG.md` |
| CI green | The transform is fixture-driven and offline |
| Linked in the matrix | FR-E-01/02/03, LEG-04, FR-H-09 (partial) |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| Media gallery and rights gates | Sprint 12 |
| Site settings, translated slugs, search | Sprint 13 |
| Submissions | v3 |

## Risks

1. **The temptation to store the body "for the reviewer"** — refused; the raw payload lives in
   private storage, not the database.
2. **A URL is not a date** — outlet and date are verified against the source, never inferred.

## Carried into the next sprint

1. `media_assets`: the highest-risk table, with rights, citations, EXIF and duplicate gates
   (Sprint 12).
