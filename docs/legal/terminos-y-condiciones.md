# Terms and conditions of use — DRAFT

> **DRAFT — NOT LEGAL ADVICE.**
> Machine-drafted for engineering purposes. **Not reviewed by a qualified lawyer.** It
> contains no Colombian legal analysis, no statute or decree references, no case law, and
> no verified contact details. Bracketed `[PENDIENTE: …]` items are unresolved decisions.
> **Do not publish this as-is and do not rely on it.** Brief §11 says the final legal texts
> should be reviewed by a professional; brief §20 keeps that as an open item, to be done
> **before v3 starts** (ADR 0008).
>
> Written in English with Colombian legal concepts named in Spanish on first use. The
> operative text is expected to be Spanish; the English version is provided for
> readability, and a reviewed Spanish version must replace both drafts.

- **Status:** Draft placeholder
- **Version in database:** `[PENDIENTE: no crear fila en legal_documents hasta que exista
  texto revisado]`
- **Relates to:** brief §1, §4, §6 decision 5, §10, §11; `docs/00-acta-proyecto.md` §2, §5,
  §6; ADR 0004, ADR 0008, ADR 0010; `docs/00-contexto-proyecto.md` §11

## 1. Who runs this site

This site is a **personal, non-commercial project**: a single-part-time developer
collecting, citing, and publishing public information about the Carnaval de Negros y
Blancos de Pasto (Nariño, Colombia). It is a portfolio and engineering exercise, not a
business, and it earns nothing from visitors.

The project is not a company, has no employees, and is run by one person with no support
desk. `[PENDIENTE: identificar al titular del proyecto y su domicilio para efectos de
notificación]`

Nothing on this site is a professional service. Nothing on it is advice.

## 2. No affiliation, no endorsement, not official — read this first

**This site is unofficial.** It is **not affiliated with, not endorsed by, not sponsored
by, and not operated by Corpocarnaval, the parade organisers, the Mayor's office, the
Nariño government, or any other entity connected with the carnival.**

- The name and marks of the organisers are used only to identify what the information is
  *about*.
- No affiliation or endorsement may be inferred from the content, the domain, or the
  design.
- The disclaimer is rendered site-wide because `sources.is_official = true` marks the
  official site as a source (modelo-datos §4.3). The unofficial statement is a condition
  of continuing to publish, not decoration.
- The organisers have **not** been contacted yet about this project; that is an open item
  (brief §20). `[PENDIENTE: registrar la fecha y el resultado del contacto con
  Corpocarnaval cuando ocurra]`

## 3. The information is provided as is

The programme, history, news, and images on this site are collected from public sources
and compiled by one person who is not an organiser.

- **Every item carries its source.** Headline, source URL, outlet, publication date, and a
  short summary written in the maintainer's own words — never the full article and never
  its images (brief §11). Images carry author, source, licence, and a pre-formatted
  citation string (ADR 0004, `docs/fuentes-y-atribucion.md`).
- **Accuracy is not guaranteed.** Extraction can be wrong, a summary can misrepresent the
  original, a time can shift, and a venue can change. Nothing here has been verified by an
  organiser.
- **The programme changes once a year** (brief §5). What is shown for one edition is not
  the programme for another, and the schedule of a future edition is unknown until it is
  published. Do not assume the current edition's days apply to the next one.
- **Third-party links may be wrong, moved, or gone.** They are reproduced as found.
- **Corrections are welcome** through the contact channel; errors that reach the public are
  corrected and recorded, not quietly deleted.

## 4. Do not rely on this site for safety-critical decisions

**The site is not a safety information source.** It must not be used, alone or with other
material, to decide whether to attend, whether a route is passable, whether an area is
safe, or how to behave in an emergency.

Crowds, weather, alcohol, road closures, structural hazards, and public-order decisions
during the carnival involve real physical risk. This site knows none of that: it has no
contact with the organisers, no real-time information, and no verification of any kind.
**For anything affecting your physical safety, use official channels.** `[PENDIENTE:
enumerar los canales oficiales que el proyecto puede recomendar — deben confirmarse con
Corpocarnaval y no inventarse]`

Nothing on this site is medical, legal, or psychological advice.

## 5. Licensing: code is MIT, content is per item

Two different licensing regimes apply, and conflating them is the single most common
misreading of this repository (ADR 0004):

| Thing | Licence |
|---|---|
| Source code, tests, and repository documentation | **MIT**, `LICENSE` |
| **Anything collected or published as content** — programme data, news summaries, historical photographs, embedded video | **Per item**, as stated in that item's attribution. The MIT licence does **not** cover it |

