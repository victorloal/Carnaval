# Security test cases

- **Status:** Draft
- **Date:** 2026-10-03
- **Relates to:** `docs/02-diseno/modelo-amenazas.md` (STRIDE threat model),
  `docs/02-diseno/modelo-datos.md`, ADR 0004, ADR 0005, ADR 0006, ADR 0007, ADR 0010
- **Companion:** `docs/03-pruebas/plan-pruebas.md`
- **Rule:** no case contacts a live external source.

## How to read this register

- **ID** is stable. Retiring a case keeps its ID and records the reason; IDs are never
  reused.
- **Priority** — Critical: blocks release. High: blocks the version. Medium: blocks v3 or is
  fixed in the backlog. Low: improvement.
- **Verification** — *Automated* or *Manual*. A manual case needs a recorded result; an
  automated one is a test function whose name contains the ID, so a failure names its own
  requirement.
- **Threat** names the STRIDE category from the threat model.
- Every case names the artefact it protects, so coverage can be audited against the data
  model rather than by feel.

---

## A. Authentication (ADR 0005)

### SEC-01 — Password hashing is Argon2id
- **Threat:** Elevation of privilege / Information disclosure
- **Preconditions:** a user exists with a known password.
- **Steps:** 1. Inspect the stored credential hash. 2. Assert the algorithm identifier is
  Argon2id. 3. Assert the password string itself appears nowhere in the database.
- **Expected:** hash prefix identifies Argon2id; no cleartext password exists in any table.
- **Verification:** Automated · **Priority:** Critical
- **Protects:** `auth_user` · **Maps to:** SEC-01, NFR-09

### SEC-02 — No bearer token is ever issued to the browser
- **Threat:** Information disclosure (token exfiltration via XSS)
- **Preconditions:** none.
- **Steps:** 1. Log in. 2. Inspect every response header and body for `access_token`,
  `refresh_token`, `Authorization: Bearer`, or any JWT-shaped string. 3. Inspect
  `localStorage`, `sessionStorage`, and cookies from JavaScript. 4. Assert cookies set are
  `httpOnly` and the only one is the session key.
- **Expected:** no token of any kind is returned; `document.cookie` cannot see the session
  cookie; no token appears in any web storage. This is the executable form of ADR 0005's
  deviation from the brief's JWT plan.
- **Verification:** Automated · **Priority:** Critical
- **Protects:** `django_session`, `auth_user` · **Maps to:** SEC-02, SEC-03

### SEC-03 — Session cookie attributes
- **Threat:** Information disclosure
- **Steps:** 1. Log in over HTTPS. 2. Inspect the `Set-Cookie` header.
- **Expected:** `HttpOnly`, `Secure`, `SameSite=Lax`, and `Path=/` on the session cookie.
- **Verification:** Automated · **Priority:** Critical
- **Protects:** `django_session` · **Maps to:** SEC-02

### SEC-04 — TOTP is mandatory for the administrator role
- **Threat:** Elevation of privilege
- **Preconditions:** a user with a valid password but no TOTP device enrolled.
- **Steps:** 1. Open `/admin/login/`. 2. Confirm the page renders an OTP field. 3.
  Authenticate with the correct password and no usable device. 4. Enrol with `manage.py
  enrol_totp` and retry with a current code.
- **Expected:** the password alone is not enough, and the refusal is a **form error, never a
  server error**. There is no in-console enrolment and no recovery codes, so an account with
  no device cannot enter the console at all until `enrol_totp` is run from the shell. Once a
  device is enrolled, password + a current TOTP code authenticates, and an `admin`-group user
  who is logged in but unverified is redirected to `/accounts/step-up/` before any view.
- **Verification:** Automated · **Priority:** Critical
- **Protects:** `otp_totpdevice`, `auth_group` · **Maps to:** SEC-04

### SEC-05 — TOTP recovery codes are single-use and hashed at rest
- **Threat:** Elevation of privilege
- **Steps:** 1. Inspect stored recovery codes. 2. Consume one successfully. 3. Replay the
  same code.
- **Expected:** stored codes are hashed, not plaintext; the first use succeeds, the replay
  fails.
- **Verification:** Automated · **Priority:** High
- **Protects:** `otp_staticdevice`/recovery storage · **Maps to:** SEC-05

### SEC-06 — Replayed TOTP codes are rejected
- **Threat:** Spoofing
- **Preconditions:** capture a valid TOTP code.
- **Steps:** 1. Submit the code. 2. Immediately resubmit the identical code from a second
  session.
- **Expected:** the second submission fails (time-step reuse protection).
- **Verification:** Automated · **Priority:** High
- **Maps to:** SEC-04

