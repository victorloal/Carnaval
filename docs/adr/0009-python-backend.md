# 0009. Technology stack: Django, PostgreSQL, React

- **Status:** Accepted
- **Date:** 2026-10-03
- **Relates to:** brief §12 (technology stack), §20 (open items: backend language, database)

## Context

The brief left both the backend language and the database tentative. Neither could stay
open: the container design, the data model, the OpenAPI contract, and the test plan all
depend on them.

Two constraints decided the shape:

1. **The project needs a serious internal moderation console** — approve/reject across
   `events`, `news_items`, `media_assets` and `submissions`, configure scrape sources,
   edit site settings, read audit logs. Built from scratch in React this is months of work
   for a part-time solo maintainer.
2. **Zero infrastructure cost**, on free tiers, with no resident worker to operate.

A mature admin framework is therefore worth more than API framework novelty.

## Decision

### Backend — Python + Django + PostgreSQL

| Concern | Choice |
|---|---|
| Language | Python 3.12 |
| Framework | Django 5.x |
| Database | **PostgreSQL 16** |
| ORM / migrations | Django ORM, Django migrations |
| DB driver | psycopg 3 |
| Public API | Django REST Framework |
| OpenAPI | drf-spectacular — **generated** from the code, committed to `docs/02-diseno/openapi.yaml` by CI |
| Admin panel | **Django admin**, customized (see ADR 0005) |
| AuthN | Django sessions in an `httpOnly` cookie + `django-otp` (TOTP) |
| Password hashing | Argon2id via `argon2-cffi` |
| RBAC | Django auth groups: `admin`, `editor`, `viewer` |
| Audit | `audit_logs` table written from Django signals |
| HTTP client | httpx |
| HTML parsing | selectolax, fallback BeautifulSoup4 + lxml |
| PDF parsing | pdfplumber |
| Images | Pillow (+ EXIF removal) |
| Object storage | django-storages against Supabase Storage or Cloudflare R2 (S3-compatible) |
| CAPTCHA | Cloudflare Turnstile |
| Tests | pytest + pytest-django; HTTP mocked, never live |
| Lint / format / types | Ruff, mypy + django-stubs |
| Scheduled runs | GitHub Actions `cron` invoking Django management commands |

### Frontend — React + TypeScript

Vite, TanStack Query, `react-i18next` (es primary, en secondary — see ADR 0010).
The React app is the **public site only**. There is no React admin panel.

### Consequence for the monorepo layout

```
backend/    Django project: API, admin, ingestion commands
frontend/   React public site (es/en)
tests/      E2E (Playwright) and security suites that span both
docs/       requirements, design, ADRs, legal, sprints
```

Python owns the write paths entirely. React only reads the public API and posts
anonymous submissions.

## Consequences

**Positive**
- Django admin supplies authentication, permissions, list filters, search, bulk actions,
  and CSRF protection — the entire moderation console for free. This is the single largest
  time saving in the project.
- The OpenAPI contract is generated from the code, so it can never drift from the
  implementation. See ADR 0011.
- The Django ORM and migrations keep the schema portable across any PostgreSQL host, which
  matters because the free-tier provider (Supabase or Neon) is still undecided.
- Argon2id, TOTP, and session security are vetted library implementations, not
  hand-rolled crypto (brief §9, §18).
- One language owns the backend, so there is no cross-language type sharing to maintain;
  the generated OpenAPI contract is the seam.

**Negative**
- Django admin's interface is Django's, not React's. The portfolio demonstrates two
  different UI stacks. Accepted as an honest trade for shipping.
- DRF is heavier than a minimal ASGI framework. Accepted: admin + ORM + migrations are
  worth far more than request overhead on a read-mostly public API.
- The generated OpenAPI contract means design-first API review is not possible; the
  contract is a *result* of design, reviewed after implementation.

## Alternatives considered

- **FastAPI + SQLAlchemy.** Rejected: the admin panel would then have to be built by hand
  in React, which is the dominant cost in this project.
- **Django REST Framework replaced by plain JsonResponse.** Rejected: no serializers, no
  browsable API, no schema for drf-spectacular to generate from.
- **Django + a React admin panel.** Rejected in ADR 0005; it keeps Django admin's value but
  pays for a second UI stack and a bespoke RBAC layer.
- **MongoDB or SQLite.** Rejected: the data model is relational and heavily constrained
  (moderation state, consent records, foreign keys); SQLite was never viable for the
  target deployment.

## References

- Brief §12 (stack), §9 (security panel), §14 (risks), §18 (roadmap steps 2–4).
- `docs/02-diseno/arquitectura-c4.md`, `docs/02-diseno/modelo-datos.md`