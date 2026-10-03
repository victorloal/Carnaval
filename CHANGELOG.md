# Changelog

All notable changes to this project are recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) **for the
code**. Content and documentation versions follow the project's own rules: legal documents
are versioned per `legal_documents` and never edited after publication.

## [Unreleased]

Phase 0. No deployed version yet — see the status table in `README.md`.

### Added — project scaffolding

- `AGENTS.md` — binding rules for coding agents.
- `MEMORY.md` — session memory for coding agents, capped at 50 lines.
- `docs/00-acta-proyecto.md` — project charter: stakeholders, constraints, success
  criteria, and recorded deviations from the brief.
- `docs/01-requisitos/srs.md` — SRS with 168 numbered requirements, MoSCoW per version.
- `docs/01-requisitos/historias-de-usuario.md` — 32 user stories.
- `docs/01-requisitos/matriz-trazabilidad.md` — requirement → story → design → test.
- `docs/02-diseno/modelo-datos.md` — PostgreSQL data model.
- `docs/02-diseno/flujo-datos.md` — the ingestion pipeline, operationally.
- `docs/03-pruebas/plan-pruebas.md` — test plan and CI pipeline.
- `docs/03-pruebas/casos-seguridad.md` — 49 numbered security test cases.
- `docs/adr/0001` … `0011` — architecture decision records.
- `docs/legal/` — **draft** terms, privacy policy, content policy, and takedown procedure.
  Not legal advice; requires professional review before v3.
- `docs/fuentes-y-atribucion.md` — source register, attribution policy, scraping etiquette.
- `docs/sprints/` — sprint plan and retrospective for the documentation phase.
- `CONTRIBUTING.md`.

### Changed

- `LICENSE` — **The Unlicense replaced with MIT.** The Unlicense purported to dedicate the
  entire repository to the public domain, including third-party content the maintainer does
  not own. MIT covers code only; see ADR 0004.
- `00-contexto-proyecto.md` moved to `docs/00-contexto-proyecto.md`.
- `docs/01_requisitos/` renamed to `docs/01-requisitos/` to match the hyphenated
  convention used by the other document folders.
- `.gitignore` — added `data/raw/`, `*.pdf`, and `data/uploads/`; `lib/` is no longer
  ignored, because the file originated as GitHub's Python template and would silently drop
  real source directories.

### Removed

- `docs/01_requisitos/ad` — an empty 0-byte file.

### Notes on deviations from the original brief

Recorded in full in `docs/00-acta-proyecto.md` §9 and in `MEMORY.md`. In summary: no JWT
(session-based admin auth instead), Python + Django + PostgreSQL, Django admin rather than
a React admin panel, a generated rather than hand-written OpenAPI contract, and a
bilingual Spanish/English site. `docs/00-contexto-proyecto.md` still needs to be reconciled
with these.