Rules:

- Each published image states its author, source, licence, and citation text
  (`media_assets.author`, `source_ref`, `license`, `citation_text`). Anything with
  `rights_status = unknown` is **not published at all** (brief §11, ADR 0004).
- News is metadata plus a short original summary. Reusing an article's text, images, or
  layout requires the rights holder's own permission.
- **An image is not free of rights because it is old.** Copyright in photographs persists
  long after the subject and the era are forgotten, and archival material may have its own
  separate rights.
- If you reuse anything from this site, check **that item's** attribution and licence. Do
  not assume MIT. Do not strip a citation.
- Embedded video belongs to YouTube or Vimeo and is governed by those platforms' terms
  (ADR 0007). The project hosts no video files and has not obtained a licence for any of
  it.

## 6. Acceptable use

Do not use this site to:

- break the law, or attempt to access areas or data you are not authorised to reach;
- interfere with the site or its sources — in particular, do not scrape it at volume; use
  the public read API instead (brief §6 decision 1);
- present yourself as the project, its maintainer, or an organiser;
- use the project's name, identity, or layout for commercial purposes;
- re-publish scraped third-party material as though it were this project's own.

Abuse may be blocked and, where it involves unlawful content, handled under
`procedimiento-retiro-y-takedown.md`.

## 7. What contributors grant

If you submit material through the public contribution form (v3):

- You declare you are the author or hold the rights needed to submit it, and that you
  are authorised where identifiable people — **including minors** — appear
  (`consent_records.declaration_rights`, `declaration_minor_subject`, brief §10).
- You grant a **non-exclusive, revocable-on-request, worldwide, royalty-free licence to
  display the material on this site, with credit to you**. No exclusivity is transferred;
  you keep your rights.
- You may optionally offer a Creative Commons licence. Declaring one does not transfer
  copyright.
- You grant **no warranty** that the material is yours, accurate, or free of third-party
  claims. You indemnify the project against claims arising from material you submitted.
- The acceptance is recorded against the **exact version** of the terms and privacy policy
  you were shown (`consent_records.legal_document`). Later versions do not retroactively
  change what you agreed to.
- A submission is **unreviewed and unlicensed to the public** until a moderator approves
  it. Approval can be withdrawn (`moderation_actions.action = withdraw`), including by
  request.

See `politica-de-contenido-y-publicacion.md` for what may not be submitted at all.

## 8. Limitation of liability

**To the maximum extent permitted by applicable law**, the maintainer and contributors are
not liable for:

- the accuracy, completeness, timeliness, or availability of any content or of the site;
- any loss arising from reliance on the content, including decisions about attending the
  carnival and any physical harm, whether direct or indirect, to the fullest extent the
  law allows that limitation;
- any claim by a third party over content collected from a source, where attribution was
  given and the item was lawfully published;
- the acts of organisers, venues, platforms, or any third party, including embedded video
  providers.

Liability that cannot lawfully be excluded — including liability for wilful misconduct, and
any liability toward data subjects under `politica-de-privacidad.md` — is unaffected.

The site is provided **free of charge** and **as available**. `[PENDIENTE: decidir si se
fija un límite cuantitativo de responsabilidad y redactar la cláusula de jurisdicción —
ambos requieren revisión profesional]`

Nothing in these terms limits rights that Colombian law does not permit to be limited.
Consumer and data-subject rights are preserved in full.

## 9. Personal data

Personal data is handled under `politica-de-privacidad.md`, which is part of these terms.
In summary: no raw IP addresses are stored, images have EXIF including GPS stripped,
there is no third-party tracking or advertising cookie, and data subject rights under
**Ley 1581 de 2012** (the Colombian data-protection statute, *habeas data*) are described
there.

## 10. Intellectual property complaints

If you believe material on this site infringes your rights, or depicts you or a minor
without authorisation, use `procedimiento-retiro-y-takedown.md`. `[PENDIENTE: canal de
contacto publicado para solicitudes de retiro]`

## 11. Changes to these terms

- These terms are **versioned**. A change creates a new version in `legal_documents` with
  a new `version` and `effective_from`; the current version is always identified on the
  site.
- **A published version is never edited.** Old versions stay available so that an old
  acceptance remains interpretable.
- **Changes are not retroactive.** An acceptance of `1.0` is judged against `1.0`.
- Material changes are announced on the site. `[PENDIENTE: plazo de preaviso antes de la
  entrada en vigor de un cambio material]`

## 12. Contact

`[PENDIENTE: correo de contacto del proyecto]`

`[PENDIENTE: domicilio o medio de notificación válido para Colombia]`