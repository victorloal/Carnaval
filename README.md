# Carnaval de Negros y Blancos

A web platform about the **Carnaval de Negros y Blancos of Pasto, Nariño, Colombia** — its
programme, its history, and photographs contributed by the community.

> **This is a personal, non-commercial portfolio project.**
> It is **not affiliated with, endorsed by, or official** with Corpocarnaval or any parade
> organiser. Information is reproduced with attribution; the site is not an official source.

Available in **Español** (primary) and **English**.

---

## What this project is

A demonstration of a complete software engineering process — requirements, design,
security, implementation, testing, deployment, documentation — versioned in one repository.

### An honest note

The parade programme changes **once a year**. A continuous scraping pipeline with human
moderation, an administrative panel, audit trails, and public submissions is therefore
*more* than the underlying problem strictly requires.

It is built **deliberately**, to demonstrate data engineering, applied security, and risk
management. See `docs/00-contexto-proyecto.md` §15.

## Architecture in one paragraph

A Python/Django backend collects data from public sources through an idempotent ingestion
pipeline, stages every record as `pending`, and publishes only what a human approves. The
**database is the source of truth**; the scraper is a convenience, not a dependency — if
every external source disappears, the site keeps serving and the moderator can author
content by hand. A React + TypeScript frontend serves the public read-only site in two
locales. Moderation, configuration, and audit happen in Django admin, which no public user
can reach.

## Status

**Phase 0 — documentation — closed 2026-10-04.** The requirements, design set, test plan,
threat model, and ADRs are complete. **Sprint 01 is in progress**: `backend/` now holds the
Django skeleton — programme models and migrations, a generated and CI-enforced
`openapi.yaml`, lint and type checks, tests with a no-egress guard, and a GitHub Actions
pipeline. `frontend/` and `tests/` are still empty, and nothing is deployed. The sprint's
goal is a repository that builds and whose CI can refuse a bad change — not a feature
(`docs/sprints/sprint-01-plan.md`).

| Version | Contents | State |
|---|---|---|
| MVP | Ingestion pipeline, database, public API, frontend | Not started |
| v1 | Django admin, roles, review queue, audit log | Not started |
| v2 | News, historical gallery with citations, site settings | Not started |
| v3 | Public submissions, moderation, legal documents | Not started |

Known gaps that block a public launch, not the next sprint: Corpocarnaval has not been
contacted, and the site's terms of use were never found. The contact email is now
`victorloal513@gmail.com`. The legal texts are **permanently unreviewed drafts** — there will
be no professional review, so every legal page carries a DRAFT notice instead (ADR 0016).
See `docs/00-acta-proyecto.md` §12.2.

## Repository layout

```
├── docs/            requirements, design, tests, ADRs, legal, sprint notes
├── backend/         Django project (API, admin, ingestion) — skeleton in place
├── frontend/        React + TypeScript public site — reserved
├── tests/           cross-cutting E2E and security suites — reserved
├── AGENTS.md        rules for coding agents
├── MEMORY.md        session memory for coding agents
└── LICENSE          MIT — covers code only, not content
```

## Running the backend

```bash
python -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env        # gitignored; set SECRET_KEY — see .env.example
venv/bin/python backend/manage.py check
venv/bin/python -m pytest
```

Settings read **only** from environment variables and fail loudly when `SECRET_KEY`
is absent (SEC-46); a gitignored `.env` supplies development values. With no `DB_*`
variables set, development falls back to SQLite — `DB_*` is what enables PostgreSQL 16
(ADR 0009), the deployment database.

## Documentation

Start with `docs/00-contexto-proyecto.md` (the project brief, in Spanish).

| Document | Purpose |
|---|---|
| `docs/00-acta-proyecto.md` | Project charter: stakeholders, constraints, success criteria |
| `docs/00-contexto-proyecto.md` | The original brief — scope, decisions, risks, roadmap |
| `docs/01-requisitos/srs.md` | SRS: numbered requirements, MoSCoW per version |
| `docs/01-requisitos/historias-de-usuario.md` | User stories |
| `docs/01-requisitos/matriz-trazabilidad.md` | Requirement → story → design → test |
| `docs/02-diseno/` | C4, data model, data flow, threat model, roles, deployment |
| `docs/03-pruebas/` | Test plan and the security case register |
| `docs/adr/` | Architecture decision records |
| `SECURITY.md` | Vulnerability reporting, and the security posture as **decided, not implemented** |
| `docs/legal/` | **DRAFT** legal documents, permanently unreviewed by decision (ADR 0016) — **not legal advice** |
| `docs/comunicacion-corpocarnaval.md` | The written permission request to the organisers — drafted, not yet sent |
| `docs/sprints/` | Sprint plans and retrospectives |

## Technology

| Layer | Choice |
|---|---|
| Backend | Python 3.12, Django 5.2 LTS, Django REST Framework |
| Database | PostgreSQL 16 |
| Frontend | React + TypeScript, Vite |
| Admin | Django admin, customised |
| Object storage | Quarantine + public tiers, separate buckets |
| Scheduling | GitHub Actions `cron` (no resident worker) |
| Testing | pytest, Playwright, axe, Lighthouse |
| Deployment | Free tiers only — **zero cost is a hard constraint** |

## Requirements worth knowing before contributing

- **Nothing is published without human review.** Every record enters as `pending`.
- **Third-party material is never committed to this repository.** No PDFs, no
  photographs, no full article text.
- **An image with unknown rights is never published.** Author, source, licence, and
  citation are mandatory.
- **MIT covers the code only** — not scraped data, not third-party content.
- No raw IP addresses are stored; only a salted hash.
- Images where a minor is the focal subject require guardian authorisation.

See `AGENTS.md` for the full rules and `docs/adr/` for why each decision was made.

## Contributing

This is a solo project. See `CONTRIBUTING.md`. Issues and pull requests are welcome, but
expect slow responses.

## Licence

**MIT — code only.** Copyright © 2026 Victor Lopez.

The data collected by this project and any third-party content it displays are **not**
covered by this licence. Each published item carries its own attribution and rights
metadata.

## Ethics and data sources

- `robots.txt` and source terms of use are respected; requests are rate-limited and sent
  with an identifiable `User-Agent`.
- News is stored as headline, link, outlet, date, and a short original summary — never the
  full article.
- Removal requests are honoured through a documented takedown procedure. Illegal content
  is escalated, not merely hidden.

## Contact

Project and takedown contact: **victorloal513@gmail.com**