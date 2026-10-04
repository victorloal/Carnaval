# MEMORY.md

Session memory for agents. **Rules live in `AGENTS.md`** — read it first; it wins on any
conflict. **Hard limit: 50 lines.** Records what happened and what is next, never how to work.

## Current state

- **Phase 0 closed 2026-10-04.** Docs complete, still no code: `backend/`, `frontend/`, `tests/` empty; no CI yet. 46 Markdown files: 15 ADRs, acta, SRS (170 reqs), 32 stories, matrix, 9 design docs, **74 cases**, 4 legal, 3 sprints.
- **Stack decided** (0009): Python 3.12 + Django 5 + DRF + **PostgreSQL 16**; React for the public site only. Admin is **Django admin** (0005), **no JWT anywhere**. Site **bilingual es/en** (0010); OpenAPI **generated**, drift fails CI (0011). Platform **undecided**.
- Brief is **reconciled**. **Source spike:** WP REST API live, `robots.txt` permissive, **terms of use not found → risk accepted**, not answered.
- Contact is **victorloal513@gmail.com** (fixed 2026-10-04). Corpocarnaval letter **drafted, not sent**.
- **No professional legal review, ever** (0016). Legal texts ship as labelled drafts; `[PENDIENTE]`s are permanent.

## Decisions taken

Decisions live in `docs/adr/` (0001–0016) and are not duplicated here. The ones that keep
coming up: **no JWT** (0005), **Django admin** (0005/0009), versions MVP→v3 with submissions
last (0008), MIT covers code only (0004), quarantine before public (0006), **legal texts
unreviewed and labelled** (0016).

## Learnings

- The brief contradicted the repo, then the stack; a delegated task also reported two files that did not exist. Trust `docs/adr/`, verify every completion report with `ls`.
- **Three schemes share the `SEC-nn` shape**: SRS requirements, threats `T-nn`, test cases.
  The threat model assumed 1:1 and was wrong for T-01…T-49. Check cited IDs, never assume.
- **A stated reason can be false while the decision is right.** ADR 0014 said "Mermaid ships no C4 notation" — `mermaid@12.1.0` parses `C4Context`; the decision stood on a different ground. Check the reason, amend it, keep the decision.
- PowerShell `ReadAllLines` reads ANSI and mangles UTF-8 (`—` → `â€”`); pass `UTF8Encoding`.

## Errors to avoid

- Committing third-party PDFs, photos, or article text; publishing without review; reintroducing JWT or a React admin panel.

## Next steps

1. **Execute Sprint 01** (`docs/sprints/sprint-01-plan.md`): skeleton, 14-stage CI, first migration, committed `openapi.yaml`.
2. **Send the Corpocarnaval letter** (`docs/comunicacion-corpocarnaval.md`) and record the reply. Human act; recipient still unresolved — the official site publishes no email.
3. Platform + **ADR 0015** (egress cost). Candidates already in `despliegue.md` §3.
4. **Decide v3's gate.** ADR 0008 required reviewed legal texts for public submissions; 0016 declined them. Unresolved by design — settle it before the upload form is built, not while.

## Session log

| Date | Topics |
|---|---|
| 2026-10-03a | Audit, `AGENTS.md`, `MEMORY.md`, brief moved, folder rename, Unlicense→MIT, `.gitignore` |
| 2026-10-03b | Docs: 11 ADRs, acta, SRS, stories, matrix, data model, test plan, legal, sprint 00 |
| 2026-10-03c | 9 design docs, SEC-73/74, threat↔case IDs remapped, Mermaid validated, brief reconciled, 4 commits |
| 2026-10-03d | SRS §9 closed → ADR 0012/0013; FR-D-15/16; **source spike** — WP API live, `6 de enero` is a root category, programme is mostly the 2020 edition, terms not found |
| 2026-10-03e | Diagrams: 2 dead C4 blocks → Mermaid (**ADR 0014**), validator extended to **every** fence |
| 2026-10-03f | **Sprint 01 planned** — skeleton, 14-stage CI, first migration, `openapi.yaml`, no-egress guard |
| 2026-10-04 | **Phase 0 closed**; validator made runnable (`package.json`) — it walked `node_modules`, and **mermaid@12.1.0 parses `C4Context`, falsifying ADR 0014 §2** (amended). Contact email fixed; **ADR 0016** (no legal review, permanent DRAFT); terms-of-use risk accepted; **Corpocarnaval letter drafted** |