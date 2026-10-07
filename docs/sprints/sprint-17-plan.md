# Sprint 17 — v3 hardening and launch

- **Sprint length:** 1–2 weeks (Scrumban, ADR 0001)
- **Sprint goal:** The complete system is hardened, its security cases pass on production,
  privacy procedures are documented and exercised, and the site is **launched**. Close with a
  retrospective and a final reconciliation of documentation against reality.
- **Starts:** after Sprint 16 closes; nominal 1–2 weeks.
- **WIP limit:** 2 items (ADR 0001)
- **Status:** the v3 **backend** is delivered; this launch sprint — the deployed security sweep,
  the rehearsed privacy procedures, the backup rehearsal and the DNS/launch acts — is carried
  and needs an environment and the maintainer's accounts.

> This is the defensive pass before and after launch. No new features.

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | Full security-case sweep on the deployed system | SRS §5 | security suite | Open |
| 2 | CSP with consent-gated embeds; no `unsafe-inline` for scripts | SEC-15 | header analysis | Open |
| 3 | Data-subject access / rectification / deletion procedure documented and rehearsed | PRV-07 | demonstration | Open |
| 4 | Rate limits and quotas tuned against real traffic; egress within free tier | NFR-05, NFR-17 | analysis | Open |
| 5 | Backup/restore re-rehearsed after the v3 tables exist | NFR-20 | demonstration | Open |
| 6 | Accessibility and Lighthouse budgets re-run over submissions and gallery | NFR-01/03/04 | CI | Open |
| 7 | Logs and analytics re-checked for raw IPs and secrets | NFR-19, PRV-01 | inspection | Open |
| 8 | Documentation sweep: SRS, matrix, design, legal drafts, ADRs | ADR 0001 | inspection | Open |
| 9 | **Launch**: DNS, disclaimer, takedown channel and labelled legal drafts linked | LEG-08, FR-G-03 | demonstration | Open |
| 10 | **Retrospective** for v3 and the project | ADR 0001 | inspection | Open |

## What must be true when it ends

1. Every applicable security case passes on the deployed system.
2. Privacy procedures exist and have been rehearsed once.
3. Performance and accessibility budgets hold with all v3 content.
4. Backup/restore proven after the v3 tables exist.
5. Documentation and matrix are true; no "Done" is unsupported by a test or an inspection.
6. Site launched; retrospective written; project declared complete.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | Fixes from the sweep ship with tests; the rest is verification |
| Documentation updated | Final sweep of `README.md`, `CHANGELOG.md`, `docs/`, matrix |
| CI green | Full pipeline on `main` |
| Linked in the matrix | All remaining rows finalised; blocked rows marked blocked, not "Done" |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| Any feature not in the SRS | The "Won't" column is binding (ADR 0008) |
| Professional legal review | Never (ADR 0016) |

## Risks

1. **Launch is when traffic, abuse and legal exposure arrive** — the anti-abuse and takedown
   paths are rehearsed before, not after.
2. **Scope creep is chronic** — the SRS "Won't" column and the version gates are the guard.
3. **Documentation drift is the recurring failure mode** — the final sweep checks the
   filesystem against every claim.

## Project close

With v3 launched, the four versions of ADR 0008 are delivered. The remaining open items are
recorded, not hidden: the Corpocarnaval reply, the source's terms of use, the labelled legal
drafts (ADR 0016), and any requirement marked blocked. The `matriz-trazabilidad.md` is the
single source of truth for what was and was not done.
