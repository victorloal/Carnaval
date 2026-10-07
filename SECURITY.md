# Security policy

## Read this first: the code is built, but nothing is running

**No version of this software has been released, and nothing is deployed. There is no public
site, no API and no admin panel reachable by anyone.** The backend and the public site are
fully implemented and tested in CI (`backend/` and `frontend/`), but the **deployment is
carried**: it needs the maintainer's accounts and a host (ADR 0015 is Proposed).

This file therefore describes two things and keeps them apart: the posture the project has
**implemented** (the controls have tests), and the part that is a **decision to be exercised at
deployment** (HTTPS, backups, the production scheduler). Where a control is implemented, the
test is the evidence; where it is not, this file says so rather than implying a running system.

If you are looking for the reasoning rather than the summary:

| Document | What it holds |
|---|---|
| `docs/02-diseno/modelo-amenazas.md` | STRIDE threat model, per-element, with accepted risks and rationale |
| `docs/02-diseno/autenticacion.md` | Sessions, TOTP, RBAC, session lifecycle |
| `docs/02-diseno/roles-permisos.md` | Roles and permissions |
| `docs/03-pruebas/casos-seguridad.md` | **74 security test cases**, `SEC-01` … `SEC-74` |
| `docs/adr/0005`, `0006`, `0007`, `0009`, `0011` | The decisions the controls come from |

## Supported versions

| Version | Supported |
|---|---|
| anything after `v0.1.0` | not released yet |
| `main` | **not a released version.** A moving target; report against a commit, not against `main` |

Nothing is supported, because nothing has shipped. When releases begin, this table is the
one that says which ones still get fixes, and it will be filled in **before** the first
release rather than after.

## Reporting a vulnerability

**Email `victorloal513@gmail.com`. Do not open a public issue**, and do not open a pull
request — a public issue is a disclosure, not a report.

Please include:

- what you found, in one sentence,
- how to reproduce it — the exact request, or the steps,
- the impact you believe it has, and who it affects,
- anything you already tried, so it is not re-tested.

What to expect, stated honestly:

- **No SLA and no 24-hour response.** This is one person, part-time, with a day job. A reply
  may take a few days. If it takes longer than that, the address is probably in a spam folder
  — the published contact is the same address used for takedown requests, so treat it as
  sensitive rather than disposable.
- **No bug bounty.** There is no programme and no budget. Reporting a genuine vulnerability
  gets acknowledgement and a fix, not payment. Do not report a vulnerability expecting money.
- **No encrypted channel.** There is no PGP key. Send plain text, no attachments. If you
  believe a report must not transit ordinary email, say so in the first line and a working
  alternative will be arranged.
- **Good-faith reports are welcome**, including from people who found something casually
  rather than by hunting. Do not access data that is not yours, do not test against live
  systems once one exists without saying so, and do not build tooling that impairs the site
  for others.

### What happens next

1. **Acknowledged.** The report is triaged into: real and serious, real and minor, not a
   vulnerability, or already known.
2. **Confirmed or dismissed**, with the reasoning given either way. A dismissal without a
   reason is not acceptable; if the reasoning is thin, push back.
3. **Fixed**, or the risk is documented in `docs/02-diseno/modelo-amenazas.md` §7 if it
   cannot be fixed — with why, not as a way of closing the ticket.
4. **Disclosed** in the commit that fixes it. Commit messages are part of the permanent
   record, and a fix that names the flaw teaches more than a fix that hides it.
5. **Credit**, if you want it, in the commit and in the release notes.

Vulnerabilities affecting **data that has already been taken down on request** are still
reported normally, but the fact that the data was already removed is relevant context and
worth saying.

## What is public, and what is not

**Public by default, deliberately:**

- the entire source, including the admin, the ingestion code and the database schema
- the threat model, including its residual-risk table and the reasoning for each accepted risk
- all 74 security test cases
- the data model, the API contract, and the deployment design
- the audit-log design
- `docs/legal/` — as **unreviewed drafts**, which is what they are (see below)

**Not public until fixed:** the specifics of an unfixed vulnerability, and the address used
to receive reports is not a mechanism — it is published because a security contact that
nobody can find is not a security contact.

## The security model, as implemented

Each control below is **implemented and tested in code**; the ones that need a running system
(HTTPS, backups, the scheduler) are exercised at deployment, not here. Each row names the
source of truth.