### SEC-07 — Login throttling and lockout
- **Threat:** Spoofing / Elevation of privilege
- **Preconditions:** a known username.
- **Steps:** 1. Attempt N consecutive failures. 2. Then attempt with the **correct**
  password. 3. Wait out the backoff, then retry.
- **Expected:** access is refused while locked out; after the backoff, the correct password
  succeeds; repeated failures extend the backoff exponentially. The username must not be
  distinguishable from a non-existent one in timing or response.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** SEC-06

### SEC-08 — No user enumeration on login
- **Threat:** Spoofing / Information disclosure
- **Steps:** 1. Attempt login with a non-existent user and a wrong password for a real user.
- **Expected:** identical status code, body, and comparable timing.
- **Verification:** Automated · **Priority:** Medium
- **Maps to:** SEC-06

### SEC-09 — CSRF on every mutating endpoint
- **Threat:** Tampering / Elevation of privilege
- **Steps:** 1. Authenticate. 2. Issue a POST, PUT, PATCH, and DELETE **without** a CSRF
  token, from a foreign origin. 3. Repeat for each admin view that mutates state, including
  bulk actions.
- **Expected:** all rejected with 403. Enumerate the views; an unenumerated view is an
  untested attack surface.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** SEC-07

### SEC-10 — Session fixation
- **Threat:** Spoofing
- **Steps:** 1. Obtain a session cookie as an unauthenticated visitor. 2. Authenticate with
  that cookie. 3. Compare the session key before and after.
- **Expected:** the session key rotates on login; the pre-authentication key is invalid.
- **Verification:** Automated · **Priority:** High
- **Maps to:** SEC-02

### SEC-11 — Central session revocation
- **Threat:** Elevation of privilege
- **Preconditions:** user with two active sessions, one compromised.
- **Steps:** 1. Revoke all sessions for the account. 2. Replay the old session cookie.
- **Expected:** it is rejected. Revocation must be immediate and total — this is the
  property that makes session auth stronger than the brief's JWT rotation.
- **Verification:** Automated · **Priority:** Critical
- **Protects:** `django_session` · **Maps to:** SEC-08

### SEC-12 — No public signup path
- **Threat:** Elevation of privilege
- **Steps:** 1. Enumerate routes for any user-creation endpoint. 2. Assert the admin login
  page exposes no registration link. 3. Assert no management command other than the
  documented seed command creates users.
- **Expected:** accounts exist only via the seed command or Django's `createsuperuser`.
- **Verification:** Automated + Manual · **Priority:** Critical
- **Maps to:** FR-D-13, FR-D-14

---

## B. Authorization (ADR 0005, SRS §3.4)

### SEC-13 — Role matrix is enforced on every action
- **Threat:** Elevation of privilege
- **Preconditions:** one user per role, each authenticated with TOTP where required.
- **Steps:** for each capability in `docs/02-diseno/roles-permisos.md`, and for **each
  role**: 1. Attempt the action. 2. Record allow/deny. 3. Compare to the matrix.
- **Expected:** an exact match, with no unlisted capability reachable by any role. In
  particular: `viewer` can never transition moderation state; `editor` cannot reach site
  settings, users, or legal documents; only `admin` can.
- **Verification:** Automated, data-driven from the matrix · **Priority:** Critical
- **Maps to:** FR-D-04 … FR-D-07, SEC-09, SEC-10

### SEC-14 — Authorization is object-level, not list-level
- **Threat:** Elevation of privilege (horizontal)
- **Preconditions:** an `editor` authorised for some content.
- **Steps:** 1. Obtain the URL or primary key of a record the editor is not assigned to. 2.
  Attempt direct access, update, approve, and reject.
- **Expected:** every attempt is denied. A `has_permission` that passes while
  `get_object` does not check ownership is the failure this case exists to catch.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** SEC-09, SEC-10

### SEC-15 — Anonymous callers cannot reach any authenticated endpoint
- **Threat:** Elevation of privilege
- **Steps:** 1. Without a session, enumerate every non-GET endpoint, including DRF routes
  and admin views.
- **Expected:** 401/403 for all. The public API's only anonymous write endpoint is
  submissions, and only from v3.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** NFR-18, FR-D-13

### SEC-16 — The audit log is append-only for every role, including administrator
- **Threat:** Repudiation
- **Preconditions:** an `admin` session.
- **Steps:** 1. As `admin`, attempt to UPDATE and DELETE `audit_logs` rows — via the admin,
  the ORM, and the API.
- **Expected:** all denied. Enforce at both application and database level; the
  application-level check alone is not sufficient against a direct database connection.
- **Verification:** Automated + Manual · **Priority:** Critical
- **Protects:** `audit_logs` · **Maps to:** FR-D-09

### SEC-17 — Every moderation action is recorded
- **Threat:** Repudiation
- **Steps:** 1. Perform approve, reject, unpublish, and a settings change. 2. Query
  `moderation_actions` and `audit_logs`.
