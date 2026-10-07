# Sprint 19 — The public submission form

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** a visitor submits an **image** or a **video link** with no account, through
  a form whose rights and consent declarations are unchecked and blocking, and looks the
  submission up later by its token. Nothing is public until a reviewer approves it.
- **Starts:** after the v3 legal gate was settled (ADR 0018, 2026-10-07); nominal 1 week.
- **WIP limit:** 2 items (ADR 0001)
- **Status:** delivered.

> Writes go to the endpoints built in Sprint 15/16. This sprint is the public half: the form,
> the declarations, the honeypot and the status lookup.

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | Anonymous image / video-link form, no account | FR-F-01, FR-F-02 | component | Done |
| 2 | Rights and consent declarations, unchecked and blocking; consent states the text is an unreviewed draft | FR-F-10, FR-F-14, PRV-05 | test | Done |
| 3 | Declaration fields stored: author, year, place, description | FR-F-13 | test | Done |
| 4 | Honeypot mirrored from the server; a filled field is a silent no-op | FR-F-17 | test | Done |
| 5 | Status lookup by unguessable token | FR-F-18 | component | Done |
| 6 | Bilingual copy; the translation-key parity check passes | FR-H-02 | test | Done |

### The two declarations are the form's spine

The consent checkbox is **unchecked by default and blocking** (FR-F-10). Its label states that
the accepted text is an **unreviewed draft**, because a visitor is entitled to know what they
are accepting (ADR 0016 §2, ADR 0018). The client blocks a submit without both declarations;
the server records the `consent_records` row bound to the exact `legal_documents` version
(PRV-05).

### One small backend fix

`POST /api/submissions/` accepted `author` and `description` but ignored `year` and `place`,
so `FR-F-13` was not actually satisfiable from the form. The view now reads them (a
non-numeric year is stored as absent rather than guessed) and the serializer documents them.

## What must be true when it ends

1. The form submits both kinds; the declarations are blocking; a filled honeypot is dropped.
2. The token returned can be used to look the submission up.
3. `ruff`/`mypy`/`pytest`/`makemigrations --check`/`check --deploy` green; the frontend
   `tsc`/eslint/vitest/build green; no OpenAPI drift.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | Form, declarations, honeypot and status have tests; the year/place fix has two |
| Documentation updated | `CHANGELOG.md`, `MEMORY.md`, the matrix, this plan |
| CI green | Both jobs; the regenerated `openapi.yaml` is committed |
| Linked in the matrix | FR-F-13 → Done; the rest were already Done |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| The Turnstile provider | Needs keys; the CAPTCHA is off by default and documented, the honeypot and quotas still apply |
| Signed-URL upload transfer (SEC-13) | Needs object storage |
| Consent-gated video embeds (PRV-08) | No embed UI yet |
| PII purge enforcement (PRV-03/07) | Sprint 20 |
