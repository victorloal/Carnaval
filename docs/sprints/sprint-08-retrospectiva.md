# Sprint 08 retrospective — admin foundation: roles, auth and audit

- **Date:** 2026-10-06 (recorded 2026-10-07)
- **Sprint:** 08 — Admin foundation: roles, auth and audit
- **Method:** Start / Stop / Continue.
- **Note:** the sprint was **split** into 08a (delivered on its own, `sprint-08a-retrospectiva.md`)
  and 08b (delivered with the v1 backend, `sprint-09-retrospectiva.md`). This is the
  retrospective for the **whole** Sprint 08 plan.

## What was planned versus what happened

Planned: a hardened Django admin with the three roles, TOTP for administrators, step-up
re-authentication, login throttling, central session revocation and an append-only
`audit_logs`, with every matrix cell enforced server-side and denied by default.

What happened: **the plan was split and both halves landed**, in two commits and two sprints'
worth of time.

- **08a** (`d6287f4`) — `carnaval.accounts` (roles, `seed_roles`, `seed_admin` as staff **not**
  superuser, TOTP, the login throttle, central revocation, step-up) and `carnaval.audit`
  (`AuditLog` append-only). **92 backend tests.** Its own retrospective exists.
- **08b** (with the v1 backend, `ffcc353`) — the content registered in the admin behind the
  permission matrix (FR-D-03: a fresh staff user with no role sees nothing), the source
  dashboard, and the model-level authorization. **103 backend tests.**

Carried, and named: the **hashed** recovery codes (SEC-05 — `django-otp` stores them in plain
text), the **PostgreSQL append-only trigger** (FR-D-09 is application-level until then), the
explicit **idle/absolute expiry test** (FR-D-15), and **object-level** authorization cases
(SEC-09).

## Start

- **Enforce server-side, deny by default.** The permission matrix is asserted cell by cell,
  including the refusals: a `viewer` cannot moderate, a fresh staff user sees nothing.
- **The seed administrator is not a superuser.** `is_superuser` bypasses the whole matrix;
  creating a staff user in the `admin` group keeps the matrix meaningful for the account that
  matters most.
- **Hash the IP, never store it.** The throttle and the audit row key on the salted hash
  (PRV-01); the raw address never reaches the database or a log.
- **Split when the halves have different dependencies.** 08a needed no content model; 08b
  needed the review queue's models, so it moved with them.

## Stop

- **A global setting that satisfies one rule can break another.** Setting the language to
  Spanish for the admin translated the **OpenAPI schema**, contradicting "the API surface is
  English"; the drift check caught it, not review. The fix scopes the locale to `/admin/`.
- **Do not trust a library's summary of its own security property.** `django-otp`'s recovery
  codes are consumed once but stored **in plain text**, so SEC-05 is not satisfied and stays
  Open with the reason.
- **The append-only guarantee is half made.** The database trigger waits for PostgreSQL; the
  matrix says application-level, not database-level.
- **FR-D-03 could not be done in 08a** because 08a registered no content. It waited for the
  admin that 08b built — the correct split, stated rather than approximated.

## Continue

- **Move only what the tests cover.** SEC-05, FR-D-15 and SEC-09 stayed Open.
- **Keep the console and the API language apart** via scoped middleware, not a global setting.
- **Guard the contract with the drift check** — it caught the locale mistake.

## What the sprint proved about the project

The console is safe to open before any content exists: identities are roles, the admin demands
a second factor, sessions expire and can be revoked, brute force is slowed, and every login is
audited in an append-only table. The sprint also proved that the project's settings can
collide — the admin's language and the API's language are one Django setting.

## Concrete changes adopted

1. `LANGUAGE_CODE` stays `en-us`; the admin's Spanish is scoped middleware.
2. A third-party security claim is verified against the code before a requirement closes.
3. The append-only trigger and the hashed recovery codes are carried, not faked.
