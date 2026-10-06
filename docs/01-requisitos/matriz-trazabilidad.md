# Traceability matrix

- **Status:** Draft
- **Date:** 2026-10-03
- **Purpose:** ADR 0001 makes the fourth Definition-of-Done criterion "the requirement is
  linked in the traceability matrix". This file is where that obligation is discharged.
- **Sources:** `docs/01-requisitos/srs.md` (requirements),
  `docs/01-requisitos/historias-de-usuario.md` (stories), `docs/adr/` (decisions),
  `docs/02-diseno/` (design), `docs/03-pruebas/` (verification)

## How to read it

| Column | Meaning |
|---|---|
| **Req** | Requirement ID from the SRS. Stable — never renumbered |
| **Story** | User story implementing it, or `—` if none |
| **Design** | Implementing artefact |
| **ADR** | Governing decision |
| **Verif.** | *T* test · *I* inspection · *D* demonstration · *A* analysis |
| **Test** | Test or security-case ID |
| **Status** | *Open* (not started) · *WIP* · *Done* · *Deferred* (recorded reason) |

A requirement reaches **Done** only when its verification has actually been performed and
recorded. "Open" is the honest default for this project at present: nothing is implemented.

**Rule:** a requirement with no verification method cannot be closed. A test that verifies
no requirement should be deleted.

---

## FR-A — Catalogue and browsing

| Req | Story | Design | ADR | Verif. | Test | Status |
|---|---|---|---|---|---|---|
| FR-A-01 | US-01 | modelo-datos §3.1 | 0002 | T | unit: edition model | Done |
| FR-A-02 | US-02 | modelo-datos §3.2 | 0002 | T | unit: days are rows not enum | Done |
| FR-A-03 | US-02, US-03 | modelo-datos §3.3–3.4 | 0002 | T | unit: event model | Done |
| FR-A-04 | US-02 | modelo-datos §3.2 | 0002 | T | seed_demo: 2–6 Jan milestones | Done |
| FR-A-05 | US-03 | modelo-datos §3.3 | 0002 | T | API: venues | Open |
| FR-A-06 | US-04 | modelo-datos §2 | 0002 | T | **SEC-47** | Open |
| FR-A-07 | US-02 | arquitectura-c4 (L2) | 0009 | T | API: schema endpoints | Open |
| FR-A-08 | US-02 | — | 0009 | D | E2E: programme rendering | Open |
| FR-A-09 | US-04 | fuentes-y-atribucion | 0004 | T | E2E: disclaimer on all pages | Open |
| FR-A-10 | US-01 | modelo-datos §3.1 | 0008 | T | **SEC-47** (unpublished 404) | Open |
| FR-A-11 | — | modelo-datos §3.1 | 0009 | T | API: filters | Open — no story (see gaps) |
| FR-A-12 | US-04 | modelo-datos §3.5 | 0004 | T | E2E: source link present | Open |
| FR-A-13 | US-05 | arquitectura-c4 (L2) | 0009 | T | E2E 360 px + axe | Open |

## FR-B — Ingestion pipeline

