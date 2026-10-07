# Changelog

All notable changes to this project are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) **for the
code**. Content and documentation versions follow the project's own rules: legal documents
are versioned per `legal_documents` and never edited after publication.

## [Unreleased]

Phase 0 (documentation) is **closed**. No deployed version yet — see the status table in
`README.md`. Implementation begins with Sprint 01, `docs/sprints/sprint-01-plan.md`.

### Fixed — the admin console was unreachable (2026-10-07)

- **SEC-04:** `/admin/` could not be entered by anyone. Sprint 08a replaced
  `admin.site.login_form` with `OTPAdminAuthenticationForm` but left `admin.site.login_template`
  pointing at Django's stock `admin/login.html`, which renders only username and password. The
  form therefore demanded a TOTP token that had **no input field**: every login failed with
  "enter your OTP token". `AccountsConfig.ready()` now sets
  `admin.site.login_template = "otp/admin111/login.html"` (django-otp ships it, and its `es`
  catalog keeps the console Spanish per FR-H-08).
- **`LOGIN_REDIRECT_URL`** is now `/admin/`. Django's default, `/accounts/profile/`, does not
  exist here, so a login that carried no `next` — a direct visit to `/admin/login/` — dead-ended
  on a 404.
- **Tests:** the regression that slipped through was an assertion on
  `admin.site.login_form`, an implementation detail, not the rendered page. `test_totp.py` now
  renders `/admin/login/` and asserts the token field is present (it fails without the fix),
  logs in end-to-end with password + a generated TOTP code, checks the bare login lands on the
  console, and confirms an account with no device is refused with a form error. **147 backend
  tests** (was 143).
- **Docs:** `autenticacion.md` §2/§9 claimed a first-login, forced, in-console enrolment with
  generated recovery codes and a guard against deleting the last device — none of which exist.
  Corrected, and the deviations are stated: enrolment is `manage.py enrol_totp`, there are no
  recovery codes (SEC-05, Open), and the login form in fact demands a second factor from every
  staff account, not only the `admin` group. `casos-seguridad.md` SEC-04's expected result now
  describes what happens; `README.md` gains the operator bootstrap.

### Added — public site pages, dependency audit and the PostgreSQL CI job (2026-10-07)

- The public site navigates between the **programme**, **news** and **search** pages per
  locale. `App` is now the shell: site title, a locale-preserving switcher and the
  disclaimer (FR-A-09, FR-H-03/05).
- `NewsList` renders published news as a **citation** — headline, outlet, date, a short
  own-words summary and the source link (FR-E-01/02, LEG-04). The article body is never
  fetched or shown.
- `SearchPage`/`SearchResults` query `/api/search/` and show matching events and news
  (FR-I-01/02); the query lives in `?q=` so a result is linkable, in both locales.
- 24 frontend tests (was 12), covering the locale-switch path helper and the two new
  components. `frontend/vitest.setup.ts` now unmounts between tests: vitest runs without
  `globals`, so React Testing Library could not register its own cleanup and a second
  `render` in a file matched duplicate elements.
- **NFR-10:** `pip-audit` runs in CI and fails the build on a known vulnerability in a
  pinned dependency. The pins were moved to their fixed versions (Django 5.2.17,
  djangorestframework 3.17.2, Pillow 12.3.0, pytest 9.0.3, python-dotenv 1.2.2,
  pdfplumber 0.11.10 → pdfminer.six 20260107); `pip-audit -r requirements.txt` is clean.
- A `postgres` CI job runs the whole suite against **PostgreSQL 16**, so the deployment
  database and the Postgres-only search branch are exercised (FR-I-03). The `ci` job keeps
  the SQLite run: fast, zero infrastructure. Both jobs are green on `4a08742`.
- `matriz-trazabilidad.md`: the summary table was stale — it read "1 Done / 167 Open" while
  the body carried 108 Done rows. It now reports the real counts (170 rows: **124 Done, 45
  Open, 1 blocked**) and FR-A-05 is Done against its existing venue test.

