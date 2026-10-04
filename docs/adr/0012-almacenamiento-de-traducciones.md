# 0012. Translations stored as columns, not as per-locale rows

- **Status:** Accepted
- **Date:** 2026-10-03
- **Supersedes:** the bullet "Editorial content that the database owns … is stored with a `locale`
  column and translated rows are linked to their source row" in ADR 0010
- **Relates to:** SRS §9 Q1, `modelo-datos.md` §10 Q1, ADR 0010, FR-H-01 … FR-H-07

## Context

ADR 0010 established that the public site is bilingual, `es` as source and `en` as a
secondary locale with fallback to Spanish. It did not settle *how* translated database
content is stored, and the data model settled it three different ways at once:

1. `*_es` / `*_en` columns on `events`, `days`, `venues`, `news_items`, `media_assets`.
2. A generic `content_translations` table (`modelo-datos.md` §4.5) keyed by
   `(content_type, object_id, field, locale)`.
3. Row-per-locale, as ADR 0010 worded it — a Spanish row and an English row linked to each
   other.

`modelo-datos.md` §10 proposed a fourth answer: columns for `events`, generic table for
`news_items` and `media_assets`. That resolves the inconsistency by splitting the codebase
across two mechanisms, which means every query, serializer, admin view and test must handle
both.

Option 3 was never spelled out and is the most dangerous here. **This system gates every
piece of content behind human review.** With one row per locale, moderation state is
duplicated: `status`, `reviewed_by`, `reviewed_at`, `rejection_reason`, `rights_status`,
`origin`. A reviewer who approves the Spanish row leaves the English twin `pending`
forever, and the public query "published" returns a Spanish event with no English
counterpart, or an English row whose rights were never checked. A translation is not an
independent document and must not be able to reach `published` independently.

## Decision

**Editorial content uses `*_es` / `*_en` columns. `content_translations` is deleted, and
row-per-locale is rejected for editorial content.**

- `*_es` is **NOT NULL**. Spanish is the source locale (ADR 0010); a missing Spanish value
  is a data bug, and the database should refuse it.
- `*_en` is **nullable** and falls back to `*_es` when null or empty.
- Fallback is one-directional. There is no `es` ← `en` path: if the source is missing the
  page is wrong, and silently substituting English would hide the defect.
- One small helper resolves the pair. Nothing else in the codebase reads `*_en` directly, so
  the fallback rule lives in exactly one place.

Three mechanisms remain, each for a non-overlapping reason:

| Content | Mechanism | Why not the others |
|---|---|---|
| Editorial (`events`, `days`, `venues`, `news_items`, `media_assets`) | `*_es` / `*_en` columns | — |
| Legal and policy texts (`legal_documents`) | one row per locale | Already modelled. A legal version is a **distinct dated artifact** with its own effective date and immutable text, not a translation of the same artifact (FR-G-02). |
| Site chrome, navigation, UI strings | Django `gettext` `.po` files | Not editorial content. Belongs in version control next to the code, not in the database. |

Contributed `submissions` are **not** translated. A submission is moderated; if it becomes
published content it becomes a `media_assets` row, which carries the columns.

Code enumerations (`origin`, `status`, `rights_status`) are translated with `gettext`, never
stored.

## Consequences

**Positive**
- The published-content read path is a single `SELECT` with no join, no `prefetch_related`,
  and no `GenericForeignKey`. This is the path the public API and the site render from.
- `NOT NULL` on `*_es` makes the source-locale guarantee a database constraint rather than a
  convention.
- Django admin renders a translation as two ordinary form fields. Editors need no concept of
  rows, links, or generic keys.
- `content_translations` disappears, so there is one mechanism to query, test and document.
- Adding a translatable field later is a migration — slow, but obvious and reviewable.

**Negative**
- Tables grow two columns per translatable field, and adding one is a migration.
- Per-field "is this translated?" becomes a null check rather than a flag. Acceptable: with
  two locales, `*_en IS NULL` already answers it.
- A third language would require migrating every editorial table. This is the accepted cost,
  and ADR 0010's fixed `es`/`en` scope is what makes it acceptable.

## Alternatives considered

- **Keep the mixed split** (columns for `events`, generic table for `news_items` and
  `media_assets`), as `modelo-datos.md` §10 suggested. Rejected: it institutionalises two
  mechanisms to avoid a handful of columns, and every consumer has to know which is which.
- **Keep `content_translations`.** Rejected: a `GenericForeignKey` is not enforced by the
  database, so `NOT NULL` on the source locale is impossible; reads need a join and are
  prone to N+1 in list views; and a missing row conflates "not translated" with "this field
  does not exist".
- **Row-per-locale, as ADR 0010 originally worded it.** Rejected: duplicates moderation
  state and lets a translation reach `published` without rights review. This is the specific
  hazard this ADR exists to close.
- **`gettext` for all database content.** Rejected: content is editable at runtime through
  the admin; it cannot live in compiled catalogues.
- **JSONB per locale.** Rejected: untyped, unindexable in a useful way, and moves validation
  out of the database into application code.
