# Sprint 05 retrospective — the public read API

- **Date:** 2026-10-06
- **Sprint:** 05 — The public read API
- **Method:** Start / Stop / Continue, plus what actually happened versus what was planned.
- **Written later:** this sprint was delivered but its retrospective was never written; it is
  reconstructed from the plan, the commit (`565a76c`) and the matrix.

## What was planned versus what happened

Planned: expose the published catalogue over HTTP as JSON — editions, days, events and venues —
read-only, filtered to `status = published`, filterable by edition and date range, rate-limited
per IP, against a committed and drift-checked OpenAPI contract, with a `/health` probe.

What happened: **all seven backlog items landed and CI is green on `565a76c`.** The suite is at
**73 tests**; `ruff`, `mypy`, `makemigrations --check` and `check --deploy` are clean. The
matrix moved **FR-A-06, FR-A-07, FR-A-11, FR-D-11, NFR-02, NFR-17 and NFR-18 to Done.**

Delivered: a `carnaval.api` app with read-only viewsets for the four catalogue models, a shared
`PublishedReadOnlyViewSet` whose queryset starts from `status = published`, date/edition
filters, page-number pagination, an anonymous per-IP rate limit, `Cache-Control: public,
max-age=300` on public reads, `/health`, and the generated schema.

## Start

- **The published filter is a mixin, not a line per view.** Every viewset inherits
  `get_queryset` from one class that applies `status = published`. A `pending` or `rejected`
  row is a **404**, never a redacted 200 — and the rule lives in one place.
- **Fail closed by default.** `REST_FRAMEWORK` declares `IsAuthenticated` as the default
  permission; the public viewsets opt **out** explicitly. A new endpoint is private until
  someone says otherwise, which is the safe direction for a mistake.
- **Read-only is structural.** `ReadOnlyModelViewSet` routes no non-GET method, so NFR-18 is a
  property of the class, not a policy someone remembers.
- **The contract is generated, not written.** `openapi.yaml` is produced by drf-spectacular and
  the drift check runs in CI, so the schema cannot lag the code (ADR 0011).

## Stop

- **The site is not here yet.** The API is technically complete but nobody can see it; Sprint
  06 is the first sprint whose output a person can actually use. Accepted, and it is the point
  of the version order.
- **Search is deferred, not half-built.** Full-text search needs PostgreSQL (`SearchVector`) or
  an honest fallback; it is v2's problem, and doing it here would have forced a decision before
  the database branch existed.
- **The rate-limit test needs its own cache.** Testing the limiter against the shared default
  cache would make results order-dependent; the over-limit case uses an isolated cache. This is
  the kind of thing that only shows up when the test is written.
- **Throttling is per-process.** `AnonRateThrottle` uses the cache backend, which in production
  is per-process unless a shared cache is configured. Recorded rather than pretended: the limit
  is a brake, not a distributed quota.

## Continue

- **One visibility rule, tested per endpoint.** FR-A-06 has a test on each endpoint, so the
  mixin cannot be "optimised" away on one of them.
- **Cache what is public and identical.** `Cache-Control` on public reads is safe precisely
  because the API is anonymous and locale-free; the personal endpoints added in v3 are
  `no-store`, the opposite decision for the opposite reason.
- **Regenerate the schema in the same commit** that changes a view (ADR 0011).

## What the sprint proved about the project

The publish-only guarantee survived contact with the network: the moderation state decided in
v1's design is the same filter the public API applies, and nothing unreviewed can be served
even by accident, because there is no code path that returns it. The API is the first surface a
stranger touches, and it can only return what a human already approved.

## Concrete changes adopted

1. The default DRF permission stays `IsAuthenticated`; public endpoints opt out one at a time.
2. `PublishedReadOnlyViewSet` is the only place the published filter is written.
3. A test that depends on shared state (the cache) gets its own isolated instance.