### Added — Sprint 18: the gallery and submission integrity (2026-10-07)

- A public **gallery** page: a published image shows its title, year, author, licence and
  **citation text** (FR-E-06, LEG-03). Only `published` rows reach it, so an image with
  `rights_status = unknown` cannot appear. The `img` bytes are a storage concern the
  deployment owns (ADR 0015 is Proposed); the card is correct without them.
- **FR-E-07:** identical image bytes are refused re-publication by a partial unique
  constraint on `MediaAsset.content_hash` (migration `editorial/0002`); the empty "no hash
  recorded" case is excluded.
- **FR-F-21:** a submission whose bytes match an earlier one is flagged for the reviewer
  (`SubmissionFile.duplicate_of`) rather than silently accepted.
- **FR-F-04:** `declared_mime_conflicts` refuses a *concrete* `image/*` declaration that
  contradicts the bytes; an empty header, a generic `application/octet-stream` and the
  historical `image/jpg` spelling pass, because browsers send imperfect content types.
- **FR-C-10 (ADR 0006):** rejecting a submission deletes its quarantined files and their
  rows; the `Submission` row stays `rejected` with its reason for the register.
- **PRV-09:** the submission endpoints answer `Cache-Control: private, no-store`.
- 133 backend tests (was 127) and 27 frontend tests (was 24); no OpenAPI drift.

### Changed — ADR 0018: the v3 legal gate is resolved (2026-10-07)

- **ADR 0018** amends ADR 0008's gate: public submissions ship under the **permanently
  labelled draft** legal texts (ADR 0016). The "reviewed legal documents" condition becomes
  "published as labelled drafts"; moderation, the takedown register and blocking consent
  bound to a `legal_documents` version stand unchanged.
- Operational defaults are set by the maintainer as **revisable choices, not legal advice**:
  retention (consent 24 months; contact email 12 months after a decision; takedown email 24
  months after `responded_at`; rejected files deleted on rejection; `raw_documents` 30 days;
  `audit_logs` and `ingestion_runs` bounded) and takedown deadlines (acknowledge 7 days,
  resolve 30, minor-privacy claims prioritised at 48 h, unlawful content escalated
  immediately and never closed by a note). This unblocks **PRV-06**.
- ADR 0008, ADR 0016, `docs/legal/README.md` §2.1, the privacy policy §5, the takedown
  procedure §4 and `estados.md` §5 are updated to match. The legal-analysis items (legal
  basis per activity, supervisory-authority registration, liability/jurisdiction wording) stay
  unresolved by decision — they are not invented.
- The matrix's **Blocked** row disappears: **132 Done / 37 Open / 0 blocked**. This decision is
  conditional on scale and must be revisited before any commercial use.

### Added — Sprint 19: the public submission form (2026-10-07)

- The anonymous submission form: an **image** or a **video link**, no account (FR-F-01/02).
  The rights and consent declarations are **unchecked by default and blocking** (FR-F-10/14),
  and the consent label states that the accepted text is an unreviewed draft (ADR 0016/0018).
- Declaration fields are collected and stored — author, year, place, description (FR-F-13).
  **`POST /api/submissions/` was ignoring `year` and `place`**; the view now reads them (a
  non-numeric year is stored as absent, never guessed) and the serializer documents them.
- A **honeypot** field mirrors the server's silent no-op (FR-F-17), and the token returned can
  be used to look the submission up (FR-F-18).
- 135 backend tests (was 133) and 33 frontend tests (was 27). FR-F-13 → Done; matrix at
  **133 Done / 36 Open / 0 blocked**.
- Carried, with reasons: the Turnstile provider (needs keys; the CAPTCHA is off by default and
  the honeypot and quotas still apply), signed-URL transfer (SEC-13) and consent-gated video
  embeds (PRV-08), both needing their own feature.

