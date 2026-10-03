# User stories

- **Status:** Draft
- **Date:** 2026-10-03
- **Relates to:** `docs/01-requisitos/srs.md`, `docs/00-acta-proyecto.md` §4 (stakeholders)
- **Convention:** MoSCoW per version, per ADR 0008. IDs are stable; never renumber.

Each story cites the SRS requirements it satisfies. Every story needs at least one
verification method recorded in `matriz-trazabilidad.md` before it can be called done
(ADR 0001).

Acceptance criteria are written as testable statements. "No" in the last line of a story
marks an explicit non-goal, so scope creep is visible at the point of writing.

---

## 1. Visitor — reading the programme (MVP)

### US-01 — Browse editions
> As a visitor I want to see which years of the parade are available so I know what I can
> read about.

- Covers: FR-A-01, FR-A-10
- Priority: **Must** · MVP
- Acceptance:
  - Only editions flagged `is_published` appear.
  - Each entry shows year and localised title.
  - A withheld edition returns 404 at its URL and is absent from any listing.
- Not: editing or previewing an unpublished edition.

### US-02 — Read the programme by day
> As a visitor I want the programme grouped by day so I can plan which day to attend.

- Covers: FR-A-02, FR-A-08, FR-A-04
- Priority: **Must** · MVP
- Acceptance:
  - Days render in chronological order; events in `sort_order` within a day.
  - The five canonical January milestones (2–6 Jan) display with their correct names.
  - A day with no events still renders, with an explicit empty state.
- Not: filtering by time of day.

### US-03 — See where and when an event happens
> As a visitor I want the venue and times on each programme entry so I can find it.

- Covers: FR-A-03, FR-A-05, FR-A-07
- Priority: **Must** · MVP
- Acceptance:
  - Missing venue or time renders as an explicit absence, never as a placeholder value.
  - Venue address and coordinates display when present.
- Not: a map view or directions integration (v3+, not planned).

### US-04 — Verify where the information came from
> As a visitor I want to see the source of every programme entry so I can judge whether to
> trust it.

- Covers: FR-A-12, FR-A-09, LEG-08, LEG-10
- Priority: **Must** · MVP
- Acceptance:
  - Every programme entry links to its source URL.
  - The unofficial / not-affiliated disclaimer is visible on every page, including error
    pages.
- Not: a full citation bibliography in the MVP.

### US-05 — Use the site on a phone
> As a visitor on a phone I want the site to be usable without zooming so I can read it
> while standing in the street.

- Covers: FR-A-13, NFR-03, NFR-04
- Priority: **Must** · MVP
- Acceptance:
  - Usable at 360 px with no horizontal scrolling.
  - Passes automated axe checks with no critical violations.
  - Keyboard-navigable with a visible focus indicator.
- Not: a native app (out of scope per brief §4).

### US-06 — Read the site in Spanish or English
> As a visitor I want to read the site in my language so I understand it.

- Covers: FR-H-01 … FR-H-05, FR-H-10
- Priority: **Must** · MVP
- Acceptance:
  - `/es/…` and `/en/…` render the same content in the respective language.
  - Every user-facing string exists in both locales; a missing key fails the build.
  - A locale switch preserves the current page and persists the choice in a cookie.
  - The root redirects to the negotiated locale, defaulting to `es`.
- Not: a third language.

---

## 2. Moderator — review and configuration (v1)

### US-07 — Review scraped content before it is public
> As the moderator I want to approve or reject everything the pipeline extracts so nothing
> unverified reaches the public.

- Covers: FR-C-01 … FR-C-07, FR-C-09, LEG-01
- Priority: **Must** · v1
- Acceptance:
  - Every ingested record appears in the queue as `pending` with its source URL and raw
    payload available for comparison.
  - Approving sets `status = published`, `reviewed_by`, `reviewed_at`.
  - Rejecting requires a non-empty `rejection_reason`.
  - Each decision appends a `moderation_actions` row.
- Not: approving without looking at the source.

### US-08 — Unpublish content that turns out to be wrong
> As the moderator I want to withdraw a published item so I can correct a mistake without
> deleting the record.

- Covers: FR-C-05
- Priority: **Must** · v1
- Acceptance:
  - `published → pending` is possible and is recorded as a deliberate action.
  - The item disappears from the public API immediately.
  - The transition is audited.