- **Expected:** each produces a row with actor, action, object, and timestamp; a rejection
  without `rejection_reason` is impossible (CHECK constraint).
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** FR-C-03 … FR-C-07, FR-D-08

### SEC-18 — Login successes and failures are both audited, with a hashed IP
- **Threat:** Repudiation / Information disclosure
- **Steps:** 1. Perform a successful and a failed login. 2. Inspect the rows.
- **Expected:** both present with the correct action. The IP column contains a **salted
  hash**: two different IPs must not collide, the same IP must produce a stable hash, and
  no raw IP appears anywhere — including in `last_error` text and application logs.
- **Verification:** Automated · **Priority:** High
- **Protects:** `audit_logs`, `consent_records` · **Maps to:** PRV-01, PRV-02

---

## C. Public submissions and uploads (ADR 0006)

### SEC-19 — Magic-byte validation rejects a renamed executable
- **Threat:** Tampering / Elevation of privilege
- **Steps:** 1. Upload a file named `photo.jpg` whose bytes are a shell script, a ZIP, and a
  PDF, in turn.
- **Expected:** each rejected on detected type. The check must read content, never the
  extension or the client-declared MIME type.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** FR-F-03, FR-F-04, SEC-11

### SEC-20 — Polyglot image/archive files are neutralised
- **Threat:** Tampering
- **Preconditions:** a file that is simultaneously a valid JPEG and a valid ZIP.
- **Steps:** 1. Upload it. 2. Read the stored object back and confirm the archive structure
  is gone.
- **Expected:** the file is re-encoded and no longer valid as an archive. A magic-byte check
  alone would pass this file; only re-encoding defeats it.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** FR-F-05, SEC-11

### SEC-21 — EXIF and GPS are stripped, verified by reading the object back
- **Threat:** Information disclosure
- **Preconditions:** a JPEG containing GPS, camera, and timestamp EXIF.
- **Steps:** 1. Upload. 2. Read the **stored** object, not the in-memory buffer. 3. Assert no
  EXIF segment remains.
- **Expected:** zero EXIF. Verifying in memory would miss a bug in the write path; there
  must be no configuration to retain EXIF.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** PRV-04, FR-F-06, FR-E-08

### SEC-22 — Oversized and over-quota uploads are rejected
- **Threat:** Denial of service
- **Steps:** 1. Upload a file exceeding the size limit. 2. Repeat until the per-IP count
  limit. 3. Fill the global daily pending quota.
- **Expected:** each rejected with a distinct, non-informative error; quotas enforced
  server-side regardless of what the client sends.
- **Verification:** Automated · **Priority:** High
- **Maps to:** FR-F-16

### SEC-23 — Duplicate uploads are detected by hash
- **Threat:** Denial of service / Tampering
- **Steps:** 1. Upload an image. 2. Upload identical bytes under a different filename.
- **Expected:** flagged as a duplicate of the first for the reviewer, not silently accepted
  as new.
- **Verification:** Automated · **Priority:** Medium
- **Maps to:** FR-F-21, FR-E-07

### SEC-24 — Quarantine storage is not publicly readable
- **Threat:** Information disclosure
- **Preconditions:** a submitted, unapproved upload.
- **Steps:** 1. Request the object URL directly, unauthenticated. 2. Request it with a
  signed URL whose signature is altered. 3. Request an expired signed URL. 4. Enumerate
  bucket keys.
- **Expected:** 403/404 in every case. A publicly readable quarantine bucket makes the
  entire moderation model decorative.
- **Verification:** Automated · **Priority:** Critical
- **Protects:** `submission_files.quarantine_key` · **Maps to:** FR-F-07, SEC-12

### SEC-25 — Quarantine and public buckets are distinct and separately addressed
- **Threat:** Information disclosure
- **Steps:** inspect storage configuration and response headers.
- **Expected:** separate buckets on a separate domain from the application; no path allows
  reading a quarantine key through the public storage configuration.
- **Verification:** Manual · **Priority:** Critical
- **Maps to:** FR-F-08, ADR 0006

### SEC-26 — Public assets are served with defensive headers
- **Threat:** Information disclosure / Tampering
- **Steps:** request a published image directly.
- **Expected:** `X-Content-Type-Options: nosniff` and an explicit `Content-Disposition`, so
  an SVG/HTML payload cannot be rendered as script.
- **Verification:** Automated · **Priority:** High
- **Maps to:** FR-F-20

### SEC-27 — CAPTCHA and honeypot resist automation
- **Threat:** Denial of service / Tampering
- **Steps:** 1. Submit repeatedly without solving the CAPTCHA. 2. Submit with the honeypot
  field filled.
- **Expected:** rejected. The honeypot submission is dropped silently — a visible error
  teaches the bot what to avoid.
