# 0016. The legal texts ship as permanently labelled drafts; no professional review

- **Status:** Accepted
- **Date:** 2026-10-04
- **Relates to:** brief §11 and §20; `docs/legal/README.md`; ADR 0008 (submissions gated
  behind reviewed legal documents); ADR 0004; `docs/00-acta-proyecto.md` §12.2 item 4;
  `docs/02-diseno/despliegue.md` §10; Ley 1581 de 2012 (habeas data, Colombia)

## Context

Brief §20 listed, as an open item: *"cerrar los borradores de `docs/legal/` con **revisión
profesional** antes de iniciar la v3"*. `docs/legal/README.md` made it **blocking**: no
`legal_documents` row could be marked `is_current` for `terms`, `privacy` or
`content_policy` until a reviewed text existed. ADR 0008 leaned on the same thing —
public submissions were placed last *because* they are gated behind working moderation and
reviewed legal texts.

The four drafts exist. They were written in English by a non-lawyer, contain no Colombian
legal analysis, no article references and no case law, and are riddled with `[PENDIENTE]`
items that only qualified Colombian counsel could resolve: the legal basis for each
processing activity, retention periods, the limitation-of-liability clause, the jurisdiction
clause, whether a supervisory-authority registration is required.

On 2026-10-04 the maintainer decided: **there will be no professional review.** Not
deferred — declined. The cost is real and was stated plainly at the time: a portfolio
project, no budget, and no realistic path to hiring a Colombian data-protection and
copyright lawyer.

That leaves two ways to behave, and only one of them is honest:

1. Publish the drafts as if they were reviewed terms. This is the failure mode the entire
   `docs/legal/` directory was written to prevent — it manufactures the appearance of legal
   coverage the project does not have, and does it in the one document set where a visitor
   is asked to accept obligations.
2. Publish them as what they are — an engineer's drafts, permanently labelled — and accept
   the exposure that comes with running a public site under them.

This ADR records the second choice, and what it obliges.

## Decision

**The legal texts are published as drafts, permanently and visibly labelled, and are never
presented as reviewed, binding, or as legal advice.**

Concretely:

1. **Every legal page carries a DRAFT notice, above the content, not in a footer.** The
   notice states that the text was written by the project maintainer, not by a lawyer; that
   it has not been professionally reviewed; and that it is not legal advice. ADR 0011's drift
   discipline applies to the notice as much as to the body: it cannot be removed without a
   new `legal_documents` version.
2. **The submission consent checkbox cannot present these texts as enforceable terms.** It
   must state what they are. A visitor is entitled to know that the text in front of them
   was not written by a lawyer.
3. **`[PENDIENTE]` items that require legal judgement stay unresolved, by decision.** They
   are not implementation gaps to be closed with a plausible value; `docs/legal/README.md` §5
   already forbids that, and this ADR is the reason the register is permanent rather than
   provisional. The implementer's obligation is unchanged: fail loudly, do not guess.
4. **The `legal_documents` rows are created and marked current.** The blocking rule in
   `docs/legal/README.md` §2 is replaced: the blocker was "unreviewed", and unreviewed is now
   the project's declared state, so it cannot also be the gate. Each row records that state,
   so a future reader can tell from the database that these texts were never reviewed.
5. **The no-affiliation disclaimer is not optional and is not a substitute for anything
   here.** It was already mandatory (FR-A-09); it is now one of two protections rather than
   the only one, because the second — a legal basis confirmed by a lawyer — will not exist.

### What this does not decide

**ADR 0008's gate on v3 is now unsatisfied and this ADR does not satisfy it.** Public
submissions were placed last because they create legal exposure, and reviewed legal texts
were part of what made that exposure acceptable. With review declined, the reasoning behind
ADR 0008 no longer holds for v3.

That conflict is **not** resolved here. It is recorded as open, and it must be decided
before v3 begins — not silently at the moment someone starts building the upload form. The
options are visibly: v3 never ships, v3 ships under drafts with the exposure stated on the
form, or a reviewer is found. Choosing is the maintainer's; this ADR only makes sure the
choice is made with the conflict visible.

## Consequences

**Positive**

- The project stops carrying an open item it was never going to close. A permanent,
  labelled draft is a state that can be maintained; a pending professional review is a
  permanent state of guilt.
- Nobody is misled. The drafts' purpose in this project is to give consent something
  versioned to bind to and reviewers something to argue with. Both still work when the text
  is honestly labelled; neither works if the label is a lie.
- The `docs/legal/` register stays accurate. Keeping "awaiting review" on documents that will
  never be reviewed would make the whole directory untrustworthy.

**Negative, accepted**

- **Real legal exposure, on a public site, knowingly.** Colombian data-protection law applies
  to the processing this site does regardless of whether anyone reviewed the notice. The
  notices may be wrong in ways nobody has checked.
- Retention periods, legal bases and the takedown deadlines stay `[PENDIENTE]`. In practice
  this means the takedown procedure has **no deadline**, which is itself a defensible posture
  — no deadline means never refusing a claim — but it must be stated, not left implied.
- Consent binds to a draft. That is weaker than binding to reviewed terms, and a claim about
  the quality of a consent flow becomes easier to sustain.
- The DRAFT notice is a permanent scar on the site's credibility. Accepted: it is cheaper
  than the alternative.

## Alternatives considered

1. **Keep the review as a launch blocker; ship nothing legal until it happens.** Rejected:
   that is the status quo, which produces a site with no takedown notice, no privacy notice
   and no consent flow — worse than a labelled draft, because the *absence* of a notice is
   the thing that actually creates liability.
2. **Publish the drafts silently, as ordinary terms.** Rejected without discussion. This is
   the one option that makes the project's risk profile worse while making it look better,
   and it is precisely what the DRAFT notice in `docs/legal/README.md` was written to
   prevent.
3. **Remove the legal documents and rely on the disclaimer alone.** Rejected: consent has
   nothing to bind to, the takedown procedure has no published text, and the brief's §10
   requirement for an explicit consent declaration becomes unimplementable.
4. **Ask a lawyer for a short review of the privacy notice only.** Not rejected on merit —
   it is the cheapest version of the thing that was declined, and it remains available. It was
   not taken because no such arrangement exists today, and this ADR documents the decision as
   it stands rather than as it might stand after someone finds a pro bono contact.

## Verification

- `docs/legal/README.md`, its status line, and all four documents state the permanent-draft
  position and cite this ADR. No document may still say the review is pending or that it
  blocks v3.
- `docs/02-diseno/despliegue.md` §10's pre-launch checklist reflects the DRAFT-notice
  obligation instead of a professional review.
- The consent checkbox copy in the v3 design states that the accepted text is an unreviewed
  draft. (Not buildable until v3 is decided — carried in the sprint that starts it.)
- The unresolved v3 conflict in ADR 0008 is visible wherever v3 is described.