# Legal document set — index and lifecycle

> **DRAFT — NOT LEGAL ADVICE, AND NOT GOING TO BE.**
> Every document in this directory was machine-drafted for **engineering purposes only**.
> They exist so the system has something reviewable to store, version, and bind consent to.
> They have **not** been reviewed by a qualified lawyer, they are written in English by a
> non-lawyer, and they contain no Colombian legal analysis, no article references, and no
> case law. Anything bracketed as `[PENDIENTE: …]` is an unresolved decision, not a
> stylistic choice.
>
> **These are published as drafts, permanently and visibly labelled.** This is not a temporary
> state: on 2026-10-04 the maintainer decided that no professional review will be obtained,
> and **ADR 0016** records that decision, its consequences, and what it obliges. Every legal
> page carries a DRAFT notice above the content. Nothing here may be presented as binding,
> and nobody should rely on it. Colombian data-protection law applies to this site whether or
> not anyone reviewed these words — that exposure is accepted knowingly.

- **Status:** Drafts, permanently unreviewed by decision (ADR 0016)
- **Date:** 2026-10-03 (drafted), 2026-10-04 (status fixed)
- **Relates to:** brief §10 (public submissions and consent), §11 (legal and ethical
  considerations), §20 (open items); `docs/00-acta-proyecto.md` §4.2, §5, §9; ADR 0004,
  ADR 0006, ADR 0007, ADR 0008, ADR 0010, **ADR 0016**; `docs/02-diseno/modelo-datos.md`
  §6.3–§6.6, §8; `docs/fuentes-y-atribucion.md`

## 1. What is in this directory

| File | `doc_type` | What it covers | Depends on the others? |
|---|---|---|---|
| `terminos-y-condiciones.md` | `terms` | Nature of the project, non-affiliation, information provided as-is, per-item licensing, limitation of liability, changes to the terms | References the content policy and the privacy policy |
| `politica-de-contenido-y-publicacion.md` | `content_policy` | What may be published, mandatory human review, attribution requirements, the minors rule, prohibited content, repeat infringers | Operates the takedown procedure |
| `politica-de-privacidad.md` | `privacy` | Personal data handled, hashed IPs, purposes and legal basis, retention, data subject rights, cookies, embeds | Referenced by the terms |
| `procedimiento-retiro-y-takedown.md` | `takedown` | The operational procedure moderators follow for removal and notification requests | Implemented by the other three |

`docs/fuentes-y-atribucion.md` is **not** in this directory and is **not** a legal
document — it is the operational register of sources, citation formats, and scraping
etiquette. It is the place to look for *where content came from*; these four documents
are the place to look for *what the project's rules are*.

## 2. Who reviews, and what "unreviewed" now means

**Nobody.** ADR 0016 records the decision, taken 2026-10-04, that no professional review
will be obtained. The table below is kept because each row states an obligation that still
exists in some form — but the answer is no longer "a Colombian data-protection and
copyright lawyer".

| Requirement | Detail |
|---|---|
| **Reviewer** | **None, by decision.** A lawyer qualified in Colombian law would be the right reviewer; that is not going to happen. ADR 0016 alternative 4 records the cheapest version — a privacy-notice-only review — as still available if a pro bono contact ever appears |
| **DRAFT notice** | **This is the control that replaces review.** Every legal page carries a notice, above the content, stating the text was written by the maintainer, not reviewed by a lawyer, and is not legal advice. It cannot be removed without a new `legal_documents` version (ADR 0016 §1) |
| **`legal_documents` rows** | **No longer blocked.** The old rule — no row may be `is_current` until a reviewed text exists — is replaced. "Unreviewed" is now the declared state, so it cannot also be the gate. Each row records that state, so a future reader can tell from the database that these texts were never reviewed |
| **Consent copy** | The submission checkbox must state that the accepted text is an unreviewed draft. A visitor is entitled to know what they are agreeing to |
| **`[PENDIENTE]` register** | **Permanent, not provisional** (§5). An implementer must not fill a legal-judgement item with a plausible value. Failing loudly is the correct behaviour, and no longer looks like an unfinished project |
| **Also review** | `docs/fuentes-y-atribucion.md` §3 (terms-of-use status of each source) — a factual review, not a drafting one, and it is brief §20's *"revisar robots.txt y términos de uso del sitio"*. **Done for the official site** 2026-10-04: `robots.txt` permissive, no terms found, absence accepted as a documented risk (ADR 0016 does not apply here; see §9.5 of that register) |
| **Also contact** | Corpocarnaval / the parade organisers, before launch: brief §20 *"escribir a Corpocarnaval para informarles del proyecto"*. **Not yet done** — the letter is drafted in `docs/comunicacion-corpocarnaval.md`. This is the mitigation for the missing terms, and it is the one protection that is actually in reach |

