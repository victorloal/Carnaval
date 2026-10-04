# Privacy and personal data policy — DRAFT

> **DRAFT — NOT LEGAL ADVICE, AND NOT GOING TO BE REVIEWED.**
> Machine-drafted for engineering purposes and **published as a draft on purpose.** It has
> **not** been reviewed by a qualified lawyer and none will be: that was decided on
> 2026-10-04 and is recorded in **ADR 0016**. It describes data handling in engineering
> terms and reaches **no legal conclusions** about Colombian law: no statute articles, no
> decrees, no case law, no verification of any obligation. Bracketed `[PENDIENTE: …]` items
> are **unresolved by decision, not by oversight** — including every retention period and the
> entire data-subject request procedure, which is exactly what professional review would have
> settled. No implementer may fill one with a plausible value.
> **Do not rely on it.** Ley 1581 de 2012 applies to this site's processing whether or not
> anyone reviewed this notice.
>
> Colombian legal concepts are named in Spanish on first use, per brief §10. The operative
> notice is expected to be Spanish; this English draft is provided for readability. ADR 0016
> keeps the draft rather than replacing it with a reviewed version.

- **Status:** Draft, permanently unreviewed (ADR 0016)
- **Version in database:** `legal_documents` row to be created. `is_current = true` is
  permitted and the row records that the text was never professionally reviewed (ADR 0016
  §1).
- **Relates to:** brief §10, §11, §14; `docs/00-acta-proyecto.md` §4.2, §6; ADR 0005,
  ADR 0006, ADR 0007, **ADR 0016**; `docs/02-diseno/modelo-datos.md` §5, §6.3, §8

## 1. Who handles your data

The project is run by **one individual** with no employees and no server-side
organisation. In Colombian terms that person is intended to act as the
**responsable del tratamiento** (data controller) of the personal data described here.
`[PENDIENTE: confirmar la figura jurídica que aplica (responsable o encargado) y los datos
de identificación exigidos para una notificación en Colombia — requiere revisión
profesional]`

There is no data protection officer, no DPO, and no privacy team.

**Data controller:** Victor Lopez, reachable at **victorloal513@gmail.com**. The project is a
personal, non-commercial portfolio project with no employees and no legal entity; the
individual maintainer is therefore the data controller for everything described in this
notice. `[PENDIENTE: confirmar si esta figura jurídica es la que aplica bajo la Ley 1581 de
2012, y si procede algún registro ante la autoridad de protección de datos — punto que
requeriría asesoramiento profesional y que ADR 0016 deja sin resolver de forma deliberada]`

## 2. What personal data is processed

| Data | Where | Form | Why it exists |
|---|---|---|---|
| IP address of a submission, of an admin login, and of a takedown email | `consent_records.ip_hash`, `audit_logs.ip_hash` | **Hashed only. Never stored raw** (brief §10) | Abuse limits, audit evidence, proving consent was given |
| Browser identification | `consent_records.user_agent_hash` | Hashed | Distinguish a contributor from a script; not read as a fingerprint |
| Optional contributor email | `submissions.contact_email` | **Cleartext**, optional | Reply to questions about a submission. **Never exposed by the public API** |
| Claimant details | `takedown_requests.requester_name`, `requester_email` | **Cleartext**, email required | A reply is required; without an address there is no way to respond |
| Admin account identity | `auth_user`, `otp_totpdevice` | Cleartext, plus hashed passwords (Argon2id) | Access control. No public sign-up; the first admin comes from a seed command (ADR 0005) |
| Server request logs | Hosting provider | As emitted by the server and the CDN | Security and operations; not under the application's control |
| IP and location embedded in an uploaded photograph | — | **Never retained.** EXIF including GPS is stripped unconditionally before storage (ADR 0006) | There is no legitimate case for keeping a contributor's location |

**Not processed:** raw IP addresses, EXIF/GPS, facial recognition, advertising
identifiers, cross-site tracking profiles, or any sale or sharing of personal data.

Note the deliberate inconsistency: two email fields are stored in cleartext because a
reply is legally required, while the address that gave consent is never stored at all —
`consent_records` holds hashes only.

## 3. Why IP addresses are salted hashes

Where an IP address must be recorded (consent evidence, abuse limits, audit trail), it is
stored as **SHA-256 of the IP address concatenated with a secret salt held in an
environment variable**.

The reason is not obscurity, it is a concrete weakness:

- **An unsalted hash of an IPv4 address is trivially reversible.** The entire IPv4 space
  is 2³² candidates — about 4.3 billion, exhaustible in minutes on ordinary hardware. You
  do not need the pre-image; you hash all of them and compare. A stored `sha256(ip)` on an
  IPv4-only system **is** the address, just wearing a disguise, and it also degrades the
  stored value into a stable cross-context identifier.
