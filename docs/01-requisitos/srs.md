# Software Requirements Specification (SRS)

- **Project:** Carnaval de Negros y Blancos
- **Version:** 0.1 (draft for review)
- **Date:** 2026-10-03
- **Status:** Draft. Supersedes nothing; subordinate to nothing except the brief's constraints.
- **Relates to:** `docs/00-acta-proyecto.md` (charter, stakeholders, success criteria),
  `docs/00-contexto-proyecto.md` (brief), ADR 0001–0011,
  `docs/02-diseno/modelo-datos.md` (authoritative data model)
- **Traceability:** every requirement here must gain a row in
  `docs/01-requisitos/matriz-trazabilidad.md` and at least one verification method.

## 1. Introduction

### 1.1 Purpose

This SRS specifies the requirements for the Carnaval de Negros y Blancos platform: an
ingestion pipeline that collects the parade programme from public sources, a PostgreSQL
database that is the source of truth, a public read-only API, a public React site, and a
Django admin console for moderation, configuration, and audit.

It exists to make the work verifiable. Per ADR 0001 the Definition of Done requires every
requirement to be linked in the traceability matrix, so this document is the anchor for
that obligation rather than a descriptive document.

### 1.2 Intended readers

The sole maintainer (developer and product owner), and any reviewer assessing whether the
engineering process is real. Reviewers may assume nothing about the brief beyond what is
written here.

### 1.3 Definitions

Terms follow the brief §21 glossary: **ingestion**, **staging**, **quarantine**,
**idempotence**, **edition**, **RBAC**, **EXIF**, **takedown**, **ADR**, **MoSCoW**.

Additional definitions used here:

| Term | Meaning |
|---|---|
| **Edition** | One year of the parade |
| **Published** | A record a human has approved for public display |
| **Origin** | How a record came to exist: `scraped`, `manual`, `community` |
| **Quarantine** | Private object storage where visitor uploads wait for review |
| **Source locale** | `es`; all translation keys originate in Spanish (ADR 0010) |

### 1.4 Priority scheme

MoSCoW, applied **per version** (ADR 0008):

- **Must** — the version cannot ship without it.
- **Should** — ship it unless something forces a trade; a deliberate omission is recorded.
- **Could** — only if the sprint has room.
- **Won't** — explicitly out of that version. Binding, not aspirational.

## 2. Overall description

### 2.1 Product perspective

The system is a single deployable website with two surfaces: a **public read-only React
site** (plus anonymous submissions from v3) and an **authenticated Django admin console**
for the single moderator. There are no public user accounts and no transactional features.

The defining property: **the database is the source of truth and the scraper is optional.**
If every external source disappears tomorrow, the site keeps serving and the moderator can
still author content by hand (ADR 0002).

### 2.2 User classes

| Class | Authentication | Capabilities |
|---|---|---|
| **Visitor** | None | Browse published content in `es`/`en` |
| **Contributor** | None | Submit an image or video link with consent (v3); check submission status |
| **Viewer** | Django session + role | Read-only across admin and data; cannot change moderation state |
| **Editor** | Django session + role + TOTP | Approve, reject, unpublish content; respond to takedowns |
| **Administrator** | Django session + role + TOTP | Everything Editor can do, plus configuration, users, legal versions, ingestion runs |

### 2.3 Operating environment

- Python 3.12 + Django 5 + DRF on a free-tier application host; PostgreSQL 16 on a free
  tier; object storage with separate quarantine and public buckets; GitHub Actions `cron`
  for scheduled ingestion. No resident worker (ADR 0009).
- React + TypeScript SPA, static assets.
- **Hard constraint: zero monetary cost** (acta §6 C1). Free-tier limits change frequently
  and must be re-verified before each release.

### 2.4 Constraints

Carried from the acta §6: zero cost; one part-time developer; unstable external sources;
third-party copyright; changing free-tier limits; no implied affiliation with
Corpocarnaval.

### 2.5 Assumptions

- The official site `carnavaldepasto.org` remains reachable; if not, the admin's manual
  entry path keeps the product usable.
- The programme is republished roughly yearly; the January edition changes on a schedule
  that is not under the project's control.
