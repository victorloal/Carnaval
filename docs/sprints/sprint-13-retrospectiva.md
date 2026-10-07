# Sprint 13 retrospective — the v2 backend (11–13: editorial, media, settings, search)

- **Date:** 2026-10-06
- **Sprint:** 11–13, delivered together as the v2 backend
- **Method:** Start / Stop / Continue, plus what actually happened versus what was planned.

## What was planned versus what happened

Planned: the `sources` citation registry, `news_items`, `media_assets` with its rights gates,
typed `site_settings`, per-locale slugs, verbatim citations with a translation, and full-text
search over published events and news.

What happened: **the v2 backend landed and CI is green on its commit.** The suite is at **111
tests**; `ruff`, `mypy` (126 files), `makemigrations --check`, `check --deploy`, the secret
scan and the generated-schema check are clean. The matrix moved **FR-E-01/02/04/05/08/09/10/11/12,
FR-I-01/02, LEG-02/04/09 to Done.**

Delivered: a `carnaval.editorial` app — `Source`, `NewsItem`, `MediaAsset`, `SiteSetting` —
with the media rights gate as **database `CHECK` constraints plus a `publish_blockers()` hook
the moderation service consults**, the settings' secret refusal, before/after audit, and
read-only published-only API endpoints for news and media plus `/api/search/`.

Carried, with reasons: the **news transform** (news is entered by hand as `pending` for now),
the **gallery UI** (frontend), **duplicate refusal** by content hash, **per-locale slugs**,
**verbatim citations with a translation**, the **PostgreSQL full-text** verification (the code
branches on the DB vendor, so the Postgres path is unrun), and the **quarantine-key** guarantee
(v3).

## Start

- **The rights gate is data, not a form.** `rights_status = unknown`, a missing author, source
  or citation, an un-stripped EXIF tag or a minor without guardian consent each block
  publication **at the database**, and `publish_blockers()` gives the reviewer the reason. A
  bulk action or a future pipeline cannot bypass it.
- **Secrets are refused where they would be stored.** `SiteSetting.clean` rejects a key that
  names a secret, so `site_settings` cannot become an environment-variable graveyard.
- **Search degrades honestly.** On PostgreSQL it is the documented `SearchVector`/`SearchRank`;
  on the SQLite development database it is `icontains`. The visibility rule — `published` only
  — is identical on both.
- **The admin mixin is shared.** `ModeratedAdmin` lives in `moderation.admin` and is imported by
  `programme.admin` and `editorial.admin`, so the verbs have exactly one implementation.

## Stop

- **I forgot the UUID primary key on `NewsItem` and `MediaAsset`.** The design gives every
  table a UUID PK; these inherited an auto-increment one, and a test caught it only because it
  compared a string id to an int. Fixed by adding the field and regenerating the migration.
- **A test built data that the gate forbids.** A factory created a `published` `MediaAsset`
  with default `unknown` rights, which the `CHECK` refuses — the test was wrong, not the code.
  **Test data must be as lawful as the gate demands.**
- **A 2-tuple on the base class blocked wider overrides.** `ModeratedAdmin.list_filter` was
  inferred as `tuple[str, str]`, so a subclass with six filters failed type-checking. The base
  no longer declares it.
- **Two `Could`/v3-adjacent items were left Open rather than approximated** (duplicate refusal,
  per-locale slugs) and FR-I-03 is recorded as a Postgres branch that has not run.

## Continue

- **Move only what the tests cover.** FR-E-03, FR-E-06/07, FR-I-03, FR-H-07/09 and the
  quarantine guarantee stayed Open.
- **Keep the gate at the database.** A `CHECK` is the difference between a rule and a hope.
- **Name every carried item** in the plans and here.

## What the sprint proved about the project

The highest-risk table in the schema — an image — is now publishable only when it is lawfully
publishable, and the rule is enforced below the application. The rest of v2 is the same shape:
a registry, a news record with no article body, typed settings that refuse secrets, and search
that can only return what is already public.

## Concrete changes adopted

1. `NewsItem` and `MediaAsset` carry a UUID primary key like every other table.
2. Test factories produce data that satisfies the constraints; the gate is not weakened for
   tests.
3. A base admin does not narrow an attribute its subclasses will widen.