| Req | Story | Design | ADR | Verif. | Test | Status |
|---|---|---|---|---|---|---|
| FR-B-01 | US-14 | flujo-datos | 0002 | T | integration: 4 stages | Open |
| FR-B-02 | US-14 | flujo-datos §RAW | 0002 | T | unit: raw storage + hash | Open |
| FR-B-03 | US-14 | modelo-datos §3.6 | 0002 | T | **SEC-37** | Open |
| FR-B-04 | US-14 | flujo-datos (idempotency) | 0002 | T | **SEC-37** | Open |
| FR-B-05 | US-14 | flujo-datos §TRANSFORM | 0002 | T | unit: schema validation | Open |
| FR-B-06 | US-07 | modelo-datos §2 | 0002 | T | unit: pending on ingest | Open |
| FR-B-07 | US-14 | flujo-datos §LOAD | 0002 | T | integration: upsert | Open |
| FR-B-08 | US-14 | modelo-datos §3.7 | 0002 | T | integration: run stats | Open |
| FR-B-09 | US-15 | flujo-datos (failure) | 0002 | T | **SEC-38** | Open |
| FR-B-10 | US-12 | flujo-datos (breaker) | 0002 | T | **SEC-39** | Open |
| FR-B-11 | US-12 | flujo-datos (§4) | 0002 | T | **SEC-40** | Open |
| FR-B-12 | US-16 | modelo-datos §3.5 | 0002 | T | admin: CRUD | Open |
| FR-B-13 | US-16 | flujo-datos (rate limit) | 0004 | T | **SEC-41** | Open |
| FR-B-14 | US-16 | fuentes-y-atribucion | 0004 | T | **SEC-42** | Open |
| FR-B-15 | US-14 | fuentes-y-atribucion §9.2 | 0002 | I | spike: WP API probe — **ran 2026-10-03, API available** (368 routes, no auth) | Open — spike passed, pipeline not built |
| FR-B-16 | — | modelo-datos §10 Q3 | 0002 | T | unit: retention prune | Open — no story |
| FR-B-17 | US-14 | despliegue | 0009 | D | GH Actions cron run | Open |
| FR-B-18 | US-17 | modelo-datos §3.7 | 0002 | T | admin: manual trigger | Open |
| FR-B-19 | US-14 | `.gitignore`, ADR 0004 | 0004 | T | **SEC-35** | Open |

## FR-C — Moderation and review

| Req | Story | Design | ADR | Verif. | Test | Status |
|---|---|---|---|---|---|---|
| FR-C-01 | US-07 | modelo-datos §2 | 0002 | T | unit: mixin fields | Open |
| FR-C-02 | US-07 | estados | 0002 | T | **SEC-47**, integration | Open |
| FR-C-03 | US-07 | estados | 0005 | T | **SEC-13** (editor allow) | Open |
| FR-C-04 | US-07 | modelo-datos §9 | 0005 | T | **SEC-17**, CHECK constraint | Open |
| FR-C-05 | US-08 | estados (unpublish) | 0002 | T | integration: published→pending | Open |
| FR-C-06 | US-09 | estados | 0009 | T | admin: queue filters | Open |
| FR-C-07 | US-07 | modelo-datos §6.5 | 0005 | T | **SEC-17** | Open |
| FR-C-08 | US-09 | flujo-datos | 0002 | A | inspection: default off | Open — Could |
| FR-C-09 | US-07, US-26 | modelo-datos §3.6 | 0002 | T | E2E: raw payload visible | Open |
| FR-C-10 | US-26 | ADR 0006 | 0008 | T | integration: rejection deletes | Open |
| FR-C-11 | US-09 | estados | 0005 | T | **SEC-17** (per-item rows) | Open |

## FR-D — Administration, roles, audit

| Req | Story | Design | ADR | Verif. | Test | Status |
|---|---|---|---|---|---|---|
| FR-D-01 | US-10 | arquitectura-c4 (L2) | 0005 | D | admin reachable | Open |
| FR-D-02 | US-10 | roles-permisos | 0005 | T | unit: groups | Open |
| FR-D-03 | US-10 | roles-permisos | 0005 | T | **SEC-12**, **SEC-13** | Open |
| FR-D-04 | US-10 | autenticacion (RBAC) | 0005 | T | **SEC-13** | Open |
| FR-D-05 | US-10 | roles-permisos | 0005 | T | **SEC-13** (viewer deny) | Open |
| FR-D-06 | US-10 | roles-permisos | 0005 | T | **SEC-13** (editor deny) | Open |
| FR-D-07 | US-10 | roles-permisos | 0005 | T | **SEC-13** (admin allow) | Open |
| FR-D-08 | US-11 | modelo-datos §5.1 | 0005 | T | **SEC-17**, **SEC-18** | Open |
| FR-D-09 | US-11 | modelo-datos §5.1 | 0005 | T | **SEC-16** | Open |
| FR-D-10 | US-11 | autenticacion (throttling) | 0005 | T | **SEC-18** | Open |
| FR-D-11 | US-31 | arquitectura-c4, despliegue | 0009 | T | integration: /health | Open |
| FR-D-12 | US-12 | modelo-datos §3.5 | 0002 | T | admin: source status | Open |
| FR-D-13 | US-10 | autenticacion (provisioning) | 0005 | T | **SEC-12** | Open |
| FR-D-14 | US-10 | autenticacion (provisioning) | 0005 | I | inspection: seed command | Open |
| FR-D-15 | — | autenticacion §7.3 | 0013 | T | **SEC-02**; v1 idle- and absolute-expiry tests | Open |
| FR-D-16 | US-10 | autenticacion §7.4 | 0013 | T | **SEC-04**, **SEC-13**; step-up gate on roles-permisos matrix rows 4, 13, 14, 24, 25, 30 | Open |