- **Salting with a server secret removes that.** The hash cannot be recomputed without the
  salt, so an attacker with a copy of the database cannot enumerate the address space, and
  hashes of the same address cannot be compared across contexts or linked to an external
  IP list.
- **It is irreversible for us too**, deliberately. A hashed address can prove that *the
  same* client did something twice, and nothing more. It cannot be turned back into an
  address, so it cannot leak one either.

Consequences that must be respected when implementing:

- The salt is a **secret in an environment variable** — never in the database, never in
  `site_settings`, never in git (brief §9; modelo-datos §4.4).
- **Rotating the salt invalidates every existing hash**, breaking abuse limits and
  continuity of the audit trail for historical records. `[PENDIENTE: decidir si la sal rota
  o si se documenta como irreversible]`
- A hash may still be personal data for as long as it exists. It is minimised, not exempt.

## 4. Purposes and legal basis

| Processing | Purpose | Legal basis |
|---|---|---|
| Recording a submission and its consent | Operating the contribution feature | `[PENDIENTE: definir la base legal]` |
| Hashed IP for rate limiting and CAPTCHA | Preventing abuse of an anonymous public form | `[PENDIENTE: definir la base legal]` |
| Cleartext email of a contributor or claimant | Being able to answer them | `[PENDIENTE: definir la base legal]` |
| Admin accounts, sessions, TOTP | Security of the moderation panel | `[PENDIENTE: definir la base legal]` |
| Audit trail (`audit_logs`) | Evidence of who approved, rejected, or changed configuration | `[PENDIENTE: definir la base legal]` |

**The legal basis for every activity is an open item and is deliberately not guessed
here.** Under **Ley 1581 de 2012** (the Colombian data-protection statute, *habeas data*)
a basis must be identified for each purpose; whether consent, another basis, or a
combination applies to an anonymous open submission is exactly the question that needs a
lawyer. The consent collected at submission is a **declaration recorded per version of the
legal text** (`consent_records` → `legal_documents`), not a substitute for that analysis.

`[PENDIENTE: determinar si el proyecto debe inscribirse en el registro de bases de datos
personales de la autoridad de control competente, y con qué periodicidad]`

## 5. Retention and deletion

**Every period below is unresolved.** No period may be invented by an implementer, and no
feature may ship with an indefinite default.

| Category | Period | Note |
|---|---|---|
| `consent_records` (with its `ip_hash`) | `[PENDIENTE: N days from acceptance]` | Must outlive moderation of the submission; must not outlive its justification |
| `submissions.contact_email` | `[PENDIENTE: N days after the submission is decided]` | Modelo-datos §8 says this field carries a deletion deadline once the matter is closed |
| `takedown_requests.requester_email` | `[PENDIENTE: N days after `responded_at`]` | Same rule: a reply is required, indefinite storage is not |
| Rejected upload files in quarantine | `[PENDIENTE: N days from rejection]` | ADR 0006: rejection deletes the file or retains it per the retention policy |
| `raw_documents` (ingested payloads) | `[PENDIENTE: N documents per source / N days]` | Open question 3 in modelo-datos §10; also bounds free-tier storage |
| `audit_logs` | `[PENDIENTE: N days]` | Tension: the audit trail is evidence in a dispute, so shortening it can destroy the proof a rights holder needs. Decide deliberately, per event class |
| `django_session` rows | `[PENDIENTE: N days after expiry]` | Expired sessions are among the few things that may be hard-deleted (modelo-datos §1) |
| `ingestion_runs` | `[PENDIENTE: N days]` | Operational, contains no personal data beyond a hashed IP |

Deletion means **hard deletion of the row or the object**, not anonymisation by default.
Where a record must be kept as evidence, keep the evidence and drop the personal data, and
record that decision in `notes`. Secrets are never stored in the database at all
(modelo-datos §4.4).

## 6. Your rights under Ley 1581 de 2012

Described at a **high level only**, for orientation. This is not a statement of the law,
and the procedure below does not exist yet.

| Right (derecho) | In plain terms |
|---|---|
| **Derecho de información** | To be told, before or at the time, that data is being collected and for what purpose |
| **Derecho de acceso** | To ask what data is held about you |
| **Derecho de rectificación o actualización** | To have inaccurate data corrected |
| **Derecho de supresión** | To ask for data to be deleted, subject to legal exceptions |
| **Derecho de reclamo** | To complain about how data was handled, and to escalate to the competent authority |
| **Derecho de consulta** | To consult what is held about you |
| Rights regarding **minors and adolescents** | Extra protection applies to children's data |

Practical reality that must be stated plainly in the final notice: **contributors do not
have accounts** (brief §4). There is therefore no account identifier to look up, and in
most cases the site cannot even confirm whether a given person submitted anything. That does
not excuse ignoring a request — it defines what the response will often be.

`[PENDIENTE: procedimiento formal de atención de derechos — canal, plazo de respuesta,
identificación del solicitante, y forma de respuesta]`