### Added — Sprint 20: retention enforcement and the data-subject procedure (2026-10-07)

- A new `carnaval.privacy` app with `purge_personal_data`, which **enforces the ADR 0018
  periods**: a submission's contact email is cleared 12 months after the submission is
  decided, `consent_records` are deleted after 24 months, a takedown requester's email is
  cleared 24 months after `responded_at`, and `ingestion_runs` are pruned after a year. A
  still-`pending` submission keeps its email — its clock has not started. `--dry-run` reports
  without changing anything; a real run is atomic.
- **`audit_logs` is never purged**: it is append-only (FR-D-09) and holds only salted hashes,
  so the evidence value outweighs the period. The exception is stated in the privacy policy
  and ADR 0018, not silently applied.
- The data-subject procedure is documented (privacy policy §6: channel, 15 business-day
  response, best-effort identification) and the deletion path is rehearsed by the command's
  tests. **PRV-03 and PRV-07 → Done**; matrix at **135 Done / 34 Open / 0 blocked**.
- 141 backend tests (was 135); factories for `Submission`, `ConsentRecord` and
  `TakedownRequest`.

### Added — Sprint 21: per-locale slugs (2026-10-07)

- `Edition` and `Day` now carry `slug_es` **and** `slug_en` (FR-H-07), matching what
  `modelo-datos.md` §3.1/§3.2 already specified. The migration **renames** `slug` to
  `slug_es` — existing rows keep their slug — and adds `slug_en` (blank by default).
- `slug_for(locale)` resolves the slug with one-directional fallback to the source locale,
  the same rule ADR 0012 gives for content. `slug_en` is unique when set: two rows cannot
  share a translated URL, and an empty English slug is not a duplicate.
- The public API exposes both slugs (`slug_es`, `slug_en`); the admin searches both. OpenAPI
  regenerated.
- 143 backend tests (was 141); matrix at **136 Done / 33 Open / 0 blocked**.
- Carried: locale-prefixed detail routes (there are no public detail pages yet) and verbatim
  citations with a translation (FR-H-09).

### Closed — the project (2026-10-07)

- **The project is closed in code; it is not launched.** All four versions of ADR 0008 are
  implemented, tested and green in CI. The single remaining act is the **deployment**, which
  needs the maintainer's accounts (ADR 0015 is Proposed); it is carried, not hidden.
- The retrospection is now complete **per sprint**. Written for the sprints that lacked one:
  `sprint-05` (the read API), `sprint-08` (the whole admin-foundation plan), `sprint-10` (v1
  release, **not run**), `sprint-11` (news and the citation registry), `sprint-12` (media and
  rights), `sprint-14` (v2 release, **not run**), `sprint-15` (submission intake), `sprint-17`
  (v3 launch, **not launched**) and `sprint-18`, `sprint-19`, `sprint-20`, `sprint-21`. The
  project close is `docs/sprints/proyecto-retrospectiva.md`.
- The documentation sweep reconciled `AGENTS.md` and `SECURITY.md` — both still described a
  project several sprints (or a whole build) behind the tree — and `README.md` and the matrix.
- Final state: **143 backend + 33 frontend tests**; matrix at **136 Done / 33 Open / 0
  blocked**. No "Done" rests on a report: each row names its verification.



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

### Added — Sprint 05: the public read API (2026-10-06)

- A new `carnaval.api` app: read-only endpoints for **editions, days, events and venues**
  (FR-A-07). Every queryset starts from `status = published`, so a `pending` or `rejected`
  row is a 404 (FR-A-06, SEC-47); the viewsets opt in to `AllowAny` explicitly and expose no
  non-GET route (NFR-18).
- Filtering by edition (year) and by date range, and page-number pagination (FR-A-11).
- Anonymous requests are rate-limited per IP (NFR-17); public reads carry
  `Cache-Control: public, max-age=300` (NFR-02).