- Not: hard-deleting content.

### US-09 — Work in the queue efficiently
> As the moderator reviewing many records I want to filter and bulk-approve so a large
> import does not take hours.

- Covers: FR-C-06, FR-C-11
- Priority: Must / Should · v1
- Acceptance:
  - The queue filters by `status`, `origin`, and content type.
  - Bulk approval records each decision individually in `moderation_actions`.
- Not: auto-publishing without review (FR-C-08 stays off by default).

### US-10 — Trust that roles are enforced
> As the moderator I want a viewer account to be unable to approve anything so I can give
> read-only access safely.

- Covers: FR-D-02 … FR-D-07, FR-D-09, SEC-04, SEC-09, SEC-10
- Priority: **Must** · v1
- Acceptance:
  - `viewer` cannot reach any state transition, by any route including direct URL and API.
  - `editor` cannot reach site configuration, user management, or legal documents.
  - Only `admin` can manage users, roles, settings, scrape sources, legal versions.
  - No role can modify or delete an `audit_logs` row.
  - Every `admin` account requires TOTP.
- Not: a per-object permission model beyond the role matrix.

### US-11 — See who changed what
> As the moderator I want an audit trail so I can answer "who published this, and when?"

- Covers: FR-D-08, FR-D-10, SEC-08
- Priority: **Must** · v1
- Acceptance:
  - Every approval, rejection, unpublish, settings change, login, and failed login produces
    an `audit_logs` row with actor, action, object, timestamp, and hashed IP.
  - The table is append-only for every role including `admin`.
  - An administrator can revoke all sessions for an account centrally.
- Not: analytics or usage reporting.

### US-12 — Keep the site usable when a source breaks
> As the moderator I want to know when a source has stopped working so I can fix it or fall
> back to manual entry.

- Covers: FR-D-12, FR-B-10, FR-B-11
- Priority: **Must** · v1
- Acceptance:
  - Admin shows each source's active flag, consecutive failures, last success, last error.
  - After N consecutive failures the source auto-disables and an alert is raised.
  - A source that returns HTTP 200 but extracts zero records raises an alarm.
- Not: automatic recovery without review.

### US-13 — Enter content by hand
> As the moderator I want to author records manually so the site stays useful when
> scraping is impossible.

- Covers: FR-A-03 (manual path), FR-C-01 (`origin = manual`)
- Priority: **Must** · v1
- Acceptance:
  - A record created by hand stores `origin = manual` and `created_by`, enters as
    `pending`, and publishes the same way as a scraped record.
  - Losing the scraper does not affect this path.
- Not: bulk CSV import (not planned).

---

## 3. Ingestion operations (MVP / v1)

### US-14 — Run the pipeline on a schedule
> As the moderator I want the pipeline to run unattended so the site updates without me
> remembering to trigger it.

- Covers: FR-B-01 … FR-B-09, FR-B-17
- Priority: **Must** · MVP
- Acceptance:
  - GitHub Actions `cron` invokes a Django management command.
  - Running the pipeline twice produces zero duplicates.
  - A fetch whose `content_hash` already exists is a recorded no-op.
  - Each run produces an `ingestion_runs` row with per-stage statistics.
- Not: a resident worker process.

### US-15 — Never lose published content to a pipeline failure
> As the moderator I want a failed extraction to leave the live site untouched so visitors
> never see an empty page.

- Covers: FR-B-09, NFR-06
- Priority: **Must** · MVP
- Acceptance:
  - A failed run modifies or deletes no `published` record.
  - The public API serves the last good data with no code change.
- Not: automatic rollback of a bad *successful* extraction — that is a manual decision.

### US-16 — Configure a source
> As the moderator I want to add or disable a source from the admin so I do not need a
> deployment to change ingestion.

- Covers: FR-B-12, FR-D-07
- Priority: **Must** · MVP
- Acceptance:
  - URL, type, active flag, rate-limit interval, and cron schedule are editable.
  - Changes are written to `audit_logs` with before/after values.
- Not: arbitrary code execution from the admin (selectors are data, not code).

### US-17 — Re-run a single source
> As the moderator I want to trigger one source manually so I can recover a failed run
> without waiting for the schedule.

