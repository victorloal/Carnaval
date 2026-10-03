# 0001. Scrumban methodology

- **Status:** Accepted
- **Date:** 2026-10-03
- **Relates to:** brief §6 decision 3, §16 (methodology)

## Context

This is a solo, part-time project. Sources are uncertain (a WordPress site that may change
markup yearly, a PDF that may not parse), and there is no team to coordinate. Waterfall
would front-load a plan that cannot be trusted; pure Scrum would impose ceremony sized for
a team that does not exist.

## Decision

Adopt **Scrumban**, adapted for a single developer:

- **Sprints of one week**, each with one explicit objective.
- A Kanban board on GitHub Projects with columns
  `Backlog → Listo → En curso → Revisión → Hecho` (kept in Spanish; it is the working
  surface for the maintainer, and repository documentation is English).
- **Work-in-progress limit of 2.** Hard limit. A part-time developer cannot hold more than
  two open loops, and an unbounded board is how solo projects stall.
- **Definition of Done** applies to every item, not just code:
  1. code with tests,
  2. documentation updated,
  3. CI green,
  4. the requirement linked in the traceability matrix (`docs/01-requisitos/matriz-trazabilidad.md`).

  Work that misses any of the four is not done. It stays in `Revisión`.
- Sprint planning notes and retrospectives live in `docs/sprints/`.

## Consequences

**Positive**
- Weekly objectives stay small enough to finish alongside a part-time job.
- The WIP limit forces prioritisation rather than accumulation.
- Folding documentation and traceability into DoD is what makes this a demonstration of
  engineering process rather than only of working code.

**Negative**
- Retro and planning notes are untracked overhead that a solo developer tends to skip. The
  DoD requirement is the countermeasure: a skipped retro means the item is not done.
- Scope pressure is real. Mitigation: MoSCoW prioritisation per version in the SRS
  (brief §18 step 2) and an explicit "Won't" list.

## Alternatives considered

- **Waterfall.** Rejected: phase 1 design cannot be validated against sources that may not
  behave as documented.
- **Pure Scrum.** Rejected: sprint planning, standups, and retrospectives sized for a team
  are pure overhead here.