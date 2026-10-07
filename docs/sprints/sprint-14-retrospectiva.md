# Sprint 14 retrospective — v2 hardening and release (not run)

- **Date:** 2026-10-06 (recorded 2026-10-07)
- **Sprint:** 14 — v2 hardening and release
- **Method:** Start / Stop / Continue.
- **Verdict:** **not run.** Like Sprint 10, this is a release/verification sprint and there is
  no environment to run it in.

## What was planned versus what happened

Planned: re-run the Lighthouse and axe budgets over the news, gallery and search pages, add
their E2E flows, rehearse the rights workflow (unknown → licensed → published), spot-check
search relevance against the real catalogue, place image storage at the provider with public
and quarantine separated, re-check the `estados.md` §7 and `flujo-datos.md` §5.1 open items,
sweep the docs, and close v2.

What happened: **none of it ran** — every item needs a browser, a deployment or object storage,
and Sprint 07 had already carried those. The v2 **backend** — the citation registry,
`news_items`, `media_assets` with its rights gate, typed `site_settings`, search — was delivered
in Sprints 11–13 (`5e73a4f`) and its retrospective exists (`sprint-13-retrospectiva.md`). The
**gallery UI** that v2's release assumed was still missing; it landed later, in Sprint 18.

The parts that were answerable without an environment were answered in the backend sprints:
the rights gate is a database `CHECK` with tests, the settings refuse secret-shaped keys with
tests, and search is published-only on both database backends.

Carried, and still carried: the **Lighthouse/axe budgets** (NFR-01/03), the **news/gallery E2E
flows**, the **rights-workflow rehearsal** on real data, the **search relevance spot-check**
(FR-I-03), and **image storage at the provider** (ADR 0015 is Proposed).

## Stop

- **A budget you cannot measure is not held.** "Performance holds" is a claim about a running
  page; a component test cannot stand in for Lighthouse, and the project does not pretend it
  can.
- **The gallery was in the plan's *goal* and absent from its backlog.** The release sprint
  assumed a UI that no sprint actually built. The lesson is not "write more backlog" — it is
  that a **frontend item must have an owning sprint**, or it falls between two release sprints.

## Continue

- **Keep the gate below the application.** The rights `CHECK` outlived the missing UI: the
  model was correct before anything rendered it, so Sprint 18 only had to render fields that
  already could not be wrong.
- **Record the reason, not just the status.** Every carried row says *why*, which is what makes
  it safe to close later.

## What this sprint recorded about the project

v2's riskiest object — an image — was made lawfully publishable **before** any gallery existed,
and the release that would have proven it visually never happened. The guarantee is still real,
because it lives in the database rather than in the page.

## Concrete changes adopted

1. A feature named in a release sprint's goal must have a backlog item somewhere; the gallery
   went missing between Sprints 12 and 14 and was found in the Sprint 18 sweep.
2. Release/verification items stay Open until an environment exists to run them.