## FR-E — Editorial content

| Req | Story | Design | ADR | Verif. | Test | Status |
|---|---|---|---|---|---|---|
| FR-E-01 | US-18 | modelo-datos §4.1 | 0009 | T | API: news endpoint | Open |
| FR-E-02 | US-18 | modelo-datos §4.1 | 0004 | T | **SEC-34** | Open |
| FR-E-03 | US-18 | estados | 0002 | T | integration: news pending | Open |
| FR-E-04 | US-19 | modelo-datos §4.2 | 0004 | T | API: gallery | Open |
| FR-E-05 | US-19 | modelo-datos §4.2 | 0004 | T | **SEC-30** | Open |
| FR-E-06 | US-19 | modelo-datos §4.2 | 0004 | D | E2E: citation visible | Open |
| FR-E-07 | US-19 | modelo-datos §4.2 | 0006 | T | **SEC-23** | Open |
| FR-E-08 | US-19 | modelo-datos §4.2 | 0006 | T | **SEC-21** | Open |
| FR-E-09 | US-19 | modelo-datos §4.2 | 0009 | T | admin: feature toggle | Open |
| FR-E-10 | US-20 | modelo-datos §4.4 | 0009 | T | admin: settings CRUD | Open |
| FR-E-11 | US-20 | modelo-datos §4.4 | 0005 | T | **SEC-46** | Open |
| FR-E-12 | US-11, US-20 | modelo-datos §4.4 | 0005 | T | **SEC-17** | Open |

## FR-F — Public submissions

| Req | Story | Design | ADR | Verif. | Test | Status |
|---|---|---|---|---|---|---|
| FR-F-01 | US-22 | arquitectura-c4 (L2) | 0006 | T | E2E: submit image | Open |
| FR-F-02 | US-24 | ADR 0007 | 0007 | T | **SEC-36** | Open |
| FR-F-03 | US-22 | modelo-datos §6.2 | 0006 | T | **SEC-19** | Open |
| FR-F-04 | US-22 | modelo-datos §6.2 | 0006 | T | **SEC-19** | Open |
| FR-F-05 | US-22 | ADR 0006 | 0006 | T | **SEC-20** | Open |
| FR-F-06 | US-22 | modelo-datos §8 | 0006 | T | **SEC-21** | Open |
| FR-F-07 | US-22 | ADR 0006 | 0006 | T | **SEC-24** | Open |
| FR-F-08 | US-26 | ADR 0006 | 0006 | T | **SEC-25** | Open |
| FR-F-09 | US-26 | estados (submission) | 0006 | T | integration: move on approve | Open |
| FR-F-10 | US-22 | modelo-datos §6.3 | 0006 | T | **SEC-29** | Open |
| FR-F-11 | US-23 | modelo-datos §6.3 | 0006 | T | **SEC-28** | Open |
| FR-F-12 | US-22 | modelo-datos §8 | 0006 | T | **SEC-32** | Open |
| FR-F-13 | US-23 | modelo-datos §6.1 | 0006 | T | form: declaration fields | Open |
| FR-F-14 | US-23 | modelo-datos §6.3 | 0006 | T | form: consent declaration | Open |
| FR-F-15 | US-26 | modelo-datos §4.2 | 0004 | T | **SEC-31** | Open |
| FR-F-16 | US-22 | modelo-datos §6.2 | 0006 | T | **SEC-22** | Open |
| FR-F-17 | US-22 | arquitectura-c4 (CAPTCHA) | 0006 | T | **SEC-27** | Open |
| FR-F-18 | US-25 | modelo-datos §6.1 | 0006 | T | integration: token lookup | Open |
| FR-F-19 | US-24 | ADR 0007 | 0007 | T | **SEC-36** | Open |
| FR-F-20 | US-26 | ADR 0006 | 0006 | T | **SEC-26** | Open |
| FR-F-21 | US-26 | modelo-datos §6.2 | 0006 | T | **SEC-23** | Open |
| FR-F-22 | US-26 | estados | 0002 | T | integration: pending | Open |

