# C4 Architecture

- **Status:** Draft for review
- **Date:** 2026-10-03
- **Relates to:** ADR 0002 (scraper optional; database as source of truth), ADR 0003 (monorepo), ADR 0005 (Django admin; sessions + TOTP; no JWT), ADR 0006 (two storage tiers: quarantine and public), ADR 0009 (Python 3.12/Django 5/DRF, PostgreSQL 16, React TS public only), ADR 0010 (bilingual), ADR 0011 (generated OpenAPI, drift-checked in CI), brief §7 (architecture), §9 (security), §10 (submissions).

> The backend language and stack are **decided** by ADR 0009. The brief §6/§9/§12 describing JWT and an undecided stack are **superseded** (see `docs/00-acta-proyecto.md` §9).

## 1. Level 1 — System Context

The system is the “Carnaval de Negros y Blancos” web platform. It ingests, moderates, and exposes programme and editorial content with attribution. Scraping is **optional** (ADR 0002).

**Actors**
- Public site visitor (reader): reads published content, switches locale (es/en), searches.
- Community contributor: submits anonymous image or video link, accepts terms and consent (v3).
- Moderator/editor (maintainer): reviews queue, approves/rejects with reason, manages settings, audit log.
- Administrator (maintainer role): manages users/roles, legal documents, configuration (RBAC, server-side).

**External systems**
- `carnavaldepasto.org` (official WordPress site) — ingestion source, may expose WP REST API (unverified, brief §5).
- News outlets/archives — ingestion sources (headline/link/summary only; no full articles committed).
- PostgreSQL host — managed PostgreSQL 16 instance (free tier; provider **undecided**).
- Object storage — quarantine and public tiers as separate buckets (two-tier storage per ADR 0006; provider/domain separation; R2 has no egress fees — **decisive**, provider **undecided**).
- Cloudflare Turnstile — CAPTCHA for anonymous submissions.
- Email provider — for takedown responses/notifications as needed (**undecided**, zero-cost preferred).
- GitHub Actions — scheduling (cron) and CI/CD; runs ingestion via Django management command.

**Mermaid (Level 1)**
```text
C4Context
title System Context — Carnaval de Negros y Blancos

Person(visitor, "Public site visitor (reader)", "Views published programme/news/gallery; switches locale es/en")
Person(contributor, "Community contributor", "Anonymous submits image or video link; accepts consent")
Person(moderator, "Moderator/editor", "Reviews queue, approves/rejects with reason, manages settings/audit")
Person(admin, "Administrator", "Manages users/roles, legal docs, configuration")

System(system, "Carnaval platform", "Django+DRF API, Django admin, React TS SPA; database-as-truth; moderated content")

System_Ext(src_official, "carnavaldepasto.org", "Official WordPress/Elementor site; WP REST API (unverified)")
System_Ext(src_news, "News outlets/archives", "External sources; headline, URL, outlet, date, short summary only")
System_Ext(dbhost, "PostgreSQL 16 host", "Managed DB (free tier; provider undecided)")
System_Ext(stor, "Object storage", "Quarantine (private) and public tiers as separate buckets; separate domain (ADR 0006)")
System_Ext(turnstile, "Cloudflare Turnstile", "CAPTCHA for anonymous submissions")
System_Ext(email, "Email provider", "Notifications/takedown responses (undecided; zero-cost)")
System_Ext(actions, "GitHub Actions", "CI/CD and cron scheduler for ingestion command")

Rel(visitor, system, "HTTPS/JSON + HTML", "Reads published content; locale switching; search")
Rel(contributor, system, "HTTPS/JSON (form submission)", "Anonymous submission with consent; CAPTCHA")
Rel(moderator, system, "HTTPS (Django admin)", "Moderation queue, approvals/rejections, audit, settings")
Rel(admin, system, "HTTPS (Django admin, RBAC)", "User/role mgmt, legal docs, config")

Rel(system, src_official, "HTTPS (GET, rate-limited, UA identified)", "Ingestion fetch (prefer WP REST API if responds; idempotent by content_hash)")
Rel(system, src_news, "HTTPS (GET, rate-limited, UA identified)", "Ingestion fetch; store minimal metadata only")
Rel(system, dbhost, "TCP/Postgres", "Persistent state (editions, events, news, media, submissions, audit)")
Rel(system, stor, "HTTPS/API (signed URLs)", "Quarantine writes (private) -> move to public on approval; EXIF stripped; magic-bytes validated")
Rel(system, turnstile, "HTTPS (verify token)", "Validate CAPTCHA on anonymous submissions")
Rel(system, email, "SMTP/HTTPS", "Outbound messages (takedown/notifications) if configured")
Rel(actions, system, "Invoke Django mgmt command (cron)", "Scheduled ingestion run (not a resident worker)")
Rel(system, actions, "Reports status/logs", "ingestion_runs as pipeline observability")

UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

## 2. Level 2 — Container diagram

Containers are the deployable/runnable units (per ADR 0009 and constraints). The public site availability **does not depend** on any external source; the scraper is **optional** (ADR 0002).

**Containers**
- `django_app` (process): Django 5 + DRF. Serves public read API, submission endpoints (v3), Django admin surface (same process), moderation logic, ingestion pipeline (`ingestion` management command), RBAC/server-side session auth, audit logging. **Technology:** Python 3.12. **Deployment:** application host (free tier, **undecided**).
- `django_admin` (surface): Django admin UI exposed by the same `django_app` process (separate surface). RBAC enforced server-side; sessions + TOTP; **no JWT**. **Deployment:** same host.
- `spa_public` (static assets): React + TypeScript **public site only**. Read-only plus anonymous submissions; **no React admin panel** (ADR 0005/0009). **Deployment:** static host/CDN (free tier, **undecided**; can be separate from API).
- `postgres` (data): PostgreSQL 16. Source of truth. **Deployment:** managed DB (free tier, **undecided**: Supabase/Neon or other zero-cost; verify limits).
- `object_storage` (buckets): Two-tier object storage: `quarantine` (private, access via signed URLs, server-side only) and `public` (readable by public where appropriate). Separate buckets and preferably separate domain (ADR 0006). **R2 has no egress fees** — **decisive** for image-heavy site; provider **undecided**.
- `ingestion_runner` (ephemeral): Django management command invoked by **GitHub Actions cron** — **NOT a resident worker** (fits zero-cost constraint C1). Runs idempotently (gate on `raw_documents.content_hash`), retry with backoff, circuit breaker after N consecutive failures; marks source disabled on failure. **Technology:** Python (same code). **Deployment:** GitHub Actions workflow (free tier).

**Relationships**
- SPA -> Django app: HTTPS/REST (public read, anonymous submissions, locale). Uses session cookies for CSRF where applicable; no tokens.
- Browser -> Django admin: HTTPS (session + TOTP). Server-side RBAC on every request.
- Django app -> Postgres: TCP (ORM). Append-only audit; moderation state transitions recorded.
- Django app -> Object storage: HTTPS/API (signed uploads/downloads). Quarantine private; move to public on approval. EXIF stripped, magic-bytes validated.
- Ingestion runner (GA) -> Django app codebase via checkout; executes `manage.py <ingest>` against configured sources: HTTPS GET to external sources (rate-limited, identifiable User-Agent). Writes to Postgres (`raw_documents`, `ingestion_runs`, proposed pending records). Does **not** delete published data if sources fail.
- CAPTCHA verification: SPA/submission -> Turnstile (browser) + server-side verify via Django app.
- Email: Django app -> email provider (SMTP/HTTPS) if configured.

**Mermaid (Level 2)**
```text
C4Container
title Container diagram — Carnaval de Negros y Blancos

