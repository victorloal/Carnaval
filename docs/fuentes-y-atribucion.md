# Sources and attribution

> **NOT a legal document.** This is an **operational register**: which sources the project
> uses, what their terms say, how a citation is written, and how the collector behaves
> towards them. It contains no legal conclusions and it is not a legal notice.
>
> It does, however, feed the legal texts in `docs/legal/`, and **those texts are
> machine-drafted and unreviewed** — see `docs/legal/README.md`. Nothing here overrides
> them. The professional review that brief §11 and §20 kept open **is no longer outstanding:
> it was declined on 2026-10-04** (ADR 0016), and the DRAFT notice on each legal page is what
> stands in its place. Nothing in this register substitutes for it either.

- **Status:** Working register. Phase 0 closed 2026-10-04 — §9 is the source spike record
- **Date:** 2026-10-03 (register), 2026-10-03 (§9 spike)
- **Relates to:** brief §5 (research findings), §6 decision 5, §11 (legal and ethical
  considerations), §14 (risks), §20 (open items); `docs/00-acta-proyecto.md` §3, §4.2,
  §6 (C3, C4); ADR 0002, ADR 0004, ADR 0006, ADR 0007; `docs/02-diseno/modelo-datos.md`
  §3.5, §3.6, §4.1–§4.3

## 1. The attribution policy

**Every published item carries author, source, licence, and citation text. An item whose
rights are unknown is not published.** This is the operational rule behind ADR 0004 and
brief §11, and it is enforced by the schema rather than by good intentions:

| Content type | Mandatory for publication | Enforced by |
|---|---|---|
| `media_assets` (historical image) | `author`, `source_ref`, `license`, `citation_text`, `exif_stripped = true`, `rights_status != unknown` | `clean()` and serializer validation, repeated in the admin form (modelo-datos §4.2) |
| `news_items` | `source`, `headline`, `url`, `outlet`, `published_on`, own-words `summary_es` | Schema + review |
| `events` | `source` in `sources`, own-words description, provenance via `origin` + `ingestion_run` | Schema + review |

Two consequences that are easy to forget:

- **`rights_status = unknown` blocks publication, permanently, not pending research.** An
  old photograph is not free of rights; age is not a licence.
- **The MIT licence covers code only.** It does not cover any content on this site, and a
  visitor who reads `LICENSE` must not infer that it does (ADR 0004).

## 2. `sources` versus `scrape_sources`

Two tables, two different jobs. Conflating them produces both a broken citation trail and a
broken circuit breaker.

| | `sources` | `scrape_sources` |
|---|---|---|
| Purpose | **Citation registry** — who to credit for a piece of content | **Fetch configuration** — where and how to collect |
| One row per | An outlet, archive, or document that is *credited* | A URL the pipeline *requests* |
| Key fields | `name`, `kind`, `url`, `is_official`, `notes` | `url`, `source_type` (`wp_api`/`html`/`pdf`), `selector_*`, `is_active`, `rate_limit_seconds`, `schedule_cron`, `consecutive_failures`, `last_error`, `user_agent` |
| Referenced by | `news_items.source` | `raw_documents.scrape_source`, `ingestion_runs.scrape_source` |
| Who edits it | Maintainer | Maintainer, in Django admin |
| If it fails | Nothing — it is a reference | Circuit breaker counts `consecutive_failures` and auto-disables the source |

`is_official = true` exists on exactly one row: the official site. It is what triggers the
unofficial, not-affiliated disclaimer site-wide. It confers **no** rights and **no**
endorsement.

A source may exist in `sources` with its terms unreviewed. Its `notes` say so, and no
content derived from it may be published. That is the state every row below is in right now.

## 3. Seed register

**ToS status: only the `official_site` row has moved, and only halfway.** Its `robots.txt`
was read on 2026-10-03 (§9); its **terms of use were not found**, so the row is still not
`reviewed`. Brief §20 keeps *“revisar robots.txt y términos de uso del sitio”* open for that
reason. Until a row reads `reviewed`, it may not be used to justify publishing anything.