- `/health` reports application and database reachability and discloses nothing else
  (FR-D-11).
- The generated schema now covers the catalogue and drift is checked in CI (NFR-12, ADR 0011).
- `django-filter==26.2` added; `rest_framework`/`django_filters` joined the mypy
  missing-import override because neither ships `py.typed`.

### Added — Sprint 06: the public site (2026-10-06)

- `frontend/` — a React + TypeScript site built with Vite, in its own package (the root
  manifest stays documentation tooling only). It renders the programme grouped by day in
  chronological order with a source link per entry (FR-A-08, FR-A-12) and the unofficial /
  not-affiliated disclaimer (FR-A-09).
- Bilingual routing: `/es/…` and `/en/…`, the unprefixed root redirected to the negotiated
  locale, the choice persisted in a cookie, and no machine translation (FR-H-01/03/04/05/10).
- A build-failing check that both locales define the same, non-empty keys (FR-H-02), and
  content fallback to the source locale rather than an empty page (FR-H-06).
- `tsc`, eslint and 12 vitest + testing-library tests; the CI stages for the frontend land in
  Sprint 07.

### Added — Sprint 07: hardening, and the road to the MVP (partially delivered, 2026-10-06)

- A strict `Content-Security-Policy` for everything but `/admin/`, plus `Referrer-Policy` and
  `X-Content-Type-Options`; CORS restricted to the site's own origins (SEC-15, NFR-07/08).
- The frontend stages (`tsc`, eslint, vitest, build) are now in CI, completing the non-browser
  half of `plan-pruebas.md` §7 (NFR-11).
- `scripts/check_secrets.py` scans the tracked tree and fails the build on a secret, closing
  **NFR-09**.
- The backend test step enforces ≥ 80 % coverage of the ingestion pipeline and the public API
  (NFR-15; measured 93 %).
- A console `LOGGING` config that never receives a secret, a raw IP or a session identifier
  (NFR-19).
- **ADR 0015 (Proposed)** — the zero-cost platform, decided by egress cost: Cloudflare Pages +
  a Python container host + Neon/Supabase + Cloudflare R2. The deployment itself needs the
  maintainer's accounts and is carried.
- `despliegue.md` §11 documents the backup and restore procedure (NFR-20); the rehearsal is
  carried.
- **Carried, not silently skipped:** the deployment, the PostgreSQL CI service, the browser
  stages (docker compose + Playwright, Lighthouse, axe, dependency audit) and the
  dependency-triage process. See `docs/sprints/sprint-07-retrospectiva.md`.

### Added — Sprint 08a: identity and audit (2026-10-06)

- A `carnaval.accounts` app: the `admin`/`editor`/`viewer` groups with their permissions
  (`seed_roles`), `seed_admin` creating a staff user in `admin` and **never** a superuser
  (FR-D-01/02/06/07/14, FR-D-13), TOTP for administrators (`enrol_totp`, an OTP-aware admin
  login form and an enforcement middleware), central session revocation, a step-up page and
  gate (FR-D-16), and a login throttle with exponential backoff behind a custom auth backend
  (SEC-06, FR-D-10). Sessions use a 12 h idle window and a 72 h absolute cap enforced in
  middleware (SEC-02/03/08).
- A `carnaval.audit` app: an append-only `AuditLog` (app-level `save`/`delete` guards, an
  append-only manager and no add/change/delete permission) with `login`/`login_failed`
  signals and a read-only admin (FR-D-08/09/10).
- Middleware adds a correlation id and a **salted IP hash** (PRV-01), forces Spanish on the
  admin while the API surface stays English (FR-H-08), and sets `noindex` on the console
  (NFR-21).
- Carried and named: **08b** (FR-D-03, object-level authorization), hashed recovery codes
  (SEC-05 — `django-otp` stores them in plain text), the PostgreSQL append-only trigger, and
  the explicit session-expiry test (FR-D-15).

