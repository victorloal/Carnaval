# 0007. Community videos as external links only

- **Status:** Accepted
- **Date:** 2026-10-03
- **Relates to:** brief §6 decision 9, §10 (public contributions)

## Context

Visitors should be able to contribute video of past parades. Accepting video files would
mean storing and serving media the project does not own the rights to, at a cost that
free tiers cannot absorb: video is the single most expensive asset class in both storage
and bandwidth.

## Decision

**The platform accepts video links only, and never hosts video files.**

- Providers in v3: **YouTube** and **Vimeo**, embedded via their official player.
- Only canonical watch URLs are accepted, stored normalised. The embed is rendered from
  the stored provider + video id — a submitted URL is never turned into an iframe `src`
  directly.
- Links are submitted as `pending` and follow the same moderation path as images.
- **Any request to upload a video file is rejected**, including a video disguised with an
  image extension. The magic-byte allowlist in ADR 0006 makes disguised files impossible
  to store.
- Removal requests (takedown) for an embedded video are handled by contacting the
  provider; the project removes its own reference to the embed.

## Consequences

**Positive**
- Zero video storage and egress cost, which protects the zero-cost constraint.
- No unlicensed video is redistributed — the provider's own terms and takedown process
  apply to the copy they host.
- No transcoding, no player, no video-specific moderation tooling.

**Negative**
- The site depends on a third party's embed availability and its advertising or tracking
  behaviour. Mitigation: `youtube-nocookie.com` for YouTube embeds, consent notice before
  loading, and a plain link as fallback if the embed is blocked.
- A video that disappears from the provider leaves a dead embed. Accepted; recorded in the
  moderation queue for re-review.
- Contributors who cannot host elsewhere are excluded. Accepted, and stated in the
  submission form rather than discovered after the fact.

## Alternatives considered

- **Accept video uploads.** Rejected on cost and on rights: the project cannot license
  what it does not own, and video egress exceeds free-tier limits immediately.
- **Link to files without embedding.** Rejected: takes visitors off-site with no context
  about what they are about to open.