## FR-G — Legal and takedown

| Req | Story | Design | ADR | Verif. | Test | Status |
|---|---|---|---|---|---|---|
| FR-G-01 | US-27 | modelo-datos §6.4 | 0008 | T | unit: one current version | Open |
| FR-G-02 | US-27 | modelo-datos §6.4 | 0008 | T | **SEC-28** | Open |
| FR-G-03 | US-27 | legal/README | 0008 | I | inspection: published | Open |
| FR-G-04 | US-28 | modelo-datos §6.6 | 0008 | T | integration: claim types | Open |
| FR-G-05 | US-29 | legal/takedown | 0008 | T | state-machine test | Open — gap noted |
| FR-G-06 | US-28 | modelo-datos §6.6 | 0008 | T | integration: action_taken | Open |
| FR-G-07 | US-24 | ADR 0007 | 0007 | I | inspection: remove ref only | Open |
| FR-G-08 | US-04 | fuentes-y-atribucion | 0004 | T | E2E: disclaimer | Open |

## FR-H — Internationalisation

| Req | Story | Design | ADR | Verif. | Test | Status |
|---|---|---|---|---|---|---|
| FR-H-01 | US-06 | ADR 0010 | 0010 | T | i18n: two locales | Open |
| FR-H-02 | US-06 | plan-pruebas §3.7 | 0010 | T | **SEC-48** | Open |
| FR-H-03 | US-06 | ADR 0010 | 0010 | T | E2E: prefixed URLs | Open |
| FR-H-04 | US-06 | ADR 0010 | 0010 | T | E2E: root redirect | Open |
| FR-H-05 | US-06 | ADR 0010 | 0010 | T | E2E: cookie persists | Open |
| FR-H-06 | — | modelo-datos §4.5 | 0010 | T | unit: fallback | Open — no story |
| FR-H-07 | — | modelo-datos §4.5 | 0010 | T | unit: per-locale slug | Open — no story |
| FR-H-08 | US-10 | ADR 0010 | 0010 | I | inspection: admin es only | Open |
| FR-H-09 | US-19 | ADR 0010 | 0010 | I | inspection: verbatim citation | Open |
| FR-H-10 | US-06 | ADR 0010 | 0010 | A | inspection: no MT dependency | Open |

## FR-I — Search

| Req | Story | Design | ADR | Verif. | Test | Status |
|---|---|---|---|---|---|---|
| FR-I-01 | US-21 | SRS §9 Q4 | 0009 | T | API: search | Open |
| FR-I-02 | US-21 | modelo-datos §2 | 0002 | T | unit: published scope | Open |
| FR-I-03 | US-21 | SRS §9 Q4 | 0009 | A | analysis: no paid service | Open |

## NFR — Non-functional