- A WordPress REST API may be available at `/wp-json/wp/v2/`. **Unverified** — the first
  sprint is a spike to confirm (brief §5, §20).
- No commercial interest in the data; the project is a portfolio piece.

## 3. Functional requirements

### 3.1 FR-A — Catalogue and browsing (MVP)

| ID | Requirement | Priority | Version |
|---|---|---|---|
| FR-A-01 | The system shall store parade **editions**, each identified by year, with a slug and a publication flag. | Must | MVP |
| FR-A-02 | Each edition shall contain **days**, stored as rows rather than a fixed enumeration, because day names vary by year. | Must | MVP |
| FR-A-03 | Each day shall contain **events** with an optional venue, optional start/end times, and a display name. | Must | MVP |
| FR-A-04 | The canonical January milestones shall be representable without code changes: 2 Jan Carnavalito, 3 Jan choreographic collectives, 4 Jan Desfile Familia Castañeda, 5 Jan Day of Blacks, 6 Jan Day of Whites / Gran Parade. | Must | MVP |
| FR-A-05 | The system shall store **venues** with name, optional address, city, and optional coordinates. | Should | MVP |
| FR-A-06 | The public API shall return **only** records with `status = published`. | Must | MVP |
| FR-A-07 | The public API shall expose editions, days, events, and venues as read-only endpoints. | Must | MVP |
| FR-A-08 | The public site shall render the programme grouped by day, in chronological order. | Must | MVP |
| FR-A-09 | The public site shall display an unofficial / not-affiliated disclaimer on every page. | Must | MVP |
| FR-A-10 | An edition shall be publishable or withheld as a unit, so a future edition can be prepared without appearing publicly. | Should | MVP |
| FR-A-11 | The public API shall support filtering by edition and by date range. | Should | MVP |
| FR-A-12 | The public site shall provide a link to the source of any programme entry it displays. | Must | MVP |
| FR-A-13 | The public site shall be responsive and usable on a 360 px-wide viewport. | Must | MVP |

### 3.2 FR-B — Ingestion pipeline (MVP)

| ID | Requirement | Priority | Version |
|---|---|---|---|
| FR-B-01 | The system shall implement the stages `EXTRACT → RAW STORE → TRANSFORM → STAGING → review → LOAD`. | Must | MVP |
| FR-B-02 | Each successful fetch shall store the raw payload in object storage together with its SHA-256 `content_hash`. | Must | MVP |
| FR-B-03 | `raw_documents.content_hash` shall be unique, and a fetch whose hash already exists shall be recorded as a no-op rather than reprocessed. | Must | MVP |
| FR-B-04 | The pipeline shall be **idempotent**: two consecutive runs shall produce zero duplicates. | Must | MVP |
| FR-B-05 | Transformed records shall be schema-validated before entering staging; invalid records shall be rejected with a recorded reason. | Must | MVP |
| FR-B-06 | Every record produced by the pipeline shall enter as `status = pending` with `origin = scraped` and a reference to its `ingestion_run`. | Must | MVP |
| FR-B-07 | Publishing after review shall be an **upsert**, so re-processing a corrected record updates rather than duplicates it. | Must | MVP |
| FR-B-08 | The system shall record an `ingestion_runs` row per execution with trigger, status, timings, and per-stage statistics. | Must | MVP |
| FR-B-09 | A failed run shall never modify or delete any record with `status = published`. | Must | MVP |
| FR-B-10 | The pipeline shall retry with exponential backoff, and after N consecutive failures shall disable the affected `scrape_source` and raise an alert. | Must | MVP |
| FR-B-11 | An extraction that yields **zero** records from a source that previously yielded records shall raise an alarm and shall **not** be treated as success. | Must | MVP |
| FR-B-12 | `scrape_sources` shall be admin-configurable with URL, type, active flag, rate-limit interval, and cron schedule. | Must | MVP |
| FR-B-13 | Fetches shall respect a configurable per-source minimum interval between requests. | Must | MVP |
| FR-B-14 | Fetches shall send an identifiable `User-Agent` containing contact information. | Must | MVP |
| FR-B-15 | The pipeline shall prefer the WordPress REST API over HTML parsing where available. | Should | MVP |
| FR-B-16 | Raw payloads shall be retained under a per-source retention limit and pruned beyond it, to bound free-tier storage. | Should | MVP |
| FR-B-17 | The pipeline shall be invocable as a Django management command from GitHub Actions `cron`. | Must | MVP |
| FR-B-18 | The pipeline shall be invocable manually by an Editor or Administrator for a single source. | Should | MVP |
| FR-B-19 | The system shall never commit raw third-party payloads to the repository. | Must | MVP |

