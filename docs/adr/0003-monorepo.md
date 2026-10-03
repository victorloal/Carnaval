# 0003. Monorepo

- **Status:** Accepted
- **Date:** 2026-10-03
- **Relates to:** brief §6 decision 4, §17 (repository structure)

## Context

The project's stated purpose is to demonstrate the full engineering process — requirements,
design, security, implementation, testing, deployment, documentation — in one versioned
place (brief §1). Splitting documentation from code across repositories would work against
that: the traceability matrix, ADRs, and sprint notes must change in the same commit as
the code that satisfies them.

## Decision

**One repository** containing documentation and code together:

```
Carnaval/
├── docs/                  requirements, design, tests, ADRs, legal, sprints
├── backend/               Python (Django) — see ADR 0009
├── frontend/              React + TypeScript
├── tests/                 cross-cutting suites (E2E, security) that span both
├── AGENTS.md              rules for coding agents
├── MEMORY.md              session memory for coding agents
└── .github/               CI workflows, issue and PR templates
```

Consequences of the choice, stated so they are not rediscovered later:

- **One commit can satisfy a requirement end to end** (code + tests + docs + traceability
  row). This is what makes the Definition of Done in ADR 0001 atomic.
- **Cross-stack changes are one commit**, not a coordinated pair across a dependency
  boundary. With a solo maintainer this is decisive.
- **The frontend client is generated from `docs/02-diseno/openapi.yaml`**, not from a
  shared-types package. A monorepo does not imply shared types across languages; see
  ADR 0009 for why they are not shared.

## Consequences

**Positive**
- The traceability matrix can point at code paths in the same repository.
- CI can build and test backend, frontend, and E2E in one pipeline.
- The whole portfolio artifact is a single clone.

**Negative**
- No per-component versioned releases. Accepted: there is one deployable site and one API,
  both versioned together by commit.
- CI must install two toolchains (Python and Node). Mitigation: separate workflow jobs so
  they run in parallel.
- Repository root carries more than one ecosystem's ignore rules. Mitigation:
  `.gitignore` is maintained deliberately; see ADR 0009.

## Alternatives considered

- **Separate `docs` site or wiki.** Rejected: no atomic commits with code, and the
  traceability requirement becomes unenforceable.
- **Separate repos per component.** Rejected: adds coordination cost with no benefit for a
  single-maintainer project.