| Req | Story | Design | ADR | Verif. | Test | Status |
|---|---|---|---|---|---|---|
| NFR-01 | US-05 | plan-pruebas §3.7 | 0009 | T | Lighthouse CI | Open |
| NFR-02 | — | plan-pruebas §3.7 | 0009 | T | latency script | Open — no story |
| NFR-03 | US-05 | plan-pruebas §3.6 | 0009 | T | axe + manual | Open |
| NFR-04 | US-05 | plan-pruebas §3.4 | 0009 | T | E2E 360 px | Open |
| NFR-05 | US-31 | despliegue | 0001 | A | analysis: no paid dep | Open |
| NFR-06 | US-15 | flujo-datos | 0002 | T | **SEC-38** | Open |
| NFR-07 | US-05 | despliegue | 0005 | T | **SEC-43** | Open |
| NFR-08 | US-05 | despliegue | 0005 | T | **SEC-44** | Open |
| NFR-09 | US-20 | despliegue (secrets) | 0005 | T | **SEC-46** | Open |
| NFR-10 | — | plan-pruebas §2 | 0004 | I | inspection: Dependabot | Done — no story |
| NFR-11 | — | plan-pruebas §7 | 0001 | T | CI stage order | Done — no story |
| NFR-12 | — | ADR 0011 | 0011 | T | **schema drift check** | Done — no story |
| NFR-13 | US-32 | despliegue (migrations) | 0009 | I | inspection: PR review | Done |
| NFR-14 | — | plan-pruebas §2 | 0009 | T | ruff + mypy | Done — no story |
| NFR-15 | — | plan-pruebas §3.1 | 0001 | T | coverage gate | In Progress — no story |
| NFR-16 | — | plan-pruebas §1 | 0002 | T | CI: no egress | Done — no story |
| NFR-17 | — | despliegue | 0004 | T | **SEC-45** | Open — no story |
| NFR-18 | US-04 | modelo-datos §6.1 | 0005 | T | **SEC-15** | Open |
| NFR-19 | — | plan-pruebas | 0005 | T | log scan | Open — no story |
| NFR-20 | US-32 | despliegue (backup) | 0009 | D | rehearsal | Open |
| NFR-21 | US-10 | despliegue | 0005 | T | robots + header check | Open |

## SEC — Security requirements

| Req | Story | Design | ADR | Verif. | Test | Status |
|---|---|---|---|---|---|---|
| SEC-01 | US-10 | autenticacion | 0005 | T | **SEC-01** | Open |
| SEC-02 | US-10 | autenticacion | 0005 | T | **SEC-02**, **SEC-03** | Open |
| SEC-03 | US-10 | autenticacion | 0005 | T | **SEC-02** | Open |
| SEC-04 | US-10 | autenticacion | 0005 | T | **SEC-04** | Open |
| SEC-05 | US-10 | autenticacion | 0005 | T | **SEC-05** | Open |
| SEC-06 | US-12 | autenticacion (throttling) | 0005 | T | **SEC-06**, **SEC-07** | Open |
| SEC-07 | US-10 | autenticacion | 0005 | T | **SEC-09** | Open |
| SEC-08 | US-11 | autenticacion (revocation) | 0005 | T | **SEC-11** | Open |
| SEC-09 | US-10 | autenticacion (RBAC) | 0005 | T | **SEC-14** | Open |
| SEC-10 | US-10 | roles-permisos | 0005 | T | **SEC-13**, **SEC-14** | Open |
| SEC-11 | US-22 | ADR 0006 | 0006 | T | **SEC-19**, **SEC-20**, **SEC-21** | Open |
| SEC-12 | US-26 | ADR 0006 | 0006 | T | **SEC-24** | Open |
| SEC-13 | US-22 | ADR 0006 | 0006 | I | inspection: presigned flow | Open |
| SEC-14 | US-22 | modelo-datos §6.2 | 0006 | T | **SEC-22**, **SEC-27** | Open |
| SEC-15 | US-05 | despliegue (headers) | 0005 | T | **SEC-43** | Open |
| SEC-16 | — | plan-pruebas §2 | 0004 | I | inspection: Dependabot | Open — no story |

## PRV — Privacy requirements

