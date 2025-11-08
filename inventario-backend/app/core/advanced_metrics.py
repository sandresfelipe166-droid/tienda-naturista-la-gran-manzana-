"""Advanced metrics and observability utilities.

Provides comprehensive monitoring capabilities including:
- Request latency and throughput metrics
- Business metrics (inventory, sales)
- Error tracking and rates
- Prometheus integration
"""

import time
from collections.abc import Callable
from datetime import datetime
from typing import Any

from fastapi import Request, Response
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging_config import inventario_logger as logger

# ==================== Prometheus Metrics ====================

# Create a custom registry
REGISTRY = CollectorRegistry()

# HTTP Request Metrics
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint", "status_code"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0),
    registry=REGISTRY,
)

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
    registry=REGISTRY,
)

http_request_size_bytes = Histogram(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint"],
    registry=REGISTRY,
)

http_response_size_bytes = Histogram(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint", "status_code"],
    registry=REGISTRY,
)

# Error Metrics
error_counter = Counter(
    "application_errors_total",
    "Total application errors",
    ["error_type", "endpoint"],
    registry=REGISTRY,
)

# Business Metrics
inventory_total_value = Gauge(
    "inventory_total_value",
    "Total inventory value",
    registry=REGISTRY,
)

inventory_low_stock_count = Gauge(
    "inventory_low_stock_count",
    "Number of products with low stock",
    registry=REGISTRY,
)

inventory_near_expiry_count = Gauge(
    "inventory_near_expiry_count",
    "Number of products near expiry date",
    registry=REGISTRY,
)

sales_total = Counter(
    "sales_total",
    "Total sales count",
    ["product_category"],
    registry=REGISTRY,
)

sales_revenue_total = Counter(
    "sales_revenue_total",
    "Total sales revenue",
    ["product_category"],
    registry=REGISTRY,
)

# Database Metrics
database_query_duration_seconds = Histogram(
    "database_query_duration_seconds",
    "Database query execution time",
    ["query_type", "table"],
    registry=REGISTRY,
)

database_connection_pool_size = Gauge(
    "database_connection_pool_size",
    "Database connection pool size",
    registry=REGISTRY,
)

# Cache Metrics
cache_hits_total = Counter(
    "cache_hits_total",
    "Total cache hits",
    ["cache_key"],
    registry=REGISTRY,
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Total cache misses",
    ["cache_key"],
    registry=REGISTRY,
)

# Auth Metrics
auth_login_attempts_total = Counter(
    "auth_login_attempts_total",
    "Total login attempts",
    ["result"],
    registry=REGISTRY,
)

auth_token_validations_total = Counter(
    "auth_token_validations_total",
    "Total token validations",
    ["result"],
    registry=REGISTRY,
)


# ==================== Metrics Helpers ====================


class MetricsCollector:
    """Helper class for recording metrics."""

    @staticmethod
    def record_http_request(
        method: str,
        endpoint: str,
        status_code: int,
        duration_seconds: float,
        request_size: int = 0,
        response_size: int = 0,
    ) -> None:
        """Record HTTP request metrics."""
        http_request_duration_seconds.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).observe(duration_seconds)

        http_requests_total.labels(method=method, endpoint=endpoint, status_code=status_code).inc()

        if request_size > 0:
            http_request_size_bytes.labels(method=method, endpoint=endpoint).observe(request_size)

        if response_size > 0:
            http_response_size_bytes.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).observe(response_size)

    @staticmethod
    def record_error(error_type: str, endpoint: str) -> None:
        """Record error metric."""
        error_counter.labels(error_type=error_type, endpoint=endpoint).inc()

    @staticmethod
    def set_inventory_metrics(
        total_value: float,
        low_stock_count: int,
        near_expiry_count: int,
    ) -> None:
        """Set inventory metrics."""
        inventory_total_value.set(total_value)
        inventory_low_stock_count.set(low_stock_count)
        inventory_near_expiry_count.set(near_expiry_count)

    @staticmethod
    def record_sale(product_category: str, amount: float) -> None:
        """Record a sale."""
        sales_total.labels(product_category=product_category).inc()
        sales_revenue_total.labels(product_category=product_category).inc(amount)

    @staticmethod
    def record_db_query(query_type: str, table: str, duration_seconds: float) -> None:
        """Record database query metric."""
        database_query_duration_seconds.labels(query_type=query_type, table=table).observe(
            duration_seconds
        )

    @staticmethod
    def set_db_pool_size(size: int) -> None:
        """Set database connection pool size."""
        database_connection_pool_size.set(size)

    @staticmethod
    def record_cache_hit(cache_key: str) -> None:
        """Record cache hit."""
        cache_hits_total.labels(cache_key=cache_key).inc()

    @staticmethod
    def record_cache_miss(cache_key: str) -> None:
        """Record cache miss."""
        cache_misses_total.labels(cache_key=cache_key).inc()

    @staticmethod
    def record_login_attempt(success: bool) -> None:
        """Record login attempt."""
        result = "success" if success else "failure"
        auth_login_attempts_total.labels(result=result).inc()

    @staticmethod
    def record_token_validation(valid: bool) -> None:
        """Record token validation."""
        result = "valid" if valid else "invalid"
        auth_token_validations_total.labels(result=result).inc()