- **Verification:** Automated · **Priority:** Medium
- **Maps to:** FR-F-17

### SEC-28 — Consent is recorded and version-bound
- **Threat:** Repudiation
- **Steps:** 1. Submit with consent. 2. Assert `consent_records` links to the exact
  `legal_documents` version. 3. Publish a new version, then check the historical record.
- **Expected:** the historical consent still resolves to the version accepted at the time;
  publishing a new version does not rewrite history.
- **Verification:** Automated · **Priority:** Critical
- **Protects:** `consent_records`, `legal_documents` · **Maps to:** PRV-05, FR-G-01

### SEC-29 — The consent checkbox cannot be pre-checked
- **Threat:** Tampering
- **Steps:** 1. Load the form and inspect the checkbox HTML. 2. Submit directly via HTTP
  without it.
- **Expected:** no `checked` attribute, and the server rejects a submission lacking explicit
  consent regardless of what the client claims.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** FR-F-10

---

## D. Copyright and privacy (ADR 0004, brief §11)

### SEC-30 — `rights_status = unknown` cannot be published by any path
- **Threat:** Information disclosure (unlawful publication)
- **Preconditions:** an asset with `rights_status = unknown`.
- **Steps:** attempt to publish by **each** route: the admin form, a single ORM save, a
  `bulk_create`, a `QuerySet.update()`, and any API endpoint.
- **Expected:** every route refuses. A model-level validator plus a DB constraint is
  stronger than a form check, because the pipeline bypasses forms.
- **Verification:** Automated · **Priority:** Critical
- **Protects:** `media_assets` · **Maps to:** LEG-02, FR-E-05

### SEC-31 — Minor-subject guard
- **Threat:** Information disclosure
- **Steps:** attempt to publish an asset with `minor_subject = true` and
  `guardian_consent_on_file = false`, through every route.
- **Expected:** all refuse.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** LEG-09, FR-F-15

### SEC-32 — No raw IP address anywhere
- **Threat:** Information disclosure
- **Steps:** 1. Exercise login, submission, and takedown paths from a known IP. 2. Search
  **every** table and the application logs for the raw address.
- **Expected:** zero occurrences. Salted hash only (PRV-02): the same IP yields a stable
  hash, different IPs do not collide, and the salt lives only in an environment variable.
- **Verification:** Automated + Manual · **Priority:** Critical
- **Maps to:** PRV-01, PRV-02

### SEC-33 — Contributor email never leaves the system
- **Threat:** Information disclosure
- **Preconditions:** a submission with `contact_email`.
- **Steps:** enumerate public API endpoints, the sitemap, RSS, and the admin list views
  reachable by a `viewer`; search each response body.
- **Expected:** the address never appears in any public or viewer-level response, and it is
  excluded from any export.
- **Verification:** Automated · **Priority:** Critical
- **Protects:** `submissions.contact_email`, `takedown_requests.requester_email`
  **Maps to:** PRV-03

### SEC-34 — News never contains full article text or article images
- **Threat:** Information disclosure
- **Preconditions:** a pipeline run over a news fixture.
- **Steps:** 1. Inspect `news_items`. 2. Search every column for long verbatim blocks and
  for third-party image references.
- **Expected:** headline, URL, outlet, date, and a short original summary only. Long
  verbatim overlap with the source is the signal to check.
- **Verification:** Automated · **Priority:** High
- **Maps to:** LEG-04, FR-E-02

### SEC-35 — No third-party material in the repository
- **Threat:** Information disclosure
- **Preconditions:** none.
- **Steps:** 1. Assert `data/raw/` and `*.pdf` are gitignored. 2. Scan the tracked tree for
  PDFs and binary image files. 3. Check history, not just the working tree.
- **Expected:** none present. The repo carries code, fixtures **we authored**, and docs.
- **Verification:** Automated (CI) + Manual · **Priority:** Critical
- **Maps to:** LEG-05, FR-B-19

### SEC-36 — Video links are validated and never used raw as an embed source
- **Threat:** Tampering (stored XSS)
- **Steps:** 1. Submit links for every provider, plus near-miss hosts
  (`youtube.com.evil.example`, uppercase, `//` protocol-relative, embedded quotes). 2.
  Inspect the rendered embed markup.
- **Expected:** only the allowlisted providers are accepted; the `src` is always built from
  a stored provider + id, never from submitted text. A video file upload is rejected.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** FR-F-02, FR-F-19, ADR 0007

---

## E. Data integrity and pipeline (ADR 0002)

### SEC-37 — The pipeline is idempotent
- **Threat:** Tampering / Denial of service
- **Steps:** 1. Seed a clean database. 2. Run the pipeline twice against the same fixture.
  3. Diff the resulting tables.
