# Sprint 15 — Submission intake

- **Sprint length:** 2 weeks (Scrumban, ADR 0001) — split if needed
- **Sprint goal:** A visitor can submit an **image** or a **video link** with no account.
  Every upload is validated by content, re-encoded, stripped of metadata, stored in
  quarantine and tied to a consented legal-text version. Abuse is bounded. Nothing is public.
- **Starts:** after Sprint 14 closes; the v3 gate was settled by ADR 0018 on 2026-10-07; nominal 2 weeks.
- **WIP limit:** 2 items (ADR 0001)
- **Status:** the submission **backend** is delivered (models, validation, endpoints, quotas);
  the declared/detected mismatch (FR-F-04) and **duplicate detection** (FR-F-21) landed in
  Sprint 18. The **signed-URL transfer** (SEC-13) is carried, and the Turnstile provider
  itself is unverified.

> **Gate — settled 2026-10-07.** `ADR 0008` gated public submissions behind *reviewed* legal
> documents; `ADR 0016` permanently declined professional review. **`ADR 0018` amends the
> gate**: v3 ships under the labelled drafts, with retention and takedown deadlines set as the
> maintainer's operational defaults. The form may be built; its consent copy must state that
> the accepted text is an unreviewed draft.

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | Anonymous image and video-link submission form | FR-F-01, FR-F-02 | tests | Done |
| 2 | Magic-byte validation against a JPEG/PNG/WebP allowlist; declared/detected mismatch rejected | FR-F-03, FR-F-04, SEC-11 | tests | Done |
| 3 | Full decode and re-encode, stripping embedded payloads | FR-F-05 | test | Done |
| 4 | EXIF stripped unconditionally, including GPS, with no config to retain it | FR-F-06, PRV-04 | test | Done |
| 5 | Quarantine storage, not publicly readable; written via a short-lived signed URL | FR-F-07, SEC-12, SEC-13 | test | Private quarantine Done; signed URL carried |
| 6 | Consent checkbox unchecked by default and blocking; `ConsentRecord` bound to the exact legal version | FR-F-10, FR-F-11, PRV-05 | tests | Done |
| 7 | CAPTCHA + honeypot; per-IP counts, size limits, global daily pending quota | FR-F-16, FR-F-17, SEC-14 | tests | Done (Turnstile provider unverified) |
| 8 | Only a **salted** IP hash is stored; no raw IP anywhere, including logs | FR-F-12, PRV-01, PRV-02 | test | Done |
| 9 | Video links restricted to YouTube/Vimeo, normalised to provider + id; the URL is never an embed `src` | FR-F-02, FR-F-19, ADR 0007 | test | Done |
| 10 | Status lookup by unguessable `public_token`; an invalid token reveals nothing | FR-F-18 | test | Done |
| 11 | Duplicate submissions detected by content hash and flagged for the reviewer | FR-F-21 | test | Done |
| 12 | Submissions enter the moderation queue as `pending`, `origin = community` | FR-F-22, LEG-01 | test | Done |

### The main attack surface

Image processing is the primary one. Pillow runs with limits; the pipeline decodes and
re-encodes rather than trusting the declared type or dimensions; a file that will not decode
is refused.

## What must be true when it ends

1. Every upload is validated by content, re-encoded and EXIF-stripped; quarantine is private.
2. Only a salted IP hash is stored; no raw IP in any table or log.
3. Consent is blocking and bound to an exact legal version.
4. Anti-abuse limits and CAPTCHA are enforced and tested.
5. Video links are normalised; no raw URL is ever an embed source.
6. `ruff`/`mypy`/`pytest`/`makemigrations --check`/`check --deploy` green.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | Each validation, the privacy rule, quotas and the token lookup are tested |
| Documentation updated | `modelo-datos.md` §6, `autenticacion.md`/`despliegue.md` storage notes, `CHANGELOG.md`, the gate ADR |
| CI green | Fixtures generated locally, never committed binaries |
| Linked in the matrix | FR-F-01…08/10…17/19/21/22, SEC-11…14, PRV-01/02/04/05 |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| Approving submissions, moving files to public storage | Sprint 16 |
| Takedown and legal-document versioning | Sprint 16 |
| Any change to the programme, news or gallery | Frozen at v2 |

## Risks

1. **Legal exposure is the whole point of the gate** — do not start without it settled.
2. **Image processing is the main attack surface** — decode-and-reencode, never trust input.
3. **Free-tier storage egress** — signed URLs and private buckets keep egress bounded.
4. **Scope** — split intake (this sprint) from approval/storage-move (Sprint 16) if needed.

## Carried into the next sprint

1. Submission moderation, the quarantine-to-public move, takedown and legal versioning.