| Req | Story | Design | ADR | Verif. | Test | Status |
|---|---|---|---|---|---|---|
| PRV-01 | US-26 | modelo-datos §8 | 0006 | T | **SEC-32** | Open |
| PRV-02 | US-22 | modelo-datos §8 | 0006 | T | **SEC-32** | Open |
| PRV-03 | US-30 | legal/privacidad | 0008 | T | **SEC-33** | Open |
| PRV-04 | US-22 | modelo-datos §8 | 0006 | T | **SEC-21** | Open |
| PRV-05 | US-23 | modelo-datos §6.3 | 0006 | T | **SEC-28** | Open |
| PRV-06 | US-27 | legal/privacidad | 0008 | I | inspection | **Blocked — ADR 0016.** Retention periods need legal judgement that will not be obtained. The requirement is left intact rather than weakened; do not fill it with a plausible value |
| PRV-07 | US-30 | legal/privacidad | 0008 | A | inspection: procedure | Open |
| PRV-08 | US-27 | legal/privacidad | 0007 | T | E2E: consent gate | Open |
| PRV-09 | US-22 | plan-pruebas | 0005 | T | **SEC-49** | Open |

## LEG — Copyright and content integrity

| Req | Story | Design | ADR | Verif. | Test | Status |
|---|---|---|---|---|---|---|
| LEG-01 | US-07 | estados | 0002 | T | **SEC-47** | Open |
| LEG-02 | US-19 | modelo-datos §4.2 | 0004 | T | **SEC-30** | Open |
| LEG-03 | US-19 | modelo-datos §4.2 | 0004 | D | E2E: citation | Open |
| LEG-04 | US-18 | modelo-datos §4.1 | 0004 | T | **SEC-34** | Open |
| LEG-05 | US-14 | `.gitignore`, ADR 0004 | 0004 | T | **SEC-35** | Open |
| LEG-06 | US-04 | `LICENSE`, ADR 0004 | 0004 | I | inspection | **Done** — LICENSE is MIT with the carve-out |
| LEG-07 | US-16 | fuentes-y-atribucion | 0004 | T | **SEC-41**, **SEC-42** | Open |
| LEG-08 | US-04 | fuentes-y-atribucion | 0004 | T | E2E: disclaimer | Open |
| LEG-09 | US-19 | modelo-datos §4.2 | 0004 | T | **SEC-31** | Open |
| LEG-10 | US-04 | fuentes-y-atribucion | 0004 | D | inspection: sources | Open |

---

## Summary

| Group | Count | Done | Open |
|---|---|---|---|
| FR-A … FR-I (functional) | 112 | 0 | 112 |
| NFR | 21 | 0 | 21 |
| SEC | 16 | 0 | 16 |
| PRV | 9 | 0 | 9 |
| LEG | 10 | 1 | 9 |
| **Total** | **168** | **1** | **167** |

**Everything is Open except LEG-06**, which is satisfied by the repository state. This is
the honest picture at the end of Phase 0: the documentation exists, nothing is built.

## Gaps and open decisions

Requirements with **no user story**. Each needs either a story or a recorded decision to
defer, before its version ships:

| Req | Why it has no story | Proposed action |
|---|---|---|
| FR-A-11 | Filtering is an implementation detail of US-02, not a user-visible need | Fold into US-02; no new story |
| FR-B-16 | Retention is an operational concern with no actor | Record as an operations task, not a story |
| FR-H-06, FR-H-07 | Translation of DB content is an editorial task, not a user journey | New story in v2 for the editorial workflow |
| NFR-02, NFR-17, NFR-19 | Quality attributes with no actor-facing behaviour | Verify via the test plan only; explicitly *not* stories |
| NFR-10, NFR-11, NFR-12, NFR-14, NFR-15, NFR-16 | Process and tooling requirements | Tracked in `plan-pruebas.md` §7; they constrain the pipeline, not the product |
| SEC-16 | Dependency scanning is tooling | Tracked in `plan-pruebas.md` §2 |

Open decisions inherited from the SRS §9 and `modelo-datos.md` §10 that block the rows
marked above: field-level versus generic translations, session timeout values, raw-document
retention window, search implementation, `site_settings` typed schema.

Security register gaps recorded in `casos-seguridad.md`: a dedicated takedown state-machine
case, and an i18n case for the database translation fallback (FR-H-06).