- **Expected:** the second run produces **zero** inserts and zero duplicates. Content-hash
  gating means the second run records a no-op.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** FR-B-03, FR-B-04, ADR 0002

### SEC-38 — A failed run never modifies published data
- **Threat:** Tampering / Denial of service
- **Preconditions:** published rows exist.
- **Steps:** 1. Configure a source to fail (500, then malformed markup). 2. Run the
  pipeline. 3. Diff every `published` row.
- **Expected:** byte-identical. This is the property that guarantees the site survives when
  the outside world does not.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** FR-B-09, NFR-06

### SEC-39 — The circuit breaker disables a failing source
- **Threat:** Denial of service
- **Steps:** 1. Fail a source N times. 2. Attempt another run.
- **Expected:** the source is auto-disabled, an alert is raised, `last_error` and
  `last_failure_at` are recorded, and no further request is made to it until re-enabled.
- **Verification:** Automated · **Priority:** High
- **Maps to:** FR-B-10

### SEC-40 — A zero-extraction run is treated as a failure, not a success
- **Threat:** Tampering
- **Preconditions:** a source that previously extracted 5 records now returns HTML with a
  changed structure.
- **Steps:** run the pipeline against that fixture.
- **Expected:** an alarm, no silent success, no mass deletion of `published` rows. This is
  the single most likely real-world failure (brief §14).
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** FR-B-11

### SEC-41 — Rate limiting is respected per source
- **Threat:** Denial of service (toward third parties)
- **Steps:** instrument HTTP calls; run the pipeline over a multi-page fixture.
- **Expected:** the configured interval is observed between requests to the same source.
- **Verification:** Automated · **Priority:** High
- **Maps to:** FR-B-13, LEG-07

### SEC-42 — The identifiable User-Agent is actually sent
- **Threat:** Repudiation / good citizenship toward sources
- **Steps:** inspect outbound headers in a fixture run.
- **Expected:** a `User-Agent` containing contact information, not a library default.
- **Verification:** Automated · **Priority:** Medium
- **Maps to:** FR-B-14, LEG-07

---

## F. Transport, headers, and rate limiting

### SEC-43 — Security headers on every response
- **Threat:** Tampering / Information disclosure
- **Steps:** request public pages and API endpoints, including error responses.
- **Expected:** CSP without `unsafe-inline` for scripts, `Strict-Transport-Security`,
  `X-Content-Type-Options: nosniff`, and a `Referrer-Policy`. Error responses are included:
  a 500 page with no headers is a common miss.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** NFR-07, SEC-15

### SEC-44 — CORS is restricted to our own origins
- **Threat:** Tampering
- **Steps:** send requests with a foreign `Origin`, and with `null`.
- **Expected:** rejected. A wildcard is a failure.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** NFR-08

### SEC-45 — Public API rate limiting
- **Threat:** Denial of service
- **Steps:** exceed the per-IP limit on a read endpoint and on the submission endpoint.
- **Expected:** 429 after the threshold, with `Retry-After`.
- **Verification:** Automated · **Priority:** High
- **Maps to:** NFR-17, FR-F-16

### SEC-46 — Secrets are absent from the repository
- **Threat:** Information disclosure
- **Steps:** run a secret scanner over the tree and over history; assert `.env` is ignored.
- **Expected:** no secrets. Django settings must fail loudly if a required environment
  variable is absent rather than defaulting.
- **Verification:** Automated (CI) · **Priority:** Critical
- **Maps to:** NFR-09, FR-E-11

### SEC-47 — Public API exposes published content only
- **Threat:** Information disclosure / Repudiation
- **Steps:** create `pending` and `rejected` records; request every list and detail
  endpoint; request an unpublished edition's URL directly.
- **Expected:** none appear, and unpublished editions 404. A leaked `pending` record
  publishes unreviewed content.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** FR-A-06, FR-A-10, LEG-01

---

## G. Internationalisation (ADR 0010)

### SEC-48 — A missing English key fails the build
- **Threat:** Information disclosure (mixed-language rendering)
- **Steps:** 1. Remove a key from the English catalogue. 2. Run the i18n check.
- **Expected:** the build fails. Additionally, assert no page renders raw interpolation
  keys such as `{{...}}` in either locale, and that `<html lang>` matches the URL prefix.
- **Verification:** Automated · **Priority:** High
- **Maps to:** FR-H-02, FR-H-10

### SEC-49 — No cross-locale cache poisoning
- **Threat:** Information disclosure
- **Steps:** request `/es/event` and `/en/event` for the same object; assert the `Vary`
  header and `Cache-Control` differ correctly.
- **Expected:** no locale serves another's cached content. Translated slugs resolve only
  within their own locale.
- **Verification:** Automated · **Priority:** Medium
- **Maps to:** FR-H-03, PRV-09

---

## H. Database, audit internals, and notifications (SEC-50 … SEC-72)