### 3.3 FR-C — Moderation and review (v1)

| ID | Requirement | Priority | Version |
|---|---|---|---|
| FR-C-01 | Every content record shall carry `status`, `origin`, `reviewed_by`, `reviewed_at`, and `rejection_reason`. | Must | v1 |
| FR-C-02 | No record shall reach `published` without a recorded human decision. | Must | v1 |
| FR-C-03 | An `editor` shall be able to approve a pending record. | Must | v1 |
| FR-C-04 | An `editor` shall be able to reject a pending record, and a rejection shall require a non-empty `rejection_reason`. | Must | v1 |
| FR-C-05 | An `editor` shall be able to move a published record back to `pending` (unpublish), as a deliberate manual action. | Must | v1 |
| FR-C-06 | The review queue shall be filterable by `status`, `origin`, and content type. | Must | v1 |
| FR-C-07 | Every approval, rejection, and unpublish shall append a `moderation_actions` row. | Must | v1 |
| FR-C-08 | Auto-publish rules shall be configurable by an Administrator but **disabled by default**. | Could | v1 |
| FR-C-09 | The queue shall surface the source URL and the raw payload for each pending scraped record, so the reviewer can verify extraction. | Must | v1 |
| FR-C-10 | Rejected uploads shall be deleted or retained per a configurable retention policy, and the outcome shall be recorded. | Must | v3 |
| FR-C-11 | The system shall support bulk approval, recording each decision individually in `moderation_actions`. | Should | v1 |

### 3.4 FR-D — Administration, roles, and audit (v1)

| ID | Requirement | Priority | Version |
|---|---|---|---|
| FR-D-01 | The system shall expose an administration console implemented as Django admin. | Must | v1 |
| FR-D-02 | Roles shall be implemented as Django auth groups: `admin`, `editor`, `viewer`. | Must | v1 |
| FR-D-03 | Django admin shall be effectively unusable until roles are configured — the shipped console must not expose unreviewed `pending` content by default. | Must | v1 |
| FR-D-04 | Authorization shall be enforced server-side on every request; hiding a control in the interface shall never be the enforcement mechanism. | Must | v1 |
| FR-D-05 | A `viewer` shall never transition moderation state. | Must | v1 |
| FR-D-06 | An `editor` shall not change site configuration, manage users, or edit legal documents. | Must | v1 |
| FR-D-07 | Only `admin` shall manage users, roles, site settings, scrape sources, and legal document versions. | Must | v1 |
| FR-D-08 | The system shall maintain an append-only `audit_logs` table recording actor, action, object, timestamp, before/after changes, hashed IP, and a request correlation ID. | Must | v1 |
| FR-D-09 | No role shall be able to update or delete an `audit_logs` row, including `admin`. | Must | v1 |
| FR-D-10 | Successful and failed login attempts shall both be written to `audit_logs`. | Must | v1 |
| FR-D-11 | The system shall expose a `/health` endpoint reporting application and database reachability. | Must | MVP |
| FR-D-12 | The admin shall display each scrape source's active flag, consecutive failures, and last successful run. | Must | v1 |
| FR-D-13 | There shall be no public signup path for any account. | Must | v1 |
| FR-D-14 | The first administrator shall be created by a documented seed management command, never through the API. | Must | v1 |
| FR-D-15 | Administrative sessions shall expire 12 hours after the last request (idle) and 72 hours after authentication regardless of activity (absolute), and shall end when the browser closes. | Must | v1 |
| FR-D-16 | Publishing content, changing roles or group membership, editing `site_settings`, and creating or superseding a `legal_documents` version shall each require re-entering the password and TOTP code, even within an active session. | Must | v1 |

### 3.5 FR-E — Editorial content (v2)

