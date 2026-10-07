# Sprint 19 retrospective — the public submission form

- **Date:** 2026-10-07
- **Sprint:** 19 — The public submission form
- **Method:** Start / Stop / Continue.
- **Note:** second of the four close-out sprints (18–21); see also
  `sprint-18-21-retrospectiva.md`.

## What was planned versus what happened

Planned: a visitor submits an **image** or a **video link** with no account, through a form whose
rights and consent declarations are unchecked and blocking, and looks the submission up later by
its token.

What happened: **all six items landed and CI is green on `876e7ae`.** The suite reached **135
backend + 33 frontend tests.** The matrix moved **FR-F-13 to Done** (the rest of the form's
requirements were already Done from the backend sprint).

Delivered: the submission form (kind radio, file or video URL, author, year, place,
description, minor flag, honeypot), the two blocking declarations whose consent label states the
accepted text is an **unreviewed draft** (ADR 0016/0018), status lookup by token, bilingual copy,
and one small **backend fix**: `POST /api/submissions/` had ignored `year` and `place`, so
FR-F-13 was not actually satisfiable from the form.

## Start

- **The two declarations are the form's spine.** The consent checkbox is unchecked by default
  and blocking, and it says in the visitor's language that the text was not reviewed by a
  lawyer — a visitor is entitled to know what they are accepting.
- **Mirror the server's honeypot.** A filled hidden `website` field is a silent no-op on both
  sides, so a bot gets the same answer whether it is caught in the client or the server.
- **The token is the only handle.** Contributors have no accounts, so the unguessable token is
  the one way to look a submission up, and an invalid token reveals nothing.
- **Sequenced after the decision.** The form was built only after ADR 0018 resolved the legal
  gate — before it, this sprint could not start.

## Stop

- **A backend gap hid behind a Done row.** FR-F-13's plan row said "form", and the form is where
  it was satisfied; but the endpoint silently dropped two of the fields the form collects. Found
  by writing the form against the endpoint, not by reading the plan.
- **A non-numeric year is stored as absent, not guessed.** Validation belongs at the edge; the
  server refuses to invent a value.
- **The CAPTCHA provider is still unverified.** The form leaves a hook; the Turnstile keys do
  not exist, and the honeypot and quotas carry the load.

## Continue

- **Blocking means blocking on both sides.** The client refuses to submit without both
  declarations; the server records the consent row and enforces `rights` regardless.
- **Keep the copy honest.** The label names the exact condition of the accepted text.

## What the sprint proved about the project

The riskiest public surface now has a public front. A stranger can contribute a photo or a video
link with real consent, and nothing is visible until a reviewer approves it — the moderation and
rights gates built in earlier sprints still stand between the form and the site.

## Concrete changes adopted

1. Test the endpoint against the form it is meant to serve, not only against its own unit tests.
2. A declared value that does not parse is stored as absent, never coerced.
3. The consent copy must state the accepted text is an unreviewed draft.