| Name | `kind` | URL | Terms of use | Licence constraint |
|---|---|---|---|---|
| **carnavaldepasto.org** | `official_site` | `https://carnavaldepasto.org` | **`robots.txt` reviewed 2026-10-03** (§9): allows all, disallows `/wp-admin/`, no `Crawl-delay`. **Terms of use still not found** — no such document among all 19 pages or all 42 posts, and the site's only legal link is a privacy policy on a second host. Review not closed; brief §20 *“revisar … términos de uso”* remains open, as does *“escribir a Corpocarnaval”* | Facts only, cited. **Unofficial / not-affiliated disclaimer mandatory** (`is_official = true`). Page prose is never copied — descriptions are rewritten in the maintainer's own words. Its name and marks are nominative references only |
| **Official programme PDF** | `pdf` | Published by the official site; canonical URL `[PENDIENTE: registrar la URL canónica y la edición]` | **unknown — must be reviewed** | **The PDF is never redistributed and never committed to git** (`*.pdf` in `.gitignore`, ADR 0004). Only extracted facts, cited to the document and edition. Stored in `raw_documents` + object storage, never in the repository |
| **News outlets** | `news_outlet` | `[PENDIENTE: one row per outlet actually reviewed; the example name in modelo-datos §4.3 is illustrative, not a verified source]` | **unknown — must be reviewed** | Headline (verbatim fine) + canonical URL + outlet + `published_on` + **short original summary**. Never the article body, never its images (brief §11) |
| **Community-submitted video** | `other` | YouTube / Vimeo, embedded (ADR 0007) | Governed by the **platform's** terms, not ours | We store provider + normalised video id and render the embed. We host no video file and hold no licence over it. Removal means contacting the provider and dropping our reference |
| **Personal or family archives** | `archive` | `[PENDIENTE: named contributors appear here as they do]` | Contributor's declaration + guardian authorisation where a minor is the focal subject | `rights_status = permission_on_file` only when the authorisation is **on file**. `declared_author` alone is a claim, not a right |
| **Public-domain / open-licence images** | `archive` | `[PENDIENTE: per asset]` | Per-asset | `rights_status = public_domain` or `licensed`, with the licence string and `citation_text` recorded verbatim |

Rule for adding a row: a `sources` row may be added at any time with
`notes = "terms of use not reviewed"`; a `scrape_sources` row **must stay `is_active = false`
until its `robots.txt` and terms have been read**. Nothing from an unreviewed source may be
published, and an item whose `rights_status` is `unknown` is blocked regardless of the
source row.

## 4. Canonical day names — January milestones

From brief §5, for the January carnival:

| Date | Canonical name | `label_es` | `label_en` |
|---|---|---|---|
| 2 January | Carnavalito | Carnavalito | Carnavalito |
| 3 January | Choreographic collectives | Colectivos coreográficos | Choreographic collectives |
| 4 January | Desfile Familia Castañeda | Desfile Familia Castañeda | Castañeda Family Parade |
| 5 January | **Day of Blacks** | Día de Negros | Day of Blacks |
| 6 January | **Day of Whites / Gran Parade** | Día de Blancos / Desfile Magno | Day of Whites / Grand Parade |

These are the canonical names, but **days are rows, not an enum** (modelo-datos §3.2). The
programme changes **once a year** (brief §5), and the next January edition is published near
the end of December. Never hard-code a year into a day name, and never assume one edition's
days apply to the next. Pipeline-extracted day labels are proposed as `pending` rows, never
created silently.

## 5. Scraping etiquette

The collector is a guest on someone else's server. The rules are not optional.

1. **Respect `robots.txt`.** Read it before any request, re-read it when the site's
   behaviour changes. **Done for the official site on 2026-10-03** (§9): it allows all
   agents, disallows `/wp-admin/`, and sets no `Crawl-delay`. Brief §20's item is only half
   closed — the *terms of use* half is still open (§9, §3). Re-read it whenever the site's
   behaviour changes; a `robots.txt` is a live signal, not a one-time finding.
2. **Send an identifiable `User-Agent` with contact information.** It is a
   `scrape_sources.user_agent` field precisely so it is configured, not hard-coded. A
   browser-spoofing default is not acceptable.
3. **Rate-limit.** `rate_limit_seconds` sets a minimum delay between requests per source.
   Requests are batched politely, and the collector stops rather than hammering.
