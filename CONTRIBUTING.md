# Contributing

Thanks for your interest. This is a **solo, part-time portfolio project** with one
maintainer, so expectations are low and response times may be slow.

## What is useful

- **Factual corrections** — especially to the parade programme, history, or sources.
  These are the most valuable contributions and the easiest to accept.
- **Source leads** — a more stable source than HTML scraping, or a programme PDF that
  parses correctly.
- **Accessibility and internationalisation (Spanish/English) fixes.**
- **Security findings** — please report them privately first, see below.
- **Translation corrections** in `docs/`, which are written in English about a
  Spanish-language subject.

## What is not useful

- Feature proposals. The scope is fixed per version in `docs/01-requisitos/srs.md`; a new
  feature needs a requirement and a version slot first.
- Refactors of code that does not exist yet.
- Dependencies. The project runs at **zero cost** on free tiers; a paid or heavyweight
  dependency has to be rejected.
- Contributions that would require committing third-party material. PDFs, photographs, and
  article text are **never** accepted into this repository.

## Before opening a pull request

1. Read `AGENTS.md`. It contains the binding project rules.
2. Read `MEMORY.md` for current state and known deviations from the brief.
3. Check `docs/01-requisitos/matriz-trazabilidad.md` — if your change affects a
   requirement, the matrix must be updated in the same pull request.
4. If your change implements a decision, check whether an ADR needs writing. Significant
   decisions go in `docs/adr/`, not in a commit message.

## Commit and branch conventions

- Branch names: `docs/…`, `feat/…`, `fix/…`. Short-lived.
- Commit messages: [Conventional Commits](https://www.conventionalcommits.org/) —
  `feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`, `perf:`.
- `main` is kept stable and protected.

## Definition of Done

An item is **done** only when all four hold (ADR 0001):

1. code with tests,
2. documentation updated,
3. CI green,
4. the requirement linked in the traceability matrix.

Anything less stays open. If you cannot meet criterion 1 because your contribution is
documentation-only, say so in the pull request.

## Language

All repository content is written in **English**, including documentation, ADRs, code
comments, and identifiers. The public site is bilingual, Spanish-primary — see ADR 0010.

`docs/00-contexto-proyecto.md` is still in Spanish and is pending translation; it is a
legacy exception, not a precedent.

## Reporting a security issue

**Do not open a public issue.** Email the maintainer at
**victorloal513@gmail.com** with:

- what you found,
- how to reproduce it,
- the impact you believe it has.

You can expect an acknowledgement. Fixes for confirmed issues are documented in the
security test register (`docs/03-pruebas/casos-seguridad.md`) so the fix is verifiable.

## Reporting a rights or takedown request

If you are a photographer, a publisher, or a person depicted in an image on this site and
want content removed or corrected, use the takedown procedure in
`docs/legal/procedimiento-retiro-y-takedown.md`. Do not open a public issue for this.

## Conduct

Be respectful and assume good faith. Disagreeing with a technical decision is welcome and
normal — that is what the ADR process is for.