These cases close the threats in `docs/02-diseno/modelo-amenazas.md` §4 that the sections
above did not cover. Most are lower likelihood than the upload and authorization cases,
which is why they sit at the end rather than being scattered.

### SEC-50 — Audit rows cannot be updated or deleted
- **Threat:** Repudiation / Tampering
- **Steps:** 1. As `admin`, attempt `UPDATE` and `DELETE` on `audit_logs` via the ORM, the
  admin, and raw SQL on a test database. 2. Attempt `TRUNCATE`.
- **Expected:** all rejected. Database-level protection is required, not just application
  permissions — an application-only check fails against a direct connection.
- **Verification:** Automated · **Priority:** Critical
- **Protects:** `audit_logs` · **Maps to:** T-50, FR-D-09

### SEC-51 — Request correlation propagates end to end
- **Threat:** Repudiation
- **Steps:** 1. Make a request that triggers several audit writes (e.g. a bulk approval).
  2. Assert every resulting row shares one `request_id`.
- **Expected:** one correlation id per request, across all rows it produced. Without this,
  reconstructing an incident from the log requires guessing.
- **Verification:** Automated · **Priority:** Medium
- **Maps to:** T-51

### SEC-52 — No secrets or raw PII in audit `changes`
- **Threat:** Information disclosure
- **Steps:** 1. Change every `site_settings` key. 2. Attempt to set a key whose value looks
  like a secret. 3. Scan all `changes` payloads.
- **Expected:** before/after values recorded, but secret-shaped values redacted; no raw IP,
  no password hash, no token. `site_settings` must refuse secrets outright (FR-E-11).
- **Verification:** Automated · **Priority:** High
- **Maps to:** T-52, PRV-01

### SEC-53 — Audit retention is bounded and documented
- **Threat:** Denial of service (storage)
- **Steps:** verify a retention policy exists and is applied; assert older rows are pruned by
  an operational job, never by a cascade from a parent table.
- **Expected:** `audit_logs` cannot be emptied by deleting related content. Retention is a
  **decision to record**, not a default — see SRS §9.
- **Verification:** Manual + Automated · **Priority:** Low
- **Maps to:** T-53

### SEC-54 — Audit fields are not attacker-controlled
- **Threat:** Elevation of privilege
- **Steps:** 1. Attempt to write `audit_logs` rows directly through any input path. 2.
  Submit text containing newlines and control characters in a moderated field.
- **Expected:** rows are written only by application code. Stored text is escaped, so
  injected content cannot forge a log line or break downstream parsers.
- **Verification:** Automated · **Priority:** Medium
- **Maps to:** T-54

### SEC-55 — Database credentials are absent from the repository and least-privileged
- **Threat:** Information disclosure / Elevation of privilege
- **Steps:** 1. Secret-scan the tree and history. 2. Inspect the production DB role's grants.
- **Expected:** no credentials in git; the application role can do its work and **not**
  create roles, alter schema, or read another environment's database. Django settings must
  fail loudly when a required variable is absent rather than defaulting.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** T-55, NFR-09

### SEC-56 — Schema changes are reviewed and migrations are non-destructive
- **Threat:** Tampering
- **Steps:** 1. Assert `makemigrations --check` passes in CI. 2. Review that no migration
  drops or rewrites a populated column without a documented plan.
- **Expected:** model and migration drift fails the build; destructive migrations require a
  documented rollback path.
- **Verification:** Automated + Manual review · **Priority:** High
- **Maps to:** T-56, NFR-13

### SEC-57 — Bulk operations generate individual audit entries
- **Threat:** Repudiation
- **Steps:** bulk-approve 10 records; count `moderation_actions` and `audit_logs` rows.
- **Expected:** 10 entries each, one per object. A single "bulk approve" row would make it
  impossible to tell what was approved.
- **Verification:** Automated · **Priority:** High
- **Maps to:** T-57, FR-C-11

### SEC-58 — No SQL injection
- **Threat:** Information disclosure / Elevation of privilege
- **Steps:** attempt injection through search, filters, sort/order parameters, and slug
  lookup on the public API and in the admin.
- **Expected:** the ORM parameterizes; no raw SQL built from untrusted input; sort fields
  resolved through an allowlist rather than interpolated.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** T-58

### SEC-59 — Database connection pool stays within free-tier limits
- **Threat:** Denial of service
- **Steps:** inspect pool configuration against the provider's connection allowance.
- **Expected:** pool and worker counts are set so the app cannot exhaust the limit and lock
  itself out. Relevant because the zero-cost constraint rules out a large instance.
- **Verification:** Manual · **Priority:** Medium
- **Maps to:** T-59, NFR-05