- Covers: FR-B-18
- Priority: **Should** · v1
- Acceptance: an Editor or Administrator can run one source on demand; the run is recorded
  with `trigger = manual`.
- Not: cancelling an in-flight run.

---

## 4. Editorial content (v2)

### US-18 — Browse news with attribution
> As a visitor I want to read news items about the parade, each linked to its source, so I
> can follow a story without the site pretending to be the publisher.

- Covers: FR-E-01, FR-E-02, FR-E-03, LEG-04
- Priority: **Must** · v2
- Acceptance:
  - Each item shows headline, outlet, date, a short original summary, and a link out.
  - No full article text or article image is stored or served.
  - Items follow the same review path as everything else.
- Not: archiving full articles.

### US-19 — Browse the historical gallery with citations
> As a visitor I want to see old photographs with a clear credit line so I know who took
> them and can cite them myself.

- Covers: FR-E-04, FR-E-05, FR-E-06, FR-E-07, FR-E-09, LEG-02, LEG-03, LEG-09
- Priority: **Must** · v2
- Acceptance:
  - Citation text is displayed with every image.
  - An asset with `rights_status = unknown` is never published by any path, including a
    bulk operation or a direct ORM write.
  - An asset flagged `minor_subject` without `guardian_consent_on_file` cannot be
    published.
  - Duplicate bytes are refused.
  - EXIF stripping is re-verified at approval time.
- Not: an asset with unknown rights shown as a teaser.

### US-20 — Configure the site without a deployment
> As the moderator I want to edit site settings in the admin so small changes do not need
> a release.

- Covers: FR-E-10, FR-E-11, FR-E-12
- Priority: **Must** · v2
- Acceptance:
  - Typed key/value settings are editable; every change is audited with before/after.
  - Secrets cannot be stored here.
- Not: storing credentials or API tokens.

### US-21 — Find something with search
> As a visitor I want to search the site so I can find a specific name or event.

- Covers: FR-I-01, FR-I-02, FR-I-03
- Priority: **Should** · v2
- Acceptance: search covers published events and news only, using PostgreSQL full-text
  search with no paid external service.
- Not: fuzzy matching or an external search product.

---

## 5. Community contributions (v3)

### US-22 — Contribute a photograph without registering
> As a member of the community I want to send an old photograph without creating an
> account so contributing is not a barrier.

- Covers: FR-F-01, FR-F-03 … FR-F-07, FR-F-10, FR-F-13, FR-F-14, FR-F-17, FR-F-22
- Priority: **Must** · v3
- Acceptance:
  - No account, no email requirement for the basic path.
  - The file is validated by magic bytes; a renamed executable is rejected.
  - EXIF and GPS are stripped and verified by reading the stored object back.
  - The file is not publicly readable before approval.
  - The terms checkbox is unchecked by default and blocks submission.
  - The submission arrives as `pending`.
- Not: immediate publication, ever.

### US-23 — Declare rights honestly
> As a contributor I want to state that I am the author or have permission, so the site
> does not publish something it has no right to use.

- Covers: FR-F-13, FR-F-14, FR-F-11, PRV-05
- Priority: **Must** · v3
- Acceptance:
  - A `consent_records` row binds the submission to the exact legal version accepted.
  - Declared author, year, place, and description are stored.
- Not: a rights declaration that is not recorded.

### US-24 — Contribute a video link
> As a member of the community I want to link a video that is already hosted elsewhere so
> parade footage can be included without the site storing video.

- Covers: FR-F-02, FR-F-19, FR-G-07
- Priority: **Must** · v3
- Acceptance:
  - Only YouTube and Vimeo links are accepted, normalised to provider + video id.
  - The submitted URL is never used directly as an embed source.
  - Any attempt to upload a video file is rejected.
- Not: hosting, transcoding, or downloading video.

### US-25 — Check my submission's status
> As a contributor I want to know whether my photograph was accepted, without an account.

- Covers: FR-F-18
- Priority: **Should** · v3
- Acceptance: an unguessable token shows status and, when rejected, the reason.
- Not: an account, notifications by email, or a public contributor profile.

### US-26 — Moderate a community contribution
> As the moderator I want to review anonymous uploads with all the context I need, so I
> can approve or reject responsibly.