| ID | Requirement | Priority | Version |
|---|---|---|---|
| FR-E-01 | The system shall store `news_items` with headline, source URL, outlet, publication date, and a short **original** summary. | Must | v2 |
| FR-E-02 | The system shall **not** store or serve full article text or article images. | Must | v2 |
| FR-E-03 | News shall be sourced into `pending` and require review like any other content. | Must | v2 |
| FR-E-04 | The system shall store `media_assets` with file, approximate year, description, author, source, licence, citation text, and rights status. | Must | v2 |
| FR-E-05 | A `media_assets` record shall not reach `published` unless `author`, `source_ref`, `citation_text` are present and `rights_status != unknown`. | Must | v2 |
| FR-E-06 | The gallery shall display the citation text alongside each image. | Must | v2 |
| FR-E-07 | The system shall detect duplicate images by content hash and refuse re-publication of identical bytes. | Must | v2 |
| FR-E-08 | Exif-stripping shall be verified at approval time, not only at upload time. | Must | v2 |
| FR-E-09 | An editor shall be able to feature an approved asset in the gallery. | Should | v2 |
| FR-E-10 | The system shall store `site_settings` as typed key/value configuration, editable by an Administrator. | Must | v2 |
| FR-E-11 | Secrets shall never be stored in `site_settings`. | Must | v2 |
| FR-E-12 | Every `site_settings` change shall be written to `audit_logs` with before/after values. | Must | v2 |

### 3.6 FR-F — Public submissions (v3)

| ID | Requirement | Priority | Version |
|---|---|---|---|
| FR-F-01 | A visitor shall submit an image without registering. | Must | v3 |
| FR-F-02 | A visitor shall submit a video **link** (YouTube or Vimeo) without registering; the system shall never accept a video file. | Must | v3 |
| FR-F-03 | Uploads shall be validated by **magic bytes** against a JPEG/PNG/WebP allowlist, never by file extension. | Must | v3 |
| FR-F-04 | A file whose detected type does not match its declared type shall be rejected. | Must | v3 |
| FR-F-05 | Every upload shall be fully decoded and re-encoded before storage, stripping embedded payloads. | Must | v3 |
| FR-F-06 | Every upload shall have EXIF metadata, including GPS, removed before storage. | Must | v3 |
| FR-F-07 | Uploads shall be written to **quarantine** storage and shall not be publicly readable before approval. | Must | v3 |
| FR-F-08 | Public object storage shall be a separate bucket on a separate domain from the application. | Must | v3 |
| FR-F-09 | On approval, the file shall move from quarantine to public storage and an approved `media_assets` record shall be created. | Must | v3 |
| FR-F-10 | The terms-acceptance checkbox shall be **unchecked by default** and blocking. | Must | v3 |
| FR-F-11 | The system shall record a `consent_records` row binding the submission to the exact `legal_documents` version accepted. | Must | v3 |
| FR-F-12 | The system shall store a **salted hash** of the submitter's IP address, never the raw address. | Must | v3 |
| FR-F-13 | The submission form shall collect a rights declaration (author or permission) plus author, year, place, and description. | Must | v3 |
| FR-F-14 | The submission form shall collect a declaration regarding consent from identifiable individuals. | Must | v3 |
| FR-F-15 | An asset flagged `minor_subject = true` shall not be published without `guardian_consent_on_file = true`. | Must | v3 |
| FR-F-16 | The system shall enforce per-IP submission counts, size limits, and a global daily pending quota. | Must | v3 |
| FR-F-17 | The system shall use a CAPTCHA plus a honeypot field to deter automated submissions. | Must | v3 |
| FR-F-18 | The contributor shall be able to check submission status via an unguessable token. | Should | v3 |
| FR-F-19 | Video links shall be normalised to a provider and video id; the submitted URL shall never be used directly as an embed source. | Must | v3 |
| FR-F-20 | Public responses for stored assets shall include `X-Content-Type-Options: nosniff` and an explicit `Content-Disposition`. | Must | v3 |
| FR-F-21 | The system shall detect duplicate submissions by content hash and flag them for the reviewer. | Must | v3 |
| FR-F-22 | Submissions shall follow the same moderation path as all other content, entering as `pending`. | Must | v3 |

### 3.7 FR-G — Legal and takedown (v3)

