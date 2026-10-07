# Sprint 09 — Review queue, moderation and the published-change ADR

- **Sprint length:** 1 week (Scrumban, ADR 0001)
- **Sprint goal:** A human decision becomes the only way content is public — approve, reject
  with a reason, unpublish, request changes — each recorded in `moderation_actions` and
  `audit_logs`. This is also where `flujo-datos.md` §5.1 gets its ADR and schema amendment.
- **Starts:** after Sprint 08 closes; nominal 1 week.
- **WIP limit:** 2 items (ADR 0001)
- **Status:** delivered with the second half of Sprint 08 as the **v1 backend**; item 9
  (auto-publish) is `Could` and remains Open. See `sprint-09-retrospectiva.md`.

> Every transition writes **three** things in one transaction: the field update, a
> `moderation_actions` row, and an `audit_logs` row. Nothing reaches `published` without this.

## Sprint backlog

| # | Item | Requirement | Verification | Status |
|---|---|---|---|---|
| 1 | `approve` sets `status = published`, `reviewed_by`, `reviewed_at` | FR-C-03 | test | Done |
| 2 | `reject` requires a non-empty `rejection_reason` (DB `CHECK` already exists) | FR-C-04 | test | Done |
| 3 | `unpublish` returns a published row to `pending`, deliberate and manual | FR-C-05 | test | Done |
| 4 | Every transition writes `moderation_actions` and `audit_logs` atomically | FR-C-07 | SEC test | Done |
| 5 | Queue filterable by `status`, `origin` and type; shows source URL and payload to the right roles | FR-C-06, FR-C-09 | tests | Done |
| 6 | Bulk approval records each decision individually | FR-C-11 | test | Done |
| 7 | **ADR for `flujo-datos.md` §5.1** + `staged_changes` on the mixin; the pipeline proposes, never overwrites | FR-B-07, FR-B-09 | SEC-38 | Done (ADR 0017) |
| 8 | Source dashboard: active flag, consecutive failures, last success, `last_error` | FR-D-12 | test | Done |
| 9 | Auto-publish configurable by `admin` and **off by default** | FR-C-08 | test | Open — Could |

### The one open mechanism

The data model has one row per record, not a revision history. Proposed default for §5.1 is
**Option A**: a nullable `staged_changes` jsonb holding proposed field values plus the
proposing `ingestion_run`; a reviewer applies them, which writes `moderation_actions` and
`audit_logs` and clears the proposal. Until this ADR lands, published content fields stay
**read-only** for every role, so no path exists for an unreviewed edit to public content.

## What must be true when it ends

1. No code path reaches `published` without a recorded human decision (LEG-01, FR-C-02).
2. Approve/reject/unpublish/request-changes write both logs atomically.
3. The queue filters and exposes source and payload only to permitted roles.
4. The §5.1 ADR is accepted and `modelo-datos.md` amended.
5. `seed_demo` is retired as a public-content path (kept for local demo only).
6. `ruff`/`mypy`/`pytest`/`check --deploy` green; matrix rows updated.

## Definition of Done

| Condition | How it is met here |
|---|---|
| Code with tests | Each verb, the three-row transaction, filters and bulk approval are tested |
| Documentation updated | New ADR, `modelo-datos.md`, `estados.md` §7, `flujo-datos.md` §5.1, `CHANGELOG.md` |
| CI green | PostgreSQL service exercises the append-only trigger and `CHECK` constraints |
| Linked in the matrix | FR-C-01…11, FR-D-12, FR-B-07 |

## Explicitly out of scope

| Deferred | Why it waits |
|---|---|
| Public submissions and their moderation | v3 |
| Takedown and legal versioning | v3 |
| News/gallery moderation surfaces | v2 (they reuse this queue) |

## Risks

1. **Published-row mutation** is the one path that breaks SEC-38; the proposal mechanism must
   make an automatic write structurally impossible.
2. **`moderation_actions` vs `audit_logs` drift** — write both in one transaction and test it.
3. **Scope** — the ADR is mandatory (it unblocks v1's publishing); bulk approval is `Should`
   and can slip.

## Carried into the next sprint

1. v1 completion: backup/restore, admin hardening, matrix sweep, retrospective.
