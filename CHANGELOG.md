# Changelog

All notable changes to this project are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) **for the
code**. Content and documentation versions follow the project's own rules: legal documents
are versioned per `legal_documents` and never edited after publication.

## [Unreleased]

Phase 0 (documentation) is **closed**. No deployed version yet — see the status table in
`README.md`. Implementation begins with Sprint 01, `docs/sprints/sprint-01-plan.md`.

### Added — project scaffolding

- `AGENTS.md` — binding rules for coding agents.
- `MEMORY.md` — session memory for coding agents, capped at 50 lines.
- `docs/00-acta-proyecto.md` — project charter: stakeholders, constraints, success
  criteria, and recorded deviations from the brief.
- `docs/01-requisitos/srs.md` — SRS with 170 numbered requirements, MoSCoW per version.
- `docs/01-requisitos/historias-de-usuario.md` — 32 user stories.
- `docs/01-requisitos/matriz-trazabilidad.md` — requirement → story → design → test.
- `docs/02-diseno/` — the full design set: C4 context and containers
  (`arquitectura-c4.md`), PostgreSQL data model (`modelo-datos.md`), operational pipeline
  (`flujo-datos.md`), threat model (`modelo-amenazas.md`), roles and permissions
  (`roles-permisos.md`), lifecycle states (`estados.md`), session and TOTP authentication
  (`autenticacion.md`), use cases (`diagrama-casos-uso.md`), and deployment
  (`despliegue.md`).
- `docs/03-pruebas/plan-pruebas.md` — test plan and the 14-stage CI pipeline.
- `docs/03-pruebas/casos-seguridad.md` — 74 numbered security test cases.
- `docs/adr/0001` … `0014`, `0016` — architecture decision records. **ADR 0016**: the legal
  texts ship as permanently labelled drafts; no professional review will be obtained.
- `docs/comunicacion-corpocarnaval.md` — the written permission request to the organisers,
  stating exactly what will and will not be collected. **Drafted, not sent.**
- `scripts/check-diagrams.cjs` — validates **every** fenced diagram in the repository and fails
  on PlantUML syntax outside a `mermaid` fence (ADR 0014). Wired into CI in Sprint 01.
- `package.json` / `package-lock.json` — pins `mermaid` and `jsdom` so the validator is
  runnable from a clean checkout with `npm ci && npm run check:diagrams`. **Documentation
  tooling only**; the public site's package belongs under `frontend/`.
- `docs/legal/` — terms, privacy policy, content policy, and takedown procedure. Published
  as **permanently labelled drafts**; never professionally reviewed (ADR 0016). Not legal
  advice.
- `docs/fuentes-y-atribucion.md` — source register, attribution policy, scraping etiquette,
  and the §9 source spike record against `carnavaldepasto.org`.
- `docs/sprints/` — Sprint 00 plan and retrospective (Phase 0) and the Sprint 01 plan.
- `CONTRIBUTING.md`.
- `SECURITY.md` — vulnerability reporting. Opens by stating that **nothing is released and
  nothing is deployed**, so the policy describes a posture that is **decided, not
  implemented**. It records the reporting route, what is public by default, the security
  model with an ADR for every row, and the accepted risks — including that this project
  cannot give a user a verified legal basis (ADR 0016), that there is no bug bounty and no
  response-time guarantee, and that a single part-time maintainer is an unmitigated
  single point of failure.

### Added — Sprint 01: the repository that runs

- `backend/` — Django 5 project skeleton: environment-only settings, the programme spine
  (`editions`, `days`, `venues`) with the first migration set, DRF + `drf-spectacular`, and
  a generated `docs/02-diseno/openapi.yaml` that CI regenerates and fails on drift (ADR 0011).
- `.github/workflows/ci.yml` — lint, typecheck, migration check, tests, schema validation
  and drift, diagram validation (the backend stages of `plan-pruebas.md` §7).
- `backend/tests/` — pytest suite with factory_boy factories for the spine, unit tests
  verifying FR-A-01 and FR-A-02, and the no-egress guard proof tests (NFR-16).
- `.env.example` — documents every variable the settings read.

### Fixed — review findings (2026-10-05)

- **The no-egress guard was a no-op.** The fixture created a socket and returned it
  unchanged, and its test was `assert True`. It is now a session-scoped guard blocking
  outbound TCP, `sendto`, and DNS resolution for every destination but loopback, with tests
  proving both the block and the loopback exception (NFR-16, sprint 01 item 7).
- **New DRF endpoints were born public.** `REST_FRAMEWORK` declared no default permissions,
  so DRF's `AllowAny` applied. Defaults are now fail-closed (`IsAuthenticated`, session
  auth only) — RBAC is enforced server-side on every request (ADR 0005).
- **`SECRET_KEY` fell back to an insecure default and `DEBUG` defaulted to `True`**, which
  SEC-46 forbids: settings now raise `ImproperlyConfigured` when `SECRET_KEY` is absent and
  default `DEBUG` off; session and CSRF cookies are `Secure` and `SameSite=Lax` outside
  development (ADR 0005). CI provides an explicit non-production test value.
