# Removal and takedown procedure — DRAFT

> **DRAFT — NOT LEGAL ADVICE, AND NOT GOING TO BE REVIEWED.**
> Machine-drafted for engineering purposes, as an operating procedure for the sole
> moderator, and **published as a draft on purpose.** It has **not** been reviewed by a
> qualified lawyer and none will be: that was decided on 2026-10-04 and is recorded in
> **ADR 0016**. It states no Colombian legal conclusions, no statute or decree references,
> and no case law — in particular **no authority names and no hotline numbers**, because
> inventing or mis-transcribing one in an escalation document is worse than leaving a marked
> gap. Bracketed `[PENDIENTE: …]` items are **unresolved by decision, not by oversight**. The
> **deadlines are the exception**: they were set as revisable operational defaults by the
> maintainer (**ADR 0018**).
> **Do not rely on it.**
>
> **Deadlines (ADR 0018):** acknowledge within **7 days**, resolve within **30 days**,
> guardian requests about minors prioritised at **48 hours**, and unlawful content escalated
> **immediately** and never closed by a note. No claim is ever refused for arriving late.
> Brief §20 also lists *"definir el procedimiento de moderación y de denuncia de contenido
> ilegal"* as a separate open item — this file is a draft of that procedure.

- **Status:** Draft, permanently unreviewed (ADR 0016); deadlines set operationally (ADR 0018)
- **Version in database:** `legal_documents` row to be created. `is_current = true` is
  permitted and the row records that the text was never professionally reviewed (ADR 0016
  §1).
- **Audience:** the moderator (the sole maintainer, `admin` + `editor` roles)
- **Relates to:** brief §10, §11, §14; `docs/00-acta-proyecto.md` §4.2, §8; ADR 0004,
  ADR 0006, ADR 0007, ADR 0008, **ADR 0016**, **ADR 0018**; `docs/02-diseno/modelo-datos.md` §2, §6.5,
  §6.6, §8

## 1. Purpose and scope

A rights holder, a depicted person, a guardian, or anyone reporting unlawful content must be
able to make the site remove or correct something quickly, and the project must be able to
**show what it did**. This document is the procedure for that. It covers every kind of
published item:

- programme data (`events`), news (`news_items`), historical images (`media_assets`),
  community submissions (`submissions`, `submission_files`), and embedded video references;
- material in the **repository** (docs, images, fixtures) — see §9;
- material referenced from **third-party sources**, where the correct action is to contact
  the source, not to modify our record.

## 2. What counts as a valid claim

`takedown_requests.claim_type` (modelo-datos §6.6) has four values. A request may only be
actioned as one of these; anything else is triaged into `other`.

| `claim_type` | What it asserts | What makes it actionable | Typical action |
|---|---|---|---|
| **`copyright`** | The claimant owns the rights, or is authorised to act for the owner | Identification of the work and evidence of ownership or authority; a URL to the original where one exists | Withdraw the item (`withdraw`) and delete the public file; stop republishing |
| **`privacy`** | The item exposes the claimant's (or a third party's) personal data, or depicts them without consent — **including a minor without guardian authorisation** | Which item, and what specifically about it is the problem | Withdraw the item; redact personal data from descriptions; `minor_subject` cases are prioritised |
| **`illegal_content`** | The item is itself unlawful, so keeping or redistributing it is unlawful | The item, and the nature of the illegality | **Escalate, do not merely withdraw.** Never published, never redistributed, even while pending. Report to the authorities or a line such as **Te Protejo** (brief §10) |
| **`other`** | Anything else: accuracy disputes, unofficial use of the site's name, takedown requests against a *third party* to whom we should forward the complaint, spam | A description of the concern | Route to the appropriate action, or forward to the relevant party |

**A claim is not invalid because it is inconvenient.** The cost of a wrong withdrawal is one
item and one apology; the cost of ignoring a valid one is a rights-holder dispute and a
reputational loss that this project cannot absorb.

## 3. Required information from the claimant

Recorded in `takedown_requests`:

