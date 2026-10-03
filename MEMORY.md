# MEMORY.md

Session memory for agents. **Rules live in `AGENTS.md`** — read it first; it wins on any
conflict. **Hard limit: 50 lines.** Records what happened and what is next, never how to work.

## Current state

- Phase 0: **docs complete, no code.** `backend/`, `frontend/`, `tests/` empty; no CI yet.
- 40 files: 11 ADRs, acta, SRS (168 reqs), 32 stories, matrix, 9 design docs, **74 cases**, legal.
- **Stack decided** (0009): Python 3.12 + Django 5 + DRF + **PostgreSQL 16**; React for the
  public site only. Admin is **Django admin** (0005), **no JWT anywhere**.
- Site is **bilingual es/en** (0010); OpenAPI **generated**, drift fails CI (0011). Platform **undecided**.
- Brief `docs/00-contexto-proyecto.md` is Spanish and **reconciled**; ADRs still win.

## Decisions taken

- Django over FastAPI — the admin console is the dominant cost here.
- **No JWT.** Supersedes brief §6 decision 8 and part of §9.
- Quarantine then public storage, separate buckets and domains (0006).
- MVP → v1 → v2 → v3; public submissions deliberately last (0008).
- MIT covers code only (0004); `rights_status = unknown` never published.
- New repo content in English; the Spanish brief is the only legacy exception.

## Learnings

- The brief contradicted the repo, then the stack. Trust `docs/adr/`, not prose.
- A delegated task reported two large files that **did not exist**. Verify with `ls`.
- **Three schemes share the `SEC-nn` shape**: SRS requirements, threats `T-nn`, test cases.
  The threat model assumed 1:1 and was wrong for T-01…T-49. Check cited IDs, never assume.
- PowerShell `ReadAllLines` reads ANSI and mangles UTF-8 (`—` → `â€”`); pass `UTF8Encoding`.

## Errors to avoid

- Committing third-party PDFs, photos, or article text. Publishing without review.
- Reintroducing JWT or a React admin panel; both were decided against.

## Next steps

1. Source spike: probe the WP REST API and `robots.txt`; capture fixtures (unblocks FR-B).
2. Decide SRS §9 items: translations strategy, session timeouts, raw retention, search.
3. Pick concrete providers; ADR 0012 would hold the egress-cost criterion.
4. Contact Corpocarnaval (brief §20) before any public launch.

## Session log

| Date | Topics |
|---|---|
| 2026-10-03a | Audit, `AGENTS.md`, `MEMORY.md`, brief moved, folder rename, Unlicense→MIT, `.gitignore` |
| 2026-10-03b | Docs: 11 ADRs, acta, SRS, stories, matrix, data model, test plan, legal, sprint 00 |
| 2026-10-03c | 9 design docs finished, SEC-73/74 added, threat↔case IDs reconciled, Mermaid validated |