# Sprint 06 — The public site and bilingual routing

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** A React + TypeScript public site renders the programme grouped by day, in
  Spanish and English, linkable per locale, usable at 360 px and with a keyboard, with the
  unofficial disclaimer on every page.
- **Starts:** after Sprint 05 closes; nominal 1 week.
- **WIP limit:** 2 items (ADR 0001)

> The site is a pure reader. It has no account, no session and no write path; the only cookie
> it sets is the locale preference.

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | `frontend/` app: Vite + React + TS; its own package (the root manifest stays docs-only) | ADR 0003 | build | Open |
| 2 | Locale-prefixed routes `/es/…`, `/en/…`; root redirect; cookie persistence; no machine translation | FR-H-01/03/04/05/10 | tests | Open |
| 3 | Programme grouped by day, chronological; a source link per entry | FR-A-08, FR-A-12 | E2E | Open |
| 4 | Unofficial / not-affiliated disclaimer on every page | FR-A-09 | E2E | Open |
| 5 | Responsive at 360 px; WCAG 2.1 AA; missing translation key fails the build | FR-A-13, NFR-03, NFR-04, FR-H-02 | axe + build | Open |
| 6 | Content translation with fallback to the source locale | FR-H-06 | test | Open |

## What must be true when it ends

1. `tsc --noEmit`, eslint, vitest and `vite build` all pass.
2. The site renders seeded content in both locales, keyboard-navigable, with no horizontal
   overflow at 360 px.
3. A missing translation key fails the build, not the page.
4. The root `package.json` still exists only for the diagram check.
5. `ruff`/`mypy`/`pytest` remain green; the frontend stages run locally.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | vitest + testing-library; axe in component tests; an E2E happy path |
| Documentation updated | `README.md` run guide, `CHANGELOG.md`, `arquitectura-c4.md` |
| CI green | The frontend stages land here and are completed in Sprint 07 |
| Linked in the matrix | FR-A-08/09/12/13, FR-H-01…06/10, NFR-03/04 |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| E2E/Lighthouse/axe in CI, deployment | Sprint 07 |
| Search, news, gallery | v2 |
| Any authenticated surface | There is none until v1, and the public site never gets one |

## Risks

1. **The frontend stages are the ones Sprint 01 could not wire.** They land here; the pipeline
   must not claim them green before they exist.
2. **Translation drift** — the build-failing key check is the guard; add keys as strings are
   added.
3. **Two manifests** — the root one stays documentation-only; the site's lives under
   `frontend/`.

## Carried into the next sprint

1. The remaining `plan-pruebas.md` §7 stages: `tsc`/eslint/vitest/build in CI, docker-compose
   E2E, Lighthouse, axe, dependency audit.
2. Security headers, CORS and the deployment (ADR 0015).