4. **Prefer the official machine interface.** `carnavaldepasto.org/wp-json/wp/v2/pages` and
   `.../wp-json/wp/v2/posts` **respond — verified 2026-10-03** (§9): HTTP 200, 368 routes,
   no authentication required for reads, pagination and `_fields` working. Use them
   (`source_type = wp_api`) rather than scraping HTML — the structure is more stable and the
   load is smaller. This closes brief §5's "sin verificar" and satisfies **FR-B-15**'s
   verification method. Fallback chain: `wp_api` → `html` → `pdf`, in that preference order.
   Note that the HTML fallback is *unattractive* here: the site is built with Elementor and
   JetEngine, so article body content sits in post meta as structured JSON rather than in
   readable HTML (§9).
5. **Be idempotent and cheap.** `raw_documents.content_hash` is unique, so an unchanged
   payload is recorded as a no-op and never re-transformed (ADR 0002). Re-running costs one
   conditional request, not a re-crawl.
6. **Fail without damage.** Retries with exponential backoff; after N consecutive failures a
   source is auto-disabled and the admin shows `last_error`. Published data is never deleted
   or degraded by a failure, and the database remains the source of truth.
7. **Never test against the live site.** Tests replay local fixtures only (`AGENTS.md`). The
   live site is for ingestion, never for CI — source markup changes yearly and that is the
   top documented risk in the brief (§14).
8. **Contact the owner.** Rate limits, an identifiable `User-Agent`, and citation are the
   minimum; writing to Corpocarnaval first is still an open item (brief §20,
   `docs/00-acta-proyecto.md` §6 C6).

## 6. Citation formats

Templates. Placeholders are filled from the item's own columns — never typed by hand into
a rendered page, always rendered from `citation_text`.

**News item** (`news_items`):

```
"<headline>", <outlet>, <published_on>.
<url>
Original summary in the maintainer's own words; the full article is not reproduced.
```

**Historical image** (`media_assets`) — `citation_text` is stored pre-formatted:

```
"<title>", <year_approx, or "year unknown">.
Photograph: <author>. Source: <source_ref> (<source name>, <url>).
Licence: <license>. Rights status: <rights_status>.
```

**Programme event** (`events`):

```
<event title> — <day label_es> (<date>), per <source name> (<source url>).
Accessed <date>. Editorial wording is the maintainer's own.
```

**Community submission** (`submissions`, after approval):

```
Submitted by <declared_author>, <declared_year>, <declared_place>.
Licence: <license> or "all rights reserved by the contributor".
Displayed with permission; revocable on request.
```

House rules for all of them: attribution travels with the item — it is not a page footer; a
citation without a resolvable URL is not a citation; and no template may be edited to omit
the licence line or the source.

## 7. Repository hygiene

**Raw third-party material is never committed to this repository** (ADR 0004, brief §11).

| Rule | Implementation |
|---|---|
| Raw fetched payloads stay out of git | `data/raw/` in `.gitignore` |
| No PDFs of third-party schedules | `*.pdf` in `.gitignore` |
| Visitor uploads stay out of git | `data/uploads/` in `.gitignore` |
| Raw payloads go to object storage, not the repo | `raw_documents.storage_key`; quarantine vs public tiers are separate buckets on separate domains (ADR 0006) |
| Test fixtures must be sanitised or synthetic | Never a real article, a real photograph of a person, or a real PDF. Replay them locally |
| Before any scraping work | Confirm `data/raw/` and `*.pdf` are still in `.gitignore` (`AGENTS.md`) |

`lib/` is deliberately **not** ignored — it is commonly a real source package. Do not
"fix" that by ignoring it.

If third-party material is ever found committed, remove it in a follow-up commit, record
what happened, and note that published repository history is hard to erase — which is why
prevention is the control.

## 8. Maintenance

- The register is updated **before** a source is used, never after a problem: add the
  `sources` row, review `robots.txt` and the terms, record the finding in `notes`, and only
  then activate any `scrape_sources` row.
- Any source whose terms forbid or restrict collection is marked and its `scrape_sources`
  row stays `is_active = false`, permanently.
- Terms-of-use findings should end the "unknown" state. Until then, this register documents
  a **known legal gap**. That gap survives the close of Phase 0: it is not a documentation
  debt that more writing would clear, it is an unanswered question about a third party's
  site that only Corpocarnaval can answer (brief §20). Carried as
  `docs/00-acta-proyecto.md` §12.2 item 3.
