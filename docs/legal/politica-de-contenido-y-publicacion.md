# Content and publication policy — DRAFT

> **DRAFT — NOT LEGAL ADVICE.**
> Machine-drafted for engineering purposes. **Not reviewed by a qualified lawyer.** It
> states no Colombian legal conclusions, cites no statute, decree, or case, and contains
> no verified contact details. Bracketed `[PENDIENTE: …]` items are unresolved decisions.
> **Do not publish this as-is and do not rely on it.** Brief §11 requires professional
> review of the final texts; brief §20 keeps that open and requires it **before v3 starts**
> (ADR 0008).

- **Status:** Draft placeholder
- **Version in database:** `[PENDIENTE: no crear fila en legal_documents hasta que exista
  texto revisado]`
- **Relates to:** brief §4, §7, §10, §11, §14; `docs/00-acta-proyecto.md` §5, §6 (C4, C6),
  §8; ADR 0002, ADR 0004, ADR 0006, ADR 0007, ADR 0008; `docs/02-diseno/modelo-datos.md`
  §2, §4.2, §6; `docs/fuentes-y-atribucion.md`

## 1. Purpose and scope

This policy governs **what may appear on the public site**, and it is binding on every
path into publication: the ingestion pipeline, manual entry in the admin, and public
community submissions. It applies to the schedule (`events`), news (`news_items`),
historical images (`media_assets`), and community submissions (`submissions`).

## 2. What may be published

| Content | Allowed in this form | Not allowed |
|---|---|---|
| **Programme / schedule** | Facts extracted from a cited source: title, date, time, venue, with the source cited and the description written in the maintainer's own words | Copied prose from the source; a whole page reproduced |
| **News** | Headline (verbatim is fine), canonical URL, outlet, publication date, and a **short original summary** | The article body, its images, its layout, or a copy-paste excerpt (brief §11) |
| **Historical images** | Only with author, source, licence, citation text, EXIF stripped, and a determined `rights_status` | An image whose rights are `unknown`; an image of a minor as focal subject without guardian authorisation |
| **Video** | A link to a public YouTube or Vimeo video, embedded from the stored provider and video id | Hosted video files; any attempt to upload one, including disguised with an image extension (ADR 0007) |
| **Editorial text** | The maintainer's own words | Content pasted from a source with no permission |

The full list of sources, their terms-of-use status, and the citation formats are in
`docs/fuentes-y-atribucion.md`. That register is the operational companion to this policy.

## 3. Nothing is published without human review

This is the rule that makes the rest of the policy enforceable.

- Every item from every origin enters as **`status = pending`** and is only ever promoted
  to `published` or moved to `rejected` with a non-empty `rejection_reason` by a human
  moderator (modelo-datos §2; brief §7; ADR 0002).
- **Origin is always recorded** — `scraped` (with `ingestion_run`), `manual` (with
  `created_by`), or `community` (with a `submissions` row). What happens offline cannot be
  laundered through the pipeline.
- Every decision writes a `moderation_actions` row and an `audit_logs` row. Nothing
  transitions out of `published` automatically; downgrading or withdrawing is an explicit
  human action.
- Auto-publish rules are permitted by ADR 0002 but are **off by default** and, for content
  in the table above, should stay off. `[PENDIENTE: ¿se permite auto-publicación para algún
  tipo de contenido? recomendación: no]`
- **The scraper is a convenience, not a dependency.** A failed ingestion never deletes or
  degrades anything already published, and the maintainer can create every record by hand.

## 4. Attribution is mandatory, and unknown rights block publication

Every published item carries its provenance:

- **Images:** `author`, `source_ref`, `license`, `citation_text` — all mandatory to publish.
  `rights_status` must be one of `permitted`, `licensed`, `public_domain`,
  `permission_on_file`. **`rights_status = unknown` blocks publication**, enforced in
  model validation and repeated in the admin form so a direct ORM write from the pipeline
  cannot bypass it (modelo-datos §4.2; brief §11; ADR 0004).
- **News:** `source`, `url`, `outlet`, `published_on`, and an own-words summary.
- **Events:** the source that published them, recorded in `sources` and shown with the
  edition they belong to.
- **Old photographs are not free of rights.** Age is not a licence. An unknown photographer
  means `rights_status = unknown`, which means not published.
- A published item whose rights turn out to be doubted is **withdrawn**
  (`moderation_actions.action = withdraw`), not quietly edited into compliance.

## 5. Minors — absolute rule

**An image in which a minor is the focal subject is not published without authorisation
from their guardian** (brief §10, brief §14 risk register, `docs/00-acta-proyecto.md` §4.2).

- `media_assets.minor_subject = true` requires `guardian_consent_on_file = true` before
  publication. Both are booleans on the asset and both are checked at approval time.
- `consent_records.declaration_minor_subject` records the **contributor's own
  declaration**, which is evidence, not proof. A declaration is not authorisation.
- A minor visible incidentally in a crowd scene, not as the subject, is a judgement call
  made by the moderator, recorded in `moderation_actions.reason`. `[PENDIENTE: criterio
  formal para "foco" del menor — requiere revisión profesional]`
