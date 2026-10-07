# AGENTS.md

## Read this first

**The project is complete in code; it is not deployed.** All four versions of ADR 0008 are
implemented: `backend/` holds a Django 5.2 LTS project (ingestion pipeline, published-only read
API, Django admin with roles/TOTP and the review queue, editorial content, public submissions
and the legal register) and `frontend/` holds the React + TypeScript public site (programme,
news, gallery, search and the submission form). The traceability matrix is at **136 Done /
33 Open / 0 blocked**; the Open rows need a **deployment, a browser or object storage — not new
code**. `docs/sprints/proyecto-retrospectiva.md` closes the project.

The deployment is the one remaining act and it needs the maintainer's accounts (ADR 0015 is
Proposed). Stages 12–14 of `plan-pruebas.md` §7 (docker compose E2E, Lighthouse, axe) are
**not wired** — do not claim them green. The backend and docs stages run in
`.github/workflows/ci.yml`, which also runs the suite on PostgreSQL 16 and audits dependencies;
`docs/02-diseno/openapi.yaml` is committed and CI-enforced (ADR 0011).

`AGENTS.md` is the durable context and `MEMORY.md` is the capped session state. The root
`package.json` exists **for the diagram check alone** — the backend is Python and the public
site has its own package under `frontend/`, so do not grow the root manifest into an
application manifest.

The stack is **decided** — do not re-litigate it, and do not substitute a framework:

| Layer | Choice | ADR |
|---|---|---|
| Backend | Python 3.12, Django 5.2 LTS, Django REST Framework | 0009 |
| Database | PostgreSQL 16 | 0009 |
| Frontend | React + TypeScript (public site **only**) | 0009, 0005 |
| Admin | **Django admin** — there is no React admin panel | 0005 |
| Auth | Server-side sessions + TOTP. **No JWT anywhere** | 0005 |
| OpenAPI | **Generated** by drf-spectacular; CI fails on drift | 0011 |

`docs/adr/` is authoritative for **decisions**. `docs/00-contexto-proyecto.md` is the
original brief and is **partly superseded** — its §6 decision 8, §9, and §12 still describe
JWT and an undecided stack. Where they disagree, the ADRs win. The deviations are listed in
`docs/00-acta-proyecto.md` §9.

`MEMORY.md` holds session state: current status, decisions, learnings, errors to avoid,
next steps, and a dated session log. Read it after this file; where they conflict, this
file wins.

## Layout

- `docs/00-acta-proyecto.md` — charter: stakeholders, constraints, success criteria, deviations
- `docs/00-contexto-proyecto.md` — the original brief (Spanish, pending translation, partly superseded)
- `SECURITY.md` — vulnerability reporting; the security posture (implemented in code, not deployed)
- `docs/01-requisitos/` — `srs.md`, `historias-de-usuario.md`, `matriz-trazabilidad.md`
- `docs/02-diseno/` — C4, data model, data flow, threat model, roles, states, auth, deployment
- `docs/03-pruebas/` — `plan-pruebas.md`, `casos-seguridad.md`
- `docs/adr/` — `000N-kebab-title.md`
- `docs/legal/` — **draft** legal texts, not legal advice
- `docs/sprints/` — sprint plans, retrospectives, and the project close
- `docs/fuentes-y-atribucion.md` — source register and scraping etiquette
- `scripts/check-diagrams.cjs` — the diagram validator; run it with `npm run check:diagrams`
- `package.json` / `package-lock.json` — **documentation tooling only**; `node_modules/` is ignored
- `backend/` — Django project: `carnaval/` settings and the apps (`core`, `programme`,
  `ingestion`, `api`, `accounts`, `audit`, `moderation`, `editorial`, `submissions`, `legal`,
  `privacy`), and `backend/tests/` (pytest suite, factories, no-egress guard). Run
  `python backend/manage.py check` (see `README.md` for the full local run guide)
- `.github/` — `workflows/ci.yml` (backend, frontend, PostgreSQL and docs CI) and `dependabot.yml`
- `frontend/` — the React + TypeScript public site (programme, news, gallery, search, submit)
- `tests/` — reserved, still empty at the root; backend tests live under `backend/tests/`

Docs use an `NN-` prefix for ordering. ADRs are the exception: `000N-`, no prefix.

## Language

All repo content is **English**: docs, ADRs, comments, identifiers, branch names, commits,
API surface. The brief `docs/00-contexto-proyecto.md` is the only legacy exception.

The **public site** is bilingual — Spanish source locale, English secondary (ADR 0010). The
**Django admin is Spanish only**. Spanish is not a language option for new documents.

## Conventions

- Commits: Conventional Commits — `feat:`, `fix:`, `docs:`, `chore:`, `test:`.
- Branches: `main` stays stable and protected; short-lived `docs/...`, `feat/...`, `fix/...`.
- **Definition of Done** (ADR 0001), all four required: code with tests, docs updated, CI
  green, and the requirement linked in `matriz-trazabilidad.md`. Anything less is not done.
