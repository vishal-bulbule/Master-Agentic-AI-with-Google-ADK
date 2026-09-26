# Author: Vishal Bulbule
# Date: 2026-09-22

"""Checklist item 1: bearer-token authentication middleware.

Validates `Authorization: Bearer <token>` on every request before it reaches
the MCP endpoint. Tokens come from the MCP_BEARER_TOKENS environment variable
(comma-separated) to keep the sample self-contained.

For production on Cloud Run, prefer IAM: deploy with
--no-allow-unauthenticated and grant roles/run.invoker to the calling service
account, so Google verifies identity tokens before your code runs. Use this
middleware when one service must tell several tenants apart, and load the
tokens from Secret Manager rather than plain environment variables.
"""

import hashlib
import hmac
import os

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

VALID_TOKENS = {t.strip() for t in os.environ.get("MCP_BEARER_TOKENS", "").split(",") if t.strip()}

# Paths that stay open, for example a load balancer health check.
PUBLIC_PATHS = {"/healthz"}


def _is_valid(token: str) -> bool:
    # compare_digest takes the same time whether or not the prefix matches,
    # so response timing does not leak how much of a token was right.
    return any(hmac.compare_digest(token, valid) for valid in VALID_TOKENS)


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Rejects requests without a valid bearer token (401 or 403)."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        header = request.headers.get("authorization", "")
        if not header.startswith("Bearer "):
            return JSONResponse({"error": "missing bearer token"}, status_code=401)

        token = header.removeprefix("Bearer ").strip()
        if not _is_valid(token):
            return JSONResponse({"error": "invalid bearer token"}, status_code=403)

        # A stable, non-secret caller ID for rate limiting and audit logs.
        request.state.principal = hashlib.sha256(token.encode()).hexdigest()[:16]
        return await call_next(request)
