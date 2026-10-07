# Sprint 16 retrospective — the v3 backend (15–16: submissions, legal and takedown)

- **Date:** 2026-10-06
- **Sprint:** 15–16, delivered together as the v3 backend
- **Method:** Start / Stop / Continue, plus what actually happened versus what was planned.

## What was planned versus what happened

Planned: anonymous image and video-link submissions, validated by content, re-encoded, stripped
of metadata, stored in quarantine and tied to a consented legal version; anti-abuse; versioned
legal documents and a takedown channel.

What happened: **the v3 backend landed and CI is green on its commit.** The suite is at **126
tests**; `ruff`, `mypy` (148 files), `makemigrations --check`, `check --deploy`, the secret scan
and the generated-schema check are clean. The matrix moved **FR-F-01/02/03/05/06/07/10/11/12/14/15/16/17/18/19/22,
FR-G-01…06, SEC-11/12/14 and PRV-02/04/05 to Done.**

Delivered: a `carnaval.submissions` app — the `Submission`, `SubmissionFile` and `ConsentRecord`
models, image validation by **magic bytes via Pillow** with a full decode + re-encode that strips
EXIF including GPS (verified, not assumed), video links normalised against a YouTube/Vimeo
allowlist, salted-IP quotas, a honeypot and a Turnstile hook, and the submit/status endpoints —
and a `carnaval.legal` app — versioned `LegalDocument`s that are never edited in place, a
`TakedownRequest` register whose illegal-content claims escalate, and a public takedown endpoint.

Carried, with reasons: the **quarantine → public move** and the `MediaAsset` creation on approval
(needs object storage — ADR 0015 is still Proposed), the **rejected-upload policy**, **signed-URL
transfer**, **duplicate detection**, **PII purge**, **consent-gated embeds**, **`Cache-Control`
for personal data**, and every deployment/browser verification.

## Start

- **Validate by content, not by name.** Pillow decides the format from the bytes; the file is
  then fully decoded and **re-encoded**, which is what strips an embedded payload and every EXIF
  tag. The result is re-opened to confirm the metadata is gone rather than trusting the re-encode.
- **A video is a provider and an id, never a URL.** `normalise_video` returns `(provider, id)`
  from an allowlist, so the submitted URL can never become an embed `src` (ADR 0007).
- **Anti-abuse on the salted hash.** Quotas count the **salted IP hash**, and the honeypot and
  quotas are always active even where the CAPTCHA is disabled.
- **A current legal version is immutable.** `LegalDocument.save` refuses to edit a version that
  is current; a change is a new version, so an old consent stays interpretable.

## Stop

- **The CAPTCHA is off by default**, which is convenient for development and tests and
  **fail-open in production**. It is documented, and the honeypot and quotas still apply, but a
  production deployment that forgets `SUBMISSION_CAPTCHA_ENABLED=true` loses a control.
- **The quarantine move is not implemented.** A file is stored privately and approved as a
  `Submission`, but it is not yet moved to public storage and turned into a `MediaAsset`; FR-F-09
  stays Open rather than being faked.
- **`declared_mime` is recorded but not enforced.** FR-F-04 asks for a mismatch to be rejected;
  browsers send imperfect content types, so the decision needs a rule, and it is carried.
- **Several guarantees are only structural.** Signed URLs, duplicate refusal and PII purge are
  modelled but not performed; each stays Open with the reason written.

## Continue

- **Move only what the tests cover.** The move, the policy, the purge and the embeds stayed Open.
- **Name the fail-open default** rather than leaving it to a reviewer to notice.
- **Keep the validation pure** so it is unit-testable without a network or a bucket.

## What the sprint proved about the project

The riskiest public surface — an anonymous upload — is now processed defensively and cannot reach
the site without review: content-validated, re-encoded, private, consented and `pending`. The
legal side is a versioned register with an escalation path, not a page of prose. What remains is
the part that needs a bucket and a browser, and the project says so instead of implying it is
done.

## Concrete changes adopted

1. The CAPTCHA's fail-open default is documented and mitigated by the honeypot and quotas.
2. FR-F-09, FR-F-04, FR-F-21, SEC-13, PRV-03/07/09 and FR-C-10 stay Open with reasons.
3. The v3 backend stops at the bucket: no half-written storage move.