- Guardian authorisation must be **on file**, and must survive the retention deadline for
  the contributor's email (privacy policy §5) and the closure of any takedown dispute.
  `[PENDIENTE: formato, medio de almacenamiento y periodo de conservación del
  consentimiento del tutor]`
- Identifiable people generally: the contributor declares that they have permission from
  identifiable people. A privacy complaint about an identifiable person is handled under
  the takedown procedure.

## 6. Advertising and commercial use

- **The site carries no advertising.** Advertising is explicitly out of scope (brief §4),
  and the project is non-commercial with zero revenue.
- **Unauthorised commercial advertising is prohibited.** No submission, description, or
  image may promote a product, service, event, fundraiser, or business without the
  maintainer's prior written authorisation. A commercial submission is rejected with a
  reason, and repeated attempts are treated as abuse.
- `news_items` may report on commercial activity as journalism, with attribution. Reporting
  on it is not advertising it.
- The project never sells, lends, or shares contributor data with anyone.
- `[PENDIENTE: si en el futuro se plantea monetizar algo — Patreon, publicidad, licencias —
  eso abre obligaciones nuevas y requiere una decisión registrada y revisión legal]`

## 7. Prohibited content

The following are **never published**, whatever their origin, and are rejected at review
with a recorded reason:

| Prohibited | Handling |
|---|---|
| **Illegal content** — anything whose publication or redistribution would itself be unlawful | Never published, never redistributed, **not even while pending**. Reported to the authorities or a line such as **Te Protejo** (brief §10). `takedown_requests.claim_type = illegal_content` forces `status = escalated` (modelo-datos §6.6) |
| **Sexual content involving minors**, in any form, including suggestive framing | Rejected and escalated. Kept out of quarantine review views and never served from the public bucket |
| **Hate speech**, slurs, or content attacking people because of race, ethnicity, religion, gender, sexual orientation, disability, or origin | Rejected. The carnival's own tradition is satirised in the subject material; a costume is not a licence for a slur |
| **Personal data of third parties** — home addresses, phone numbers, identity documents, private contact details, tracked locations | Rejected. Publishing someone's personal data without consent is a privacy violation, not editorial content |
| **Doxxing** — deliberately exposing or aggregating someone's identifying information | Rejected and escalated as illegal content if serious |
| **Sexual, violent, or otherwise explicit content** with no documentary or historical purpose | Rejected |
| **Misinformation presented as fact** — invented dates, invented attributions, fabricated quotes or credits | Rejected. Attributing a fake image to a real photographer is the worst version of this |
| **Content encouraging self-harm, violence, or illegal acts** | Rejected and escalated |
| **Spam, SEO text, and link dumps** | Rejected |

Review of quarantined uploads is done in private storage over short-lived signed URLs
(ADR 0006). Reviewers must not re-share a quarantined file.

## 8. Repeat infringers

Because the site has **no public accounts** (brief §4), the usual ban-and-suspend mechanism
does not exist. The controls are different, and they are the honest ones:

1. **Quarantine before publication.** Untrusted uploads never touch public storage, so a
   bad file cannot be served even momentarily (ADR 0006).
2. **Duplicate and hash control.** The same image cannot be submitted twice
   (`submission_files.content_hash`, `duplicate_of`).
3. **Per-submission abuse limits.** CAPTCHA, a honeypot, per-IP send limits, and a global
   daily quota on pending items (brief §10).
4. **Documented, per-item decisions.** Every rejection has a reason and a `moderation_actions`
   row, so a pattern is visible after the fact.
5. **Refusing further submissions.** Where a repeated infringer can be identified — a
   recurring contact address, or a recurring `ip_hash`, which is comparable inside the
   system because the salt is constant — future submissions are refused and existing
   published items are re-examined. `[PENDIENTE: mecanismo concreto de bloqueo — comparar
   `contact_email` e `ip_hash` es internamente viable, pero la rotación de la sal lo
  invalidaría; decidir la política antes de implementar]`
6. **Sources are not treated as infringers.** If an outlet or an archive republishes
   material, the response is a takedown request to them, not retaliation.

## 9. Requesting removal

If you are a rights holder, a depicted person, or a guardian, ask for removal here:
`procedimiento-retiro-y-takedown.md`. `[PENDIENTE: canal de contacto publicado para
solicitudes de retiro]`

## 10. Enforcement

- The sole maintainer is the moderator and holds the `admin` and `editor` roles; RBAC is
  enforced server-side on every request and never relies on the admin UI hiding a control
  (brief §9; `docs/roles-permisos.md`).
- **Every approval, rejection, withdrawal, and configuration change is audited**
  (`audit_logs`, `django_admin_log`). `audit_logs` is append-only: no role, including
  `admin`, has update or delete permission on it.
- Content published in breach of this policy is withdrawn, not deleted silently, and the
  correction is recorded.
- If the organisers, a rights holder, or an authority objects, the objection is treated as
  a takedown request and handled through the procedure, whatever its `claim_type`.