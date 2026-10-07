# Sprint 09 retrospective — the v1 backend (admin surface + review queue)

- **Date:** 2026-10-06
- **Sprint:** 09, delivered together with the second half of Sprint 08 (this is the v1 backend)
- **Method:** Start / Stop / Continue, plus what actually happened versus what was planned.

## What was planned versus what happened

Planned: register the content in the admin behind permissions (FR-D-03), the moderation verbs
(approve / reject with a reason / unpublish / request changes), a `moderation_actions` log
written with `audit_logs` in one transaction, a filterable queue that surfaces the source and
the raw payload, bulk approval, the source dashboard, and an ADR for the change-to-published
mechanism (`flujo-datos.md` §5.1).

What happened: **the v1 backend landed and CI is green on its commit.** The suite is at **103
tests**; `ruff`, `mypy` (116 files), `makemigrations --check`, `check --deploy`, the secret
scan and the OpenAPI drift check are clean. The matrix moved **FR-B-01, FR-B-07, FR-C-01…07,
FR-C-09, FR-C-11, FR-D-03, FR-D-05 and FR-D-12 to Done.**

Delivered: a `carnaval.moderation` app (`ModerationAction`, append-only; a `service` that is
the only path to `published`), content and ingestion registered in the admin behind the
permission matrix (a fresh staff user sees nothing — FR-D-03), the reject-with-reason
intermediate page, an admin that surfaces `source_url` and a link to the stored payload
(gated by `view_rawdocument`, matrix row 11), the source dashboard fields, and **ADR 0017**
with `staged_changes`: the pipeline now **proposes** a change to a published row instead of
skipping it, and a reviewer applies it.

Carried, with reasons: FR-C-08 (auto-publish, a `Could`), FR-C-10 (rejected-upload policy,
v3), FR-B-18 (the admin's manual-run action; the CLI exists), SEC-05 (hashed recovery codes),
SEC-09 (object-level authorization cases), FR-D-15 (the explicit expiry test) and the
PostgreSQL append-only trigger.

## Start

- **One service is the only way to `published`.** `carnaval.moderation.service` checks the
  permission, writes the field, the `moderation_actions` row and the `audit_logs` row in one
  transaction. The admin actions call it; nothing writes a status directly.
- **An edition is published as a unit.** Approving an `edition` (or a `day`) also publishes its
  **pending** children, matching `modelo-datos.md` §3.1 — otherwise the public API would return
  events under an invisible day.
- **FR-D-03 falls out of the permission model.** The content is registered, but a staff user
  with no role has no `view` permission, so the console shows nothing. That is a real check,
  not a hidden model.
- **The pipeline proposes, the reviewer applies.** `staged_changes` carries the proposed values
  and the proposing run; `apply_proposal` is the only code that writes a published field, and
  it writes both logs.

## Stop

- **A previous stage's test expired again.** `test_content_models_are_not_exposed_in_admin`
  asserted the content models were **not registered** — true of the "MVP ships no admin"
  decision, false the moment v1 registered them behind permissions. It was rewritten to assert
  the permission gate. This is the same lesson as Sprint 04: **when a stage changes, revisit
  the tests that encoded the old stage.**
- **`Meta.permissions` is not inherited from the abstract base either**, like `Meta.constraints`.
  Each moderated model composes `moderation_permissions(...)`; the helper returns a **tuple**
  because `tuple` is covariant and `list` did not satisfy the stubs.
- **Object-level authorization is not really done.** The matrix's SEC-09 wants checks at the
  object level; the implementation is model-level (`has_perm`). FR-D-05 (viewer denied) is
  done, but SEC-09 stays Open rather than closed by proximity.
- **The database append-only trigger still waits for PostgreSQL.** FR-D-09 is done at the
  application layer only, and says so.

## Continue

- **Move only what the tests cover.** FR-C-08, FR-C-10, SEC-09 and FR-D-15 stayed Open.
- **Keep the decision trail in the docs.** ADR 0017 amends `flujo-datos.md` §5.1 and
  `modelo-datos.md` §2 rather than leaving the question open.
- **Name every carried item** in the plan's Status column and here.

## What the sprint proved about the project

The full pipeline is now real end to end: fetch → raw store → transform → staging as `pending`
→ **human review** → `published`, with the public API serving only the last step. The one rule
that shaped the whole design — a failed run never touches published data — survived the
addition of the last stage, because the only write to a published field goes through a reviewed
proposal.

## Concrete changes adopted

1. A test that encodes a stage's decision is revisited when the next stage changes that
   decision.
2. `moderation_permissions` returns a tuple, for the same reason `rejection_reason_constraint`
   exists: abstract Meta options are not inherited.
3. Object-level and database-level guarantees that are not implemented stay Open with the
   reason recorded.