| ID | Requirement | Priority | Version |
|---|---|---|---|
| FR-G-01 | `legal_documents` shall be versioned with one current version per type and locale. | Must | v3 |
| FR-G-02 | A published legal document shall never be edited in place; a change creates a new version. | Must | v3 |
| FR-G-03 | The site shall publish a takedown channel with a contact address placeholder. | Must | v3 |
| FR-G-04 | The system shall record takedown requests with claim type `copyright`, `privacy`, `illegal_content`, or `other`. | Must | v3 |
| FR-G-05 | A claim of `illegal_content` shall set the request to `escalated` and shall not be closed by an internal note alone. | Must | v3 |
| FR-G-06 | The system shall record `action_taken` and `responded_at` for every takedown request. | Must | v3 |
| FR-G-07 | For embedded video, takedown shall mean removing the reference and contacting the provider. | Must | v3 |
| FR-G-08 | The site shall state that it is unofficial and not affiliated with or endorsed by Corpocarnaval. | Must | v3 |

### 3.8 FR-H — Internationalisation (MVP)

| ID | Requirement | Priority | Version |
|---|---|---|---|
| FR-H-01 | The public site shall ship in exactly two locales: `es` (source) and `en`. | Must | MVP |
| FR-H-02 | Every user-facing string shall exist in both locales at release; a missing key shall fail the build. | Must | MVP |
| FR-H-03 | URLs shall be locale-prefixed (`/es/…`, `/en/…`) so content is linkable and cacheable per locale. | Must | MVP |
| FR-H-04 | The unprefixed root shall redirect to the negotiated locale, defaulting to `es`. | Must | MVP |
| FR-H-05 | The locale choice shall persist in a cookie and shall not require an account. | Must | MVP |
| FR-H-06 | Database content shall be translatable per locale, with fallback to the source locale rather than an empty page. | Should | MVP |
| FR-H-07 | Slugs shall be stored per locale so translated pages have translated URLs. | Should | v2 |
| FR-H-08 | The admin console shall be Spanish only. | Must | v1 |
| FR-H-09 | Citations, source URLs, and legal document bodies shall be reproduced verbatim, with a Spanish translation alongside when one exists. | Must | v2 |
| FR-H-10 | No runtime machine translation shall be used. | Must | MVP |

### 3.9 FR-I — Search and discovery (v2)

| ID | Requirement | Priority | Version |
|---|---|---|---|
| FR-I-01 | The public site shall provide full-text search across published events and news. | Should | v2 |
| FR-I-02 | Search shall be scoped to `status = published` only. | Must | v2 |
| FR-I-03 | Search shall be implemented with PostgreSQL full-text search; no external search service shall be introduced, to respect the zero-cost constraint. | Should | v2 |

## 4. Non-functional requirements

| ID | Requirement | Priority | Version |
|---|---|---|---|
| NFR-01 | Public pages shall achieve a Lighthouse performance score ≥ 90 on a mid-range mobile profile. | Should | MVP |
| NFR-02 | Public API read endpoints shall respond in under 300 ms at p95 with cached data. | Should | MVP |
| NFR-03 | The public site shall conform to WCAG 2.1 AA, verified with automated axe checks plus manual keyboard testing. | Must | MVP |
| NFR-04 | The site shall be operable at 360 px viewport width without horizontal scrolling. | Must | MVP |
| NFR-05 | The system shall operate at zero monetary cost on free tiers. | Must | MVP |
| NFR-06 | The public site shall remain available if every external source is unreachable. | Must | MVP |
| NFR-07 | All traffic shall be over HTTPS with HSTS and modern security headers (CSP, `X-Content-Type-Options`, `Referrer-Policy`). | Must | MVP |
| NFR-08 | CORS shall allow only the site's own origins. | Must | MVP |
| NFR-09 | Secrets shall be supplied only through environment variables and shall never appear in the repository. | Must | MVP |
| NFR-10 | Dependency scanning (Dependabot or equivalent) shall be enabled. | Should | MVP |
| NFR-11 | CI shall run, in order: lint → typecheck → migration check → tests → OpenAPI schema drift check. A failure at any stage blocks the pipeline. | Must | MVP |
| NFR-12 | The OpenAPI schema shall be regenerated in CI and the build shall fail if it differs from the committed copy. | Must | MVP |
| NFR-13 | Database migrations shall be reviewed in the pull request and shall not be applied destructively without a documented migration plan. | Must | MVP |
| NFR-14 | Every new source file shall pass `ruff` and `mypy` with no new errors. | Must | MVP |
| NFR-15 | Test coverage of the ingestion pipeline and the public API shall be ≥ 80 % line coverage. | Should | MVP |
| NFR-16 | No test shall contact a live external source; HTTP shall be mocked and fixtures replayed. | Must | MVP |
| NFR-17 | The public API shall be rate-limited per IP. | Must | MVP |
| NFR-18 | The public API shall be read-only for anonymous callers; no anonymous write endpoint shall exist other than submissions in v3. | Must | MVP |
| NFR-19 | Logs shall not contain secrets, raw IP addresses, or session identifiers. | Must | MVP |
| NFR-20 | The system shall support a documented backup and restore procedure for PostgreSQL. | Must | v1 |
| NFR-21 | The admin console shall be reachable only over HTTPS and shall never be indexed by search engines. | Must | v1 |

