"""
Observability and metrics utilities.

- MetricsManager: in-memory counters and latency histograms
- MetricsMiddleware: measures each request and records metrics
- Optional Prometheus integration (enabled if prometheus-client is installed and settings.prometheus_enabled = true)
"""

from __future__ import annotations

import time
from threading import Lock
from typing import Any, cast

from fastapi import Request, Response
from fastapi.responses import Response as FastAPIResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings

# Optional Prometheus integration
try:
    from prometheus_client import (  # type: ignore; type: ignore[assignment]
        CONTENT_TYPE_LATEST,
        generate_latest,  # type: ignore[assignment]
    )
    from prometheus_client import (
        CollectorRegistry as PromRegistry,
    )
    from prometheus_client import (
        Counter as PromCounter,
    )
    from prometheus_client import (
        Histogram as PromHistogram,
    )

    PROMETHEUS_AVAILABLE = True
except Exception:
    # Provide lightweight no-op shims to satisfy type checkers without adding a hard dependency
    PROMETHEUS_AVAILABLE = False
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"

    class PromRegistry:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

    class PromCounter:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):  # noqa: D401
            return self

        def inc(self, *args, **kwargs) -> None:
            pass

    class PromHistogram:  # type: ignore
        def __init__(self, *args, **kwargs):
            pass

        def labels(self, *args, **kwargs):  # noqa: D401
            return self

        def observe(self, *args, **kwargs) -> None:
            pass

    def generate_latest(*args, **kwargs):  # type: ignore
        return b""


