"""A strict Content-Security-Policy for the public surface (SEC-15, NFR-07).

`script-src 'self'` with no `unsafe-inline`. The Django admin uses inline
scripts, so the policy is skipped for `/admin/`: the admin's own CSP is a v1
concern and a broken console is worse than no header. Everything else — the API,
`/health`, and any future server-rendered page — gets the policy.
"""

from __future__ import annotations

from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

_POLICY = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "frame-ancestors 'none'"
)


class ContentSecurityPolicyMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if not request.path.startswith("/admin/"):
            response.setdefault("Content-Security-Policy", _POLICY)
        return response