### SEC-60 — The application database role has least privilege
- **Threat:** Elevation of privilege
- **Steps:** attempt `CREATE ROLE`, `ALTER`, and cross-database reads as the app role.
- **Expected:** all denied. Superuser ownership is never used by the application.
- **Verification:** Manual · **Priority:** High
- **Maps to:** T-60

### SEC-61 — TLS verification is enforced on outbound fetches
- **Threat:** Spoofing
- **Steps:** run a fetch against a server presenting an invalid certificate.
- **Expected:** the fetch fails. Verification must not be disabled to "make the scraper
  work" — that is a silent downgrade of source authenticity.
- **Verification:** Automated · **Priority:** High
- **Maps to:** T-61

### SEC-62 — Untrusted source content can never auto-publish
- **Threat:** Tampering
- **Preconditions:** a fixture whose payload contains injected instructions or unexpected
  markup.
- **Steps:** run the pipeline; attempt to enable an auto-publish rule; run again.
- **Expected:** everything enters as `pending`. Transform validation is strict about shape.
  Auto-publish is off by default (FR-C-08) and, if ever enabled, still excludes
  `origin = community` and anything with unknown rights.
- **Verification:** Automated · **Priority:** Critical
- **Maps to:** T-62, FR-C-02, FR-C-08

### SEC-63 — Fetch provenance is complete and identifiable
- **Threat:** Repudiation
- **Steps:** inspect `raw_documents` and `scrape_sources` after a run.
- **Expected:** exact URL, HTTP status, content type, byte size, hash, fetch timestamp, and
  an identifiable `User-Agent` are all recorded. Provenance must be reconstructable without
  logs.
- **Verification:** Automated · **Priority:** Medium
- **Maps to:** T-63

### SEC-64 — Redirects cannot reach unintended hosts
- **Threat:** Information disclosure
- **Steps:** 1. Serve a fixture that redirects to an unlisted host. 2. Redirect to a
  private IP range (169.254.169.254, 10.0.0.0/8, localhost).
- **Expected:** rejected. This is the SSRF guardrail: an admin-editable URL is still
  user-influenced input, and a redirect or a link can point anywhere.
- **Verification:** Automated · **Priority:** High
- **Maps to:** T-64, T-66

### SEC-65 — Rate limits and robots compliance are configured and honoured
- **Threat:** Denial of service (toward third parties)
- **Steps:** assert `robots.txt` has been reviewed and its outcome recorded per source;
  instrument a multi-page fixture run.
- **Expected:** disallowed paths are not fetched, and the configured interval is observed.
  Terms-of-use status is recorded even when unknown — an unreviewed source is a known risk,
  not a resolved one.
- **Verification:** Automated + Manual · **Priority:** High
- **Maps to:** T-65, LEG-07, FR-B-13

### SEC-66 — No fetch target reaches private network ranges
- **Threat:** Elevation of privilege (SSRF)
- **Steps:** configure `scrape_sources` entries pointing at internal addresses; attempt
  redirects into them (overlap with SEC-64).
- **Expected:** blocked at the HTTP client and again at validation. Only `admin` may create
  a source, but admin is a human who can be tricked.
- **Verification:** Automated · **Priority:** High
- **Maps to:** T-66

### SEC-67 — Notification sending is authenticated
- **Threat:** Spoofing
- **Steps:** inspect the mail transport configuration and the `From`/`Reply-To` headers.
- **Expected:** authenticated sending (provider with DKIM/SPF, or SMTP with credentials).
  **Currently undecided** — notifications are operational alerts, and no public feature
  depends on them, so this is recorded as an open item rather than an implemented control.
- **Verification:** Manual · **Priority:** Low
- **Maps to:** T-67, SRS §9

### SEC-68 — Untrusted content cannot enter notification bodies
- **Threat:** Tampering
- **Steps:** submit content containing HTML and template syntax; trigger an alert.
- **Expected:** notifications are system-generated and templated; user content is escaped or
  referenced by id, never interpolated as markup.
- **Verification:** Automated · **Priority:** Medium
- **Maps to:** T-68

### SEC-69 — Notification outcomes are logged
- **Threat:** Repudiation
- **Steps:** trigger an alert; inspect `audit_logs` for `actor_kind = system`.
- **Expected:** send, failure, and retry are recorded with a correlation id, so a silent
  alert failure is detectable.
- **Verification:** Automated · **Priority:** Medium
- **Maps to:** T-69

### SEC-70 — Notifications minimise PII
- **Threat:** Information disclosure
- **Steps:** inspect notification content for the takedown and submission flows.
- **Expected:** references (`public_token`, object ids) rather than raw email addresses,
  except where a reply is the point of the message.
- **Verification:** Manual · **Priority:** Medium
- **Maps to:** T-70, PRV-03

