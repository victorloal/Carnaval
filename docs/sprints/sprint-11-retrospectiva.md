# Sprint 11 retrospective — news intake and the citation registry

- **Date:** 2026-10-06
- **Sprint:** 11 — News intake and the citation registry
- **Method:** Start / Stop / Continue.
- **Note:** delivered with Sprints 12 and 13 as the v2 backend (`5e73a4f`); see also
  `sprint-13-retrospectiva.md` for the shared v2 retrospective.

## What was planned versus what happened

Planned: a `sources` citation registry and a news pipeline that brings in a headline, link,
outlet, date and a short **original** summary — never the article body or its images — landing
as `pending` for review.

What happened: **the models, the admin and the published-only API landed; the transform did
not.** The whole v2 backend is `5e73a4f` (**111 backend tests**). The matrix moved **FR-E-01,
LEG-04 and FR-H-09 (partial) to Done.**

Delivered: a `carnaval.editorial` app with `Source` (the citation registry: name, kind, URL,
`is_official`, notes) and `NewsItem` (source, headline, `url` as the natural key, outlet,
`published_on`, a bilingual **own-words** summary, the moderation mixin), a read-only
published-only `/api/news/` endpoint, and `is_official` driving the disclaimer wording.

Carried, and named: the **news transform** (FR-E-02/03) — news is entered by hand as `pending`
for now — because it needs a **chosen news source**, which no sprint has picked.

## Start

- **A news item is a citation, never a copy.** `NewsItem` stores a headline, a canonical URL,
  an outlet, a date and a short summary in our own words. There is no body field, so the
  article text cannot be stored even by accident (LEG-04).
- **The URL is the natural key.** `NewsItem.url` is unique, so re-staging is an upsert rather
  than a duplicate row (idempotency, ADR 0002).
- **`is_official` is data that changes the words on the page.** Whether a source is the
  organisers' own site decides how the disclaimer describes it (LEG-08), so it is a field, not
  a convention embedded in a template.

## Stop

- **No source, no transform.** The plan named a `wp_api`-style news transform, but the project
  never chose where news comes from. Rather than invent a source, the transform stayed Open and
  news is entered by hand; that is the honest state, and it is why FR-E-02/03 remain Open.
- **A hand-entered pending row is still a real feature.** The reviewer can create and moderate
  a news item today; only the automation is missing.
- **The summary is prose, not a quote.** "A short original summary" is enforced by the model's
  field set and by review, not by a length limit — a limit would have been a false guarantee.

## Continue

- **Model the citation before the pipeline.** The registry and the fields came first, so the
  transform, when it exists, has a shape to fill rather than a shape to invent.
- **Keep the public endpoint published-only**, like every other content endpoint.

## What the sprint proved about the project

The content type with the most obvious copyright trap — news — can be modelled so that the trap
is structurally absent: there is no field for the article text and no field for an article
image. The registry that makes attribution a first-class object is the part worth keeping.

## Concrete changes adopted

1. A transform whose source is undecided stays Open; the models and the manual path ship without it.
2. Citations are modelled as data (`Source`, `is_official`), not as template conventions.
