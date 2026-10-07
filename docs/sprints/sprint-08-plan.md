# Sprint 08 — Admin foundation: roles, auth and audit

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** A hardened Django admin with the three roles of `roles-permisos.md`, TOTP
  for administrators, step-up re-authentication, login throttling, central session revocation
  and an append-only `audit_logs`. No content is reviewed yet; this sprint makes the console
  safe to open.
- **Starts:** after Sprint 07 closes; nominal 1 week.
- **WIP limit:** 2 items (ADR 0001)
- **Split:** this sprint was split into **08a** (identity and audit — delivered) and **08b**
  (the admin surface: FR-D-03, object-level authorization, the source dashboard — carried).
  See `sprint-08a-retrospectiva.md`.

> Every capability in `roles-permisos.md` §3 is enforced **server-side** and denied by
> default. Hiding a control is never the enforcement.

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | Customized Django admin; groups `admin`, `editor`, `viewer` | FR-D-01, FR-D-02 | tests | Done (08a) |
| 2 | A fresh install exposes no `pending` content until roles are configured | FR-D-03 | SEC-13 | Done (08b) |
| 3 | TOTP enforced for `admin`; single-use hashed recovery codes | SEC-04, SEC-05 | tests | TOTP Done (08a); hashed codes carried (SEC-05) |
| 4 | Server-side sessions only, `httpOnly`/`Secure`/`SameSite`; no token anywhere; central revocation | SEC-02, SEC-03, SEC-08 | tests | Done (08a) |
| 5 | Login lockout with exponential backoff; successful and failed logins audited | SEC-06, FR-D-10 | tests | Done (08a) |
| 6 | Step-up re-auth before publish, role change, `site_settings` edit, legal action | FR-D-16, ADR 0013 | tests | Done (08a) |
| 7 | Object-level authorization; `viewer` can never transition state | SEC-09, SEC-10, FR-D-05 | SEC tests | Permissions Done (08b); object-level cases carry (SEC-09) |
| 8 | Append-only `audit_logs`, undeletable by any role including `admin` | FR-D-08, FR-D-09 | SEC-16 | Done (08a, app-level); DB trigger carried |
| 9 | Admin Spanish only; HTTPS only; `noindex` | FR-H-08, NFR-21 | inspection | Done (08a) except HTTPS at deploy |
| 10 | First administrator created by a management command, never through the API | FR-D-14 | test | Done (08a) |

### Why the seed administrator is not a superuser

`is_superuser` bypasses every check in the permission matrix, which would make the matrix
decorative for the one account that matters most. The seed command creates a **staff user in
the `admin` group** with an explicit permission set. If the usability cost proves too high, a
superuser is acceptable only as a recorded deviation, and SEC-13 excludes superusers.

## What must be true when it ends

1. Every cell of the permission matrix is enforced server-side (SEC-13), including refusals.
2. A fresh install exposes no unreviewed content (FR-D-03).
3. `audit_logs` cannot be updated or deleted by any role; a PostgreSQL trigger backs it
   (FR-D-09).
4. No token exists anywhere; sessions are server-side and centrally revocable.
5. `ruff`, `mypy`, `pytest` and `check --deploy` green.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | The matrix is asserted cell by cell, plus TOTP, step-up, throttle and revocation |
| Documentation updated | `roles-permisos.md` §5 enforcement points, `autenticacion.md`, `CHANGELOG.md` |
| CI green | The audit trigger requires the PostgreSQL service wired in Sprint 07 |
| Linked in the matrix | FR-D-01…16, SEC-01…10, FR-H-08, NFR-21, PRV-01 |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| The review queue and moderation verbs | Sprint 09 |
| Legal documents and takedown | v3 |
| Content types beyond the programme | v2 |

## Risks

1. **A superuser makes the matrix decorative** — the seed command must not create one.
2. **The audit trigger is PostgreSQL-specific** — CI must run PostgreSQL or the guarantee is
   untested.
3. **Step-up friction** — scope it to exactly the four actions ADR 0013 names.

## Carried into the next sprint

1. The review queue and the moderation verbs that use these permissions.
2. The ADR for proposing changes to already-published content (`flujo-datos.md` §5.1), before
   v1 can publish.