| Field | Required? | Note |
|---|---|---|
| `requester_email` | **Yes** | Needed in order to respond. This is PII and is retained only until the matter is closed (privacy policy §5) |
| `requester_name` | No | Optional; helps verify identity |
| `subject_type`, `subject_id` | **Yes** | What is being challenged. If the claimant cannot identify it, the moderator finds the item from the description |
| `claim_type` | **Yes** | From the four values above |
| `evidence_url` | No | Where the original work, the official page, or the evidence lives |
| Free-text description | **Yes** | What the claimant wants: removal, correction, or an explanation |

Minimum to be actionable: **a way to reach the claimant + a way to identify the item +
what they want**. Anything less is answered with an explanation of what is missing rather
than left unanswered; `[PENDIENTE: respuesta al solicitante incompleto — plazo y
formulario]`.

Practical note: because there are **no public accounts** (brief §4), a claimant often cannot
point at "their" submission. Ask for enough detail to find the item — approximate year,
place, subject. Do not use the fact that a claim is hard to attribute as a reason to
refuse it.

## 4. Deadlines

**These deadlines are the maintainer's operational defaults (ADR 0018)**, not legal advice.
They are written into the published procedure so a rights holder knows what to expect, and
they are deliberately short because the remedy — removing a link or an image — is cheap.

| Step | Deadline |
|---|---|
| Acknowledge receipt | **7 days from `received_at`** |
| Resolve — `actioned`, `rejected`, or `escalated` | **30 days from `received_at`** |
| Guardian requests about minors (`privacy` + `minor_subject`) | **prioritised: acknowledge within 48 hours** |
| Unlawful content (`illegal_content`) | **escalated immediately** — never closed by a note (the model enforces this) |
| Responding to the organisers if they ask for material to be removed | **7 days** |
| Retention of `requester_email` | **24 months after `responded_at`** (ADR 0018) |

Setting a deadline the maintainer cannot keep is worse than publishing none. These are chosen
against the reality of a single part-time operator: 7 days to acknowledge, 30 to resolve.

## 5. Triage procedure

1. **Receive.** A claim arrives at the published channel **victorloal513@gmail.com**.
   Create the `takedown_requests` row: `subject_type`, `subject_id`, `requester_email`,
   `claim_type`, `received_at`, `status = received`. `responded_at` stays null. The receipt
   is itself evidence that the claim arrived.
2. **Acknowledge.** Confirm to the claimant that the request was received and give the
   expected resolution date (§4). Record nothing in `notes` beyond what is factual.
3. **Triage** — decide within the same sitting whether the claim is:
   - **actionable** — a listed basis applies (§2);
   - **ambiguous** — escalate internally: withhold first, decide later. A temporary
     withdrawal is cheap and reversible; leaving unlawful material up is not;
   - **outside the project** — the complaint is about a third party's material. Tell the
     claimant that and forward it if appropriate. Do not pretend to have removed something
     you did not host.
4. **Move to `in_review`.** This is the state that means *a human is actively working on it*.
   A request stuck in `received` for weeks is a failure, not a queue.
5. **Investigate.** Identify the item and its provenance from `sources` and `media_assets`
   rights metadata. If `rights_status = unknown` for an item that is somehow published, that
   is an incident as well as a takedown — record it and withdraw the item.
6. **Decide and act** per §6, or escalate per §7.
7. **Record** `action_taken`, `responded_at`, and `notes` (§8).
8. **Close** as `actioned`, `rejected`, or `escalated`, and write `action_taken` so a later
   reader knows exactly what happened to the item.

## 6. State machine

Matches `takedown_requests.status` (modelo-datos §6.6) exactly. No other values, no other
transitions.

```
            received ──► in_review ──┬──► actioned    (claim upheld, item changed)
       ▲                          │
       │                          ├──► rejected    (unfounded or out of scope)
       │                          │
       └── (a new claim)          └──► escalated   (illegal_content: referred out)
                                                   │
                                                   ▼
                                   terminal: the matter leaves this project's hands
```

| Transition | Meaning | Mandatory side effects |
|---|---|---|
| `received → in_review` | Triage done, work started | Acknowledgement sent |
| `in_review → actioned` | The claim was upheld and something changed | `action_taken` + `responded_at`; a `moderation_actions` row; an `audit_logs` row |
| `in_review → rejected` | The claim was unfounded, or outside scope | `action_taken` states **why** + `responded_at`; the claimant is told the reason |
| `in_review → escalated` | Referred to the authorities or a protection line | `action_taken` names **where it was referred and on what date**; evidence preserved |
| `escalated → …` | **Terminal.** Nothing further is recorded on this row | — |

