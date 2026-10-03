# 0004. MIT license for the code only

- **Status:** Accepted
- **Date:** 2026-10-03
- **Relates to:** brief §6 decision 5, §11 (legal and ethical considerations), §20

## Context

The brief decided on MIT for the code, but the repository shipped `LICENSE` containing
**The Unlicense** (public-domain dedication), which contradicts the brief and, more
importantly, misrepresents the licensing of the project's actual content.

The repository holds two categorically different things:

1. **Source code** written by the maintainer — the pipeline, the API, the admin panel, the
   frontend, the tests, and the documentation.
2. **Third-party content** — news headlines and links, historical photographs, PDF
   schedules, page excerpts scraped from `carnavaldepasto.org` — whose copyright belongs
   entirely to other people.

A single license file covering both would imply rights the maintainer does not hold.

## Decision

**MIT for the code, with an explicit carve-out for content.**

- `LICENSE` contains the MIT License text, `Copyright (c) 2026 Victor Lopez`.
- It carries an explicit note stating that it covers **code only** and does not cover
  scraped data or any third-party content.
- Every third-party item carries its own attribution and rights metadata in the database
  (`author`, `source`, `license`, `citation_text`, `rights_status`). See
  `docs/fuentes-y-atribucion.md`.
- **An item whose `rights_status` is `unknown` is never published** (brief §11).
- Raw third-party material — PDFs, photographs, full article text — is never committed to
  the repository. `.gitignore` covers `data/raw/` and `*.pdf`.
- News is stored as headline + source URL + outlet + date + a short original summary.
  Never the full article or its images (brief §11).

## Consequences

**Positive**
- The license file now states something true. The Unlicense could not be honoured over
  content the maintainer does not own, so it created a misleading grant.
- MIT keeps the portfolio piece reusable while the attribution trail keeps the content
  lawful.
- Explicit carve-outs make the rights question part of the data model rather than a legal
  footnote.

**Negative**
- Downstream users must check per-item attribution before reusing content. Accepted: this
  is the actual legal situation.
- The notice in `LICENSE` is a non-standard addition. Mitigation: it is clearly separated
  from the MIT text and references the brief section that explains it.

## Alternatives considered

- **Keep The Unlicense.** Rejected: it purports to dedicate the entire repository to the
  public domain, including content the maintainer cannot dedicate.
- **No license.** Rejected: the brief chose MIT deliberately to stay permissive while
  preserving authorship, and a portfolio piece with no license is not reusable.
- **CC BY-SA for content as well.** Rejected: the maintainer does not hold the rights to
  relicense third-party material, so it would be an invalid grant.