class MetricsManager:
    """
    Singleton manager for application metrics (in-memory).
    Provides summary suitable for JSON health endpoints,
    and optional Prometheus exporters when available.
    """

    _instance: MetricsManager | None = None
    _instance_lock: Lock = Lock()

    @classmethod
    def instance(cls) -> MetricsManager:
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __init__(self):
        # Basic counters
        self.start_time: float = time.time()
        self.total_requests: int = 0
        self.total_errors: int = 0
        self.status_counts: dict[int, int] = {}

        # Latency histogram buckets (seconds)
        # Last bucket is +Inf to catch everything above the last finite bucket.
        self.buckets: list[float] = [0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, float("inf")]
        self.bucket_counts: dict[float, int] = {b: 0 for b in self.buckets}

        # Latency aggregates
        self.latency_sum: float = 0.0
        self.latency_count: int = 0

        # Lock for thread-safety in multi-thread servers
        self._lock: Lock = Lock()

        # Prometheus registry and metrics (initialized lazily)
        self._prom_registry: PromRegistry | None = None
        self._prom_counters_initialized: bool = False
        # Use Any to satisfy static type checkers whether Prometheus is available or not
        self._prom_requests_total: Any = None
        self._prom_errors_total: Any = None
        self._prom_latency_hist: Any = None

    # ---------- Internal helpers ----------

    def _bucket_for(self, duration: float) -> float:
        for b in self.buckets:
            if duration <= b:
                return b
        return float("inf")

    def _maybe_init_prometheus(self) -> None:
        if not PROMETHEUS_AVAILABLE or not settings.prometheus_enabled:
            return
        if self._prom_counters_initialized:
            return

        # Initialize a dedicated registry to avoid duplicate metrics on reload
        self._prom_registry = PromRegistry()

        # Metrics with minimal label cardinality
        self._prom_requests_total = PromCounter(
            "app_requests_total",
            "Total HTTP requests",
            ["method", "status_code"],
            registry=self._prom_registry,
        )
        self._prom_errors_total = PromCounter(
            "app_errors_total",
            "Total HTTP errors (status >= 400)",
            ["status_code"],
            registry=self._prom_registry,
        )
        self._prom_latency_hist = PromHistogram(
            "app_request_latency_seconds",
            "Request latency in seconds",
            ["method", "status_code"],
            buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, float("inf")],
            registry=self._prom_registry,
        )
        self._prom_counters_initialized = True

    # ---------- Public API ----------

    def record(self, duration: float, status_code: int, method: str, path: str) -> None:
        """
        Record a request observation.
        """
        with self._lock:
            self.total_requests += 1
            self.status_counts[status_code] = self.status_counts.get(status_code, 0) + 1
            if status_code >= 400:
                self.total_errors += 1

            b = self._bucket_for(duration)
            self.bucket_counts[b] = self.bucket_counts.get(b, 0) + 1
            self.latency_sum += duration
            self.latency_count += 1

            # Prometheus
            if PROMETHEUS_AVAILABLE and settings.prometheus_enabled:
                self._maybe_init_prometheus()
                if self._prom_counters_initialized:
                    # Labels: method and status_code
                    sc_str = str(status_code)
                    try:
                        requests_counter = cast(Any, self._prom_requests_total)
                        errors_counter = cast(Any, self._prom_errors_total)
                        latency_hist = cast(Any, self._prom_latency_hist)
                        requests_counter.labels(method=method, status_code=sc_str).inc()
                        if status_code >= 400:
                            errors_counter.labels(status_code=sc_str).inc()
                        latency_hist.labels(method=method, status_code=sc_str).observe(duration)
                    except Exception:
                        # Do not let metrics crash the request
                        pass

    def uptime_seconds(self) -> float:
        return max(0.0, time.time() - self.start_time)

    def _approx_p95(self) -> float | None:
        """
        Approximate 95th percentile using histogram buckets.
        """
        with self._lock:
            if self.latency_count == 0:
                return None
            target = int(self.latency_count * 0.95)
            cumulative = 0
            for b in self.buckets:
                cumulative += self.bucket_counts.get(b, 0)
                if cumulative >= target:
                    return b if b != float("inf") else None
            return None

    def summary(self) -> dict[str, Any]:
        """
        Return a JSON-serializable metrics summary.
        """
        with self._lock:
            uptime = self.uptime_seconds()
            avg_latency = (
                (self.latency_sum / self.latency_count) if self.latency_count > 0 else None
            )
            p95 = self._approx_p95()
            req_rate = (self.total_requests / uptime) if uptime > 0 else None
            err_rate = (self.total_errors / uptime) if uptime > 0 else None

            return {
                "uptime_seconds": uptime,
                "requests_total": self.total_requests,
                "errors_total": self.total_errors,
                "status_counts": dict(self.status_counts),
                "latency": {
                    "average_seconds": avg_latency,
                    "p95_bucket_seconds": p95,
                    "observation_count": self.latency_count,
                },
                "rates": {
                    "requests_per_second": req_rate,
                    "errors_per_second": err_rate,
                },
            }

    def get_prometheus_response(self) -> FastAPIResponse:
        """
        Build a Prometheus exposition response or a disabled placeholder if not available/enabled.
        """
        if not (settings.prometheus_enabled and PROMETHEUS_AVAILABLE):
            # Prometheus disabled or not available
            body = b"# Prometheus metrics are disabled or prometheus-client not installed.\n"
            return FastAPIResponse(content=body, media_type=CONTENT_TYPE_LATEST, status_code=200)

        self._maybe_init_prometheus()
        try:
            output = generate_latest(self._prom_registry)  # type: ignore
            return FastAPIResponse(content=output, media_type=CONTENT_TYPE_LATEST, status_code=200)
        except Exception:
            # Do not leak stacktraces on metrics endpoint
            body = b"# Error generating Prometheus metrics.\n"
            return FastAPIResponse(content=body, media_type=CONTENT_TYPE_LATEST, status_code=500)


# Singleton instance
metrics_manager = MetricsManager.instance()


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Starlette/FastAPI middleware to record per-request metrics.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        status_code = response.status_code
        # Record with method and path (path is not used in Prometheus labels to avoid cardinality explosion)
        metrics_manager.record(
            duration=duration, status_code=status_code, method=request.method, path=request.url.path
        )
        return response


def get_prometheus_metrics() -> FastAPIResponse:
    """
    Handler function to expose Prometheus metrics when enabled.
    """
    return metrics_manager.get_prometheus_response()
