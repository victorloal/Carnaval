# Sprint 15 retrospective — submission intake

- **Date:** 2026-10-06
- **Sprint:** 15 — Submission intake
- **Method:** Start / Stop / Continue.
- **Note:** delivered with Sprint 16 as the v3 backend (`802edee`); see also
  `sprint-16-retrospectiva.md`.

## What was planned versus what happened

Planned: a visitor can submit an **image** or a **video link** with no account. Every upload is
validated by content, re-encoded, stripped of metadata, stored in quarantine and tied to a
consented legal-text version. Abuse is bounded. Nothing is public.

What happened: **the submission backend landed.** The v3 backend is `802edee` (**126 backend
tests**). The matrix moved **FR-F-01/02/03/05/06/07/10/11/12/14/15/16/17/18/19/22, SEC-11/12/14
and PRV-01/02/04/05 to Done.**

Delivered: a `carnaval.submissions` app — `Submission`, `SubmissionFile` and `ConsentRecord` —
image validation by **magic bytes via Pillow** with a full decode + re-encode that strips EXIF
including GPS (verified, not assumed), video links normalised against a YouTube/Vimeo allowlist
to `(provider, id)`, salted-IP quotas, a honeypot and a Turnstile hook, and the submit/status
endpoints. Consent is bound to the exact current `legal_documents` version.

Carried, and named: the declared/detected mismatch rule (FR-F-04) and duplicate detection
(FR-F-21) — both landed later, in **Sprint 18** — the **signed-URL transfer** (SEC-13), the
**rejected-upload policy** (FR-C-10, done in Sprint 18) and the **quarantine → public move**
(FR-F-09), which needs object storage.

## Start

- **Validate by content, not by name.** Pillow decides the format from the bytes; the file is
  then fully decoded and **re-encoded**, which strips an embedded payload and every EXIF tag.
  The result is re-opened to confirm the metadata is gone.
- **A video is a provider and an id, never a URL.** `normalise_video` returns `(provider, id)`
  from an allowlist, so the submitted URL can never become an embed `src` (ADR 0007).
- **Anti-abuse on the salted hash.** Quotas count the **salted IP hash**; the honeypot and
  quotas are always active even where the CAPTCHA is disabled.
- **Consent is blocking and versioned.** A submission without a `ConsentRecord` bound to a
  specific `legal_documents` row is not a submission, and the checkbox is unchecked by default.

## Stop

- **The CAPTCHA is off by default**, convenient for development and tests and **fail-open in
  production**. It is documented, and the honeypot and quotas still apply, but a deployment that
  forgets to enable it loses a control.
- **`declared_mime` was recorded but not enforced.** FR-F-04 asks for a mismatch to be refused;
  the rule was carried to Sprint 18 rather than guessed, because browsers send imperfect
  content types and the rule needed stating.
- **Several guarantees were structural.** Signed URLs, duplicate refusal and PII purge were
  modelled but not performed; each stayed Open with the reason written.

## Continue

- **Move only what the tests cover.** The mismatch rule, the duplicates and the purge stayed
  Open until their own sprints.
- **Name the fail-open default** rather than leaving it for a reviewer to find.
- **Keep validation pure** so it is unit-testable without a network or a bucket.

## What the sprint proved about the project

The riskiest public surface — an anonymous upload — is processed defensively and cannot reach
the site without review: content-validated, re-encoded, private, consented and `pending`. What
remained was the part that needs a bucket and a browser, and the sprint says so rather than
implying it is done.

## Concrete changes adopted

1. The CAPTCHA's fail-open default is documented and mitigated by the honeypot and quotas.
2. FR-F-04, FR-F-21, FR-C-10, SEC-13 and FR-F-09 stay Open with reasons.
3. The intake stops at the bucket: no half-written storage move.
