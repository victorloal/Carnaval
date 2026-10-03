# Data model

- **Status:** Draft for review
- **Date:** 2026-10-03
- **Relates to:** brief §8, ADR 0002 (database as source of truth), ADR 0006 (storage tiers),
  ADR 0010 (bilingual), ADR 0009 (Django + PostgreSQL)
- **Implementation:** Django ORM models; PostgreSQL 16

## 1. Conventions

- **Primary keys:** UUIDv4 (`django.db.models.UUIDField`). Public identifiers must not be
  guessable or enumerable, and submission links are shared with strangers.
- **Timestamps:** `created_at`, `updated_at` on every table that represents content.
- **Slugs:** per-locale, unique within their parent, used in public URLs.
- **Naming:** `snake_case` tables, Django field names in English, human-facing content in
  `_es` / `_en` suffixed columns.
- **Soft state, not soft delete:** nothing is hard-deleted except rejected uploads and
  expired sessions. Published content is never deleted by the pipeline (ADR 0002).

## 2. The moderation mixin

Four tables carry content subject to review: `events`, `news_items`, `media_assets`,
`submissions`. They all include:

| Field | Type | Meaning |
|---|---|---|
| `status` | enum | `pending` → `published` \| `rejected` |
| `origin` | enum | `scraped` \| `manual` \| `community` |
| `reviewed_by` | FK → `auth.User`, nullable | Who decided |
| `reviewed_at` | datetime, nullable | When |
| `rejection_reason` | text, nullable | Required when `status = rejected` |
| `ingestion_run` | FK → `ingestion_runs`, nullable | Set when `origin = scraped` |
| `created_by` | FK → `auth.User`, nullable | Set when `origin = manual` |

Invariants enforced by application code and by a `CHECK` constraint where possible:

- `status = 'rejected'` requires a non-empty `rejection_reason`.
- `origin = 'scraped'` requires `ingestion_run`; `origin = 'manual'` requires `created_by`.
- `origin = 'community'` requires neither — it must have an associated `submissions` row.
- Nothing transitions out of `published` automatically. Downgrading to `pending` is an
  explicit human action.

## 3. Programme and pipeline

### 3.1 `editions` — one row per year of the parade

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `year` | int, unique | 2026, 2027… |
| `slug` | slug, unique | URL segment |
| `title_es`, `title_en` | text | Display name |
| `starts_on`, `ends_on` | date | Typically 2–6 January |
| `is_published` | bool | Default `false` |
| `summary_es`, `summary_en` | text | Editorial introduction |

A parade edition is the aggregate root: days, events, and media all hang off it, so an
edition can be published or withheld as a unit.

### 3.2 `days`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `edition` | FK → `editions` | Indexed |
| `date` | date | |
| `slug` | slug | Unique per edition |
| `label_es`, `label_en` | text | e.g. "Día de Negros" / "Day of Blacks" |

The brief's §5 identifies the fixed January milestones: 2 Jan Carnavalito, 3 Jan
choreographic collectives, 4 Jan Desfile Familia Castañeda, **5 Jan Day of Blacks**,
**6 Jan Day of Whites / Gran Parade**. These are the canonical day names, but days are
**rows, not an enum** — the programme changes yearly and must not require a migration.

### 3.3 `venues`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `name_es`, `name_en` | text | |
| `address` | text, nullable | |
| `city` | text, nullable | |
| `latitude`, `longitude` | decimal, nullable | |
| `capacity` | int, nullable | Only if published by the source |

### 3.4 `events`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `day` | FK → `days` | Indexed |
| `venue` | FK → `venues`, nullable | Many events have no fixed venue |
| `starts_at`, `ends_at` | datetime, nullable | Null when the source gives only a time or neither |
| `title_es`, `title_en` | text | |
| `description_es`, `description_en` | text, nullable | **Own words only** — never copied prose from the source |
| `sort_order` | int | Preserves source ordering within a day |
| moderation mixin | | See §2 |

Indexes: `(day, sort_order)`, `(status)`.

### 3.5 `scrape_sources` — configured ingestion targets

