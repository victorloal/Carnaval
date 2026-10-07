# 0018. v3 ships under labelled draft legal texts; retention and takedown defaults

- **Status:** Accepted
- **Date:** 2026-10-07
- **Relates to:** ADR 0008 (delivery by version), ADR 0016 (no professional review), ADR 0006
  (quarantine), ADR 0013 (SRS defaults); `docs/legal/`; SRS PRV-06; `docs/sprints/sprint-15-plan.md`

## Context

ADR 0008 placed public submissions last, *"gated behind working moderation and **reviewed**
legal documents"*. ADR 0016 permanently declined professional review, which left that gate
**unsatisfied** — a conflict ADR 0016 recorded and deliberately did not resolve. The v3
**backend** was built anyway (Sprints 15–16); the public **submission form** was left unbuilt
because building it under an unsatisfied gate is exactly what the gate was meant to prevent.

The open question is therefore narrow and concrete: *does v3 ship under unreviewed drafts,
or not?* It has to be answered before the form is written, not while.

This is a **personal, non-commercial portfolio project**. There is no budget, no legal
entity, and no realistic path to Colombian data-protection and copyright counsel. The useful
question is not "is this legally flawless", which cannot be achieved here, but "which honest
posture is defensible, buildable, and does not mislead a visitor".

## Decision

**v3 public submissions ship, under the permanently labelled draft legal texts of ADR 0016.**

1. **ADR 0008's gate is amended.** The condition "reviewed legal documents" becomes
   "**legal texts published as permanently labelled drafts**" (ADR 0016). The rest of the gate
   stands unchanged: working moderation, the takedown register, blocking consent bound to a
   specific `legal_documents` version, `origin = community`, and every submission `pending`
   until a human approves it.
2. **The labels are mandatory.** Every legal page carries the DRAFT notice above the content,
   and the submission consent cannot present the drafts as enforceable terms. The text says,
   in the visitor's language, that it was written by the maintainer, was not reviewed by a
   lawyer, and is not legal advice (ADR 0016 §1–2).
3. **Retention periods are set by the maintainer** — revisable operational defaults, chosen
   with the same judgement review would have exercised, and explicitly **not legal advice**:

   | Category | Default | Mechanism |
   |---|---|---|
   | `consent_records` (with its salted `ip_hash`) | 24 months from acceptance | purge job (PRV-03, not yet built) |
   | `submissions.contact_email` | 12 months after the submission is decided | purge job |
   | `takedown_requests.requester_email` | 24 months after `responded_at` | purge job |
   | Rejected upload files | deleted immediately on rejection | implemented (FR-C-10) |
   | `raw_documents` | 30 days and a per-source byte cap | implemented (`prune_raw_documents`, ADR 0013) |
   | `audit_logs` | **not purged — append-only evidence** | FR-D-09 forbids deletion and the trail holds only salted hashes, so the evidence value outweighs the period (`purge_personal_data` never touches it) |
   | `ingestion_runs` | 12 months | purge job |
   | `django_session` rows | removed once expired | Django `clearsessions`, scheduled |
   | Locale preference cookie | 12 months | frontend `max-age` (already set) |

   The `audit_logs` row is the one exception: the append-only guarantee (ADR 0005,
   FR-D-09) is a hard constraint, and a purge that deleted the trail would destroy the
   evidence a rights holder may need. The command enforces the rest; the exception is
   stated rather than silently applied.

   These resolve the retention placeholders that ADR 0016 left open and that **PRV-06** needed.
4. **Takedown deadlines are set operationally.** The acknowledgement-within and
   resolution-within deadlines are named (7 and 30 days; illegal-content and minor-privacy
   claims prioritised at 48 hours and always escalated). This replaces the "no deadline"
   posture ADR 0016 stated as a consequence, which was defensible but a poor service to a
   rights holder.
5. **The genuinely legal-analysis items stay unresolved and labelled.** The legal basis per
   processing activity, whether registration with a supervisory authority is required, and the
   liability-cap / jurisdiction wording are **not asserted**, because inventing them would
   manufacture coverage the project does not have. They are accepted as known gaps of a
   non-commercial prototype rather than closed with a plausible value.

### What this does not decide

- It is not legal advice, and it does not make the drafts accurate or complete.
- It asserts no conclusion about Colombian law.
- **PRV-03/PRV-07 stay Open**: the purge code and a rehearsed data-subject procedure do not
  exist yet. Naming a period is not the same as enforcing it.

## Consequences

**Positive**

- The last product blocker is removed by a written decision, not by silence at the moment
  someone starts the form. The consent flow, the takedown channel and the retention policy
  become buildable.
- The placeholders that were blocking *engineering* (retention, takedown deadlines) stop
  blocking; the ones that were blocking *legal certainty* stay visible instead of being faked.

**Negative, accepted**

- **Real exposure on a public site, under texts nobody checked.** Knowingly accepted.
- The retention numbers are the maintainer's, not counsel's. They may be wrong; they are
  bounded and reversible, which an invented legal basis would not be.
- **This decision is conditional on scale.** A personal prototype with a handful of visitors
  is not the same risk as a service with a real user base. If the site ever becomes
  commercial, or its use grows materially, this ADR must be revisited **before** that happens.

## Alternatives considered

1. **Never ship v3.** Rejected: the backend exists, the feature is the demonstration, and
   refusing to ship it refuses the point of the project.
2. **Wait for a lawyer.** Rejected: declined (ADR 0016) and unaffordable (ADR 0016 alt 4).
3. **Ship and present the drafts as ordinary terms.** Rejected without discussion —
   ADR 0016 alternative 2; it manufactures coverage and misleads the one person asked to
   accept obligations.
4. **Ship with only the disclaimer, no legal pages.** Rejected: consent would bind to
   nothing and the takedown procedure would have no published text (ADR 0016 alt 3).

## Verification

- ADR 0008 and ADR 0016 carry an "Amended by / Resolved by 0018 (2026-10-07)" note; neither
  still reads as an open conflict.
- `docs/legal/README.md` §2.1 and the §5 register no longer say the v3 gate is unsatisfied,
  and the retention row names the periods.
- `docs/legal/politica-de-privacidad.md` §5 names the periods and cites this ADR;
  `docs/legal/procedimiento-retiro-y-takedown.md` names the deadlines.
- `docs/sprints/sprint-15-plan.md` records the gate as settled; the form and its consent copy
  state that the accepted text is an unreviewed draft.
- `matriz-trazabilidad.md`: **PRV-06 → Done**; PRV-03/PRV-07 remain Open with reasons.
