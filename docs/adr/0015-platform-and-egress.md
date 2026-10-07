# 0015. Platform, database and object storage: the zero-cost choice

- **Status:** Proposed — awaiting the maintainer's accounts. ADR 0009 settled the stack and
  left the platform open; `despliegue.md` §3 names the candidates. Nothing here is deployed.
- **Date:** 2026-10-06
- **Relates to:** brief §12 (platform), §20 (open items), §14 (risks); `despliegue.md` §1 and
  §3; ADR 0002 (database as source of truth), ADR 0006 (quarantine), ADR 0009 (stack),
  ADR 0016 (legal texts); NFR-05 (zero cost), NFR-20 (backup).

## Context

The zero-cost constraint is the organising one, and its sharp edge is **egress cost**, not
compute: an image-heavy site served from a free database or storage plan can generate a bill
that no free tier covers. `despliegue.md` §1 states the corollary plainly — **free tiers
change**, so the choice is a decision with a re-verification date, not a permanent fact.

The stack is already decided (ADR 0009): Django 5.2 LTS + PostgreSQL 16 + React. What is
open is *where* those run. Sprint 03 made one thing easier: `raw_documents.storage_key` is
an opaque key behind a storage module, so a provider change is a settings change, not a
migration.

## Decision (proposed)

| Layer | Choice | Why |
|---|---|---|
| Frontend | **Cloudflare Pages** | Static build, free, global CDN, no egress |
| API + admin | A **Python container host with a free tier** | The admin is stateful and session-backed (ADR 0005); this is the least-settled choice |
| Database | **Neon** (or Supabase) PostgreSQL | A usable free tier; Neon is PostgreSQL-only and purest, Supabase co-locates Storage |
| Object storage | **Cloudflare R2**, two buckets (quarantine, public) | **No egress fees**, which is decisive (ADR 0006) |
| Scheduling | **GitHub Actions `cron`** | No resident worker; already the plan (ADR 0009) |

Egress decides the storage; the API/admin host is decided by testing, early, whether Django
admin sessions and the ingestion command run on a free container.

## What is still open

- **The API/admin host** is the least-settled choice in the project. It must be tested with a
  running admin session and a `manage.py` command, not chosen from a marketing page.
- **Accepting this ADR** requires creating accounts and is a human act; until then it stays
  **Proposed**.
- **PostgreSQL in CI** and the **browser end-to-end stages** (`docker compose` + Playwright,
  Lighthouse, axe) are not wired: they need a service container and a browser, and could not
  be verified in the development environment. They remain carried items.

## Consequences

**Positive**
- No egress bill, which is the only cost that scales with use.
- The storage abstraction and environment-only settings mean a provider change touches
  configuration, not code.
- No resident worker to operate.

**Negative**
- Free tiers change; the choice needs re-verification and a documented date.
- Cloudflare Pages + a separate container host is two systems where Supabase would be one.

## Alternatives considered

- **Supabase for everything** (database + storage + hosting). Simpler, one provider; rejected
  as the default because its egress is metered where R2's is not, and the site is
  image-heavy (ADR 0006).
- **A paid host.** Rejected: it violates NFR-05, which is a constraint, not a preference.