Editable from Django admin. This is the circuit-breaker state.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `name` | text | Human label |
| `url` | URL | Target |
| `source_type` | enum | `wp_api` \| `html` \| `pdf` |
| `wp_object_type`, `wp_object_id` | text, nullable | For `wp_api`: which WP collection to walk |
| `selector_*` | jsonb | CSS selectors for `html` sources, per section |
| `is_active` | bool | Auto-disabled by the circuit breaker |
| `rate_limit_seconds` | int | Minimum delay between requests |
| `schedule_cron` | text | GitHub Actions cron expression |
| `consecutive_failures` | int | Breaker counter |
| `last_success_at`, `last_failure_at` | datetime, nullable | Shown in admin |
| `last_error` | text, nullable | |
| `user_agent` | text | Must be identifiable with contact info (brief §11) |

### 3.6 `raw_documents` — the RAW STORE

The idempotency mechanism. One row per successfully fetched payload.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `scrape_source` | FK → `scrape_sources` | Indexed |
| `url` | URL | Exact URL fetched |
| `http_status` | int | |
| `content_type` | text | |
| `content_hash` | char(64), unique | SHA-256 of the bytes. **Unique** is what makes re-runs idempotent |
| `byte_size` | int | |
| `storage_key` | text | Object-storage key for the raw payload; never committed to git |
| `fetched_at` | datetime | |

A fetch whose `content_hash` already exists is recorded as a no-op, not re-transformed.

### 3.7 `ingestion_runs`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `scrape_source` | FK → `scrape_sources`, nullable | Null for a manual admin run |
| `trigger` | enum | `cron` \| `manual` \| `admin` |
| `status` | enum | `running` \| `succeeded` \| `failed` \| `skipped` |
| `started_at`, `finished_at` | datetime | |
| `stats` | jsonb | `{extracted, inserted, updated, skipped, rejected}` |
| `error_message` | text, nullable | |

## 4. Editorial content

### 4.1 `news_items`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `source` | FK → `sources`, nullable | The outlet |
| `headline` | text | Verbatim headline is fine |
| `url` | URL | Canonical article link |
| `outlet` | text | Denormalised for display and citation |
| `published_on` | date, nullable | |
| `summary_es`, `summary_en` | text | **Short original summary only.** Never the article body or its images (brief §11) |
| moderation mixin | | |

### 4.2 `media_assets` — historical images

The highest-risk table in the schema. Every column before the moderation mixin exists to
make an image lawfully publishable.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `edition` | FK → `editions`, nullable | Which parade year it depicts |
| `file` | text | Public storage key. Absent while the asset is unapproved |
| `quarantine_file` | text, nullable | Private key; cleared on approval |
| `content_hash` | char(64), unique | Duplicate detection |
| `year_approx` | int, nullable | Approximate year depicted |
| `title_es`, `title_en` | text | |
| `description_es`, `description_en` | text | |
| `author` | text | **Photographer or archive.** Mandatory to publish |
| `source_ref` | text | Where the image came from: archive, family, own |
| `license` | text, nullable | e.g. CC BY 4.0, public domain, permission granted |
| `citation_text` | text | **Pre-formatted attribution string**, mandatory to publish |
| `rights_status` | enum | `unknown` \| `permitted` \| `licensed` \| `public_domain` \| `permission_on_file` |
| `exif_stripped` | bool | Must be `true` to publish |
| `featured` | bool | Gallery highlight |
| moderation mixin | | |

**Hard rule (brief §11, ADR 0004):** `rights_status = unknown` blocks publication. Enforced
in a `clean()`/serializer validation and repeated in the admin form, so it cannot be
bypassed by a direct ORM write in the pipeline.

**Minors:** a boolean `minor_subject` flag. When `true`, `guardian_consent_on_file` must
also be `true` before publication.

### 4.3 `sources` — third-party sources for attribution

Separate from `scrape_sources`: this is the *citation* registry, not a fetch target.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `name` | text | e.g. "carnavaldepasto.org", "El Tiempo" |
| `kind` | enum | `official_site` \| `news_outlet` \| `archive` \| `pdf` \| `other` |
| `url` | URL, nullable | |
| `is_official` | bool | Only `carnavaldepasto.org` — used to render the unofficial disclaimer |
| `notes` | text | Terms of use, contact, licence constraints |

### 4.4 `site_settings`

| Column | Type | Notes |
|---|---|---|
| `key` | text, PK | |
| `value` | jsonb | Typed values |
| `value_type` | enum | `string` \| `int` \| `bool` \| `json` |
| `description` | text | What it controls |
| `updated_by` | FK → `auth.User`, nullable | |
| `updated_at` | datetime | |

