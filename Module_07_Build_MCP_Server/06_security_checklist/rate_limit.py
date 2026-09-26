# Author: Vishal Bulbule
# Date: 2026-09-22

"""Checklist item 5: per-caller rate limiting middleware.

A model can call a tool in a tight loop. A token bucket per caller caps the
request rate, so one runaway agent cannot exhaust a downstream API quota.

The buckets live in process memory, so the limit applies per instance: with
N Cloud Run instances a caller gets up to N times the rate. For a global limit,
keep the counters in Memorystore for Redis, or rate-limit in front of the
service (Cloud Armor, API Gateway).
"""

import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp


class TokenBucket:
    """Allows `capacity` requests at once, refilled at `refill_per_second`."""

    def __init__(self, capacity: int, refill_per_second: float) -> None:
        self.capacity = capacity
        self.refill_per_second = refill_per_second
        self.tokens = float(capacity)
        self.last = time.monotonic()

    def take(self) -> bool:
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.refill_per_second)
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Returns 429 when a caller exceeds its bucket."""

    def __init__(self, app: ASGIApp, *, capacity: int = 60, refill_per_second: float = 1.0) -> None:
        super().__init__(app)
        self.buckets: dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(capacity, refill_per_second)
        )

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Key on the principal set by BearerAuthMiddleware when auth runs
        # first; fall back to the client IP.
        principal = getattr(request.state, "principal", None) or (
            request.client.host if request.client else "anonymous"
        )
        if not self.buckets[principal].take():
            return JSONResponse({"error": "rate limit exceeded"}, status_code=429)
        return await call_next(request)
