# Legal document set — index and lifecycle

> **DRAFT — NOT LEGAL ADVICE.**
> Every document in this directory was machine-drafted for **engineering purposes only**.
> They exist so the system has something reviewable to store, version, and bind consent to.
> They have **not** been reviewed by a qualified lawyer, they are written in English by a
> non-lawyer, and they contain no Colombian legal analysis, no article references, no case
> law, and no verified contact details. Anything bracketed as `[PENDIENTE: …]` is an
> unresolved decision, not a stylistic choice.
> **Do not publish any of these as-is, do not present them as binding, and do not rely on
> them.** Brief §11 states that the final texts should be reviewed by a professional, and
> brief §20 lists *“redactar los documentos legales (con revisión profesional) antes de
> iniciar la v3”* as an open item. That item is **not** closed by the existence of these
> files.

- **Status:** Draft placeholders, awaiting professional review
- **Date:** 2026-10-03
- **Relates to:** brief §10 (public submissions and consent), §11 (legal and ethical
  considerations), §20 (open items); `docs/00-acta-proyecto.md` §4.2, §5, §9; ADR 0004,
  ADR 0006, ADR 0007, ADR 0008, ADR 0010; `docs/02-diseno/modelo-datos.md` §6.3–§6.6,
  §8; `docs/fuentes-y-atribucion.md`

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

## 2. Who must review, and when

| Requirement | Detail |
|---|---|
| **Reviewer** | A lawyer qualified in Colombian law, ideally with data-protection and copyright experience. `[PENDIENTE: nadie contratado — definir cómo se consigue la revisión]` |
| **Trigger** | Before **v3** begins. Public submissions are gated behind reviewed legal documents (ADR 0008); shipping an upload path before the texts exist would create legal exposure and an unmoderated public channel |
| **Blocking?** | Yes. `legal_documents` rows must not be marked `is_current = true` for `terms`, `privacy`, or `content_policy` until a reviewed text exists. The submission form has no document to bind consent to otherwise |
| **Also review** | `docs/fuentes-y-atribucion.md` §3 (terms-of-use status of each source) — that is a factual review, not a drafting one, and it is brief §20's *“revisar robots.txt y términos de uso del sitio”* |
| **Also contact** | Corpocarnaval / the parade organisers, before launch: brief §20 *“escribir a Corpocarnaval para informarles del proyecto”*. Until that happens, the unofficial disclaimer is not a courtesy — it is the only protection there is (`docs/00-acta-proyecto.md` §6, C6) |

What professional review will most likely change, so it is not treated as settled: the
entity that holds the data, whether a privacy notice or data-processing agreement is
required from any provider, the legal basis for each processing activity, the retention
periods, the limitation-of-liability clause, and the jurisdiction clause.

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

| Placeholder | Lives in | Blocks |
|---|---|---|
| Identity and contact details of the project and its maintainer | all four documents | v3 launch |
| Named contact channel for takedown requests | terms, content policy, privacy, takedown | v3 launch |
| Retention periods, in days, per data category | privacy | v3 launch |
| Formal data-subject request procedure and its response deadline | privacy | v3 launch |
| Legal basis per processing activity | privacy | Professional review |
| Whether a registration with a supervisory authority is required | privacy | Professional review |
| Acknowledgement and resolution deadlines for takedown requests | takedown | v3 launch |
| Authorities and hotlines to escalate illegal content to | takedown | v3 launch |
| Liability cap wording and jurisdiction clause | terms | Professional review |
| Ingestion command for loading documents into `legal_documents` | this file | v1/v2 tooling |
| Consent-to-locale binding rule | this file | v3 |

## 6. Related documents

- `docs/00-contexto-proyecto.md` §10, §11, §20 — the requirements these drafts answer.
- `docs/00-acta-proyecto.md` §4.2 — stakeholders whose interests these rules protect.
- `docs/fuentes-y-atribucion.md` — attribution policy, source register, scraping etiquette.
- ADR 0004 — MIT covers code only; `rights_status = unknown` is never published.
- ADR 0006 — quarantine and public tiers; EXIF/GPS stripped before storage.
- ADR 0007 — videos are external embeds; takedown of a video means contacting the provider.
- ADR 0008 — public submissions are gated behind moderation and reviewed legal documents.
- ADR 0010 — bilingual `es`/`en`; legal documents are not machine-translated.