| Area | Decision | Source |
|---|---|---|
| Authentication | **Server-side sessions. No JWT, no bearer token, nothing in `localStorage`** | ADR 0005 |
| Session cookie | `httpOnly`, `Secure`, `SameSite`, CSRF-protected. Central revocation is the point | ADR 0005 |
| Second factor | TOTP (`django-otp`), plus single-use hashed recovery codes | ADR 0005 |
| Password hashing | **Argon2id** via `argon2-cffi`. No custom cryptography | ADR 0005 |
| Authorisation | RBAC enforced **server-side on every request**. Never the interface hiding a control | `docs/02-diseno/roles-permisos.md` |
| Admin exposure | A fresh install must not expose unreviewed `pending` content — Django admin ships with full permissions by default, so this needs deliberate work | FR-D-03 |
| Audit | `audit_logs` is **append-only**, for every role including `admin` | SRS |
| Client IPs | **Salted hash only.** An unsalted IPv4 hash is brute-forceable over 2³² candidates, which is why the salt is not optional | SRS |
| Uploads | Validated by **magic bytes, not extension**; fully decoded and re-encoded; **EXIF including GPS stripped unconditionally**; private quarantine until approved | ADR 0006 |
| Storage separation | Quarantine and public storage are **separate buckets on a separate domain** | ADR 0006 |
| Videos | External embeds only. A submitted URL is **never** used directly as an embed `src` | ADR 0007 |
| Copyright | `rights_status = unknown` is **never published**. No full texts, no third-party PDFs or photos committed | ADR 0004 |
| Publishing | **Nothing reaches `published` without human review.** Scraped, manual and community content all land as `pending` | brief §11 |
| Secrets | Environment variables only. Never in the repository | brief §6 |
| API contract | Generated by drf-spectacular; **CI fails on drift** | ADR 0011 |
| Missing translations | Fail the build, do not degrade at runtime | ADR 0010 |
| Migrations | Reviewed in the pull request; `makemigrations --check` gates the build | ADR 0001 |

## Limitations and accepted risks

The honest list. A security policy that only lists what was done is marketing.

### This project cannot give you a verified legal basis

The legal texts in `docs/legal/` are **permanently unreviewed drafts**. A Colombian
data-protection and copyright lawyer will not review them — that was decided on 2026-10-04
and recorded in **ADR 0016**. Every legal page carries a DRAFT notice saying so.

The consequence is not abstract. The privacy notice may be wrong in ways nobody has checked.
Retention periods and takedown deadlines were set as the maintainer's **operational defaults**
(ADR 0018), not legal advice; the **legal basis for each processing activity** and whether a
supervisory registration is required remain **unresolved by decision**. Ley 1581 de 2012
applies to this site's processing whether or not anyone reviewed the words describing it. Do
not rely on those documents. If you need to know what this project does with your data, read
the code and the data model — both are public.

The v3 gate that ADR 0008 placed on public submissions (**reviewed** legal documents) was
**amended by ADR 0018**: submissions ship under the labelled drafts, with moderation, blocking
consent bound to a `legal_documents` version, the takedown register and the DRAFT notices as
the controls that remain.

### Structural risks

- **One person.** A single maintainer, part-time. There is no second operator, no break-glass
  account, and no way to recover from the maintainer being unavailable. This is the largest
  operational risk and no control mitigates it.
- **Free-tier infrastructure, by choice.** Zero cost is a hard constraint. It means no
  managed WAF, no DDoS mitigation worth the name, no premium object storage, and no paid
  monitoring. Providers change free tiers without notice; a re-pricing is an *existence*
  risk, not a cost one. The limits are re-verified before every release, and that check can
  fail.
- **Third-party embeds.** YouTube and Vimeo links mean the visitor's IP address and referrer
  reach those providers. The project cannot see what they log. `youtube-nocookie.com` is used
  where applicable, which reduces but does not remove this.
- **Dependency supply chain.** Python and npm dependencies are pinned by lockfile, but they
  are numerous and the audit tooling is a CI stage, not a guarantee.
- **Scraping a third-party site is itself a legal exposure.** The official site's terms of
  use were never found. That risk was **accepted on 2026-10-04**, and a written permission
  request was sent — unanswered as of the last update. Silence is not permission, and the
  decision is reversible.
- **Free tier database sizes** are small, which is a capacity constraint that can turn into
  an availability one under load.

### Deliberate deviations from the original brief

The brief asked for JWT. **It is not used** — server-side sessions with TOTP replace it, and
central revocation is the reason (ADR 0005). If you were expecting a token-based API, this
is why there isn't one.

## Not in scope

- **Physical security**, and the personal security of the maintainer.
- **Social engineering** of the maintainer — there is one person and they can be persuaded.
  This is a real and unmitigated exposure, not an oversight.
- **Vulnerabilities in third-party services**, including the official Carnaval site, the
  hosting provider, or an embedded video platform. Report those to them. If you think this
  project's *use* of one is unsafe, that is in scope.
- **Legal advice.** Nothing here is legal advice, including this file.
- **Content accuracy, copyright, or takedown disputes** as such — those have a procedure,
  not a security channel. Use the contact in `docs/legal/`.
- **Denial of service.** Report it, but do not attempt to cause one.

## References

- `docs/03-pruebas/casos-seguridad.md` — the 74 cases, `SEC-01` … `SEC-74`
- `docs/02-diseno/modelo-amenazas.md` §7 (residual risk), §8 (accepted risks)
- `docs/02-diseno/despliegue.md` §10 — the pre-launch checklist, including the legal
  DRAFT-notice obligation
- `CONTRIBUTING.md` — contribution and branch conventions
- `docs/comunicacion-corpocarnaval.md` — the organisers' permission request, and what happens
  if the answer is no