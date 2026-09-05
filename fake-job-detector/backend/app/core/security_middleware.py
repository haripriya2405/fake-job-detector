"""Production Security, Request Correlation ID, and Rate Limiting Middlewares (Phase 18)."""

import time
from typing import ClassVar, Dict, List, Tuple
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from app.core.config import settings
from app.core.logging import logger


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Applies strict HTTP security headers to all outgoing responses."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        
        # In production or HTTPS, enforce HSTS
        if settings.ENVIRONMENT == "production" or request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content-Security-Policy for API endpoints
        if not response.headers.get("Content-Security-Policy"):
            response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"

        return response


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """Assigns and logs request correlation IDs for end-to-end tracing."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        # Read or generate Request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        # Obfuscate sensitive credentials from logs
        path = request.url.path
        method = request.method
        client_ip = request.client.host if request.client else "unknown"

        response: Response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id

        # Structured request logging
        logger.info(
            f"[{request_id}] {method} {path} -> {response.status_code} ({duration_ms}ms) [client: {client_ip}]"
        )

        return response


class InMemoryRateLimiterMiddleware(BaseHTTPMiddleware):
    """Process-local sliding-window rate limiter per client IP.
    Note: Single-instance in-memory protection. For multi-worker distributed clusters,
    a shared Redis-backed store would be configured.
    """

    _shared_requests: ClassVar[Dict[str, List[float]]] = {}

    @classmethod
    def reset(cls):
        """Clear recorded requests (used for test isolation)."""
        cls._shared_requests.clear()

    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        path = request.url.path
        # Exclude telemetry, docs, and static endpoints from rate limiting
        if path in ["/health", "/ready", "/docs", "/redoc", "/openapi.json", "/api/v1/health", "/api/v1/ready"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"

        # If running automated tests from testclient, bypass unless explicitly testing rate limits
        is_test_env = getattr(settings, "TESTING", False) or settings.ENVIRONMENT == "testing"
        force_test = getattr(settings, "TESTING_RATE_LIMIT", False)
        if client_ip == "testclient" and not force_test:
            return await call_next(request)

        # Determine limit by route sensitivity
        if "/auth/login" in path or "/auth/register" in path:
            limit = settings.RATE_LIMIT_AUTH_PER_MINUTE
            bucket = "auth"
        elif "/analysis" in path and request.method == "POST":
            limit = settings.RATE_LIMIT_ANALYSIS_PER_MINUTE
            bucket = "analysis"
        else:
            limit = settings.RATE_LIMIT_PER_MINUTE
            bucket = "general"

        key = f"{client_ip}:{bucket}"
        now = time.time()
        
        # Clean expired timestamps older than 60s
        if key in self._shared_requests:
            self._shared_requests[key] = [t for t in self._shared_requests[key] if now - t < 60.0]
            if not self._shared_requests[key]:
                del self._shared_requests[key]

        history = self._shared_requests.get(key, [])
        if len(history) >= limit:
            request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
            logger.warning(f"[{request_id}] Rate limit exceeded for IP {client_ip} on {path} ({limit}/min)")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Too many requests. Limit is {limit} per minute for this endpoint.",
                    "type": "RateLimitExceeded",
                    "request_id": request_id,
                },
                headers={"Retry-After": "60", "X-Request-ID": request_id},
            )

        history.append(now)
        self._shared_requests[key] = history

        return await call_next(request)
