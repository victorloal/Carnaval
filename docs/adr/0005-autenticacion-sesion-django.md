# 0005. Admin authentication: Django sessions with TOTP, not JWT

- **Status:** Accepted — **supersedes brief §6 decision 8 and part of §9**
- **Date:** 2026-10-03
- **Relates to:** ADR 0009 (stack), brief §6 decisions 7 and 8, §9 (admin security)

## Context

The brief decided, before any framework was chosen, that the admin panel would use
short-lived access tokens plus rotating refresh tokens in `httpOnly`, `Secure`, `SameSite`
cookies — explicitly **not** `localStorage` — and referenced it as planned ADR 0005.

That decision assumed a **React admin panel** talking to a token-issuing API. ADR 0009
chose Django, whose admin authenticates with server-side sessions.

So the brief's JWT requirement and the chosen stack are now in conflict, and this ADR
records the resolution rather than leaving the contradiction undocumented.

The underlying **intent** of the brief's decision is worth stating precisely, because that
is what must survive: *a stolen browser session must not hand an attacker a long-lived,
ungovernable credential.* JWT in `localStorage` fails that intent because any XSS can
exfiltrate it.

## Decision

The admin panel **is Django admin**. Authentication is:

1. **Password**, hashed with **Argon2id** (`argon2-cffi` behind Django's
   `Argon2PasswordHasher`).
2. **Server-side session** in an `httpOnly`, `Secure`, `SameSite=Lax` cookie. Django stores
   only a session key client-side; session contents live in the database.
3. **TOTP** as a second factor for every account with the `admin` group
   (`django-otp`), with single-use recovery codes.
4. **CSRF** protection on every mutating request (Django middleware, on by default).
5. **Login throttling** — lockout after N consecutive failures, with exponential backoff.
6. **No public admin sign-up.** The first administrator is created by a Django management
   command (`createsuperuser` wrapped as a documented seed command), never over the API.

> **Correction (2026-10-05):** the package originally named in this ADR, `django-argon2`,
> does not exist on PyPI. The implementation uses **`argon2-cffi`**, the library Django's
> `Argon2PasswordHasher` binds to. The decision — Argon2id — is unchanged.

**Consequences for the brief's requirements:**

| Brief §9 requirement | Resolution |
|---|---|
| Argon2id passwords | Kept — `argon2-cffi` |
| TOTP MFA for administrators | Kept — `django-otp` |
| Tokens in `httpOnly` cookies, never `localStorage` | Kept and strengthened — a session cookie holds no bearer token at all |
| Short access token + rotating refresh token | **Dropped.** No token is issued, so none can leak. Sessions are revoked centrally, which is strictly better than rotation |
| RBAC checked server-side on every request | Kept — Django permissions + middleware; admin UI hiding is never the control |
| Audit every approval, rejection, config change | Kept — `audit_logs` via signals |
| Login attempt limits and temporary lockout | Kept |
| Secrets only in environment variables | Kept — Django settings from env |

**JWT is not used anywhere in this project.** The public API is anonymous read plus
anonymous submission; there is no third-party or mobile client that would need a token.

## Consequences

**Positive**
- Satisfies the brief's security intent more strongly than JWT did: there is no bearer
  credential in the browser at all, and revocation is immediate and central.
- Removes an entire class of failure — refresh rotation races, token reuse detection,
  clock skew — from a project with no need for it.
- Session storage is in PostgreSQL, so an admin can be logged out centrally, which is
  required by the incident-response requirements in the threat model.
- The React app never handles authentication, so no token ever crosses the JS boundary.

**Negative**
- **This deviates from the brief.** The brief's §6 decision 8 and part of §9 explicitly
  specified JWT with rotating refresh tokens. The brief should be updated to record the
  change; §20's open items do not currently capture it.
- Database-backed sessions add a read on every authenticated admin request. Irrelevant at
  this scale.
- If a future mobile or third-party client is added, a token scheme will be needed then,
  and it should be designed at that point rather than carried speculatively now.

## Alternatives considered

- **JWT with rotating refresh tokens, as the brief specifies.** Rejected: it requires a
  React admin panel (ADR 0005 alternative in ADR 0009) plus refresh rotation, reuse
  detection, and revocation lists — all to protect a credential that a session cookie
  avoids entirely.
- **Django admin plus a React admin panel.** Rejected: two admin interfaces to build,
  document, and keep consistent, for one operator.
- **Django admin without TOTP.** Rejected: the brief requires MFA for administrators, and
  a single-operator site is exactly the account worth protecting.

## Action required

Update `docs/00-contexto-proyecto.md` §6 decision 8 and §9 to reflect this decision, and
move it out of §20 as resolved.