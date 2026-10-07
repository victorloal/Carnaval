# Sprint 17 retrospective — v3 hardening and launch (not launched)

- **Date:** 2026-10-07
- **Sprint:** 17 — v3 hardening and launch
- **Method:** Start / Stop / Continue, plus what actually happened versus what was planned.
- **Verdict:** **the executable half ran; the launch did not.** There is no deployment, so the
  deployed security sweep, the backup rehearsal, the browser budgets and the DNS/launch acts
  are **carried**. The project is complete in code and honest about not being live.

## What was planned versus what happened

Planned: sweep every security case on the **deployed** system, put CSP in front of
consent-gated embeds with no `unsafe-inline`, rehearse the privacy procedures, tune limits
against real traffic, re-rehearse backups, re-run the accessibility and Lighthouse budgets,
re-check logs, sweep the docs, **launch**, and close the project with a retrospective.

What happened, item by item:

| # | Item | Outcome |
|---|---|---|
| 1 | Security-case sweep on the deployed system | **Carried** — no deployment |
| 2 | CSP, no `unsafe-inline`; consent-gated embeds | **CSP done and tested** on the public surface (`test_security_headers.py`); **embeds carried** with the video-embed feature |
| 3 | Data-subject procedure documented and rehearsed | **Done** — documented in the privacy policy §6, deletion rehearsed by the `purge_personal_data` tests (Sprint 20); PRV-07 Done |
| 4 | Limits tuned against real traffic; egress in the free tier | **Carried** — no traffic, no deployment |
| 5 | Backup/restore re-rehearsed | **Carried** — needs the deployed database |
| 6 | Accessibility and Lighthouse budgets over submissions and gallery | **Carried** — needs a browser |
| 7 | Logs and analytics free of raw IPs and secrets | **Done** — inspection: `REMOTE_ADDR` is only ever passed to `hash_ip`, the `LOGGING` handler is console-only, and the pipeline's `logger.error` calls carry a source name and a message, never a raw IP or a secret |
| 8 | Documentation sweep | **Done** — this retrospective set, the regenerated matrix, `README.md`, `SECURITY.md`, `AGENTS.md` and `CHANGELOG.md` reconciled against the filesystem |
| 9 | Launch: DNS, disclaimer, takedown channel, legal drafts linked | **Carried** — a human act needing the maintainer's accounts and a host |
| 10 | Retrospective for v3 and the project | **Done for the retrospection; "launched" is not claimed** (see `proyecto-retrospectiva.md`) |

## Start

- **Reconcile the documents against the filesystem, not against each other.** The sweep found
  `SECURITY.md` still saying "nothing is deployed, the directories are empty" and `AGENTS.md`
  still one sprint into the project. Both were corrected against what is actually in the tree.
- **A note is not a control; find the test.** "No raw IP" is closed here by pointing at the one
  function every `REMOTE_ADDR` reaches (`hash_ip`) and at the logging config, not by repeating
  the intention.
- **Name the not-launched state everywhere it could be mistaken.** The README, `SECURITY.md`
  and the matrix each say the deployment is carried.

## Stop

- **Do not call a project "launched" when nothing is live.** The site cannot be visited, so it
  is not launched, and no aggregate of green checks changes that. The value of this sprint is
  the honesty, not the closure.
- **Do not run a "deployed" sweep against a development server and call it the same thing.**
  Four items (1, 4, 5, 6) cannot be faked, and they were not.
- **The launch is not a coding task.** It needs a host, a database, a bucket, DNS and the
  maintainer's accounts. Recording it as "blocked on accounts" is more useful than an eighth
  attempt to approximate it.

## Continue

- **Keep the post-launch checklist live.** `despliegue.md` §10 holds the acts that remain; they
  are the first things to run when an environment exists, not a backlog to rediscover.
- **Keep the matrix as the single source of truth.** It, not a sprint retrospective, is where
  "was it done" is answered.

## What the sprint recorded about the project

The project reached the end of its **buildable** scope: four versions implemented, a bilingual
public site, the moderation console, the ingestion pipeline, submissions with legal consent, and
a retention job. What remains is not code — it is access. That is the project's real shape, and
the retrospective says so instead of shading it into a launch.

## Concrete changes adopted

1. The deployment-dependent rows keep "needs a deployment" as their reason, in the matrix.
2. `README.md`, `SECURITY.md` and `AGENTS.md` were corrected to match the tree.
3. No deployed-system claim is made anywhere without a deployment behind it.
