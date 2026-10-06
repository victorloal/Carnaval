# MEMORY.md

Session memory for agents. **Rules live in `AGENTS.md`** — read it first; it wins on any
conflict. **Hard limit: 50 lines.** Records what happened and what is next, never how to work.

## Current state

- **Phase 0 closed 2026-10-04; Sprint 01 delivered** (retro 2026-10-06). Django skeleton in `backend/` on **Django 5.2.9 LTS**: spine models + moderation mixin (migration `0003`), DRF/spectacular, committed `openapi.yaml`, CI workflow + `check --deploy`, **real no-egress guard**, factories, settings hardened. `frontend/` and root `tests/` still empty. **Sprint 01 closed: the review fixes and the Django 5.2 upgrade are pushed and CI is green on `main`; the rest of `plan-pruebas.md` §7 waits on frontend/E2E components.** 50 Markdown files: 15 ADRs, acta, SRS (170 reqs), 32 stories, matrix, 9 design docs, **74 cases**, 4 legal, 5 sprints.
- **Stack decided** (0009): Python 3.12 + Django 5.2 LTS + DRF + **PostgreSQL 16** (settings enable it via `DB_*` env; SQLite is a dev fallback only). React for the public site only. Admin is **Django admin** (0005), **no JWT anywhere**. Site **bilingual es/en** (0010); OpenAPI **generated**, drift fails CI (0011). Platform **undecided**.
- Brief is **reconciled**. **Source spike:** WP REST API live, `robots.txt` permissive, **terms of use not found → risk accepted**, not answered.
- Contact is **victorloal513@gmail.com**. Corpocarnaval letter **sent 2026-10-04 to `comunicacion@carnavaldepasto.org`, no reply** — silence is not permission. **Watch for a bounce**: the spike found no email on that site, so the address's existence is unverified.
- **No professional legal review, ever** (0016). Legal texts ship as labelled drafts; `[PENDIENTE]`s are permanent.
- **Settings fail loudly without `SECRET_KEY`** (SEC-46): local gitignored `.env` (see `.env.example`) or env vars; `DEBUG` defaults off; CI sets an explicit test value.

## Decisions taken

Decisions live in `docs/adr/` (0001–0016) and are not duplicated here. The ones that keep
coming up: **no JWT** (0005), **Django admin** (0005/0009), versions MVP→v3 with submissions
last (0008), MIT covers code only (0004), quarantine before public (0006), **legal texts
unreviewed and labelled** (0016).

## Learnings

- The brief contradicted the repo, then the stack; a delegated task also reported two files that did not exist. Trust `docs/adr/`, verify every completion report with `ls`.
- **Sprint items marked "Done" can be false.** The egress guard was a no-op (`assert True`) and the factories did not exist while the plan said Done — re-verify every Done against the filesystem.
- **`django-argon2` does not exist on PyPI** — the vetted library is `argon2-cffi`; ADR 0005/0009 + 3 more docs corrected 2026-10-05. Check that a package name resolves before wiring it.
- **Three schemes share the `SEC-nn` shape**: SRS requirements, threats `T-nn`, test cases.
  The threat model assumed 1:1 and was wrong for T-01…T-49. Check cited IDs, never assume.
- **A stated reason can be false while the decision is right.** ADR 0014 said "Mermaid ships no C4 notation" — `mermaid@12.1.0` parses `C4Context`; the decision stood on a different ground. Check the reason, amend it, keep the decision.
- PowerShell `ReadAllLines` reads ANSI and mangles UTF-8 (`—` → `â€”`); pass `UTF8Encoding`.

## Errors to avoid

- Committing third-party PDFs, photos, or article text; publishing without review; reintroducing JWT or a React admin panel.

## Next steps

1. **Sprint 02:** add the remaining `plan-pruebas.md` §7 stages (frontend/E2E/dependency audit) as their components land; automate SEC-46's secret scan (NFR-09 stays Open); optional Postgres service for CI.
2. **Corpocarnaval request: awaiting reply.** Check for a bounce (`comunicacion@carnavaldepasto.org` — unverified) and set a review date. Human act.
3. Platform + **ADR 0015** (egress cost). Candidates already in `despliegue.md` §3.
4. **Decide v3's gate.** ADR 0008 required reviewed legal texts for public submissions; 0016 declined them. Unresolved by design — settle it before the upload form is built, not while. **PRV-06 is blocked for the same reason** (retention periods); left intact, not weakened.

## Session log

| Date | Topics |
|---|---|
| 2026-10-03 | Six sessions: audit/AGENTS/MEMORY, 11 ADRs + acta + SRS + stories + matrix, 9 design docs + threat↔case remap, source spike (WP API live, terms not found), ADR 0012/0013/0014, Sprint 01 planned |
| 2026-10-04 | **Phase 0 closed**; validator runnable — **mermaid@12.1.0 parses `C4Context`, falsifying ADR 0014 §2** (amended). Contact email; **ADR 0016**; terms risk accepted; **Corpocarnaval letter sent, unanswered**; 0016 broke **PRV-06** → marked blocked |
| 2026-10-05 | **Sprint 01 items 1–9** (skeleton, migrations, ruff/mypy, OpenAPI, CI, fixtures), green locally; **review fixes** — real no-egress guard (NFR-16), DRF fail-closed, SECRET_KEY fail-loud (SEC-46) + DEBUG off, Argon2id first, django-otp wired, factories + FR-A-01/02 tests (→ Done); `django-argon2` → `argon2-cffi` in 5 docs |
| 2026-10-06 | **Sprint 01 retrospective** (`docs/sprints/sprint-01-retrospectiva.md`); **AGENTS.md corrected** — it was a full sprint behind (claimed empty backend, no linter/tests/CI); CI verified on GitHub — green on `e3f5c52`, **HEAD `5d08331` unpushed**; 9 Dependabot PRs open with failing CI; **code review fixes** — Django 5.0.6 (EOL) → **5.2.9 LTS**, DRF 3.16.1, spectacular 0.30.0, mypy 2.3.1, production security + `check --deploy` in CI, **moderation mixin** on the spine (migration `0003`), pytest hack removed; **Sprint 02 implemented** (`docs/sprints/sprint-02-plan.md`): MVP data model — `carnaval.ingestion` (`scrape_sources`, `raw_documents` unique hash, `ingestion_runs`), `Event`, `ingestion_run` FK on the mixin, `seed_demo`; no admin until v1 |
