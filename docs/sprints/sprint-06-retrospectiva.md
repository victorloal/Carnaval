# Sprint 06 retrospective — the public site

- **Date:** 2026-10-06
- **Sprint:** 06 — The public site and bilingual routing
- **Method:** Start / Stop / Continue, plus what actually happened versus what was planned.

## What was planned versus what happened

Planned: a React + TypeScript site in `frontend/` that renders the programme grouped by day,
in two locales with prefixed URLs, with the disclaimer and a source link, at 360 px.

What happened: all six backlog items landed and **CI is green on `cf23bf8`**. `tsc --noEmit`,
eslint, **12 vitest + testing-library tests** and `vite build` all pass locally. The matrix
moved **FR-A-08, FR-A-09, FR-A-12 and FR-H-01/02/03/04/05/06/10 to Done**; FR-A-13 and
NFR-03/04 stay Open because their verification is browser E2E (axe, 360 px), which Sprint 07
wires.

Two things are deliberately not done here and are named rather than hidden: the frontend
stages are **not yet in CI** (they land in Sprint 07), and jsdom cannot honestly assert the
360 px or accessibility claims.

## Start

- **Keep the logic pure and the components thin.** `groupEventsByDay`, `localeFromPath`,
  `localeFromCookie` and `redirectTarget` are plain functions with no React and no network, so
  they are fully unit-tested; the components only render what the functions return.
- **Make the translation contract a test, not a habit.** A test fails the build if the two
  locales do not define the same, non-empty keys (FR-H-02) — the whole missing-key failure
  mode is one assertion.
- **Its own package, from the first commit.** `frontend/package.json` is separate and the root
  manifest stays documentation tooling only (ADR 0003, AGENTS.md).
- **Pin exact versions.** Every dependency is saved exact, matching the backend's
  `requirements.txt`, and the lockfile is committed.

## Stop

- **Frontend code that CI does not yet build.** The site is tested locally but the pipeline
  ignores `frontend/` until Sprint 07. That is the plan's own split, but it means this commit
  is not covered by the thing that refuses bad changes; it is first on the next sprint's list.
- **jsdom is not a browser.** Overlap and axe are browser facts; claiming them from a jsdom
  test would be a false green. They wait for Playwright.
- **The site reads `pending`-free data only because the API filters it**, not because the
  frontend could not render more. That is the correct boundary, but it is the API's guarantee,
  not the site's.

## Continue

- **Verify with the project's own commands.** `npm run typecheck && npm run lint && npm test
  && npm run build` is the local gate, and it is what Sprint 07 will run in CI.
- **Fallbacks, not empty pages.** `localized(es, en, locale)` returns the Spanish value when
  the English one is empty (FR-H-06), tested.
- **No machine translation, no tracking.** The only cookie is the locale preference.

## What the sprint proved about the project

The public site can be a pure reader of the published API, and the bilingual requirement is
enforceable at build time rather than by review. The remaining risk is not the code but the
pipeline: until Sprint 07 runs these commands in CI, "it builds" is a local claim.

## Concrete changes adopted

1. The frontend stages (`tsc`, eslint, vitest, build) go into CI first in Sprint 07.
2. Layout and accessibility claims (360 px, axe) wait for the browser, never a jsdom proxy.
3. Every frontend dependency is pinned exact, like the backend.
