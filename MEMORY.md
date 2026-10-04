# MEMORY.md

Session memory for agents. **Rules live in `AGENTS.md`** — read it first; it wins on any
conflict. **Hard limit: 50 lines.** Records what happened and what is next, never how to work.

## Current state

- Phase 0: **docs complete, no code.** `backend/`, `frontend/`, `tests/` empty; no CI yet.
- 44 files: 14 ADRs, acta, SRS (170 reqs), 32 stories, matrix, 9 design docs, **74 cases**, legal, 2 sprints.
- **Stack decided** (0009): Python 3.12 + Django 5 + DRF + **PostgreSQL 16**; React for the
  public site only. Admin is **Django admin** (0005), **no JWT anywhere**.
- Site is **bilingual es/en** (0010); OpenAPI **generated**, drift fails CI (0011). Platform **undecided**.
- Brief `docs/00-contexto-proyecto.md` is Spanish and **reconciled**; ADRs still win. **Source spike 2026-10-03:** WP REST API live, `robots.txt` permissive, **terms of use not found** (`fuentes-y-atribucion.md` §9).

## Decisions taken

- Django over FastAPI — the admin console is the dominant cost here.
- **No JWT.** Supersedes brief §6 decision 8 and part of §9.
- Quarantine then public storage, separate buckets and domains (0006).
- MVP → v1 → v2 → v3; public submissions deliberately last (0008).
- MIT covers code only (0004); `rights_status = unknown` never published.
- New repo content in English; the Spanish brief is the only legacy exception.

## Learnings

- The brief contradicted the repo, then the stack; a delegated task also reported two files that did not exist. Trust `docs/adr/`, verify every completion report with `ls`.
- **Three schemes share the `SEC-nn` shape**: SRS requirements, threats `T-nn`, test cases.
  The threat model assumed 1:1 and was wrong for T-01…T-49. Check cited IDs, never assume.
- PowerShell `ReadAllLines` reads ANSI and mangles UTF-8 (`—` → `â€”`); pass `UTF8Encoding`.

## Errors to avoid

- Committing third-party PDFs, photos, or article text. Publishing without review.
- Reintroducing JWT or a React admin panel; both were decided against.

## Next steps

1. **Execute Sprint 01** (`docs/sprints/sprint-01-plan.md`): skeleton, 14-stage CI, first migration, committed `openapi.yaml`. Then ADR 0015 (egress cost) and the storage provider.
2. Brief §20 follow-ups: the official site's **terms of use were never found**, the `[PENDIENTE]` contact email FR-B-14 needs in the User-Agent, and contacting Corpocarnaval.

## Session log

| Date | Topics |
|---|---|
| 2026-10-03a | Audit, `AGENTS.md`, `MEMORY.md`, brief moved, folder rename, Unlicense→MIT, `.gitignore` |
| 2026-10-03b | Docs: 11 ADRs, acta, SRS, stories, matrix, data model, test plan, legal, sprint 00 |
| 2026-10-03c | 9 design docs, SEC-73/74, threat↔case IDs remapped, Mermaid validated, brief reconciled, 4 commits |
| 2026-10-03d | SRS §9 closed → ADR 0012 (translations) + ADR 0013 (defaults); FR-D-15/16; corrected a backwards Django timeout claim; **source spike** — WP API live (FR-B-15), `6 de enero` is a root category (traps any "children of DIAS" query), programme data is mostly the 2020 edition, terms of use not found |
| 2026-10-03e | Diagrams: 2 dead C4 blocks → Mermaid (**ADR 0014**), 4 `erDiagram` + 1 `classDiagram` + 2 `sequenceDiagram`, validator extended to **every** fence (the old one counted 11 of 30 and went green) |
| 2026-10-03f | **Sprint 01 planned** — `sprint-01-plan.md`: skeleton, 14-stage CI, first migration, `openapi.yaml`, no-egress guard; diagram check wired into `plan-pruebas` §7 |