## 5. Security requirements

| ID | Requirement | Priority | Version |
|---|---|---|---|
| SEC-01 | Passwords shall be hashed with Argon2id. | Must | v1 |
| SEC-02 | Administrative sessions shall be stored server-side; the client cookie shall hold only a session key and shall be `httpOnly`, `Secure`, and `SameSite=Lax`. | Must | v1 |
| SEC-03 | **No bearer token shall ever be issued or stored in `localStorage` or any JavaScript-readable location.** This supersedes the brief's JWT plan (ADR 0005). | Must | v1 |
| SEC-04 | Every account in the `admin` role shall require TOTP as a second factor. | Must | v1 |
| SEC-05 | TOTP recovery codes shall be single-use and stored hashed. | Must | v1 |
| SEC-06 | Repeated failed logins shall trigger lockout with exponential backoff. | Must | v1 |
| SEC-07 | CSRF protection shall be enforced on every mutating request. | Must | v1 |
| SEC-08 | An administrator shall be able to revoke all sessions for an account centrally. | Must | v1 |
| SEC-09 | Authorization shall be checked at the object level, not only at the list level. | Must | v1 |
| SEC-10 | Privilege escalation shall be impossible: no role shall reach capabilities outside its matrix, and object ownership shall be checked on every access. | Must | v1 |
| SEC-11 | Uploads shall be validated by content inspection, re-encoded, and stripped of metadata before storage. | Must | v3 |
| SEC-12 | Quarantine storage shall be non-public and shall be reachable only via short-lived signed URLs issued to the reviewing administrator. | Must | v3 |
| SEC-13 | Uploads shall be transferred by direct signed URL, not through the application process. | Must | v3 |
| SEC-14 | Automated submissions shall be deterred by CAPTCHA, honeypot, per-IP quotas, and a global daily pending quota. | Must | v3 |
| SEC-15 | Security headers shall include a Content Security Policy that does not require `unsafe-inline` for scripts. | Must | MVP |
| SEC-16 | Dependency vulnerabilities shall be surfaced by automated scanning, with a documented triage process. | Should | MVP |

## 6. Privacy requirements

| ID | Requirement | Priority | Version |
|---|---|---|---|
| PRV-01 | Raw IP addresses shall never be persisted in any table, log, or analytics record. | Must | v1 |
| PRV-02 | Any IP-derived value shall be a hash **salted with a server-side secret**, because an unsalted IPv4 hash is brute-forceable over a 2³² space. | Must | v3 |
| PRV-03 | Contributor email addresses shall be stored only where a reply is legally required, shall never be exposed by the public API, and shall carry a deletion deadline. | Must | v3 |
| PRV-04 | EXIF metadata shall be stripped unconditionally, including GPS coordinates. There shall be no configuration to retain it. | Must | v3 |
| PRV-05 | The system shall record the version of the legal text accepted by each contributor. | Must | v3 |
| PRV-06 | The system shall publish a privacy policy naming the categories of personal data processed, the purposes, and the retention periods. | Must | v3 |
| PRV-07 | The system shall honour data-subject access, rectification, and deletion requests through a documented procedure. | Must | v3 |
| PRV-08 | The system shall set no third-party advertising or tracking cookies. Embedded video players shall be consent-gated. | Must | v3 |
| PRV-09 | Public API responses shall set `Cache-Control` so that no response containing personal data is cached by shared caches. | Must | v3 |

