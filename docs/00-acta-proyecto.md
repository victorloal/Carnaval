# Project minutes — Carnaval de Negros y Blancos

- **Date:** 2026-10-03
- **Phase:** Fase 0 — initiation and high-level requirements (brief §16). **Closed
  2026-10-04**; see §12.1
- **Participants:** Victor Lopez (sole maintainer, developer and product owner)
- **Repository state at time of writing:** documentation only, single `Initial commit`

## 1. Purpose of this document

This is the project charter record required by brief §18 step 1. It fixes the scope, the
stakeholders, the constraints, the risks, and the criteria by which this project will be
judged successful. Later documents (SRS, design, ADRs) derive from it; where they conflict
with it, the discrepancy must be recorded rather than silently resolved.

## 2. Project identification

| Field | Value |
|---|---|
| Name | Carnaval de Negros y Blancos |
| Type | Personal portfolio project, non-commercial |
| Subject | Carnaval de Negros y Blancos de Pasto, Nariño, Colombia |
| Sponsor | None — self-initiated, self-funded |
| Repository | Carnaval (monorepo, ADR 0003) |
| License | MIT, code only (ADR 0004) |
| Methodology | Scrumban, 1-week sprints, WIP limit 2 (ADR 0001) |

## 3. Problem statement

No official public API or open dataset exists for the parade. The information lives on the
official WordPress site `carnavaldepasto.org` (built with WordPress and Elementor) and in a
PDF of the schedule, neither structured for consumption and neither stable — the schedule is
republished once a year, and the site markup can change without notice.

Beyond the schedule there is no orderly, correctly cited home for historical material
(news, old photographs), and no way for the community to contribute material under review.

## 4. Stakeholder analysis

### 4.1 Internal

| Stakeholder | Role | Interest | Influence | Engagement strategy |
|---|---|---|---|---|
| Victor Lopez | Developer, product owner, sole moderator | Completing a portfolio piece demonstrating the full engineering lifecycle; learning the data/security domain | Total — sole decision maker | Writes and approves every artefact; the Definition of Done (ADR 0001) is his own quality gate |
| Future employers / reviewers | Intended audience of the repository | Judging whether the process is real, reproducible, and complete | High, indirect | The repository *is* the deliverable. Docs, ADRs, and CI are the evidence. No account or signup needed to evaluate it |

### 4.2 External

| Stakeholder | Interest | Impact on the project | Strategy |
|---|---|---|---|
| **Visitantes / site readers** (primary) | Accurate, well-cited, fast information about the parade, in Spanish | They are the users of the public site | Public read API with no registration; mobile-first, accessible; Spanish primary, English secondary (ADR 0010) |
| **Community contributors** | To contribute historical photographs and video links without registering | The entire v3 feature set | Anonymous submission with CAPTCHA, explicit consent, and quarantine-before-publish. Their content is unreviewed and unlicensed until a moderator approves it |
| **Corpocarnaval / parade organisers** | Accuracy of the information; control over use of their material and name | Highest **legal and reputational** risk: not affiliated, yet scraping and republishing their content and using their name | **No affiliation or endorsement may be implied.** Cite sources, respect `robots.txt` and terms, use an identifiable User-Agent. Contact them before publishing, per brief §11 and §20 |
| **Rights holders** (photographers, publishers) | Attribution and control over reuse | Takedown liability; wrongful publication is the top-rated reputational risk | Mandatory citation per item; `rights_status = unknown` blocks publication; a documented takedown procedure |
| **Photographed individuals and their guardians** | Consent to appear, especially minors | Privacy exposure and, for minors, legal and ethical harm | Consent declaration required; no image where a minor is the focal subject without guardian authorization; EXIF/GPS stripped |
| **Data subjects** (submitters) | Privacy of their IP address and contact details | Ley 1581 de 2012 (habeas data) compliance | Raw IPs are never stored, only hashed; consent version recorded; takedown channel published |
| **External sources** (`carnavaldepasto.org`, news outlets) | Not to be overloaded or misrepresented | Blocking, rate limits, or complaints could end data collection | Rate-limited, cached by content hash, identifiable User-Agent, news stored as headline + link + own summary only |

