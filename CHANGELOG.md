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

- `backend/` — Django 5.2 LTS project skeleton: environment-only settings, the programme spine
  (`editions`, `days`, `venues`) with the first migration set, DRF + `drf-spectacular`, and
  a generated `docs/02-diseno/openapi.yaml` that CI regenerates and fails on drift (ADR 0011).
- `.github/workflows/ci.yml` — lint, typecheck, migration check, tests, schema validation
  and drift, diagram validation (the backend stages of `plan-pruebas.md` §7).
- `backend/tests/` — pytest suite with factory_boy factories for the spine, unit tests
  verifying FR-A-01 and FR-A-02, and the no-egress guard proof tests (NFR-16).
- `.env.example` — documents every variable the settings read.

### Added — Sprint 02: the schema the pipeline needs (2026-10-06)

- `backend/carnaval/ingestion/` — a new app with `ScrapeSource` (FR-B-12, the
  circuit-breaker state), `RawDocument` (FR-B-02/03, with a **unique** SHA-256
  `content_hash` that makes re-running a source idempotent) and `IngestionRun`
  (FR-B-08, trigger/status/stats).
- `Event` in `programme` (FR-A-03, FR-A-04): an optional venue and times, bilingual
  display fields, `sort_order`, a `source_url` for FR-A-12, and the moderation mixin.
- The `ingestion_run` FK is now on the moderation mixin, where the design always had it
  and where it was deferred until `ingestion_runs` existed (FR-B-06).
- `manage.py seed_demo` — idempotent, development-only, creates the canonical 2026
  programme **already published**. It exists only because the MVP ships no admin
  (publishing waits for v1); it never creates a user and refuses to run with `DEBUG` off.
- `modelo-datos.md` §2/§3.1/§3.4 and `estados.md` §1 are reconciled with the shipped
  mixin: it lives on the programme spine and on `events`, and editions no longer carry a
  stored `is_published`.
- Migrations `ingestion/0001` and `programme/0004`.

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

### Added — Sprint 03: the extractor, part 1 (2026-10-06)

- The ingestion HTTP layer: `robots.txt` cached per host and honoured, per-source rate
  limiting, an identifiable `User-Agent` carrying the contact address, retry with exponential
  backoff for transient failures, `Retry-After` on a 429, and no retry on other 4xx (FR-B-13,
  FR-B-14).
- The raw store: SHA-256 hashing, a hash-gated no-op, payloads written behind a storage
  abstraction, and a `raw_documents` row per unique payload (FR-B-02, FR-B-03).
- Run bookkeeping: `ingestion_runs` opened `running`, closed with `stats`, and `skipped`
  without a network call when a source is disabled (FR-B-08).
- The circuit breaker on `scrape_sources`: counters, `last_error`, auto-disable at the
  threshold, and an alarm (FR-B-10).
- `manage.py ingest_source --all|--due|--source` (plus `--dry-run`) and
  `manage.py prune_raw_documents`, which enforces ADR 0013's 30-day window and per-source byte
  cap (FR-B-16, FR-B-17, FR-B-18).
- HTTP is mocked with `httpx.MockTransport`; committed fixtures live under
  `backend/tests/fixtures/`, reduced with `_fields=` so no third-party article text is
  committed. No test touches the network (NFR-16). SEC-37/38/39/41/42 have executable tests.

### Added — Sprint 04: the extractor, part 2 (2026-10-06)

- The `wp_api` transform: a post becomes an event by taking the **day** from its day
  **category name** (`5 de enero`) and the **year** from its post **date**, because the spike
  found slugs and dates that disagree and day labels that carry no year. Days are collected by
  name pattern, so the `6 de enero` root category is not dropped (FR-B-01, FR-B-15, FR-A-03,
  FR-A-04).
- Schema validation: a post missing a required field, or an unparseable date, is rejected and
  counted in `stats.rejected` (FR-B-05).
- The sanity gate: a payload that yields nothing, drops or spikes against the last five runs,
  loses a required field, or falls outside the target edition is an **alarm**, not a silent
  success. The target year defaults to the newest edition, so the guard is on without
  configuration (FR-B-11, SEC-40).
- Staging: validated candidates become `pending` rows with `origin = scraped` and their
  `ingestion_run`. `Event.source_record_key` (migration `programme/0005`, unique per day on
  non-empty keys) makes re-staging an upsert. Published or human-authored rows are never
  modified — proposing a change to published content is `flujo-datos.md` §5.1, deferred to its
  own ADR (FR-B-06, FR-B-07 partially, SEC-37/38).
- HTTP is mocked; the `wp_posts` and `wp_posts_empty` fixtures drive the transform and the
  zero-extraction alarm. No test touches the network (NFR-16).

### Added — forward sprint plans (2026-10-06)

- `docs/sprints/sprint-03-plan.md` … `sprint-17-plan.md` — the planned path from the extractor
  to the v3 launch: one deep plan per sprint, each with its backlog, exit criteria, decisions,
  risks and what its version's release requires. They are **forward plans**: a sprint's status
  becomes `Done` only when its own work is delivered, CI is green and the matrix is updated.

### Fixed — dependency, settings and moderation review (2026-10-06)

- **Django was pinned to 5.0.6, which reached end of life in April 2025, and its
  type stubs did not support it.** Bumped to **5.2 LTS** (`Django==5.2.9`), with the
  libraries that actually support it: `djangorestframework` 3.15.2 → **3.16.1** and
  `drf-spectacular` 0.27.2 → **0.30.0** (both now classify Django 5.2; the old pins
  only listed up to 5.0). `mypy` moved from 2.4.0 to **2.3.1**, inside the
  `<2.4` range `django-stubs` 6.1.1 declares, so the toolchain is consistent again.
- **The moderation mixin promised by Sprint 01 item 4 did not exist.** It is now
  `carnaval.core.models.ModeratedModel` — `status`, `origin`, `reviewed_by`,
  `reviewed_at`, `rejection_reason`, `created_by` — applied to `editions`, `days`
  and `venues` (`modelo-datos.md` §2, `estados.md` §1). A database `CHECK` requires a
  non-empty `rejection_reason` for `status = rejected`, and `ingestion_run` is
  deliberately deferred until `ingestion_runs` exists.
- **`Edition.is_published` was a stored boolean that could publish without review.**
  It is removed; `is_published` is now a derived property of `status`. Migration
  `programme/0003` carries the change.
- **Production transport security was absent.** `SECURE_SSL_REDIRECT`,
  `SECURE_HSTS_SECONDS` (one year), `SECURE_HSTS_INCLUDE_SUBDOMAINS`,
  `SECURE_HSTS_PRELOAD`, an opt-in `SECURE_PROXY_SSL_HEADER` and
  `CSRF_COOKIE_HTTPONLY` are set, gated on `DEBUG`. `manage.py check --deploy` is
  clean with `DEBUG` off and now runs as a CI stage.
- **`settings.py` inspected `sys.modules` for `pytest`** to add `testserver` to
  `ALLOWED_HOSTS`. Removed: Django's own test setup already provides it. Tests that
  speak plain HTTP also disable `SECURE_SSL_REDIRECT` through a conftest fixture.
- `modelo-datos.md` §2 and `estados.md` §1 now state that `rejection_reason` is
  `NOT NULL DEFAULT ''` (emptiness is what the `CHECK` forbids), matching the code.

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