Person(visitor, "Public site visitor (reader)")
Person(contributor, "Community contributor")
Person(moderator, "Moderator/editor")
Person(admin, "Administrator")

System_Boundary(sys, "Carnaval platform") {
  Container(spa, "React TS SPA (public only)", "React + TypeScript, Vite/CRA", "Read-only + anonymous submissions; no React admin panel (ADR 0005/0009)")
  Container(django_app, "Django app (API + admin + pipeline)", "Python 3.12, Django 5, DRF, drf-spectacular", "Public API, submission endpoints (v3), Django admin surface (same process), ingestion pipeline, RBAC, sessions+TOTP, audit; OpenAPI generated")
  Container(ingest_cmd, "Ingestion runner (ephemeral mgmt cmd)", "Django management command", "Invoked by GitHub Actions cron — NOT a resident worker. Idempotent, retry+backoff, circuit breaker. Zero published data lost on failure.")
  ContainerDb(pg, "PostgreSQL 16", "Relational DB", "Source of truth: editions/days/events, news, media_assets, submissions, scrape_sources, raw_documents, ingestion_runs, audit_logs, legal_documents, consent_records")
  Container(stor, "Object storage (2-tier)", "Object storage (buckets)", "Quarantine (private, signed URLs) and public (separate buckets; separate domain; R2 no egress fees — decisive). EXIF stripped; magic-bytes validated.")
}

System_Ext(src_off, "carnavaldepasto.org", "WP/Elementor; WP REST API (unverified)")
System_Ext(src_news, "News outlets/archives", "Minimal metadata only")
System_Ext(turnstile, "Cloudflare Turnstile", "CAPTCHA")
System_Ext(email, "Email provider (undecided)", "Notifications/takedown")
System_Ext(gh, "GitHub Actions", "CI/CD + cron schedule")

Rel(visitor, spa, "HTTPS", "Browse published content; locale es/en")
Rel(contributor, spa, "HTTPS", "Anonymous submit (image/video link); consent")
Rel(moderator, django_app, "HTTPS (Django admin)", "Review queue, approve/reject with reason, audit, settings")
Rel(admin, django_app, "HTTPS (Django admin, RBAC)", "Users/roles, legal docs, config")

Rel(spa, django_app, "HTTPS/JSON (REST)", "Public read; submissions; no tokens")
Rel(django_app, pg, "TCP/Postgres", "ORM reads/writes; append-only audit")
Rel(django_app, stor, "HTTPS/API (signed)", "Quarantine ops; approve -> move to public; strip EXIF; validate magic bytes")

Rel(gh, ingest_cmd, "cron -> invoke manage.py ingest", "Scheduled run (ephemeral)")
Rel(ingest_cmd, django_app, "Runs in same app context", "Uses models/pipeline; writes to pg; respects circuit breaker")
Rel(ingest_cmd, src_off, "HTTPS GET (rate-limited, UA identified)", "Prefer WP REST API if responds; content_hash gate")
Rel(ingest_cmd, src_news, "HTTPS GET (rate-limited, UA identified)", "Store headline, URL, outlet, date, short summary only")
Rel(ingest_cmd, stor, "HTTPS/API", "Store raw payloads in object storage (never commit to git)")

Rel(django_app, turnstile, "HTTPS (server-side verify)", "Validate CAPTCHA token")
Rel(django_app, email, "SMTP/HTTPS", "Send messages if configured")

UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```