# ==================== Metrics Middleware ====================


class AdvancedMetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect detailed metrics from HTTP requests."""

    def __init__(self, app, exclude_paths: list | None = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json", "/metrics"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""

        # Skip metrics collection for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Get normalized endpoint path (replace IDs with {id})
        endpoint = self._normalize_path(request.url.path)

        start_time = time.time()
        request_size = request.headers.get("content-length", 0)

        try:
            response = await call_next(request)
            duration = time.time() - start_time

            # Extract response size from header if available
            response_size = response.headers.get("content-length", 0)
            try:
                response_size = int(response_size) if response_size else 0
            except ValueError:
                response_size = 0

            # Record metrics
            MetricsCollector.record_http_request(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration_seconds=duration,
                request_size=int(request_size) if request_size else 0,
                response_size=response_size,
            )

            # Log slow requests
            if duration > 1.0:
                logger.log_warning(
                    f"Slow request detected: {request.method} {endpoint}",
                    {"duration_seconds": duration, "status_code": response.status_code},
                )

            return response

        except Exception as e:
            duration = time.time() - start_time

            # Record error
            error_type = type(e).__name__
            MetricsCollector.record_error(error_type=error_type, endpoint=endpoint)

            logger.log_error(
                e,
                {
                    "method": request.method,
                    "endpoint": endpoint,
                    "duration_seconds": duration,
                },
            )

            raise

    @staticmethod
    def _normalize_path(path: str) -> str:
        """Normalize path by replacing numeric IDs with {id}."""
        import re

        # Replace UUIDs
        path = re.sub(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", "{id}", path)

        # Replace numeric IDs
        path = re.sub(r"/\d+(/|$)", r"/{id}\1", path)

        return path


# ==================== Health Check ====================


class HealthCheckCollector:
    """Collector for health check metrics."""

    @staticmethod
    def get_system_health() -> dict[str, Any]:
        """Get overall system health status."""
        from sqlalchemy import text

        from app.models.database import engine

        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
        }

        # Database health check
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            health["checks"]["database"] = {"status": "ok"}
        except Exception as e:
            health["status"] = "unhealthy"
            health["checks"]["database"] = {"status": "error", "message": str(e)}

        return health

    @staticmethod
    def get_inventory_metrics() -> dict[str, Any]:
        """Get current inventory metrics."""
        from sqlalchemy import func

        from app.models.database import SessionLocal
        from app.models.models import Producto

        db = SessionLocal()
        try:
            total_value = (
                db.query(func.sum(Producto.precio_compra * Producto.stock_actual)).scalar() or 0
            )
            low_stock = (
                db.query(func.count(Producto.id_producto))
                .filter(Producto.stock_actual <= Producto.stock_minimo)
                .scalar()
                or 0
            )
            total_products = db.query(func.count(Producto.id_producto)).scalar() or 0

            return {
                "total_value": float(total_value),
                "low_stock_count": int(low_stock),
                "total_products": int(total_products),
            }
        finally:
            db.close()

    @staticmethod
    def get_performance_metrics() -> dict[str, Any]:
        """Get performance metrics."""
        from prometheus_client import REGISTRY

        metrics = {}

        for metric in REGISTRY.collect():
            for sample in metric.samples:
                if sample.name not in metrics:
                    metrics[sample.name] = {
                        "value": sample.value,
                        "labels": sample.labels,
                    }

        return metrics