### SEC-71 — Notification failure degrades safely
- **Threat:** Denial of service
- **Steps:** make the mail provider unavailable; exercise public read and moderation.
- **Expected:** public read and the admin queue are unaffected. Notifications are alerts, not
  a dependency of the product.
- **Verification:** Automated · **Priority:** Low
- **Maps to:** T-71

### SEC-72 — No public endpoint triggers bulk notifications
- **Threat:** Elevation of privilege / Abuse
- **Steps:** enumerate endpoints reachable without a session; attempt repeated calls.
- **Expected:** none triggers email. Only system or `admin` actions do, and they are
  rate-limited.
- **Verification:** Automated · **Priority:** Medium
- **Maps to:** T-72

### SEC-73 — Takedown state machine cannot be short-circuited
- **Threat:** Repudiation / Information disclosure
- **Preconditions:** a `takedown_requests` row.
- **Steps:** 1. Walk each legal transition in `received → in_review → actioned | rejected |
  escalated`. 2. Attempt each illegal one: `received → actioned`, `rejected → actioned`,
  `escalated → rejected`. 3. On an `illegal_content` claim, attempt to close it with an
  internal note and no external action.
- **Expected:** illegal transitions are refused. `escalated` is terminal — an
  `illegal_content` claim **cannot** be closed by an internal note alone, because brief §10
  requires reporting to the authorities or a line such as Te Protejo, and an internal note
  is not that (FR-G-05). Closing a claim requires `action_taken` and sets `responded_at`.
- **Verification:** Automated · **Priority:** Critical
- **Protects:** `takedown_requests` · **Maps to:** FR-G-04 … FR-G-06, brief §10

### SEC-74 — Database translation fallback never yields an empty page
- **Threat:** Information disclosure (mixed-language or blank rendering)
- **Preconditions:** a record with `*_es` set and `*_en` **NULL** (the normal untranslated
  state under ADR 0012).
- **Steps:** 1. Request it in `/en/…`. 2. Request it in `/es/…`. 3. Attempt to create a
  record with `*_es` NULL.
- **Expected:** `en` falls back to the `*_es` source locale rather than rendering empty or
  leaking a raw key (FR-H-06). Fallback is visible, not silent-broken. The admin remains
  Spanish-only regardless of the site's locale. **Step 3 must fail** — `*_es` is `NOT NULL`
  (ADR 0012), so a record with no source-locale text cannot exist; assert the constraint,
  not the application's tolerance for it. There is no `es` ← `en` path: a missing source is
  a data bug that must surface.
- **Verification:** Automated · **Priority:** High
- **Protects:** `*_es` / `*_en` columns on the editorial tables · **Maps to:** FR-H-06, FR-H-08, ADR 0010, **ADR 0012**

---

## Coverage audit

Every threat in `docs/02-diseno/modelo-amenazas.md` (T-01 … T-72) now has at least one
executable case, and every data-model asset has at least one case.

| Data-model asset | Cases |
|---|---|
| `auth_user`, `auth_group` | SEC-01, 04, 05, 12, 13 |
| `django_session` | SEC-02, 03, 10, 11 |
| `otp_totpdevice` | SEC-04, 05, 06 |
| `audit_logs` | SEC-16, 17, 18, 32, 50, 51, 52, 54 |
| `moderation_actions` | SEC-17, 30, 31, 57 |
| `media_assets` | SEC-30, 31, 34 |
| `news_items` | SEC-34 |
| `raw_documents`, `ingestion_runs` | SEC-37 … SEC-42, 62, 63 |
| `scrape_sources` | SEC-39, 41, 42, 61, 64, 65, 66 |
| `submissions`, `submission_files` | SEC-19 … SEC-24, 36 |
| `consent_records`, `legal_documents` | SEC-28, 29, 32, 73 |
| `takedown_requests` | SEC-32, 33, 73 |
| Translation columns (`*_es` / `*_en`) on editorial tables | SEC-48, 49, 74 |
| `site_settings` | SEC-46, 52 |
| PostgreSQL (roles, schema, pool) | SEC-55, 56, 58, 59, 60 |
| Email / notification path | SEC-67 … SEC-72 |

**Previously recorded gaps, now closed:** the takedown state machine and the
`illegal_content` escalation rule (SEC-73), and the database translation fallback
(SEC-74).

**Remaining gaps, recorded rather than papered over:**

- **SEC-25** (bucket separation) is the one case that cannot be fully automated — it needs
  a manual check that the two buckets are separately addressed and that no read path spans
  them. Treat it as a release checklist item.
- **Audit retention** (SEC-53) and **notification transport** (SEC-67) depend on decisions
  still marked undecided in SRS §9; their cases are written but cannot pass until the
  decision is made.
- **No case covers availability of the free-tier dependencies themselves** (database
  provider, storage provider, CAPTCHA). Those are not code and cannot be tested from here;
  they are recorded as residual risk in the threat model.