"""
Monitoring middleware for MCP deployment
Provides request metrics, logging, and performance monitoring
"""

import time
import json
from typing import Dict, List
from collections import defaultdict
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import asyncio


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Monitoring middleware for metrics collection"""

    def __init__(self, app, settings):
        super().__init__(app)
        self.settings = settings
        self.metrics = MetricsCollector()
        self.enable_detailed_logging = settings.MONITORING_DETAILED_LOGGING

    async def dispatch(self, request: Request, call_next):
        """Monitor request processing"""
        start_time = time.time()

        # Extract request metadata
        request_metadata = {
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Add request ID for tracing
        request_id = request.headers.get("X-Request-ID", self.generate_request_id())
        request.state.request_id = request_id

        try:
            # Process request
            response = await call_next(request)

            # Calculate metrics
            duration = time.time() - start_time

            # Record metrics
            self.metrics.record_request(
                path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration=duration,
                metadata=request_metadata
            )

            # Add response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration:.3f}s"

            # Log if detailed logging is enabled
            if self.enable_detailed_logging:
                await self.log_request(request, response, duration, request_id)

            return response

        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            self.metrics.record_error(
                path=request.url.path,
                method=request.method,
                error_type=type(e).__name__,
                duration=duration
            )

            # Log error
            await self.log_error(request, e, duration, request_id)

            # Re-raise the exception
            raise

    async def log_request(self, request: Request, response: Response, duration: float, request_id: str):
        """Log request details"""
        log_entry = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }

        # Add authenticated user info if available
        if hasattr(request.state, "user"):
            log_entry["user"] = request.state.user

        # Log to file or external service
        # In production, use proper logging service
        print(f"REQUEST: {json.dumps(log_entry)}")

    async def log_error(self, request: Request, error: Exception, duration: float, request_id: str):
        """Log error details"""
        log_entry = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "duration_ms": round(duration * 1000, 2),
            "client_ip": request.client.host if request.client else "unknown"
        }

        print(f"ERROR: {json.dumps(log_entry)}")

    def generate_request_id(self) -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())


class MetricsCollector:
    """Collects and aggregates metrics"""

    def __init__(self):
        self.requests = defaultdict(lambda: defaultdict(int))
        self.durations = defaultdict(list)
        self.errors = defaultdict(int)
        self.active_requests = 0
        self.total_requests = 0
        self.start_time = time.time()

    def record_request(self, path: str, method: str, status_code: int, duration: float, metadata: dict):
        """Record request metrics"""
        # Count requests by status code
        status_bucket = f"{status_code // 100}xx"
        self.requests[f"{method}:{path}"][status_bucket] += 1

        # Track duration
        self.durations[f"{method}:{path}"].append(duration)

        # Update totals
        self.total_requests += 1

    def record_error(self, path: str, method: str, error_type: str, duration: float):
        """Record error metrics"""
        self.errors[f"{method}:{path}:{error_type}"] += 1
        self.durations[f"{method}:{path}"].append(duration)
        self.total_requests += 1

    def get_metrics(self) -> dict:
        """Get current metrics snapshot"""
        uptime = time.time() - self.start_time

        # Calculate percentiles for durations
        percentiles = {}
        for endpoint, durations in self.durations.items():
            if durations:
                sorted_durations = sorted(durations)
                percentiles[endpoint] = {
                    "p50": self._percentile(sorted_durations, 50),
                    "p95": self._percentile(sorted_durations, 95),
                    "p99": self._percentile(sorted_durations, 99),
                    "avg": sum(durations) / len(durations),
                    "count": len(durations)
                }

        return {
            "uptime_seconds": uptime,
            "total_requests": self.total_requests,
            "requests_per_second": self.total_requests / uptime if uptime > 0 else 0,
            "endpoints": dict(self.requests),
            "latency_percentiles": percentiles,
            "errors": dict(self.errors)
        }

    def _percentile(self, sorted_list: List[float], percentile: int) -> float:
        """Calculate percentile from sorted list"""
        index = int(len(sorted_list) * percentile / 100)
        if index >= len(sorted_list):
            index = len(sorted_list) - 1
        return sorted_list[index]

    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format"""
        lines = []

        # Request counts
        for endpoint, statuses in self.requests.items():
            for status, count in statuses.items():
                method, path = endpoint.split(":", 1)
                lines.append(
                    f'mcp_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}'
                )

        # Latency metrics
        for endpoint, durations in self.durations.items():
            if durations:
                method, path = endpoint.split(":", 1)
                for d in durations:
                    lines.append(
                        f'mcp_request_duration_seconds{{method="{method}",path="{path}"}} {d}'
                    )

        # Error counts
        for error_key, count in self.errors.items():
            parts = error_key.split(":", 2)
            if len(parts) == 3:
                method, path, error_type = parts
                lines.append(
                    f'mcp_errors_total{{method="{method}",path="{path}",error="{error_type}"}} {count}'
                )

        # System metrics
        lines.append(f'mcp_uptime_seconds {time.time() - self.start_time}')
        lines.append(f'mcp_requests_total {self.total_requests}')

        return "\n".join(lines)


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Health check middleware with dependency checking"""

    def __init__(self, app, settings):
        super().__init__(app)
        self.settings = settings
        self.health_checks = []

    def add_health_check(self, name: str, check_func):
        """Add a health check function"""
        self.health_checks.append((name, check_func))

    async def dispatch(self, request: Request, call_next):
        """Process health check requests"""
        if request.url.path == "/health/detailed":
            # Perform detailed health checks
            health_status = await self.check_health()
            return Response(
                content=json.dumps(health_status),
                media_type="application/json",
                status_code=200 if health_status["healthy"] else 503
            )

        return await call_next(request)

    async def check_health(self) -> dict:
        """Perform health checks"""
        results = {}
        overall_healthy = True

        for name, check_func in self.health_checks:
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                results[name] = {"status": "healthy", "result": result}
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}
                overall_healthy = False

        return {
            "healthy": overall_healthy,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results
        }