# 0008. Incremental delivery by version (MVP → v3)

- **Status:** Accepted
- **Date:** 2026-10-03
- **Relates to:** brief §4 (scope by version), §6 decision 10, §14 (risks), §18

## Context

Brief §15 states plainly that the problem does not strictly require this system: the parade
schedule changes once a year, so a continuous ingestion pipeline with moderation and public
submissions is more than the problem demands. It is built deliberately to demonstrate data
engineering, security, and risk management.

That creates a real risk for a part-time solo developer: **scope exceeds capacity**. The
brief's own top risk is "excessive scope for one person", rated high impact.

## Decision

Deliver in four versions, each of which is **deployed and working before the next begins**.
A version is never partially started.

| Version | Contents |
|---|---|
| **MVP** | Ingestion pipeline, database, public read API, public frontend |
| **v1** | Admin (Django admin), roles, review queue for scraped content, audit log |
| **v2** | News, historical gallery with citations, site and scrape-source settings |
| **v3** | Public submissions (images and video links), moderation, legal documents |

Supporting rules:

- Each version's requirements are prioritised **MoSCoW** in the SRS. A "Won't" in a
  version is binding, not aspirational.
- Sprints (§16) deliver within one version; the version is not declared done early.
- **Public submissions are deliberately last (v3)**, gated behind working moderation and
  reviewed legal documents. Publishing an upload path before moderation exists and before
  the takedown and privacy documents are written would create legal exposure and an
  unmoderated channel on the public site.
- Anything not required by the current version's SRS is deferred, including ideas that
  appear mid-sprint. They go to the backlog, not into the sprint.

## Consequences

**Positive**
- There is always something deployed and demonstrable, which suits a portfolio piece and
  protects against the project stalling half-built.
- The highest-risk feature (anonymous uploads) is last, so it is only built once the
  machinery it depends on is proven.
- MoSCoW gives an explicit, written permission to say no.

**Negative**
- Features visible in the roadmap are unavailable for months. Accepted, and mitigated by
  publishing the version status honestly on the site.
- Early versions cannot demonstrate the moderation queue, which is the most interesting
  part. Accepted: v1 is reached quickly since it reuses Django admin.
- Discipline is required to actually stop. Mitigation: the WIP limit of 2 (ADR 0001) and
  the traceability matrix make scope creep visible in writing.

## Alternatives considered

- **Build everything, then deploy once.** Rejected: nothing is demonstrable until the end,
  and a solo project that runs out of energy leaves nothing deployed at all.
- **Public submissions in the MVP.** Rejected: it front-loads the legal and moderation
  work and inverts the dependency order the brief established.
- **Skip v1 by using Django admin without roles.** Rejected: the audit trail and role
  separation are requirements in their own right (brief §9), not optional polish.