`claim_type = illegal_content` **forces** `escalated` (modelo-datas §6.6). An internal note
is not a sufficient response to a report of unlawful content — the content must be
**reported** (brief §10). A request may not stay in `in_review` indefinitely: if a decision
cannot be reached, escalate.

## 7. What happens per claim type

### 7.1 `copyright`

- **Immediately** mark the item unpublished (`moderation_actions.action = withdraw`,
  `status = pending`), so it stops being served while the claim is examined. Only a human
  does this — nothing transitions out of `published` automatically (modelo-datos §2).
- Remove the public file from public storage; keep nothing in public storage.
- If the item is **scraped from a source**, the correct primary action is to stop
  collecting it and to contact the source. Our repository row is a citation, not a copy —
  except for images, which we do host.
- If permission can be established quickly (an archive under an open licence, or the owner
  grants it), the item may be re-published with `rights_status` and `license` updated and a
  `moderation_actions` row explaining it. Re-publishing after a withdrawal is an explicit
  human decision.
- Close as `actioned`.

### 7.2 `privacy`

- Withdraw the item first. Personal-data harm is ongoing while the item is live.
- Then decide the narrower remedy: redact identifying details from a description, crop an
  image `[PENDIENTE: ¿se permite recortado o solo retirada? el recorte destruye el contexto y
  requiere decisión registrada]`, or withdraw the whole item.
- **Guardian requests** (`privacy` where a minor is the focal subject) take priority. Also
  check whether guardian authorisation was ever on file; if it was not, the item should
  never have been published and that is an incident worth recording.
- **Unauthorised commercial advertising** in a description: withdraw, and treat as
  `other` if it also breaches the content policy.
- Close as `actioned`.

### 7.3 `illegal_content`

**Never publish it. Never redistribute it. Never serve it while pending.** Brief §10 is
unambiguous on this.

1. Stop the content being visible immediately, including in the review interface. Do not
   open it further; do not re-share it; do not download it to inspect it.
2. Preserve what is needed to report it — the URL, the claim, the date — without
   redistributing the material itself.
3. **Report it to the competent authorities or to a line such as Te Protejo**
   (brief §10). `[PENDIENTE: definir la autoridad o línea concreta, su canal, y el
   responsable de la notificación — no se cita ninguna aquí para no consignar un dato o un
   número sin verificar]`
4. Set `status = escalated` and record **where it was referred and when** in `action_taken`.
5. If the material was submitted by a member of the public, treat the submission itself as
   a policy breach and apply §7.5.
6. Do not warn the submitter before escalation where warning would risk tipping off or
   enabling the behaviour. `[PENDIENTE: criterio del mantenimiento al avisar o no al
   remitente]`

### 7.4 `other`

Accuracy disputes, unofficial use of the project's name, or a complaint about a third
party.

- Accuracy: correct the record, record the correction in `audit_logs`, and reply. The
  database is the source of truth, so the fix is cheap (ADR 0002).
- About a third party: say plainly that the project does not host that material, and forward
  the request to whoever does. `[PENDIENTE: a quién se reenvía y con qué autorización para
  compartir datos del solicitante]`
- Close as `actioned` or `rejected`, with the reason recorded either way.

### 7.5 Repeat infringers

No public accounts exist, so there is no account to ban. See
`politica-de-contenido-y-publicacion.md` §8 for the full control set. In takedown terms:

- Record every claim in `moderation_actions`, so a pattern by contributor, by contact
  address, or by hashed IP is visible after the fact.
- Re-examine previously published items from the same source of a successful claim.
- Refuse future submissions from a contributor with a documented pattern, and say why.
  `[PENDIENTE: mecanismo concreto de bloqueo y cómo se comunica]`
- Where a source — a publication, an archive — is the infringer, the remedy is a request to
  them, recorded here as a forwarded `other` claim, not retaliation.

## 8. Recording: `moderation_actions` and `audit_logs` are append-only evidence