- `requirements.txt` was missing `argon2-cffi`, without which Argon2id hashing cannot run,
  and `django-otp` was installed but unregistered — its apps and middleware are now wired;
  `PASSWORD_HASHERS` puts Argon2id first (ADR 0005).
- The package `django-argon2`, named in ADR 0005, ADR 0009, `autenticacion.md`,
  `SECURITY.md` and `AGENTS.md`, **does not exist on PyPI**; all five now say
  `argon2-cffi`, and ADR 0005 carries the correction note. The decision is unchanged.
- README claimed `backend/`, `frontend/` and `tests/` were empty; its status and layout
  now describe the skeleton, and a short run guide was added.

### Changed

- `LICENSE` — **The Unlicense replaced with MIT.** The Unlicense purported to dedicate the
  entire repository to the public domain, including third-party content the maintainer does
  not own. MIT covers code only; see ADR 0004.
- `00-contexto-proyecto.md` moved to `docs/00-contexto-proyecto.md`.
- `docs/01_requisitos/` renamed to `docs/01-requisitos/` to match the hyphenated
  convention used by the other document folders.
- `.gitignore` — added `data/raw/`, `*.pdf`, and `data/uploads/`; `lib/` is no longer
  ignored, because the file originated as GitHub's Python template and would silently drop
  real source directories.
- `scripts/check-diagrams.cjs` — **now skips dependency and build directories.** The first
  run with `node_modules` present walked into `mermaid`'s own `README.md`, found PlantUML C4
  blocks there and failed on a third party's documentation. It also learned the C4 diagram
  keywords, which it had been reporting as `(unknown: C4Context)` while parsing them
  successfully.
- ADR 0014 — amended. Its claim that *"Mermaid ships no C4 notation"* is **false** against
  `mermaid@12.1.0`, which parses `C4Context` natively; the C4 approximation is kept anyway
  because GitHub renders Mermaid with a version we do not control. Its claim that Mermaid has
  no activity diagram was re-verified and still holds.
- `docs/00-acta-proyecto.md` §12 — the source spike is recorded as **partially** done: the WP
  API and `robots.txt` are closed, the terms of use are not. Added §12.1 (Phase 0 closed) and
  §12.2 (the five open items, none of which a document can close).
- `docs/01-requisitos/matriz-trazabilidad.md` — **FR-A-01 and FR-A-02 moved from Open to
  Done**: their verification (unit: edition model; unit: days are rows not enum) is now
  performed and recorded in `backend/tests/test_programme_models.py`.

### Removed

- `docs/01_requisitos/ad` — an empty 0-byte file.

### Notes on deviations from the original brief

Recorded in full in `docs/00-acta-proyecto.md` §9 and in `MEMORY.md`. In summary: no JWT
(session-based admin auth instead), Python + Django + PostgreSQL, Django admin rather than
a React admin panel, a generated rather than hand-written OpenAPI contract, and a
bilingual Spanish/English site.

`docs/00-contexto-proyecto.md` has been **reconciled** with all of them: it carries a
supersession banner and each reconciled paragraph names the ADR that supersedes it, so it
can no longer mislead a reader on its own. The brief is no longer a source of
contradiction.

### Known open items at the close of Phase 0

None of these block Sprint 01. All of them block a public launch.

- **Corpocarnaval has not replied.** The written permission request was **sent by email on
  2026-10-04** to `comunicacion@carnavaldepasto.org` (`docs/comunicacion-corpocarnaval.md`,
  recorded in `docs/fuentes-y-atribucion.md` §9.7). No answer has arrived, and **nothing about
  the project's position moved** — silence is not permission, and §7 of that document fixes in
  advance what happens if the answer is no. **The address itself is unverified**: the source
  spike found no public email anywhere on that site, so a bounce would mean the request never
  arrived. Watch the sending mailbox. Required before publishing (brief §11, §20).
- **The official site's terms of use were not found.** `robots.txt` is permissive and the
  WordPress REST API is live, but enumerating all 19 pages and 42 posts found no terms,
  conditions, or cookie policy. **Accepted as a documented risk on 2026-10-04** — no terms
  were found, so none are treated as stated. The mitigation is the written request above, not
  an inference of permission. `docs/fuentes-y-atribucion.md` §9.5.
- **`docs/legal/` will never be professionally reviewed** (ADR 0016). The texts ship as
  permanently labelled drafts, and every `[PENDIENTE]` that needed legal judgement stays
  unresolved *by decision*. One consequence is now stated rather than implied: the takedown
  procedure has **no deadline**.
- **ADR 0015** (network egress cost) is unwritten; it decides the storage provider and
  belongs after the schema exists.
- **ADR 0008's gate on v3 is unsatisfied.** Public submissions were gated behind reviewed
  legal documents; review has been declined. Deliberately left undecided — it must be settled
  before the upload form is built, not while.
- **PRV-06 is blocked.** It requires the privacy policy to name retention periods, which need
  legal judgement that will not be obtained. The requirement is left intact and marked
  blocked rather than weakened to look satisfiable.

Resolved during Phase 0's close: the project contact is **victorloal513@gmail.com**, written
into `README.md`, `CONTRIBUTING.md`, and the `docs/legal/` placeholders that depended on it
(FR-B-14 requires contact information in the scraper's `User-Agent`).