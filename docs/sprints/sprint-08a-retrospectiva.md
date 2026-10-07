# Sprint 08a retrospective — identity and audit

- **Date:** 2026-10-06
- **Sprint:** 08a — Admin foundation, first half: roles, auth and audit
- **Method:** Start / Stop / Continue, plus what actually happened versus what was planned.

## What was planned versus what happened

Planned (the first half of Sprint 08): the three role groups, TOTP for administrators,
step-up, 12 h idle / 72 h absolute sessions with central revocation, login throttling, and an
append-only `audit_logs` with the auth events.

What happened: **08a landed and CI is green on its commit.** The backend suite is at **92
tests**; `ruff`, `mypy` (104 files), `makemigrations --check`, `check --deploy`, the secret
scan, the diagram check and the OpenAPI drift check are all clean. The matrix moved **FR-D-01,
02, 04, 06, 07, 08, 09, 10, 13, 14, 16, FR-H-08, NFR-21 and SEC-01/02/03/04/06/07/08 to Done.**

Delivered: a `carnaval.accounts` app (roles and `seed_roles`, `seed_admin` as staff **not**
superuser, `enrol_totp`, a cache-based login throttle behind a custom auth backend, central
session revocation, a step-up page and gate) and a `carnaval.audit` app (`AuditLog` with an
append-only manager and `save`/`delete` guards, `login`/`login_failed` signals, a read-only
admin). Middleware adds a correlation id and a salted IP hash, forces **Spanish on the admin**
while the API stays English, and sets `noindex` on the console.

Carried, and named in `sprint-08-plan.md`: **08b** (FR-D-03 and object-level authorization),
the **hashed** recovery codes (SEC-05), the PostgreSQL append-only trigger, and the explicit
idle/absolute expiry test (FR-D-15).

## Start

- **Satisfy the admin-locale requirement without breaking the API rule.** `LANGUAGE_CODE`
  is global; a middleware activates Spanish for `/admin/` and `/accounts/`, so the admin is
  Spanish (FR-H-08) while the generated contract stays English.
- **Hash the IP, never store it.** The throttle keys on the **salted** hash, and the audit row
  stores only the hash (PRV-01) — the raw address never reaches the database or a log.
- **Append-only where it can be proven.** The `AuditLog` manager blocks `update`/`delete`, the
  model blocks re-`save`, and `default_permissions = ("view",)` means no change/delete
  permission is ever created. All of that is testable on SQLite; the PostgreSQL trigger is left
  out until it can be run.
- **The seed administrator is not a superuser.** `is_superuser` would bypass the whole matrix.

## Stop

- **A global setting that satisfies one rule can break another.** Setting `LANGUAGE_CODE =
  "es"` for the admin translated the **OpenAPI schema descriptions** into Spanish — which
  contradicts "the API surface is English" and would have failed the drift check. It was caught
  by running the drift check, not by review. The fix keeps the global setting English and
  scopes the locale to the admin.
- **Do not trust a library's summary of its own security property.** `django-otp`'s recovery
  codes are consumed once, but `StaticToken` stores the token **in plain text**, not hashed, so
  SEC-05 is **not** satisfied. It stays Open with the reason recorded, rather than closed by
  the library's reputation.
- **The append-only guarantee is only half made.** The database trigger waits for PostgreSQL;
  until then the guarantee is the application's, and the matrix says so.
- **Two items were split out, not done.** FR-D-03 (a fresh install exposes no `pending`) and
  object-level authorization belong with the review queue, in 08b — they concern content that
  08a never registers.

## Continue

- **Move only the requirements the tests actually cover.** SEC-05 and FR-D-15 stayed Open.
- **Scope middleware narrowly.** TOTP enforcement skips the login/logout/step-up paths so the
  console cannot redirect-loop, and the admin locale is limited to the two URL prefixes.
- **Guard the API contract with the drift check** — it is what caught the locale mistake.

## What the sprint proved about the project

The v1 identity layer is real: roles are groups with permissions, the admin demands a second
factor, sessions expire on a clock and can be revoked, brute force is slowed, and every login
is audited in an append-only table. What the sprint also proved is that the project's
of-use settings can collide — the admin's language and the API's language are the same Django
setting — and that only running the checks reveals it.

## Concrete changes adopted

1. `LANGUAGE_CODE` stays `en-us`; the admin's Spanish is a scoped middleware, and the OpenAPI
   drift check guards the English API surface.
2. A third-party security claim is verified against the code before a requirement is closed.
3. The append-only trigger and the hashed recovery codes are carried, not faked.
