# Sprint 21 retrospective — per-locale slugs

- **Date:** 2026-10-07
- **Sprint:** 21 — Per-locale slugs
- **Method:** Start / Stop / Continue.
- **Note:** fourth of the four close-out sprints (18–21); see also
  `sprint-18-21-retrospectiva.md`.

## What was planned versus what happened

Planned: content has a **slug per locale** (FR-H-07), so a translated page has a translated URL
and the source slug is the fallback rather than a shared identifier.

What happened: **all four items landed and CI is green on `38753f0`.** The suite reached **143
backend tests.** The matrix moved **FR-H-07 to Done.**

Delivered: `slug_es` and `slug_en` on `Edition` and `Day`, matching what `modelo-datos.md`
§3.1/§3.2 had specified; a migration that **renames** `slug` to `slug_es` and adds `slug_en`; a
`slug_for(locale)` helper with one-directional fallback; partial unique constraints so an English
slug cannot collide when set; both slugs exposed on the public API; and the admin searching both.

## Start

- **The design already said this.** `modelo-datos.md` specified `slug_es` / `slug_en`; the code
  carried a single `slug`. The sprint closed a drift rather than inventing a feature.
- **Migrate, do not drop.** The migration is a `RenameField`: existing rows keep their slug as
  the Spanish one, and no data is lost. Remove-and-add would have been simpler and destructive.
- **Fallback is one-directional.** `slug_for("en")` returns `slug_en` when it exists and
  `slug_es` otherwise; there is no `es ← en` path, for the same reason ADR 0012 gives for
  content — if the source is missing the record is wrong, and substituting English hides it.
- **Unique only when set.** The English constraints are partial, so two rows with an empty
  English slug are not "duplicates".

## Stop

- **The rename needed a guess Django had to confirm.** `makemigrations` cannot know a rename
  from a remove-and-add; the question was answered "yes" deliberately, and the generated
  migration was read to confirm it renamed rather than recreated. An unanswered prompt would
  have dropped the column.
- **The API field names changed.** `slug` became `slug_es` / `slug_en` on the serializers, so
  the OpenAPI contract changed and both were regenerated and committed. There is no external
  consumer, but the change is a contract change and was treated as one.
- **No public detail page uses the slugs yet.** They are stored now so the routes are a
  rendering concern later; building routes without pages would have been speculative.

## Continue

- **Keep the fallback rule in one place.** `slug_for` is the only reader of `slug_en`, exactly as
  ADR 0012 wants for translatable fields.
- **Change the contract in the same commit as the schema.**

## What the sprint proved about the project

A bilingual requirement that had been satisfied for content could finally be satisfied for
**URLs**: an English page can have an English address, with the Spanish one as the honest
fallback. The sprint also showed the value of the design document — the code was the thing that
had drifted, not the model.

## Concrete changes adopted

1. A field rename is reviewed in the generated migration before it is committed.
2. A serializer field rename regenerates and commits `openapi.yaml`.
3. Slugs are stored before they are routed; no speculative detail pages.
