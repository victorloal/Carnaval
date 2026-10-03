# Test plan

- **Status:** Draft
- **Date:** 2026-10-03
- **Relates to:** ADR 0001 (Definition of Done), ADR 0002 (idempotency), ADR 0009 (stack),
  ADR 0010 (bilingual), ADR 0011 (generated OpenAPI),
  `docs/01-requisitos/srs.md`, `docs/02-diseno/modelo-datos.md`
- **Companion:** `docs/03-pruebas/casos-seguridad.md` (the security register)

## 1. The one rule that overrides everything else

**No test may ever contact `carnavaldepasto.org`, or any other live external source.**

Why this is stated first and in bold: brief §14 rates "the site changes its structure and
breaks the scraper" as the highest-likelihood risk in the project. A test suite that
depends on the network converts that risk into a source of flaky, unfixable failures, and
it also means CI cannot run offline or on a free tier without egress limits.

How compliance is achieved:

- **HTTP is mocked.** `responses` (or `respx`) intercepts outbound calls. A test that
  forgets to mock a request fails against a local stub, not against the internet.
- **Fixtures are committed and replayed.** Captured payloads live in
  `backend/tests/fixtures/<source_name>/<case_name>/`, each directory containing the raw
  response body plus a `meta.json` with the URL, HTTP status, content type, and the
  `content_hash` the pipeline should compute.
- **Scraper tests are written against fixtures, not URLs.** If a test needs the real site,
  that is a manual spike, not an automated test.
- CI has no credentials for any external service, so a network call would fail anyway.

## 2. Tooling

| Purpose | Tool | Notes |
|---|---|---|
| Unit + integration | **pytest** + **pytest-django** | Django test database is created per run |
| HTTP mocking | **responses** / **respx** | Every outbound call intercepted |
| HTML fixtures | **pytest-recording** or plain fixtures | Prefer plain committed fixtures — reproducible |
| E2E | **Playwright** (Python or Node) | Against a running stack with seeded data |
| Accessibility | **axe-core** via Playwright | Automated pass, plus manual keyboard testing |
| Performance | **Lighthouse CI** | Budgets enforced in CI, not just observed |
| API contract | **drf-spectacular** `--validate` + diff | Fails the build on drift (ADR 0011) |
| Static analysis | **ruff** (lint + format), **mypy** + django-stubs | Gate the build |
| Migration safety | `makemigrations --check --dry-run` | Fails if models and migrations disagree |
| Dependency audit | **pip-audit**, Dependabot | Free; required by NFR-10 |
| Frontend | **vitest**, **Playwright**, eslint, tsc | For the React app |

## 3. Test levels

### 3.1 Unit

Pure logic with no database: hash computation, EXIF stripping, magic-byte detection,
URL normalisation for YouTube/Vimeo, CSP header construction, salted-IP hashing, and the
publication-rule validators (notably: *`rights_status = unknown` cannot be published*).

Target: these are where coverage matters most, because they encode the hard domain rules.

### 3.2 Integration

Django `TestCase` against a real PostgreSQL database (not SQLite — `django-storages` and
PostgreSQL full-text search behave differently, and ADR 0009 commits to PostgreSQL).

Covers: model constraints, the `CHECK` that a rejection requires a reason, `bulk_create`
behaviour, the moderation mixin's audit side effects, and pipeline stages against a real
database.

### 3.3 API contract

`drf-spectacular` regenerates the schema and the build fails if the committed
`docs/02-diseno/openapi.yaml` differs (ADR 0011, NFR-12). Additionally:

- Schema validation: `manage.py spectacular --validate` must pass.
- Anonymous-access tests: every read endpoint returns only `status = published` records
  (FR-A-06). This is a security assertion as much as a functional one.
- Every write path verifies it returns 401/403 without a session.

### 3.4 End-to-end (Playwright)

Realistic journeys only, against seeded data:

