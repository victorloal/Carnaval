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

**Phase 0 — documentation — closed 2026-10-04. The project is complete in code; it is not
deployed.** The requirements, design set, test plan, threat model and ADRs are complete, and
all four versions of ADR 0008 are implemented: the **backend** (ingestion, published-only API,
Django admin with roles/TOTP and the review queue, editorial content, submissions and legal)
and the **React site** (programme, news, gallery, search and the submission form), in two
locales. **143 backend + 33 frontend tests**; the matrix is at **136 Done / 33 Open / 0
blocked**, and every Open row needs a **deployment, a browser or object storage — not new
code**. The one remaining act is the deployment, which needs the maintainer's accounts (ADR
0015 is Proposed); the project closes with `docs/sprints/proyecto-retrospectiva.md`.

| Version | Contents | State |
|---|---|---|
| MVP | Ingestion pipeline, database, public API, frontend | Delivered (deployment carried) |
| v1 | Django admin, roles, review queue, audit log | Delivered |
| v2 | News, historical gallery with citations, site settings | Delivered |
| v3 | Public submissions, moderation, legal documents | Delivered; gate resolved (ADR 0018) |

CI runs the suite on SQLite and on **PostgreSQL 16**, audits dependencies with `pip-audit`,
and checks the frontend (`tsc`, eslint, vitest, build). The browser stages — Playwright E2E,
Lighthouse and axe — are carried; they need a browser environment and are not claimed green.

Known gaps that block a public launch, not the next unit of work: Corpocarnaval was asked in
writing (`comunicacion@carnavaldepasto.org`, 2026-10-04) and **has not replied** — silence is
not permission — and the site's terms of use were never found. The contact email is
`victorloal513@gmail.com`. The legal texts are **permanently unreviewed drafts** — there will
be no professional review, so every legal page carries a DRAFT notice instead (ADR 0016); the
v3 gate they used to block was resolved by ADR 0018. See `docs/00-acta-proyecto.md` §12.2.

## Repository layout

```
├── docs/            requirements, design, tests, ADRs, legal, sprint notes
├── backend/         Django project (API, admin, ingestion) — backend for MVP–v3
├── frontend/        React + TypeScript public site (programme, news, search)
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

## Running the frontend

```bash
cd frontend
npm ci
npm run typecheck && npm run lint && npm test
npm run dev          # the site reads /api (set VITE_API_BASE to point elsewhere)
```

The public site is bilingual: `/es/…` and `/en/…`, with the unprefixed root redirecting to
the negotiated locale and the choice kept in a cookie. Its package is separate from the root
manifest, which exists only for the diagram validator.

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