## 5. Scope

### In scope, by version

| Version | Contents |
|---|---|
| MVP | Ingestion pipeline, PostgreSQL, public read API, public frontend |
| v1 | Django admin, roles, review queue, audit log |
| v2 | News, historical gallery with citations, site and scrape-source settings |
| v3 | Public submissions (images + video links), moderation, legal documents |

### Explicitly out of scope (brief §4)

Ticket sales or any transaction; public user accounts; hosting video files; accepting
arbitrary file types; advertising; reproducing protected third-party content without
permission; native mobile applications.

### Deliberately over-engineered — declared honestly

Brief §15 requires stating this plainly, and it must appear in the public README: the
schedule changes **once a year**, so a continuous pipeline with moderation and public
submissions exceeds what the problem strictly requires. It is built deliberately to
demonstrate data engineering, security, and risk management.

## 6. Constraints

| # | Constraint | Consequence for the work |
|---|---|---|
| C1 | Zero monetary cost | Free tiers only; no resident worker to operate (scheduling via GitHub Actions cron); storage and egress stay within free allowances |
| C2 | One developer, part-time | WIP limit 2; MoSCoW per version; versioned delivery (ADR 0008) |
| C3 | External sources are unstable and may disappear | Database is the source of truth; scraper is optional; fixtures for tests; admin can author everything by hand (ADR 0002) |
| C4 | Copyright of content belongs to third parties | Nothing published without author, source, licence, and citation; no third-party material committed to git (ADR 0004) |
| C5 | Free-tier limits change frequently | Verify limits before publishing; keep the stack portable; do not depend on a specific provider's proprietary feature |
| C6 | Must not imply affiliation with Corpocarnaval | Disclaimer on every page; contact them before launch (open item, brief §20) |

## 7. Success criteria

The project is judged complete when:

1. The site is deployed and publicly reachable at zero cost.
2. All public content carries source attribution and, for editorial content, licence and
   citation metadata.
3. The ingestion pipeline is idempotent and demonstrably so — running it twice produces no
   duplicates.
4. No content reaches `published` without a recorded human decision, and every decision is
   in `audit_logs`.
5. The test suite covers the pipeline, the API, and the security cases in
   `docs/03-pruebas/casos-seguridad.md`, and CI is green.
6. Every requirement in the SRS is linked to at least one test and one artefact in the
   traceability matrix.
7. ADRs record every significant decision, including this document's deviations from the brief.

## 8. Risks accepted at initiation

Full register with mitigations in brief §14. Highest-impact items carried into the threat
model: source markup changes breaking the scraper; copyright claim; compromise of the
admin account; malicious uploads; illegal content submitted publicly; personal data and
minors in images; excessive scope for one person.

## 9. Known deviations from the brief

Recorded here because the brief is the original statement of intent and these changes were
made deliberately. The brief itself has been reconciled: it carries a supersession banner and
each reconciled paragraph names its ADR, so it can no longer mislead a reader on its own.

| Brief section | Brief said | Now decided | ADR |
|---|---|---|---|
| §6 decision 8, §9 | JWT access + rotating refresh tokens in `httpOnly` cookies | **No JWT.** Django sessions in an `httpOnly` cookie + TOTP. No bearer token exists in the browser | ADR 0005 |
| §9 | Access token 10–15 min, refresh rotation | **Dropped** — sessions are revoked centrally, which is stronger | ADR 0005 |
| §12 | Backend TypeScript/Node **or** Python | **Python + Django 5 + DRF** | ADR 0009 |
| §12 | PostgreSQL (Supabase or Neon), *tentative* | **PostgreSQL 16**, confirmed | ADR 0009 |
| §12 | Admin panel with JWT front end | **Django admin**, customized | ADR 0005, 0009 |
| §12, §17 | `openapi.yaml` as a hand-written design artefact | **Generated** by drf-spectacular, drift-checked in CI | ADR 0011 |
| — | Not considered | Site is **bilingual es/en** | ADR 0010 |

## 10. Decisions taken at initiation