What professional review would most likely have changed, listed so it is not mistaken for
settled: the entity that holds the data, whether a privacy notice or data-processing
agreement is required from any provider, the legal basis for each processing activity, the
retention periods, the limitation-of-liability clause, and the jurisdiction clause. **None of
these is now verified, and none of them will be.**

### 2.1 The unresolved consequence for v3

ADR 0008 placed public submissions last *because* they are gated behind working moderation
**and reviewed legal documents**. Review has been declined, so **that gate is unsatisfied**.
Shipping anonymous public uploads under permanently unreviewed drafts would contradict the
reasoning of ADR 0008.

This is deliberately left undecided. It must be settled before v3 begins, by someone who can
see the conflict — not at the moment someone starts writing the upload form.

## 3. Versioning

The repository file is the **draft source**. The **operative** copy at any moment is the
row in `legal_documents` with `is_current = true` (`docs/02-diseno/modelo-datos.md` §6.4):

| Field | Rule |
|---|---|
| `doc_type` | One of `terms`, `privacy`, `content_policy`, `takedown` — one per document in this directory |
| `version` | Semver-ish string, e.g. `1.0`, `1.1`. A wording fix is a patch; a changed obligation is a minor; a changed meaning is a major |
| `locale` | `es` or `en` (ADR 0010). Spanish is the source locale |
| `body` | Markdown |
| `effective_from` | When the version starts to bind. Never back-dated to hide a change |
| `is_current` | Partial unique index: **one current version per `(doc_type, locale)`** (modelo-datos §9) |

Rules:

1. **A published version is never edited.** Any change creates a new `version` row. The
   old row stays readable forever, because an old `consent_records` row points at it and
   must remain interpretable.
2. **A change is announced on the site**, with the version number and `effective_from`,
   before or at the moment the new version becomes current.
3. **Acceptance is never retroactive.** A contributor who accepted `terms` `1.0` is bound
   by `1.0`, not by whatever is current when their item is later moderated.
4. **Loading drafts into the database** is a deliberate, manual act, not a deployment side
   effect. `[PENDIENTE: mechanism — a management command that ingests docs/legal/*.md into
   legal_documents; it must never overwrite a row that is already is_current]`
5. **The takedown procedure is versioned too**, even though it is internal, because its
   `effective_from` dates the behaviour a rights holder was entitled to expect.

## 4. How consent binds to a version

`consent_records` (modelo-datos §6.3) is the proof that a specific human was shown a
specific text:

| Column | What it fixes |
|---|---|
| `submission` | The contribution it applies to |
| `legal_document` | **The exact `legal_documents` row accepted** — doc_type, version, and locale together |
| `accepted_at` | When |
| `ip_hash`, `user_agent_hash` | Hashed only, never raw (brief §10) |
| `declaration_rights` | "I am the author or I hold permission" |
| `declaration_minor_subject` | Whether the contributor declared that a minor is the focal subject |

Consequences that follow from that design:

- The consent checkbox is **unchecked by default and blocking** (brief §10). A submission
  without a `consent_records` row is not a submission.
- Because `legal_document` is a foreign key and not a version string, a text can never be
  silently replaced underneath an accepted consent.
- Deleting a `legal_documents` row would orphan consent. Treat the table as
  **append-only in practice**, even though no constraint enforces it:
  `[PENDIENTE: ¿debe añadirse una restricción de borrado en el admin?]`
- ADR 0010 says legal documents are reproduced verbatim and not translated, with a Spanish
  original alongside. `locale` therefore exists per row for readability, which leaves one
  genuine ambiguity: **which row does an acceptance bind to** — the Spanish operative text
  or the one the visitor actually read? `[PENDIENTE: registrar el consentimiento contra la
  fila es, o contra la fila mostrada según el locale negociado]`. Recording against both
  is acceptable if the form shows both.

## 5. Placeholder register

Every `[PENDIENTE: …]` in this directory is an open decision. None of them may be guessed
at by an implementer, and none of them may be filled in with a plausible-looking value.

**This register is now permanent, not provisional** (ADR 0016). An item whose resolution
required a lawyer is not a gap waiting to be closed; it is a decision that was taken not to
close it. The distinction matters for the implementer: a `[PENDIENTE]` is not an oversight to
fix silently, and *no* deadline in this directory may be invented to make a feature
complete.

| Placeholder | Lives in | Status |
|---|---|---|
| ~~Identity and contact details of the project and its maintainer~~ | all four documents | **Resolved** — `victorloal513@gmail.com`, 2026-10-04. The maintainer's name is stated; a verifiable postal address is still absent |
| ~~Named contact channel for takedown requests~~ | terms, content policy, privacy, takedown | **Resolved** — the same address, published in `README.md` and in the scraper's `User-Agent` |
| Retention periods, in days, per data category | privacy | **Unresolved by decision** — needs legal judgement (ADR 0016) |
| Formal data-subject request procedure and its response deadline | privacy | **Unresolved by decision** — needs legal judgement |
| Legal basis per processing activity | privacy | **Unresolved by decision** — this one was going to be settled by review; it now will not be |
| Whether a registration with a supervisory authority is required | privacy | **Unresolved by decision** |
| Acknowledgement and resolution deadlines for takedown requests | takedown | **Unresolved by decision.** Consequence, stated rather than implied: **the takedown procedure has no deadline**, which means no claim is ever refused for being late |
| Authorities and hotlines to escalate illegal content to | takedown | **Unresolved by decision** |
| Liability cap wording and jurisdiction clause | terms | **Unresolved by decision** |
| Ingestion command for loading documents into `legal_documents` | this file | Open — engineering work, belongs to v1/v2 tooling |
| Consent-to-locale binding rule | this file | Open — engineering decision, belongs to v3 |
| ADR 0008's "reviewed legal documents" gate for v3 | ADR 0008, `docs/legal/README.md` §2.1 | **Open conflict**, deliberately not resolved here |

## 6. Related documents

- `docs/00-contexto-proyecto.md` §10, §11, §20 — the requirements these drafts answer.
- `docs/00-acta-proyecto.md` §4.2 — stakeholders whose interests these rules protect.
- `docs/fuentes-y-atribucion.md` — attribution policy, source register, scraping etiquette.
- ADR 0004 — MIT covers code only; `rights_status = unknown` is never published.
- ADR 0006 — quarantine and public tiers; EXIF/GPS stripped before storage.
- ADR 0007 — videos are external embeds; takedown of a video means contacting the provider.
- ADR 0008 — public submissions are gated behind moderation and reviewed legal documents.
  **Its "reviewed" half is unsatisfiable now** — see §2.1.
- ADR 0010 — bilingual `es`/`en`; legal documents are not machine-translated.
- ADR 0016 — these texts ship as permanently labelled drafts; no professional review.