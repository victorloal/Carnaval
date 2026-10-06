# Sprint 14 — v2 hardening and release

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** v2 is releasable — the new content types meet the performance and
  accessibility budgets, the rights workflows are rehearsed end to end, and the documentation
  is honest. Close v2 with a retrospective.
- **Starts:** after Sprint 13 closes; nominal 1 week.
- **WIP limit:** 2 items (ADR 0001)

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | Lighthouse/axe budgets re-run over news, gallery and search pages | NFR-01, NFR-03 | CI | Open |
| 2 | Gallery and news E2E flows, published-only | FR-E, FR-I | E2E | Open |
| 3 | Rights workflow rehearsed: unknown → licensed → published, with citations | LEG-02/03 | demonstration | Open |
| 4 | Search relevance spot-check against the real catalogue | FR-I-01 | analysis | Open |
| 5 | Image storage at the deployed provider; public/quarantine separated | ADR 0006, FR-E | inspection | Open |
| 6 | `estados.md` §7 and `flujo-datos.md` §5.1 open items re-checked | ADR 0001 | inspection | Open |
| 7 | Documentation and matrix sweep | ADR 0001 | inspection | Open |
| 8 | **Retrospective** for v2 | ADR 0001 | inspection | Open |

## What must be true when it ends

1. Performance and accessibility budgets hold with the new content.
2. Every published image has a citation and a non-unknown rights status, verified on the
   deployed data.
3. Search returns only published content and is accent-insensitive on real data.
4. CI green; matrix complete for v2; retrospective written; v2 declared.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | No new code except fixes; the release is a verification pass |
| Documentation updated | `README.md`, `CHANGELOG.md`, `docs/sprints`, matrix |
| CI green | E2E and budget stages run |
| Linked in the matrix | All v2 rows finalised |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| Public submissions | v3; the gate (ADR 0008 vs 0016) must be settled first |

## Risks

1. **Budgets regress silently** when images arrive — Lighthouse tracks bytes and LCP.
2. **Rights data quality** — a spot-check of published images is part of the release.

## Carried into the next sprint

1. **Before Sprint 15:** settle the v3 legal gate (`ADR 0008` vs `ADR 0016`), or submissions
   do not start.
2. The submission intake: validation, re-encode, EXIF, quarantine, consent, anti-abuse.