1. Visitor reads the programme for an edition, day by day, in both locales.
2. Locale switch preserves the page and persists.
3. Admin logs in with TOTP, filters the review queue, approves, and the item appears on the
   public site.
4. Moderator rejects with a reason and the item never appears publicly.
5. (v3) Contributor submits an image, passes CAPTCHA, sees the consent recorded; moderator
   approves; the file becomes publicly readable with `nosniff`.
6. (v3) Admin triggers a pipeline run; `ingestion_runs` shows the outcome.

### 3.5 Security

See `casos-seguridad.md`. Not duplicated here.

### 3.6 Accessibility

`axe-core` on every page in both locales, asserting **zero critical violations**. Axe
cannot detect everything: keyboard-only traversal, focus visibility, and screen-reader
labels are verified manually and recorded as manual test cases in the same register.

### 3.7 Performance

Lighthouse CI budgets, run against a production build with a warm cache:

| Metric | Budget | Requirement |
|---|---|---|
| Largest Contentful Paint | ≤ 2.5 s | NFR-01 |
| Total Blocking Time | ≤ 200 ms | NFR-01 |
| Cumulative Layout Shift | ≤ 0.1 | NFR-01 |
| Lighthouse performance | ≥ 90 | NFR-01 |
| Lighthouse accessibility | ≥ 95 | NFR-03 |

API latency (NFR-02, p95 < 300 ms) is measured separately against seeded data with the
cache warm. Measuring it against a cold free-tier database would produce a number that
reflects the free tier, not the code.

## 4. Strategy per version

Per ADR 0008 each version ships only when its own tests are green.

### MVP
- Pipeline: idempotency (run twice → zero duplicates), hash gating (unchanged input is a
  no-op), circuit breaker, zero-extraction alarm, partial-failure isolation, and the
  absolute rule that a failed run never touches `published` rows.
- Public API: publication filtering, edition/day/event endpoints, no write endpoints.
- Frontend: programme rendering, both locales, mobile viewport, axe, Lighthouse budgets.
- i18n: a missing `en` key **fails the build** (FR-H-02). This is a test, not a lint.
- Static: ruff, mypy, migration check, schema drift check.

### v1
- Roles: full permission matrix, verified by attempting each action as each role and
  asserting denial. See `SEC-*` cases.
- Audit: every state change and both login outcomes produce an `audit_logs` row; the table
  is append-only for every role.
- Admin: queue filters, bulk approval recording each decision individually, unpublish.
- Sessions: fixation, revocation, CSRF, TOTP enforcement, lockout.
- Backup/restore: rehearsed at least once (NFR-20).

### v2
- Editorial: news stored as headline + link + own summary only; full-text never persisted.
- Gallery: the `rights_status = unknown` block, asserted against **every** code path
  including `bulk_create`, `QuerySet.update()`, and the admin.
- Minor-subject guard.
- Duplicate detection by hash.
- Search: published-only scope (FR-I-02).

### v3
- Uploads: the entire pipeline — magic bytes, declared-vs-detected mismatch, polyglot,
  re-encoding, EXIF/GPS verification by reading the stored object back.
- Consent: version binding, checkbox default state, salted IP hash.
- Quarantine: non-public readability, signed-URL expiry, bucket separation.
- Legal: version immutability, single current version per type and locale.
- Takedown: the state machine, and that `illegal_content` cannot be closed by an internal
  note.
- Abuse: per-IP quotas, daily pending quota, CAPTCHA and honeypot.

## 5. Test data strategy

- **Factories** (`factory_boy`) for every model. No raw model instantiation in tests.
- A **canonical fixture set** covering every moderation and origin state:
  `pending`/`published`/`rejected` × `scraped`/`manual`/`community`.
- **Seeded roles** `admin`, `editor`, `viewer` with known permission sets; permission tests
  assert the matrix, not the group names.