- Significant decisions go in `docs/adr/`, never only in a commit message.
- Solo, part-time: max 2 tasks in progress, 1-week sprints (ADR 0001).
- **Verify that delegated work actually landed** before reporting it done. A completion
  report is not evidence; check the filesystem.

## Maintaining `MEMORY.md`

`MEMORY.md` is **capped at 50 lines**. At the end of any session that changes the repo:

- Update *Current state* if the status moved; add a row to *Session log* with the date
  and the topics touched.
- Record only decisions that are actually settled, and only failures worth not repeating.
- Prune stale rows and superseded bullets to stay under the cap. Never split it into
  `MEMORY-2.md` or move the detail into it — durable context belongs in `AGENTS.md` or
  `docs/`, not here.

## Hard domain rules

An agent will violate one of these by accident. They come from the brief and the ADRs and
are not negotiable.

**Publishing**
- Nothing reaches `published` without human review. Scraped, manual, and community content
  all land as `status = pending`; a reviewer sets `published` or `rejected` with a reason.
- Every record keeps `origin` (`scraped` | `manual` | `community`) plus the ingestion run or
  user that produced it.
- The scraper is a convenience, never a dependency. If it fails, published data must not be
  deleted or degraded. Use retry with backoff and a circuit breaker that disables a source
  after N consecutive failures.
- **An extraction yielding zero records from a previously working source is a failure, not
  a success.** This is the project's top documented risk.

**Scraping**
- Idempotent: running it twice must not duplicate. Gate on `raw_documents.content_hash`.
- Respect `robots.txt` and the source's terms. Send an identifiable `User-Agent` with
  contact info. Rate-limit requests.
- Prefer the WordPress REST API over HTML scraping; the spike found it live and the `wp_api`
  transform uses it.

**Copyright and data**
- Never commit third-party PDFs, photos, or full article text. Store headline, source URL,
  outlet, date, and a short original summary only.
- An image is not publishable without author, source, license, and citation text.
  `rights_status = unknown` means do not publish. Old photos are not free of rights.
- Do not publish images where a minor is the focal subject without guardian authorization.
- The MIT license covers code only — not scraped data or third-party content.
- The site must state it is unofficial and not affiliated with or endorsed by Corpocarnaval.

**Privacy and uploads**
- Never store a raw IP; only a **salted** hash. An unsalted IPv4 hash is brute-forceable
  over 2³² candidates, which is why the salt is mandatory.
- Validate uploads by magic bytes, not extension. Fully decode and re-encode. Strip EXIF
  including GPS, unconditionally. Files stay in private quarantine until approved.
- Videos are external links (YouTube/Vimeo embeds), never hosted files. The submitted URL
  is never used directly as an embed `src`.
- Quarantine and public storage are separate buckets on a separate domain.

**Security**
- **No JWT, no bearer token, nothing in `localStorage`** (ADR 0005). This deviates from the
  brief; do not reintroduce tokens.
- Sessions are server-side with a CSRF-protected, `httpOnly`, `Secure`, `SameSite` cookie.
  Central revocation is a feature — do not replace it with token rotation.
- Use vetted libraries (Argon2id via `argon2-cffi`, `django-otp`). Never write custom
  cryptography.
- Enforce RBAC server-side on every request; never rely on the interface hiding a control.
  Django admin ships with full permissions by default — a fresh install must not expose
  unreviewed `pending` content (FR-D-03).
- `audit_logs` is append-only for every role, including `admin`.
- Secrets only in environment variables. Infrastructure must stay at zero cost.

## Working with code

- **No test may contact a live source.** HTTP is mocked; scraper tests replay committed
  fixtures under `backend/tests/fixtures/`. This is the project's highest-risk failure mode.
- The OpenAPI contract is regenerated in CI and the build **fails on drift**. Commit the
  regenerated `docs/02-diseno/openapi.yaml`; never hand-edit it (ADR 0011).
- Missing English translation keys must **fail the build**, not degrade at runtime.
- Migrations must be reviewed in the pull request; `makemigrations --check` gates the build.
- Content tables inherit `carnaval.core.models.ModeratedModel`. `status` defaults to
  `pending`, `is_published` is **derived**, and `origin` is mandatory: never add a stored
  publication boolean.
- `Meta.constraints` is **not** inherited from an abstract base model. Compose shared
  constraints per model — see `carnaval.core.models.rejection_reason_constraint` — and name
  them with `%(app_label)s_%(class)s` placeholders so they stay unique.
- New requirements get a stable ID in `srs.md`, a row in `matriz-trazabilidad.md`, and a
  verification method. Never renumber an existing requirement.
- Before scraping work, confirm `data/raw/` and `*.pdf` are still in `.gitignore`.
- `.gitignore` started as GitHub's Python template; `lib/` is deliberately un-ignored so a
  real source directory is not silently dropped.