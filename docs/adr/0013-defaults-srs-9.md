# 0013. Defaults for the open SRS §9 decisions, with explicit revisit triggers

- **Status:** Accepted
- **Date:** 2026-10-03
- **Relates to:** SRS §9 Q2–Q5, `modelo-datos.md` §10 Q2–Q3, ADR 0005, ADR 0009

## Context

SRS §9 left five questions open. Q1 (how translations are stored) needed a structural
decision and got its own ADR — see **ADR 0012**.

The remaining four are not structural. They are parameters and implementation choices where
the design must pick something concrete in order to write code, but where the honest answer
is a **default plus the condition that would invalidate it**. Guessing once and leaving the
guess invisible is what produced the stale cross-references in the threat model; guessing
once and recording the trigger for changing it is legitimate.

This ADR records all four defaults in one place so they are reviewed together, because they
share a property: each is cheap to change now and expensive to change after code exists, but
none of them is hard to change *later* if the trigger is monitored.

## Decision

### Q2 — Session timeouts: 12 h idle, 72 h absolute, plus step-up authentication

| Setting | Value |
|---|---|
| Idle timeout | 12 hours |
| Absolute timeout | 72 hours |
| Step-up re-authentication | password **and** TOTP, required to: publish content, change roles or groups, edit `site_settings`, or act on the legal documents |

The SRS proposed 8 h / 24 h. That is tight for a single part-time maintainer who reviews a
queue in bursts and would be logged out mid-review. It is also *too loose* on its own: 24 h
absolute leaves an authenticated `editor` with publish rights reachable from a stolen
cookie for a full day.

Timeouts and step-up solve different problems, so both are used. **Step-up is the stronger
control** — it re-verifies identity at the moment of the dangerous action rather than
hoping the session window is short enough. A timeout bounds exposure; step-up bounds what an
already-exposed session can do. Neither substitutes for the other, and tightening the
timeout would not compensate for dropping step-up.

`SEC-02` asserts cookie attributes and the absence of any browser-held token; the timeout
values themselves are asserted by `SEC-11` and the authentication sequence in
`autenticacion.md` §4.

### Q3 — Raw document retention: 30 days **and** a per-source byte cap, and published content is never pruned

`raw_documents` bounds storage on a zero-cost tier. Three rules:

1. **Time window.** A raw document is pruned 30 days after `fetched_at`.
2. **Byte cap.** Independently, the newest payloads are pruned when a source exceeds a
   per-source byte budget. The window alone does not bound storage, because one source
   returning 50 MB a day for a fortnight still exceeds any free tier.
3. **Published content is exempt.** A raw document that is the source of a record in
   `status = published` is retained for as long as that record exists, regardless of age.
   Pruning it would break the provenance chain from fetch to publication — the property the
   threat model relies on (T-27, T-32) and that makes an editorial correction auditable.

Only documents that never produced a published record are eligible for pruning. The
`content_hash` and the fetch metadata in `raw_documents` are what make ingestion idempotent
(FR-B-03, `SEC-37`); those rows are never deleted by retention, only the payload is dropped.

**Trigger to revisit:** measured storage, not calendar time. If any source's byte cap is hit
more than once a month, the source is producing too much and needs its fetch interval
widened rather than its retention shortened.

### Q4 — Search: `pg_trgm` + `unaccent`, re-evaluated above ~50k rows

Both candidates are free-tier-safe and both would work. `pg_trgm` is chosen for the Spanish
text specifically: it needs the `unaccent` extension so that "carnaval" matches "Carnaval"
and "tradicion" matches "tradición", which is not optional for a Spanish-language site where
users routinely type without diacritics. It also tolerates the typos a public search box
attracts. PostgreSQL's native full-text search with the `spanish` configuration has weaker
stemming and requires a separate search vector per field.

**Trigger to revisit:** above roughly 50,000 searchable rows, or if `EXPLAIN` shows the
trigram index is not being used, move to native full-text search with a maintained vector.
The corpus is expected to stay well below that — one edition per year, a few dozen news
items per edition, a bounded image gallery.

### Q5 — `site_settings` stays untyped, validated by accessor functions

No typed schema. `site_settings` remains `key` / `value`, and validation moves into a small
Python module of typed accessor functions per domain.

A typed schema would mean a migration every time a setting is added, for roughly thirty
settings that are set once and read rarely. The failure this actually guards against — a
malformed value reaching the page — is better handled where the value is read, with one
function that either returns a correctly typed value or raises. `FR-E-10` is satisfied by
that accessor, not by the column type.

**Trigger to revisit:** if settings become user-editable in the admin with per-user scope, or
if the count passes roughly a hundred and type confusion becomes a recurring source of bugs.

## Consequences

**Positive**
- The four open questions stop blocking implementation; each has a value to write against.
- Step-up authentication adds a control that ADR 0005 did not previously specify.
- Every default carries the condition that would change it, so none of them becomes an
  unexamined assumption.

**Negative**
- Three of the four are defaults rather than decisions, and a reviewer may reasonably
  disagree with any of them. That is the intent: the trigger states what evidence would
  settle the disagreement.
- The retention rule is more complex than a single date, and the published-content exemption
  is the kind of clause that gets forgotten when someone later adds a cleanup job. It is
  stated here, in `modelo-datos.md` §8, and asserted by the ingestion tests.

## Alternatives considered

- **Revert to the SRS proposal (8 h / 24 h).** Rejected: it trades a real usability cost
  during review sessions for a smaller reduction in exposure that step-up already addresses.
- **Timeouts only, no step-up.** Rejected: a stolen cookie remains fully usable inside the
  window, and the window cannot be made short enough to be safe without harming real use.
- **Step-up only, no timeouts.** Rejected: an abandoned session on a shared machine would
  stay live indefinitely. Both bound different things.
- **Count-based retention ("last N per source"), as SRS §9 proposed.** Rejected: counts do
  not bound bytes, so a source that starts returning large payloads silently overruns the
  tier. The byte budget is the bound that actually protects the constraint.
- **Native full-text search for Q4.** Deferred rather than rejected — it is the right answer
  at a scale this project is unlikely to reach. Recorded above with the trigger.
- **Typed `site_settings`.** Deferred for the same reason, and for the same reason it would
  be wrong today: migrations per setting.
