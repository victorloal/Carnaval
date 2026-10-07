# Sprint 20 — Retention enforcement and the data-subject procedure

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** the retention periods ADR 0018 set are **enforced by code**, not merely
  written down, and the data-subject procedure exists and its deletion path has been
  rehearsed. Personal data that outlives its justification is deleted or cleared.
- **Starts:** after Sprint 19; nominal 1 week.
- **WIP limit:** 2 items (ADR 0001)
- **Status:** delivered.

> Naming a retention period without a purge job enforces nothing. This sprint is the job.

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | `purge_personal_data` clears/deletes past the ADR 0018 periods | PRV-03 | tests | Done |
| 2 | The audit trail is exempt by design (append-only, salted hashes only) | FR-D-09 | test | Done |
| 3 | The data-subject access/rectification/deletion procedure is documented and its deletion path rehearsed | PRV-07 | demonstration | Done |
| 4 | `--dry-run` reports what would be purged without touching anything | PRV-03 | test | Done |

### What is purged, and what is deliberately not

A new `carnaval.privacy` app owns one command. It clears a submission's contact email 12
months after the submission was decided, deletes `consent_records` after 24 months, clears a
takedown requester's email 24 months after `responded_at`, and prunes `ingestion_runs` after a
year. A submission that is still `pending` keeps its email: it has not been decided, so its
clock has not started.

**`audit_logs` is never purged.** The append-only guarantee (FR-D-09) is a hard constraint and
the trail holds only salted hashes, so its evidence value outweighs the period. That exception
is stated in the privacy policy and in ADR 0018 rather than silently applied.

### The procedure is more than the job

Access and rectification are Django-admin operations on the personal fields; deletion is the
purge command for time-based removal and a hard delete on request. The documented procedure
(privacy policy §6: channel, 15 business-day response, best-effort identification) is the
other half of PRV-07; the job's tests are the rehearsal of the deletion path.

## What must be true when it ends

1. Every period in the policy has a mechanism, except the stated append-only exception.
2. `--dry-run` changes nothing; a real run is atomic.
3. `ruff`/`mypy`/`pytest`/`makemigrations --check`/`check --deploy` green; no OpenAPI drift.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | Six tests cover each period, the dry run and the audit exemption |
| Documentation updated | `CHANGELOG.md`, `MEMORY.md`, the matrix, the policy and ADR 0018 |
| CI green | Both jobs |
| Linked in the matrix | PRV-03 and PRV-07 → Done |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| Scheduling the purge job in production | Needs the deployed scheduler (Sprint 17) |
| Consent-gated video embeds (PRV-08) | No embed UI yet |