`moderation_actions` exists precisely because it is the **evidence trail for a rights or
takedown dispute**, separate from the general audit log (modelo-datos §6.5).

| Field | What to write |
|---|---|
| `subject_type`, `subject_id` | The moderated object |
| `action` | `submit`, `approve`, `reject`, `request_changes`, `withdraw` |
| `actor` | The moderator, or null for an automated submission |
| `reason` | **Required for `reject`.** Also the right place for the reasoning behind a `withdraw` |
| `created_at` | Set by the system |

On `takedown_requests`:

| Field | What to write |
|---|---|
| `status` | One of `received`, `in_review`, `actioned`, `rejected`, `escalated` |
| `action_taken` | What was **actually done**, in plain language: “public file deleted and item withdrawn”, “referred to \<authority\> on \<date\>”, “forwarded to the source”. Never leave it null on a closed request |
| `responded_at` | When the claimant was told. Set **only** when the reply actually went out, not when the decision was made |
| `notes` | Internal. Facts and reasoning, never speculation about the claimant |

Hard rules:

- **`audit_logs` is append-only.** No role — including `admin` — has update or delete
  permission on it (modelo-datos §5.1). Never edit or delete a log row to "fix" it; append a
  correcting action instead.
- **`moderation_actions` rows are never deleted or edited.** They are append-only.
- **Never delete the evidence.** Removing the log entry that a claim was received would turn
  the dispute into an unanswerable one.
- Published content is normally never hard-deleted (modelo-datos §1), but **a takedown is an
  explicit human action** and may remove an item and its file. Record the removal in the log
  so the history stays reconstructable.
- Secrets never go in `notes`.

## 9. Material in the repository

A takedown can also concern the repository itself, which is public on its hosting service.

- Third-party material is never committed in the first place: `data/raw/` and `*.pdf` are in
  `.gitignore` (ADR 0004). If a PDF, photograph, or article text is found committed, it is
  removed in a follow-up commit and the error is recorded.
- Historical versions of a public repository are hard to erase completely, so prevention is
  the control: attribute, or do not commit.
- The repository's own documents and code are the maintainer's and are not subject to this
  procedure.

## 10. Moderator checklist

Per request, in order:

- [ ] `takedown_requests` row created with `subject_type`, `subject_id`, `requester_email`,
      `claim_type`, `received_at`; `status = received`
- [ ] Acknowledgement sent within **7 days**
- [ ] Is this `illegal_content`? → stop visibility first, then escalate; **never** publish,
      redistribute, or serve it while pending
- [ ] Is a minor the focal subject and no guardian authorisation on file? → withdraw,
      prioritise, record the incident
- [ ] Rights metadata checked: `author`, `source_ref`, `license`, `citation_text`,
      `rights_status`; `unknown` means it should not have been published at all
- [ ] If embedded video: remove our reference **and** contact the provider (ADR 0007) — we
      do not host the file
- [ ] If scraped: decide whether to disable the `scrape_sources` row
- [ ] `moderation_actions` row written (`withdraw`, `reject`, or `approve` if restored) with
      a `reason`
- [ ] `audit_logs` row written; **never** edited or deleted afterwards
- [ ] `status` set to `actioned`, `rejected`, or `escalated` — nothing left in `in_review`
- [ ] `action_taken` written in plain language, naming what was done
- [ ] `responded_at` set **after** the reply was actually sent
- [ ] `notes` added if the reasoning is not obvious from the above
- [ ] Retention deadlines for `requester_email` noted (**24 months after
      responded_at**)
- [ ] Repeat-infringer pattern checked against `moderation_actions`

## 11. Contacts

- Claimants: **victorloal513@gmail.com** — the same address published in `README.md` and in
  the scraper's `User-Agent`
- Emergency/law-enforcement escalation: `[PENDIENTE: definir autoridad o línea y canal —
  brief §10 menciona "líneas como Te Protejo" sin confirmar cuál aplica]`
- The organisers (Corpocarnaval / parade organisers): `[PENDIENTE: canal de contacto, y
  fecha del primer contacto — brief §20, todavía no realizado]`
- Rights holders who ask for something to be removed before v3: handle manually under this
  same procedure; there is no form until the moderation tooling exists.