- **Resolved as a risk decision, 2026-10-04.** No terms were found, so none are treated as
  stated: the project proceeds on the basis that no published restriction was found, **not**
  on the basis that permission was found. The mitigation is the written request in
  `docs/comunicacion-corpocarnaval.md`. If terms are ever published, or if Corpocarnaval
  objects, this decision is re-opened — see §9.6.

## 9. Source spike record — 2026-10-03

**What this section is:** a record of a one-off, read-only observation, which closed two
questions that had been open since the brief — does the WordPress REST API respond (brief
§5, "sin verificar"), and what does `robots.txt` allow (brief §20). It is **not** a review of
the source's terms and it makes **no** source publishable. Nothing here changes §1's rule
that unknown rights block publication.

### 9.1 How it was run

| | |
|---|---|
| Method | `GET` only, sequential, no authentication, no `POST`, ~2 s between requests |
| Requests | **13** in total, against 2 hosts (`www.carnavaldepasto.org`, `carnavaldepasto.org`) |
| `User-Agent` | `CarnavalDocsSpike/0.1 (+https://github.com/victorloal/Carnaval; documentation spike, no scraping)` |
| Contact | The repository URL — **this is what the spike actually sent**, because no email address existed at the time. §9.5 below confirms the site exposes no public contact address either. **Superseded 2026-10-04:** the project contact is now `victorloal513@gmail.com` and every pipeline request must carry it (FR-B-14) |
| Where the payloads went | Temporary storage **outside this repository**. Nothing was committed |
| Preflight | `data/raw/`, `data/uploads/` and `*.pdf` confirmed in `.gitignore`; no `data/` directory existed; `git status` clean before and after |

### 9.2 Results against the questions that were open

| Question | Finding | Status |
|---|---|---|
| Does the WP REST API respond? | **Yes.** `/wp-json/` → HTTP 200, 612,602 bytes, **368 routes**, namespace `wp/v2` present. Reads need no auth; the `authentication` block only advertises `application-passwords` for writes | **Closed — available** (FR-B-15) |
| What does `robots.txt` allow? | `User-agent: *` → `Disallow: /wp-admin/`, `Allow: /wp-admin/admin-ajax.php`, `Sitemap: https://carnavaldepasto.org/wp-sitemap.xml`. **No `Crawl-delay`** | **Closed — permissive** |
| Do `posts`/`pages`/`terms` behave as expected? | Yes: `X-WP-Total`, the `Link` paging header and `_fields` field selection all worked | **Closed** |
| What do the site's terms of use say? | **Not found.** See §9.5 | **Still open** (brief §20) |
| What WordPress version is it? | **7.1.2** | Recorded as an observation. **No conflict with the brief:** §5 names no version — it only says *“construida con WordPress y Elementor”*, which the spike **confirms** (Elementor, plus JetEngine) |

### 9.3 What the source's content model actually looks like

- **17 registered types**, of which only **two are the site's own**:
  `propuesta` and `artesanos`. Everything else is WordPress core or plugin plumbing
  (`elementor_*`, `jet-engine`, `e-floating-buttons`). **There is no custom post type for
  events, news, or the programme** — it lives in ordinary `posts`, grouped by categories
  (§9.4). The brief describes the site's *output* ("publica la programación por día"), not
  its storage, so this contradicts no documented assumption; it simply rules out reading a
  dedicated endpoint that does not exist.
- The site is built with **Elementor + JetEngine** (also present: All-in-One WP Migration,
  Forminator). Consequence for the fallback chain: an HTML fallback would have to parse
  Elementor's structured output rather than readable prose, which is exactly why `wp_api`
  must stay first (§5, item 4).
- **42 posts, 19 pages, 21 categories, 5 tags.** Verified by enumerating each collection in
  full rather than sampling.

**Currency — the finding that matters most.** The 42 posts fall into four clusters by date:

| Window | Posts | What they are |
|---|---|---|
| 2019-12-25 → 2020-01-12 | **33** | The day-by-day programme: `carnavalito`, `dia-de-blancos-desfile-magno`, `dia-de-negritos-una-pintica-por-favor`, `llegada-de-la-familia-castaneda`, the `rumba-carnavalera` series. **The 2020 edition** |
| 2024-10-21, 2024-10-23 | 7 | Slugs are day or phase names (`2-de-enero` … `6-de-enero`, `pre-carnaval`, `festivales`) but the dates are late October — **slug and date disagree**, so a slug must never be read as an event date |
| 2024-11-11 | 1 | `politica-de-proteccion-de-datos` |
| 2026-09-07 | 1 | `convocatoria-…-2027`, announcing the 2027 edition |

Posting dates are **absent entirely for 2021, 2022, 2023 and 2025**. The only post dated
after 2024 is the single `convocatoria` of 2026-09-07, which announces the 2027 edition —
so its date says nothing about how much programme content exists for the intervening years.

So a pipeline pointed at this endpoint today would return a **plausible-looking, mostly
six-year-old programme**. That is the shape this project's top documented risk takes: not a
zero-record failure, but a **silent success returning stale data**. `ingestion_runs` and the
reviewer must therefore compare extracted dates against the target edition, and "the fetch
returned 42 records" must never be accepted as evidence that the fetch was *correct*.

### 9.4 Taxonomy: where days actually live — and one trap

Days are **categories**, under a root category `DIAS` (id 8):

| Group | Categories (count as reported) |
|---|---|
| Root | `SIN CATEGORIA` (4), **`DIAS` (7)**, **`6 de enero` (2)**, `EVENTOS` (1), `Participa` (1) |
| Children of `DIAS` | `24 de diciembre` (0), `27 de diciembre` (0), `28 de diciembre` (8), `29 de diciembre` (2), `30 de diciembre` (1), `31 de diciembre` (2), `2 de enero` (5), `3 de enero` (3), `4 de enero` (3), `5 de enero` (2), `7 de enero` (1), `12 de enero` (1), `Pre-carnaval` (12), `Festivales` (2) |
| Children of `EVENTOS` | `CONCIERTO` (1), `DESFILE` (0) |

Four consequences:

1. **The trap: `6 de enero` is a root category, not a child of `DIAS`** — while `5 de enero`
   and `7 de enero` are children. Any ingestion that collects days as *"children of `DIAS`"*
   **silently drops the Day of Whites**, the single most important day of the carnival. This
   is precisely the kind of omission that looks like a working pipeline. Collect the day
   categories by *name pattern* and assert the expected set is complete instead.
2. **Day names carry no year** — `2 de enero`, not `2 de enero de 2020`. They are reused
   every edition. This **refines** `modelo-datos.md` §10 Q2: the statement "day names differ
   by year" is not what the source does. The *labels* are stable; the *calendar positions*
   move. Mapping a day category to an edition must therefore derive the year from the
   dated content, never from the category name.
3. **`DIAS` is not purely days.** `Pre-carnaval` and `Festivales` are children of it but are
   not days. Filtering on the hierarchy alone will misclassify them.
4. **Term `count` values are not trustworthy and must not be used to validate a fetch.**
   `DIAS` reports 7 while its children sum to 42; several categories report 0. Use
   `X-WP-Total` on the collection endpoint, not term counts.

Tags, for the record: `ENCUENTRO CULTURAL` (15), `CONCIERTO` (11), `DESFILE` (6), `CARRERA`
(1), `conciento` (0) — the last is a **typo duplicate of `CONCIERTO`**, a small data-quality
signal about how this taxonomy is maintained.

### 9.5 Editions and the legal surface

**Editions are page slugs containing a year**, not categories: `de-negros-y-blancos-2023`,
`-2024`, `-2025`, `carnaval-de-negros-y-blancos-de-pasto-2025`, and the current homepage
`carnaval-de-negros-y-blancos-de-pasto-2027`. **There is no 2026 page.** An ingestion that
infers the current edition must not assume the year sequence is contiguous.

The pages list also contains residue (`borrador`, `pronto`, `facebook`,
`que-hacer-filter`) — another reminder that scraped records land as `pending` and are
reviewed, never trusted.

**Legal surface — what was and was not found:**

- The homepage's **only** legal link is a privacy policy,
  `politica-de-proteccion-de-datos` (post id 6965, 2024-11-11), and it points at a
  **different host**: `negrosyblancos.carnavaldepasto.org`, not `carnavaldepasto.org`. Any
  future fetch rule written for one host does not automatically apply to the other.