- Covers: FR-C-09, FR-F-09, FR-F-10, FR-F-21, F-15 via LEG-09, PRV-01
- Priority: **Must** · v3
- Acceptance:
  - The queue shows the declaration, consent version, and detected type alongside the
    image.
  - Approval moves the object from quarantine to the public bucket and creates an approved
    `media_assets` record.
  - Rejection requires a reason and deletes or retains per policy, recorded either way.
  - Duplicate submissions are flagged.
- Not: approving without reading the declaration.

---

## 6. Legal, privacy, and takedown (v3)

### US-27 — Understand what happens to my data
> As a visitor I want to know what is collected and why, so I can decide whether to submit
> anything.

- Covers: PRV-01, PRV-03, PRV-04, PRV-06, PRV-08, FR-G-01, FR-G-02, FR-G-03
- Priority: **Must** · v3
- Acceptance:
  - Terms, privacy policy, content policy, and takedown procedure are published and
    versioned, one current version per type and locale.
  - A published document is never edited in place.
  - The privacy policy names the data categories, purposes, and retention deadlines.
- Not: publishing final legal text without professional review (drafts only, brief §11).

### US-28 — Have my content removed
> As a photographer or subject I want to request removal of my image, and have it actually
> removed.

- Covers: FR-G-04, FR-G-06, LEG-02
- Priority: **Must** · v3
- Acceptance:
  - A takedown request records claim type, evidence, and timestamps.
  - `action_taken` and `responded_at` are recorded for every request.
  - A removal takes the item out of the public API without deleting the audit trail.
- Not: removing content without recording why.

### US-29 — Report illegal content
> As a member of the public I want illegal content reported to the authorities, not just
> quietly hidden.

- Covers: FR-G-05
- Priority: **Must** · v3
- Acceptance:
  - An `illegal_content` claim sets status `escalated`.
  - The case cannot be closed by an internal note alone.
  - Escalation to the competent authority or a line such as Te Protejo is recorded.
- Not: redistributing or re-hosting the material in the process.

### US-30 — Revoke access to my data
> As a data subject I want to exercise my rights under Ley 1581 de 2012, so the site
> complies with Colombian data-protection law.

- Covers: PRV-07, PRV-03
- Priority: **Must** · v3
- Acceptance:
  - A documented procedure handles access, rectification, and deletion requests.
  - Contributor email is deleted once the matter closes and no reply is owed.
- Not: automated self-service data export (not planned).

---

## 7. Operations (MVP / v1)

### US-31 — Know whether the site is up
> As the moderator I want a health check so I can tell a broken site from a broken pipeline.

- Covers: FR-D-11
- Priority: **Must** · MVP
- Acceptance: `/health` reports application and database reachability without leaking
  internals.
- Not: a public status page.

### US-32 — Recover from a bad deploy
> As the moderator I want to restore the database and roll back a bad release so a mistake
> is not permanent.

- Covers: NFR-13, NFR-20
- Priority: **Must** · v1
- Acceptance: a documented backup and restore procedure exists and has been rehearsed; a
  migration rollback path is documented.
- Not: a blue/green deployment (free tiers rarely allow two live versions).

---

## Coverage check

| SRS group | Stories covering it |
|---|---|
| FR-A Catalogue | US-01 … US-05 |
| FR-B Pipeline | US-14 … US-17 |
| FR-C Moderation | US-07, US-08, US-09, US-26 |
| FR-D Admin, roles, audit | US-10, US-11, US-12, US-13 |
| FR-E Editorial | US-18, US-19, US-20 |
| FR-F Submissions | US-22 … US-26 |
| FR-G Legal | US-27, US-28, US-29 |
| FR-H i18n | US-06 |
| FR-I Search | US-21 |
| NFR / SEC / PRV / LEG | US-05, US-10, US-15, US-19, US-22, US-26, US-27, US-30, US-32 |

Requirements with no story yet, to be covered before their version ships:
FR-A-11 (filtering by edition and date), FR-A-10 previewing a withheld edition,
FR-C-08 (auto-publish rules), FR-B-16 (raw retention), FR-H-06/H-07 (database translation
fallback and per-locale slugs), NFR-02 (API latency budget), NFR-17 (API rate limiting).
Most are Should-priority; each needs either a story or a recorded decision to defer.