- **Upload fixtures** generated locally: a valid JPEG built with Pillow, a PNG, a WebP, an
  EXIF-laden JPEG with GPS tags, a text file renamed `.jpg`, and a GIF/JPEG polyglot built
  by concatenating bytes. All generated in a fixture factory, not committed as binaries
  larger than a few KB.
- **Scraper fixtures** committed as text, per §1.
- **Two editions** of data so filtering and per-locale slugs can be tested properly.
- **Isolation:** no test may depend on data created by another test. If ordering matters,
  the design is wrong.

## 6. Definition of Done tie-in

Per ADR 0001 an item is done only when all four hold, and the fourth is the one this plan
enforces: **the requirement is linked in `docs/01-requisitos/matriz-trazabilidad.md`**.

Consequences:

- A requirement with no test and no other verification method cannot be closed.
- A test with no requirement it verifies is dead weight and should be deleted or the
  requirement added.
- "It works on my machine" is not a verification method. The four accepted methods are
  *test*, *inspection*, *demonstration*, and *analysis*.

## 7. CI pipeline

Exact order; any failure blocks, matching NFR-11:

```
1. ruff check + ruff format --check      lint
2. mypy backend/                         typecheck
3. tsc --noEmit frontend/                typecheck
4. eslint frontend/                      lint
5. vitest --coverage                     frontend unit tests
6. makemigrations --check --dry-run      migration drift
7. spectacular --validate --fail-on-warn API schema validity
8. regenerate schema + git diff --exit-code   schema drift  (ADR 0011)
9. ruff/mypy/pytest backend/             backend unit + integration
10. npm run build frontend/              production build
11. docker compose up + playwright       E2E
12. lighthouse ci                         performance budgets
13. axe in the E2E run                    accessibility
14. pip-audit / npm audit                dependencies
```

Stage 8 is the mechanical enforcement of ADR 0011: the schema is regenerated and the build
fails if the working tree differs from the committed `docs/02-diseno/openapi.yaml`.

E2E and Lighthouse run only on branches and on `main`, not on every push, to stay inside
free-tier minutes.

## 8. Non-functional verification

| NFR | How it is verified |
|---|---|
| NFR-01 performance | Lighthouse CI budgets (§3.7) |
| NFR-02 API latency | p95 measurement script against seeded data |
| NFR-03 WCAG 2.1 AA | axe automated + manual keyboard records |
| NFR-04 mobile | Playwright at 360 px, asserting no horizontal overflow |
| NFR-05 zero cost | No paid service is referenced in any config or CI secret; a review checklist item |
| NFR-06 availability without sources | Integration test: block all outbound HTTP, assert the public API still returns published data |
| NFR-07 security headers | Header assertions in the API test suite |
| NFR-08 CORS | Tests asserting disallowed `Origin` is rejected |
| NFR-09 secrets | Pre-commit secret scan plus a repository review |
| NFR-16 no live calls | Network egress blocked in CI; a scan ensures no hardcoded external URL in test code |
| NFR-17 rate limiting | Threshold tests against the limit |

## 9. Out of scope, deliberately untested for now

- **Load and stress testing.** Not meaningful on a free tier with one user. Revisit if the
  site ever gets real traffic.
- **Cross-browser matrix beyond current Chromium/Firefox/Safari.** Full matrix deferred;
  a documented manual pass replaces it.
- **Long-term data archival and migration rehearsal beyond one restore.** One rehearsal is
  enough at this scale (NFR-20).
- **Third-party service uptime.** Cloudflare Turnstile and the storage provider are
  dependencies we do not test; they are mitigated procedurally.
- **Penetration testing.** Out of budget. The security register is written to be
  executable by the maintainer instead.

## 10. Maintenance rules

- A bug fix in production **must** arrive with a regression test, or with a note in
  `MEMORY.md` explaining why not.
- The security register (`casos-seguridad.md`) is updated whenever the threat model
  changes. A new threat with no test case is an incomplete change.
- Fixtures older than one parade edition are re-captured, because the source markup changes
  yearly; stale fixtures test obsolete markup and give false confidence.