- A search of the REST index for `terminos` returned only **three Elementor footer
  templates**; `privacidad` and `condiciones` returned **zero**.
- Enumerating **all 19 pages and all 42 posts** found no terms-of-use document, no
  terms-and-conditions document, and no cookie policy.

This is **not proof that no terms exist** — the search index does not cover everything, a
footer template may hold the text, and the second host was not enumerated. It is enough to
record that brief §20's *"revisar robots.txt y términos de uso"* is **half closed**: the
`robots.txt` half is done, the terms half is not. The professional review that
`docs/legal/terminos-y-condiciones.md` required was then **declined** (ADR 0016), so no
reviewed text was ever going to clear this. The two gaps are independent, and neither closes
the other.

**What the maintainer decided on 2026-10-04.** The second half is closed as an **accepted
risk**, not as an answer. The reasoning is recorded so it can be argued with later:

- **No published terms were found, so none are treated as stated.** The project does not
  behave as though permission had been granted; it behaves as though no restriction had been
  published — the reading least favourable to itself.
- **This is not a licence to copy content.** Rights are a separate question, governed by §1
  and by `rights_status` per item. An image or article with `rights_status = unknown` is
  still never published, whatever this decision says.
- **The mitigation is a request, not an inference.** `docs/comunicacion-corpocarnaval.md`
  asks for permission in writing and states exactly what will be collected. If the answer is
  no, or restrictive, the source is disabled and anything derived from it is withdrawn.
  Deciding to proceed does not pre-empt that answer.
- **The residual risk is legal and reputational, accepted knowingly** by a maintainer with no
  legal advice available to him (ADR 0016).

What would re-open this: terms being published on the site, a `robots.txt` change, a
complaint, or any answer from Corpocarnaval.

Also observed on the homepage: links to `corpocarnaval.com` (which is why the
not-affiliated disclaimer is mandatory, FR-A-09), three `wa.me` WhatsApp links, and the
usual social networks. **No public email address was found**, which is the gap noted in
§9.1.

### 9.6 Still unverified

- **Terms of use.** Not found (§9.5); not a conclusion that none exist. **Risk accepted
  2026-10-04** — see the decision recorded in §9.5. Still open as a *fact*; closed as a
  *decision*.
- **`propuesta` and `artesanos`** endpoints were registered but not read.
- **`wp-sitemap.xml`** was advertised but not fetched.
- **Rate limits.** No `Crawl-delay` and no observed throttling across 13 requests, but a
  single polite burst proves nothing about the site's tolerance. `rate_limit_seconds` must
  be configured conservatively and lowered only deliberately.
- **The `www.` host versus the bare domain.** The API declares its canonical `url` as the
  bare `carnavaldepasto.org`; the probe used both. Pin **one** canonical host per
  `scrape_sources` row so `content_hash` idempotency is not defeated by host variance.
- **Nothing was ingested.** No `raw_documents`, no fixtures, no `scrape_sources` rows —
  `backend/` is still empty, so there is nothing yet to write records into. Captured
  payloads were discarded with the temporary directory.

### 9.7 The permission request — sent 2026-10-04, unanswered

The mitigation for §9.5 was put into action: the letter in
`docs/comunicacion-corpocarnaval.md` was **sent by email on 2026-10-04**. It states what
will be collected, what will never be collected, and how the collector will behave, and asks
for written permission.

**No reply has arrived. Nothing about the project's position changed as a result.**

This is worth stating precisely, because a sent request is easy to mistake for a cleared
one:

- The §9.5 decision stands exactly as recorded: no terms were found, so none are treated as
  stated, and the risk is accepted, unresolved and reversible.
- **Silence is not permission.** Per `docs/comunicacion-corpocarnaval.md` §7, the contingency
  if the answer is no was decided in advance: `scrape_sources.is_active` goes to `false`,
  published items derived from the source return to `pending`, and the change is recorded in
  `audit_logs` with a reason.
- **The recipient address was not recorded** when the message went out. Add it to
  `docs/comunicacion-corpocarnaval.md` §6, so a bounce or a misdirected reply is traceable.
- **Do not cite this file as permission.** If asked "did you ask?", the true answer is yes;
  if asked "did they agree?", the answer is that nobody has answered yet.