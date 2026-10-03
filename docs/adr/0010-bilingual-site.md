# 0010. Bilingual site (Spanish primary, English secondary)

- **Status:** Accepted
- **Date:** 2026-10-03
- **Relates to:** brief §6 (scoping), §12 (frontend)

## Context

The subject matter is the Carnaval de Negros y Blancos de Pasto, Nariño, Colombia. The
primary audience is Colombian and Spanish-speaking. However, the project is a portfolio
piece whose stated purpose is to demonstrate a complete software engineering process
(brief §1), and a reader outside the Spanish-speaking world cannot review that work.

The brief did not consider languages; it listed React + TypeScript as tentative.

All repository *documentation* is written in English (see `AGENTS.md`). This ADR concerns
only the user-facing interface, which is a separate concern from internal docs.

## Decision

The public site ships in **two locales**:

- **es** — the source locale. All translation keys are authored in Spanish. `Accept-Language`
  negotiation and the `<html lang>` attribute default to `es`.
- **en** — a complete English translation, not a partial one. Every user-facing string
  appears in both locales at release; a locale missing keys is a release blocker.

Rules:
- A locale switcher is present in the header on every page, persists the choice in a
  cookie, and does not require an account.
- URLs are locale-prefixed (`/es/...`, `/en/...`) so content is linkable and cacheable per
  locale. The unprefixed root redirects to the negotiated locale.
- Slugs are stored per locale in the database, so a translated page has a translated URL.
- Editorial content that the database owns (event names, news summaries, image
  descriptions and citations) is stored with a `locale` column and translated rows are
  linked to their source row. Admin-entered content may be monolingual and falls back to
  the source locale rather than rendering an empty page.
- The admin panel is **Spanish only** — it is single-operator tooling, and translating it
  would add surface area with no audience.
- No machine translation at runtime. English strings are written by hand so the
  terminology stays consistent with the English documentation.
- Citations, source URLs, and legal documents are never translated: they are reproduced
  verbatim as published, with a Spanish translation alongside when one exists.

## Consequences

**Positive**
- The portfolio piece is reviewable by non-Spanish speakers, which is most of the
  international software audience.
- Locale-prefixed URLs are correct for caching and for search engines, avoiding mixed
  content in a single index.
- Keeping the admin monolingual avoids translating forms, moderation states, and error
  messages nobody else will see.

**Negative**
- Every user-facing string is written twice, and the two must be kept in sync. Mitigation:
  a test fails the build if a key exists in `es` but not in `en`.
- Translated database content roughly doubles the editorial writing workload for a single
  part-time maintainer. Mitigation: event and news content may ship monolingual with
  fallback; only the navigation, chrome, and about pages must be complete in both.
- The routing layer is more complex than a single-locale site.

## Alternatives considered

- **Spanish only.** Simplest and best for the primary audience. Rejected because it makes
  the engineering portfolio unreadable to most reviewers.
- **English only.** Rejected: it would misrepresent the subject matter to the audience
  the project actually serves, and it conflicts with `AGENTS.md`.
- **Machine-translated English.** Rejected: inconsistent terminology, and it would
  misrender proper nouns, official titles, and citations.