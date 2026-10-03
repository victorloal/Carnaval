# Sources and attribution

> **NOT a legal document.** This is an **operational register**: which sources the project
> uses, what their terms say, how a citation is written, and how the collector behaves
> towards them. It contains no legal conclusions and it is not a legal notice.
>
> It does, however, feed the legal texts in `docs/legal/`, and **those texts are
> machine-drafted and unreviewed** — see `docs/legal/README.md`. Nothing here overrides
> them, and nothing here is a substitute for the outstanding professional review
> (brief §11, §20).

- **Status:** Working register, Phase 0
- **Date:** 2026-10-03
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

**ToS status: nothing in this register has been reviewed yet.** Brief §20 still lists
*“revisar robots.txt y términos de uso del sitio”* as an open item. Until a row reads
`reviewed`, it may not be used to justify publishing anything.

| Name | `kind` | URL | Terms of use | Licence constraint |
|---|---|---|---|---|
| **carnavaldepasto.org** | `official_site` | `https://carnavaldepasto.org` | **unknown — must be reviewed** (brief §20). Also: not contacted; brief §20 *“escribir a Corpocarnaval”* still open | Facts only, cited. **Unofficial / not-affiliated disclaimer mandatory** (`is_official = true`). Page prose is never copied — descriptions are rewritten in the maintainer's own words. Its name and marks are nominative references only |
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
   behaviour changes. **Not yet done** (brief §20) — this is the first item of the source
   spike.
2. **Send an identifiable `User-Agent` with contact information.** It is a
   `scrape_sources.user_agent` field precisely so it is configured, not hard-coded. A
   browser-spoofing default is not acceptable.
3. **Rate-limit.** `rate_limit_seconds` sets a minimum delay between requests per source.
   Requests are batched politely, and the collector stops rather than hammering.
4. **Prefer the official machine interface.** If `carnavaldepasto.org/wp-json/wp/v2/pages`
   and `.../wp-json/wp/v2/posts` respond, use them (`source_type = wp_api`) rather than
   scraping HTML — the structure is more stable and the load is smaller. **Still
   unverified** (brief §5); probing it is step 4 of the source spike. Fallback chain:
   `wp_api` → `html` → `pdf`, in that preference order.
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
  a **known legal gap**, which is the honest state of the project at Phase 0.