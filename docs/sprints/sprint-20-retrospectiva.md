# Sprint 20 retrospective — retention enforcement and the data-subject procedure

- **Date:** 2026-10-07
- **Sprint:** 20 — Retention enforcement and the data-subject procedure
- **Method:** Start / Stop / Continue.
- **Note:** third of the four close-out sprints (18–21); see also
  `sprint-18-21-retrospectiva.md`.

## What was planned versus what happened

Planned: make the retention periods ADR 0018 set **true in code**, not merely written down, and
provide a documented data-subject procedure whose deletion path has been rehearsed.

What happened: **all four items landed and CI is green on `a2b9769`.** The suite reached **141
backend tests.** The matrix moved **PRV-03 and PRV-07 to Done.**

Delivered: a new `carnaval.privacy` app with `purge_personal_data`, which clears a submission's
contact email 12 months after the submission is decided, deletes `consent_records` after 24
months, clears a takedown requester's email 24 months after `responded_at`, and prunes
`ingestion_runs` after a year; a `--dry-run` that reports without changing anything; and the
data-subject procedure documented in the privacy policy §6 (channel, 15 business-day response,
best-effort identification).

## Start

- **Enforce the number, do not publish it.** The privacy policy named the periods in Sprint 18;
  this sprint wrote the job that makes them true. A period without a mechanism is a promise.
- **A pending submission keeps its email.** Its clock has not started until it is decided, so
  the filter keys on `reviewed_at`, not on creation.
- **The dry run is a first-class path.** Being able to see what *would* be purged is what makes
  the job safe to run against real data.
- **Deletion is atomic.** The mutations run in one transaction, so a failure cannot leave
  personal data half-cleared.

## Stop

- **`audit_logs` cannot be purged, and that is a real conflict.** The retention table named a
  period, but the audit trail is **append-only** (FR-D-09) and holds only salted hashes. The
  resolution is stated, not silent: the purge job never touches it, and ADR 0018 and the privacy
  policy say so. An append-only guarantee outranks a retention period.
- **Naming a period is not enforcing it.** PRV-07 was only closed after the deletion path had a
  rehearsal (the job's tests); documentation alone would not have been enough.
- **The job is not scheduled in production.** It exists and is tested; running it on a clock is
  a deployment concern, carried with the scheduler (FR-B-17).

## Continue

- **State the exception where a reader will look for it.** The audit-log exception is in the
  policy and the ADR, not buried in the command.
- **Keep the purged data minimal.** The command clears or deletes; it never anonymises by
  keeping a richer record.

## What the sprint proved about the project

The privacy commitments became operational: the site now deletes personal data when its
justification ends, and the one thing it does not delete — the audit trail — is exactly the one
thing that is append-only and non-reversible by design. The exception is documented rather than
discovered.

## Concrete changes adopted

1. Retention is enforced by a command tested per period, with a dry-run.
2. The append-only audit trail is an explicit, documented exception to retention.
3. A still-pending submission's clock starts when it is decided, not when it arrives.