`[PENDIENTE: plazo máximo de respuesta a una solicitud de derechos]`

## 7. Minors

- The project does not knowingly collect data directly from children; the contribution form
  is addressed to adults.
- **Photographs showing minors require guardian authorisation before publication**
  (`minor_subject` + `guardian_consent_on_file`, and the contributor's
  `declaration_minor_subject`). See `politica-de-contenido-y-publicacion.md` §5.
- A guardian who wants an image removed should use the takedown procedure. Such a request
  is treated as a `privacy` claim and is prioritised. `[PENDIENTE: plazo de respuesta
  prioritario para solicitudes de menores]`

## 8. Cookies

| Cookie | Set by | Purpose | Lifetime |
|---|---|---|---|
| Session cookie | Django | Authenticates an **admin** session. Carries only a session key — **no token of any kind** — in `httpOnly`, `Secure`, `SameSite=Lax` (ADR 0005) | `[PENDIENTE: N days idle / absolute]` |
| CSRF cookie | Django | Protects mutating requests | Session |
| Locale preference | Frontend | Remembers the visitor's `es`/`en` choice, per ADR 0010. **Necessary for the choice to work; requires no account** | `[PENDIENTE: N days]` |

**No third-party tracking, analytics, advertising, or profiling cookies are used.** The site
has no ad tech, no analytics, and no social embeds. This is a deliberate constraint from
brief §4 (advertising out of scope) and the project's zero-tracking stance.

**Note on the deviation from the brief.** Brief §6 decision 8 and §9 specify JWT cookies
with rotating refresh tokens. ADR 0005 supersedes that: there is **no JWT in this project**
and no bearer credential in the browser at all. A visitor's privacy position is therefore
better than the brief required — there is nothing in `localStorage` and nothing to exfiltrate.

## 9. Embedded video and third parties

Community video is an **external embed from YouTube or Vimeo**; the project hosts no video
files (ADR 0007). Consequences for privacy:

- Loading an embed contacts a third party, which may set its own cookies, and may receive
  the visitor's IP address and referrer. That is a **transfer to a third-party processor and
  possibly to another country**, and the project's privacy position is only as strong as
  theirs.
- Mitigations already decided: **`youtube-nocookie.com`** for YouTube embeds, a **consent
  notice before the embed loads** rather than loading it automatically, and a plain link as
  fallback if the embed is blocked.
- `[PENDIENTE: decidir si los embeds requieren un clic explícito de consentimiento antes de
  cargar — muy recomendable, pero debe confirmarse en la versión revisada]`

Other third parties that receive visitor data:

| Party | Data | Note |
|---|---|---|
| Database hosting provider | All application data | `[PENDIENTE: proveedor y país]` |
| Object storage provider (quarantine and public buckets) | Uploaded files | Provider undecided between R2 and Supabase Storage (ADR 0006) |
| Database and application hosting | Requests | `[PENDIENTE: proveedor y país]` |
| CAPTCHA provider (for example Turnstile) | Visitor IP and page, on the submission form | **Runs before consent is given**, which needs analysis. `[PENDIENTE: evaluar si un CAPTCHA de terceros es compatible con el compromiso de no transmisión; alternativa: CAPTCHA propio]` |
| GitHub | Repository history, if any contributor is identified in a commit | No contributor identity is collected by the site itself |

The site hosts no font, script, or image from a third-party CDN, so no passive third-party
tracking occurs during normal reading.

## 10. Security measures

- Passwords hashed with **Argon2id**; **TOTP** as a second factor for administrators
  (ADR 0005).
- Sessions server-side and revocable centrally; no token issued to the browser.
- **RBAC enforced server-side** on every request (`admin`, `editor`, `viewer`); the admin
  UI hiding a control is never the control.
- Uploads validated by **magic bytes**, fully re-encoded, served from a **separate domain**
  with `X-Content-Type-Options: nosniff`, in **private quarantine** until approved
  (ADR 0006).
- Secrets only in environment variables; HTTPS; security headers.
- `audit_logs` is append-only, with no update or delete permission for any role.

## 11. Contact, requests, and complaints

- Personal data requests: **victorloal513@gmail.com**
- Rights or complaints about this notice: `[PENDIENTE: procedimiento y plazo de respuesta]`
- Takedown and removal requests: `procedimiento-retiro-y-takedown.md`
- **A complaint may be escalated to the competent Colombian data-protection authority**
  (*derecho de reclamo*). `[PENDIENTE: confirmar el nombre y el canal de la autoridad
  competente — no se cita aquí para no consignar un dato sin verificar]`

## 12. Changes to this policy

This policy is versioned in `legal_documents` (`doc_type = privacy`). A change creates a new
version with an `effective_from`; a published version is **never edited**, because
`consent_records` points at the exact row a contributor accepted and must remain
interpretable. `[PENDIENTE: plazo de preaviso antes de la entrada en vigor de un cambio
material]`