Every change is also written to `audit_logs`. Secrets are **never** stored here — only in
environment variables.

### 4.5 `content_translations` — database content in two locales

Supports ADR 0010 for admin-authored rows. Translation keys are authored in Spanish;
English rows are optional and fall back to Spanish when absent.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `content_type` | FK → `django_content_type` | Generic |
| `object_id` | UUID | |
| `field` | text | e.g. `description` |
| `locale` | char(2) | `es` or `en` |
| `value` | text | |
| `source_translation` | FK → self, nullable | Links an `en` row back to its `es` original |

Unique together on `(content_type, object_id, field, locale)`.

## 5. Security, administration, and audit

Authentication, roles, and sessions are Django's built-in tables plus:

| Table | Purpose |
|---|---|
| `auth_user` | Accounts. **No public signup** — created by seed command only (ADR 0005) |
| `auth_group` | The three roles: `admin`, `editor`, `viewer` (see `roles-permisos.md`) |
| `django_session` | Server-side sessions; the `httpOnly` cookie holds only the key |
| `django_admin_log` | Django's own admin change log |
| `otp_totpdevice` | `django-otp` devices for administrators |

There is **no `refresh_tokens` table** — the brief's §8 lists one, and ADR 0005 removes it
because no tokens are issued.

### 5.1 `audit_logs` — the project-wide audit trail

Django's `LogEntry` is not enough: it does not cover bulk operations, pipeline runs, or
non-admin writes. This table is the requirement from brief §9.

| Column | Type | Notes |
|---|---|---|
| `id` | bigint | PK, monotonic for chronological reads |
| `actor` | FK → `auth.User`, nullable | Null for pipeline actions |
| `actor_kind` | enum | `human` \| `pipeline` \| `system` |
| `action` | text | e.g. `approve`, `reject`, `update`, `login`, `login_failed` |
| `object_type` | text | Content type label |
| `object_id` | UUID, nullable | |
| `changes` | jsonb | Before/after for config changes |
| `ip_hash` | char(64), nullable | **Hashed, never raw** (brief §10) |
| `request_id` | char(36), nullable | Correlates with logs |
| `created_at` | datetime, indexed | |

Written from Django signals on the moderation mixin tables plus explicit calls from the
pipeline and the auth events. Append-only: no update or delete permission on this table
for any role, including `admin`.

## 6. Public submissions

### 6.1 `submissions`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `public_token` | char(32), unique | For the contributor's status lookup |
| `kind` | enum | `image` \| `video_link` |
| `declared_author` | text | The contributor's rights declaration |
| `declared_year` | int, nullable | |
| `declared_place` | text, nullable | |
| `description_es`, `description_en` | text | |
| `video_provider` | enum, nullable | `youtube` \| `vimeo` |
| `video_id` | char(32), nullable | Normalised id, never a raw URL used as an embed `src` |
| `contact_email` | text, nullable | Optional. **PII** — see §8 |
| moderation mixin | | `origin` is always `community` |

### 6.2 `submission_files`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `submission` | FK → `submissions` | |
| `quarantine_key` | text | Private storage. Never public until approval |
| `mime_detected` | text | From magic bytes, **not** the filename |
| `declared_mime` | text | What the client claimed; kept to detect mismatches |
| `content_hash` | char(64) | Duplicate detection |
| `byte_size` | int | |
| `width`, `height` | int, nullable | After re-encoding |
| `exif_stripped` | bool | Must be `true` before approval |
| `duplicate_of` | FK → self, nullable | Set when the same bytes were submitted before |

### 6.3 `consent_records`

Brief §10: the checkbox is unchecked by default and blocking, and the accepted **version**
of the legal text must be recorded.

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `submission` | FK → `submissions`, | |
| `legal_document` | FK → `legal_documents` | Exact version accepted |
| `accepted_at` | datetime | |
| `ip_hash` | char(64) | Hashed, never raw |
| `user_agent_hash` | char(64), nullable | |
| `declaration_minor_subject` | bool | Contributor's declaration |
| `declaration_rights` | bool | "I am the author or I have permission" |

