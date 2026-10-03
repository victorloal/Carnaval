# Sprint 00 retrospective — documentation phase

- **Date:** 2026-10-03
- **Sprint:** 00 — Phase 0 documentation
- **Method:** Start / Stop / Continue, plus what actually happened versus what was planned.

## What was planned versus what happened

Planned: reconcile the brief, write the ADRs, write requirements, write the design set,
write the test plan, draft the legal documents, fill in the root files.

What happened: all of that, except the brief reconciliation, which was **deferred**. The
brief reconciliation was listed as sprint item 1 and then dropped to make room, because
the stack questions had to be answered first — and answering them invalidated more of the
brief than expected.

That is the one meaningful process failure of the sprint, and it is worth naming precisely:
**the item most likely to be dropped was the one that would have caught the most errors.**

## Start

- **Reconcile the brief as a separate, first-class task before writing anything derived
  from it.** Every deviation discovered later (JWT, stack, admin panel, OpenAPI) had to be
  recorded three times: in an ADR, in the acta, and in `MEMORY.md`. Fixing the brief first
  would have made two of those unnecessary.
- **Verify the repository against its own documentation before planning.** Five
  contradictions existed before a single line of code was written. None were caught by
  reading the brief.
- **Read the config files that a stack choice implies.** `.gitignore` was an unmodified
  Python template that would have silently dropped a source directory.

## Stop

- **Trusting a completion report without checking the filesystem.** A delegated
  documentation task reported writing two large files; neither existed on disk. Two files
  had to be rewritten by hand. The cost of checking is one directory listing.
- **Deferring the brief reconciliation indefinitely.** It is still open, and the brief is
  the first document a reviewer reads.
- **Writing ADRs that depend on decisions not yet made.** ADR 0009 was written as
  FastAPI/SQLAlchemy and had to be fully rewritten once Django was chosen. Cheap to
  avoid: settle the stack first, then write its ADR.

## Continue

- **Mermaid diagrams in the repository.** They diff, they review, and they need no tool.
- **Numbered requirement IDs from the start.** The traceability matrix was written last and
  would have been far easier to write incrementally, which is what ADR 0001 intends.
- **Documenting deviations rather than quietly reconciling them.** The acta §9 table and
  ADR 0005's "Action required" section make the gap between intent and reality obvious,
  which is the honest state of the project at present.

## What the sprint proved about the project

The brief's top risk is "excessive scope for one person". The documentation phase produced
168 requirements and 32 stories from a brief that is 21 KB of prose — and none of it is
implemented. That is the correct order of operations, but it is also the warning: the
requirement count is already large enough that **deferring by version (ADR 0008) is the
only thing keeping the project tractable.** The MoSCoW "Won't" column is load-bearing.

## Concrete changes adopted

1. The next sprint's first item is the brief reconciliation, with no exceptions.
2. Every delegated task is verified with a directory listing before it is reported done.
3. The stack ADR is written only after the stack is confirmed in conversation.
4. The traceability matrix is updated as requirements are written, not at the end.