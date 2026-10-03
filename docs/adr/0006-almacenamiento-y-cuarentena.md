# 0006. Object storage with a quarantine tier for uploads

- **Status:** Accepted
- **Date:** 2026-10-03
- **Relates to:** brief §6 decision 6, §10 (public contributions), §11 (legal)

## Context

Visitors may submit historical photographs without registering. Those files are untrusted
input from anonymous users, and they are also the project's highest copyright and privacy
risk: old photographs are not free of rights, and images may show identifiable people or
minors.

The brief requires a **quarantine** tier: files land in private storage and only become
public after a human approves them. This ADR decides the mechanism and the provider
interface, not the provider itself.

## Decision

### Two storage tiers, never the same bucket

| Tier | Access | Contents |
|---|---|---|
| **Quarantine** | Private. Never served directly; only via signed, short-lived URLs for the reviewing admin | Freshly uploaded submissions awaiting review |
| **Public** | Public read, served from a **separate bucket on a separate domain** | Only files that a human approved |

A file moves from quarantine to public as part of the approval transaction. Rejection
deletes it (or retains it per the retention policy) and always records `rejection_reason`.

### Validation pipeline for every upload

1. **Size and count limits** per submission and per IP, enforced before anything is stored.
2. **Magic-byte allowlist** — JPEG, PNG, WebP verified by real content, **never by
   extension**. A file whose bytes do not match its declared type is rejected.
3. **Full decode and re-encode** through Pillow. This strips embedded payloads (e.g. files
   that are valid images and valid archives simultaneously) rather than trusting the
   decoder.
4. **EXIF removal**, including GPS. Stripped unconditionally, not configurable — there is
   no legitimate case for preserving a visitor's location.
5. **Duplicate detection** by content hash, so the same image cannot be submitted twice.
6. **Direct upload via short-lived signed URLs**, so file bytes never transit the Django
   process.
7. Public responses carry `X-Content-Type-Options: nosniff` and an explicit
   `Content-Disposition`.

### Provider

Abstracted behind `django-storages` so the free tier can change without code changes:
**Cloudflare R2** (no egress fees — the decisive factor for an image-heavy site) or
**Supabase Storage** (database and storage under one provider, fewer credentials).
Undecided until the free-tier limits are verified (brief §12, §20).

## Consequences

**Positive**
- A hostile upload never becomes publicly readable. The blast radius of a bad file is a
  rejected row, not a served asset.
- Re-encoding neutralises polyglot and embedded-code payloads that a magic-byte check
  alone would miss.
- EXIF/GPS removal happens once, in one place, before storage — not at serve time, where
  it could be forgotten.
- The `django-storages` abstraction means a provider change is a settings change.

**Negative**
- Direct signed uploads need a CORS configuration on the bucket and presigned-URL
  generation, which is more moving parts than an upload through Django.
- Re-encoding costs CPU on every upload. Acceptable: volume is low by design.
- Two buckets means two sets of credentials in the environment.

## Alternatives considered

- **One public bucket, review in the database only.** Rejected: a mistake then exposes an
  unreviewed file publicly and instantly, with no storage-side control.
- **Validate at serve time.** Rejected: validation must not be bypassable, and serving is
  the wrong place for a mandatory security step.
- **Store files in the database as `BYTEA`.** Rejected: bloats the database, couples
  serving to the API, and forfeits CDN caching — on free tiers that egress costs money.