# Sprint 16 — Submission moderation, public storage and takedown

- **Sprint length:** 2 weeks (Scrumban, ADR 0001) — split if needed
- **Sprint goal:** An approved submission becomes a public, cited `media_asset` moved out of
  quarantine; rejected uploads are handled per policy; legal documents are versioned; and a
  takedown channel can actually pull content and answer a claim.
- **Starts:** after Sprint 15 closes; nominal 2 weeks.
- **WIP limit:** 2 items (ADR 0001)

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | Approval moves the object from quarantine to public storage and creates a lawful `MediaAsset` | FR-F-09, ADR 0006 | test | Open |
| 2 | Rejected uploads deleted or retained per a configurable policy, with the outcome recorded | FR-C-10 | test | Open |
| 3 | `LegalDocument` versioned; one current version per `(doc_type, locale)` via a partial unique index | FR-G-01 | test | Open |
| 4 | A published legal version is never edited in place; a change is a new version | FR-G-02 | test | Open |
| 5 | Public takedown channel with a contact placeholder; claim types recorded | FR-G-03, FR-G-04 | test | Open |
| 6 | `illegal_content` sets `escalated` and is never closed by an internal note alone | FR-G-05 | test | Open |
| 7 | `action_taken` and `responded_at` recorded for every request | FR-G-06 | test | Open |
| 8 | Video takedown removes the reference and contacts the provider | FR-G-07 | test | Open |
| 9 | PII (`requester_email`, `contact_email`) with a retention deadline and a purge action | PRV-03, PRV-07 | test | Open |
| 10 | Consent-gated embeds; no advertising or tracking cookies | PRV-08 | inspection | Open |
| 11 | `Cache-Control` so responses with personal data are not shared-cached | PRV-09 | test | Open |
| 12 | Status lookup returns the recorded reason for a rejection | FR-F-18 | test | Open |

### The move is the moment a file can leak

Approval is the only path from quarantine to public. Before approval no public key exists;
after approval the private key is cleared. The move is tested for the pre-approval state, not
assumed.

## What must be true when it ends

1. Approval is the only path from quarantine to public, and it creates a lawful `MediaAsset`.
2. Legal documents are versioned and immutable once current.
3. Takedown requests are recorded, escalated where required, and answered with a recorded
   action.
4. PII has a retention deadline and a purge path; no tracking cookies; consent-gated embeds.
5. `ruff`/`mypy`/`pytest`/`check --deploy` green; matrix rows updated (PRV-06 marked blocked
   where ADR 0016 applies).

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | The storage move, immutability, escalation, PII purge and cache rule are tested |
| Documentation updated | `modelo-datos.md` §6.4–6.6, `docs/legal/`, `CHANGELOG.md` |
| CI green | PostgreSQL service for the partial unique index; storage mocked with fixtures |
| Linked in the matrix | FR-C-10, FR-F-09/18, FR-G-01…07, PRV-03/06/07/08/09 |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| New intake behaviour | Sprint 15 (done) |
| Legal review | Never (ADR 0016); drafts are labelled, limitations stated |

## Risks

1. **Moving objects between buckets is where a file can leak** — tested for the pre-approval
   state.
2. **Legal drafts are drafts (ADR 0016)** — the takedown procedure has no deadline; the
   limitation stays stated on the site, not hidden.
3. **Scope** — approval/storage-move and takedown/legal can be two sprints; the storage move is
   the release-critical half.

## Carried into the next sprint

1. v3 hardening, privacy procedures, full security sweep and launch.