See `docs/adr/`. ADR 0001 through ADR 0014 exist; each records context, decision,
consequences, and rejected alternatives.

## 11. Definition of Done (binding)

Per ADR 0001, an item is done only when **all four** hold:

1. code with tests,
2. documentation updated,
3. CI green,
4. the requirement linked in the traceability matrix.

Anything less remains in `Revisión`.

## 12. Next actions

Items 1–5 are **done**; they are kept for traceability. `MEMORY.md` holds the live list.

1. ~~Reconcile `docs/00-contexto-proyecto.md` with the deviations in §9.~~ **Done.**
2. ~~Author the SRS (`docs/01-requisitos/srs.md`) with numbered RF/RNF and MoSCoW per version.~~ **Done.**
3. ~~Write user stories and the traceability matrix.~~ **Done.**
4. ~~Complete the design set in `docs/02-diseno/`.~~ **Done.**
5. ~~Run the source spike: probe the WordPress REST API, then `robots.txt` and terms of use.~~ **Partially done, 2026-10-03.** The WordPress REST API responds (368 routes, reads need no auth) and `robots.txt` is permissive with no `Crawl-delay`. The **terms of use were not found**, which is the one question still open. Full record in `docs/fuentes-y-atribucion.md` §9.

### 12.1 Phase 0 closed — 2026-10-04

Phase 0 (brief §16) is complete: the charter, the requirements, the design set, the test
plan, the threat model, the ADRs, and the draft legal texts all exist. Nothing is
implemented, and nothing is deployed.

The next unit of work is **Sprint 01**, `docs/sprints/sprint-01-plan.md` — the repository
that runs. Its seven exit criteria are the gate between "documentation exists" and "the
repository can refuse a bad change", and every later phase depends on them.

**On which gate applies here.** ADR 0001's Definition of Done governs **items on the
board** — it is written for a unit of work with code, tests, a CI run and a matrix row.
Closing a phase is not that: no exit gate for Phase 0 was ever written down, which is why
this section exists. Claiming Phase 0 either met or broke the DoD would be reading a rule
past what it says. What *does* apply, and is not negotiable, is every hard rule in
`AGENTS.md` — and none of them was broken: no third-party material was committed, nothing
was published, the brief was reconciled rather than quietly contradicted, and the
traceability matrix carries every requirement.

The condition that cannot be met here is "CI green", because there is no CI yet. Sprint 01
is the work that creates it.

### 12.2 Open items carried out of Phase 0

These do **not** block Sprint 01. Every one of them blocks a public launch, and none of
them can be closed by writing more documentation.

| # | Item | Owner | Blocks | Status |
|---|---|---|---|---|
| 1 | Define the project contact email | Maintainer | FR-B-14 requires contact information in the scraper's `User-Agent` | **Done 2026-10-04** — `victorloal513@gmail.com`, written into `README.md`, `CONTRIBUTING.md`, and the `docs/legal/` placeholders |
| 2 | Contact Corpocarnaval and record the date and the outcome (brief §11, §20) | Maintainer | C6; publishing anything | **Open.** The letter is drafted and ready to send in `docs/comunicacion-corpocarnaval.md`; sending it and recording the answer is a human act |
| 3 | Resolve the terms-of-use gap, or accept it as a permanent documented risk (`fuentes-y-atribucion.md` §9.5) | Maintainer | Source activation | **Accepted as a documented risk, 2026-10-04.** No terms were found, so none are treated as stated; the mitigation is the written permission request in item 2, not an inference of permission |
| 4 | Obtain professional review of `docs/legal/` and close its `[PENDIENTE]` decisions | — | v3 | **Will not happen — decided 2026-10-04**, see ADR 0016. The texts ship as permanently labelled drafts. The `[PENDIENTE]` deadlines and legal bases stay unresolved by decision, not by oversight |
| 5 | Choose the deployment platform and write **ADR 0015** (network egress cost) | Maintainer | Any deployed version; also decides the storage provider | **Open.** Candidates and a recommendation are already in `docs/02-diseno/despliegue.md` §3; the ADR writes down the egress reasoning and the choice |