## 7. Copyright and content-integrity requirements

| ID | Requirement | Priority | Version |
|---|---|---|---|
| LEG-01 | No content shall be published without a recorded human decision. | Must | MVP |
| LEG-02 | An image with `rights_status = unknown` shall never be published, by any code path including direct ORM writes and bulk operations. | Must | v2 |
| LEG-03 | Citation text shall be displayed alongside every published image. | Must | v2 |
| LEG-04 | News shall be stored as headline, link, outlet, date, and a short original summary; never as full text or article images. | Must | v2 |
| LEG-05 | No third-party PDF, photograph, or article text shall be committed to the repository. | Must | MVP |
| LEG-06 | The repository licence shall cover code only, and shall state that it does not cover scraped data or third-party content. | Must | MVP |
| LEG-07 | Scraping shall respect `robots.txt` and the source's terms of use, and shall use an identifiable User-Agent. | Must | MVP |
| LEG-08 | The site shall never imply affiliation with or endorsement by Corpocarnaval or any organiser. | Must | MVP |
| LEG-09 | Images in which a minor is the focal subject shall not be published without guardian authorisation. | Must | v2 |
| LEG-10 | Every published item shall reference its source, and the source shall be reproducible by a third party from the site alone. | Must | MVP |

## 8. Out of scope

Per brief §4 and ADR 0008, and binding per version: ticket sales or any transaction; public
user accounts; hosting video files; accepting arbitrary file types (executables, scripts,
documents); advertising; reproducing protected third-party content without permission;
native mobile applications; a React admin panel (ADR 0005).

## 9. Open questions

**All five are now closed.** Each records its own revisit trigger, so none of them is a
silent assumption; the trigger is the condition that would change the answer.

| # | Question | Resolution | ADR |
|---|---|---|---|
| 1 | `*_es`/`*_en` columns versus a generic `content_translations` table | Columns. `*_es` is `NOT NULL`, `*_en` nullable with one-directional fallback to `es`. `content_translations` deleted. Supersedes the storage bullet in ADR 0010. | **0012** |
| 2 | Idle and absolute session timeouts | 12 h idle, 72 h absolute, **plus step-up re-authentication (password + TOTP) before publish, role change, `site_settings` edit, or legal-document action** | **0013** |
| 3 | `raw_documents` retention window | 30 days **and** a per-source byte cap, with published content exempt for as long as the record exists | **0013** |
| 4 | Search implementation | `pg_trgm` + `unaccent`, re-evaluated above ~50k rows | **0013** |
| 5 | Whether `site_settings` needs a typed schema | No. Validation moves to typed Python accessors; revisit above ~100 settings or per-user scope | **0013** |

One further question raised by `modelo-datos.md` §10 was also closed:

- **Whether `days` are seeded per edition or created by the pipeline** — **seeded by the
  pipeline from the source** (`modelo-datos.md` §3.2). The original justification here was
  "because day names differ by year"; **the source spike disproved that** — the source reuses
  `2 de enero` on every edition, so labels are stable and only the calendar position moves.
  The decision stands for a different reason: derive the year from dated content, never from
  the label, and never carry one edition's days over to the next. See
  `fuentes-y-atribucion.md` §9.4. That document's other three questions are the same as SRS
  §9 Q1, Q3 and Q5 above.

**One question remains genuinely open**, and this document does not answer it:

- **Deployment providers** — hosting, database and object storage. The deciding criterion is
  network egress cost against the zero-cost constraint; see `despliegue.md` §3.

## 10. Requirement conventions

- IDs are stable. Never renumber; retire an ID and record the replacement.
- Every requirement needs at least one verification method in the traceability matrix:
  *test*, *inspection*, *demonstration*, or *analysis*.
- "Shall" is mandatory. "Should" is a strong recommendation whose omission must be
  recorded. "May" is optional.
- If a requirement conflicts with an ADR, the ADR wins and this document is corrected —
  the conflict is recorded in the traceability matrix, not silently resolved.