### Added — v1 backend: admin surface and review queue (Sprint 08b + 09, 2026-10-06)

- A `carnaval.moderation` app: an append-only `ModerationAction` and a `service` that is the
  only path to `published` — `approve` (which cascades to the pending children of an edition or
  a day), `reject` (a non-empty reason is required), `unpublish`, `request_changes` — each
  writing a `moderation_actions` row and an `audit_logs` row in one transaction (FR-C-03/04/05/07).
- The content and the ingestion tables are registered in the admin behind the permission matrix.
  A fresh staff user with no role sees nothing (FR-D-03); `viewer` cannot moderate (FR-D-05);
  the queue filters by `status`/`origin` and shows `source_url` plus a permission-gated link to
  the stored payload (FR-C-06/09, matrix row 11).
- The source dashboard shows each source's active flag, consecutive failures and last success
  (FR-D-12).
- **ADR 0017** and a `staged_changes` column: the pipeline now **proposes** a change to an
  already-published row instead of skipping it, and a reviewer applies it. `apply_proposal` is
  the only code path that writes a published content field (FR-B-07/09, §5.1, SEC-38).

### Added — v2 backend: editorial, media, settings and search (Sprints 11–13, 2026-10-06)

- A `carnaval.editorial` app: `Source` (the citation registry), `NewsItem` (headline, URL,
  outlet, date and a short **own-words** summary; no article body), `MediaAsset` and
  `SiteSetting`.
- `MediaAsset`'s publication gate is a pair of database `CHECK` constraints plus a
  `publish_blockers()` hook the moderation service consults: `rights_status = unknown`, a
  missing author/source/citation, un-stripped EXIF, or a minor without guardian consent all
  block publication (FR-E-05, LEG-02/09). EXIF is required at approval (FR-E-08).
- Typed `site_settings` with Python accessors, a refusal to store secret-shaped keys (FR-E-11)
  and before/after audit on every change (FR-E-10/12).
- Read-only, published-only API endpoints for **news** and **media** (FR-E-01), and `/api/search/`
  over published events and news — PostgreSQL full text on Postgres, an `icontains` fallback on
  SQLite (FR-I-01/02).
- Carried and named: the news transform, the gallery UI, duplicate refusal, per-locale slugs,
  verbatim citations with a translation, the quarantine-key guarantee and the Postgres
  full-text verification.

### Added — v3 backend: submissions, legal and takedown (Sprints 15–16, 2026-10-06)

- A `carnaval.submissions` app: `Submission`, `SubmissionFile` and `ConsentRecord`. Image uploads
  are validated by **magic bytes via Pillow**, fully decoded and **re-encoded** so embedded
  payloads and every EXIF tag (including GPS) are stripped — verified, not assumed (FR-F-03/05/06,
  SEC-11). Video links are normalised against a YouTube/Vimeo allowlist to `(provider, id)`, never
  a raw embed `src` (FR-F-02/19, ADR 0007).
- The public `POST /api/submissions/` and `GET /api/submissions/<token>/` endpoints, with a
  blocking rights declaration, a honeypot, per-**salted-IP** quotas and a Turnstile hook
  (FR-F-10/11/12/16/17/18). Submissions enter as `pending`, `origin = community` (FR-F-22).
- A `carnaval.legal` app: `LegalDocument` versioned and **never edited in place** once current
  (FR-G-01/02), and a `TakedownRequest` register whose `illegal_content` claims are escalated and
  cannot be closed by an internal note (FR-G-03/04/05/06), reachable at `POST /takedown/`.
- Carried and named: the quarantine → public move and the `MediaAsset` on approval (FR-F-09), the
  rejected-upload policy (FR-C-10), signed-URL transfer (SEC-13), duplicate detection (FR-F-21),
  PII purge (PRV-03/07), consent-gated embeds (PRV-08), `Cache-Control` for personal data (PRV-09)
  and the deployment/browser verification. The CAPTCHA is off by default and documented as such.

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