# 0017. Proposing a change to already-published content

- **Status:** Accepted
- **Date:** 2026-10-06
- **Relates to:** `flujo-datos.md` §5.1 and §11 item 1; `modelo-datos.md` §2 and §9;
  ADR 0002 (database as source of truth), ADR 0008 (versions); FR-B-07, FR-B-09, FR-C-02/03,
  FR-C-05; `roles-permisos.md` row 9.

## Context

The moderation mixin has one row per record, not a revision history, and no column holds a
proposed change. `flujo-datos.md` §5.1 is the one place where the data model provides no
mechanism, and it must not be resolved by writing to a published row: **a failed or repeated
run never modifies, degrades or deletes a `published` row** (FR-B-09, SEC-38).

The pipeline re-transforms a whole document when the source changes, then compares records
field by field. When a record it already published is one of them, it has to *say so* without
touching it.

## Decision

**Option A — a `staged_changes` jsonb column on the moderation mixin.** The pipeline writes the
proposed field values plus the proposing `ingestion_run` into `staged_changes` and leaves the
published fields untouched. A reviewer sees the proposal in the admin and applies or discards
it; applying writes the fields, clears the proposal, and records a `moderation_actions` row and
an `audit_logs` row — the same gate every other change passes through.

The pipeline may write `staged_changes` and `ingestion_run` on a published row; it may write no
other field. `apply_proposal` in `carnaval.moderation.service` is the only path that writes a
published content field, and it requires the publish permission.

## Consequences

**Positive**
- The review gate ADR 0002 requires is mechanically unavoidable: there is no code path in
  which a fetch or parse reaches a published field.
- No new table, and the column travels with the mixin, so `news_items`, `media_assets` and
  `submissions` inherit it when they land.
- The proposal is auditable: who proposed it (the run) and who applied it (the reviewer) are
  both recorded.

**Negative**
- One column per content table, and only the latest proposal is kept: a second change
  overwrites the first before a reviewer sees it. Accepted at this scale — the source changes
  once a year.
- The reviewer must notice the proposal; it is not an alarm. Mitigated by the admin exposing
  `staged_changes` on the change form and by a dedicated admin action.

## Alternatives considered

- **Option B — a revision table with `supersedes`.** A new table plus new legal and audit
  semantics, and the live row is overwritten on approval of a revision. Rejected: heavier, and
  it re-introduces the risk of an automatic write to live content.
- **Option C — report the diff and let an editor retype it.** No schema change, but the
  scraper's convenience value drops sharply and the report is easy to ignore. Rejected.

## Amendment

This decision amends `flujo-datos.md` §5.1, which carried the question as open, and
`modelo-datos.md` §2, which now lists `staged_changes` among the mixin's fields.