### 6.4 `legal_documents` — versioned terms

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `doc_type` | enum | `terms` \| `privacy` \| `content_policy` \| `takedown` |
| `version` | char(16) | e.g. `1.0` |
| `locale` | char(2) | `es` \| `en` |
| `body` | text | Markdown |
| `effective_from` | datetime | |
| `is_current` | bool | Partial unique index: one current version per `(doc_type, locale)` |

Documents are **never edited after publication**; a change creates a new version, so old
`consent_records` remain interpretable.

### 6.5 `moderation_actions`

A dedicated, append-only decision log, separate from `audit_logs`, because it is the
evidence trail for a rights or takedown dispute.

| Column | Type | Notes |
|---|---|---|
| `id` | bigint | PK |
| `subject_type`, `subject_id` | text, UUID | The moderated object |
| `action` | enum | `submit` \| `approve` \| `reject` \| `request_changes` \| `withdraw` |
| `actor` | FK → `auth.User`, nullable | Null for automated submissions |
| `reason` | text, nullable | Required for `reject` |
| `created_at` | datetime | |

### 6.6 `takedown_requests`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `subject_type`, `subject_id` | text, UUID | What is being challenged |
| `requester_name` | text, nullable | |
| `requester_email` | text | Needed to respond. **PII** |
| `claim_type` | enum | `copyright` \| `privacy` \| `illegal_content` \| `other` |
| `evidence_url` | URL, nullable | |
| `received_at` | datetime | |
| `status` | enum | `received` \| `in_review` \| `actioned` \| `rejected` \| `escalated` |
| `action_taken` | text, nullable | |
| `responded_at` | datetime, nullable | |
| `notes` | text, nullable | Internal |

`claim_type = illegal_content` sets `status = escalated`: brief §10 requires reporting to
the authorities or a line such as Te Protejo, and an internal note is not a sufficient
response.

## 7. Entity relationships

```
editions ──< days ──< events >── venues
    │                 │
    └──< media_assets │
                      │
scrape_sources ──< raw_documents        sources ──< news_items
       │
       └──< ingestion_runs ──> (events, news_items via moderation mixin)

submissions ──< submission_files
      │
      ├──< consent_records >── legal_documents
      └──< moderation_actions

site_settings        audit_logs        takedown_requests
auth_user ──< moderation mixin (reviewed_by, created_by)
```

## 8. Privacy notes

- **No raw IP addresses anywhere.** `ip_hash` is SHA-256 of the IP **salted with a server
  secret** — an unsalted hash of an IPv4 address is trivially reversible by brute force
  over 2³² candidates.
- **Raw payloads are never in git.** `data/raw/` and `*.pdf` are in `.gitignore` (ADR 0004).
- **PII with limited retention:** `submissions.contact_email` and
  `takedown_requests.requester_email` are stored in cleartext because a reply is legally
  required. Both carry a deletion deadline once the matter is closed, and neither is
  exposed through the public API.
- **EXIF and GPS are stripped** before storage, not at serve time (ADR 0006).
- `consent_records` stores hashes only, never the address that gave consent.

## 9. Indexes and constraints summary

| Constraint | Purpose |
|---|---|
| `raw_documents.content_hash` UNIQUE | Idempotent re-runs (ADR 0002) |
| `media_assets.content_hash` UNIQUE | Duplicate image detection |
| `legal_documents` partial unique on `(doc_type, locale) WHERE is_current` | One current version |
| `submissions.public_token` UNIQUE | Status lookup without enumeration |
| `content_translations` unique on `(content_type, object_id, field, locale)` | No duplicate translations |
| CHECK `status='rejected' → rejection_reason IS NOT NULL` | Rejections are always explained |

## 10. Open questions for the design phase

1. **Field-level `*_es` / `*_en` columns versus a generic `content_translations` table.**
   Columns are simple to query and type; the generic table scales to arbitrary content. The
   current model mixes both, which is inconsistent. Recommend: keep columns for `events`
   (fixed schema, high read volume) and use `content_translations` for `news_items` and
   `media_assets`. Decide in design review.
2. **Whether `days` should be seeded per edition or created by the pipeline.** Recommend
   seeded by the pipeline from the source, since day names differ by year.
3. **Retention window for `raw_documents`.** Recommend keeping the last N per source and
   pruning, to bound free-tier storage.
4. **Whether `site_settings` needs a typed schema** beyond `value_type`. Recommend yes, once
   v2 introduces site configuration.