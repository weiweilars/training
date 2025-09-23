"""
CORS middleware for MCP deployment with advanced configuration
"""

from typing import List, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CustomCORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware with flexible configuration"""

    def __init__(self, app, settings):
        super().__init__(app)
        self.settings = settings
        self.allowed_origins = self._parse_origins(settings.CORS_ALLOWED_ORIGINS)
        self.allowed_methods = settings.CORS_ALLOWED_METHODS
        self.allowed_headers = settings.CORS_ALLOWED_HEADERS
        self.allow_credentials = settings.CORS_ALLOW_CREDENTIALS
        self.max_age = settings.CORS_MAX_AGE

    def _parse_origins(self, origins: str) -> List[str]:
        """Parse origin configuration"""
        if origins == "*":
            return ["*"]
        return [origin.strip() for origin in origins.split(",")]

    async def dispatch(self, request: Request, call_next):
        """Handle CORS headers"""

        # Handle preflight OPTIONS request
        if request.method == "OPTIONS":
            return self.preflight_response(request)

        # Process the actual request
        response = await call_next(request)

        # Add CORS headers to response
        self.add_cors_headers(request, response)

        return response

    def preflight_response(self, request: Request) -> Response:
        """Handle preflight OPTIONS request"""
        response = Response(content="", status_code=200)
        self.add_cors_headers(request, response)
        return response

    def add_cors_headers(self, request: Request, response: Response):
        """Add CORS headers to response"""
        origin = request.headers.get("origin")

        # Check if origin is allowed
        if self.is_origin_allowed(origin):
            # Set allowed origin
            if "*" in self.allowed_origins:
                response.headers["Access-Control-Allow-Origin"] = "*"
            elif origin:
                response.headers["Access-Control-Allow-Origin"] = origin

            # Set other CORS headers
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)

            if self.allow_credentials:
                response.headers["Access-Control-Allow-Credentials"] = "true"

            if self.max_age:
                response.headers["Access-Control-Max-Age"] = str(self.max_age)

            # Expose custom headers if needed
            exposed_headers = ["X-Request-ID", "X-Response-Time"]
            response.headers["Access-Control-Expose-Headers"] = ", ".join(exposed_headers)

    def is_origin_allowed(self, origin: Optional[str]) -> bool:
        """Check if origin is allowed"""
        if not origin:
            return True  # Allow requests without origin header

        if "*" in self.allowed_origins:
            return True

        # Check exact match
        if origin in self.allowed_origins:
            return True

        # Check wildcard subdomain match (e.g., *.example.com)
        for allowed in self.allowed_origins:
            if allowed.startswith("*."):
                domain = allowed[2:]
                if origin.endswith(domain):
                    return True

        return False


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""

    def __init__(self, app, settings):
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next):
        """Add security headers"""
        response = await call_next(request)

        # Add security headers
        if self.settings.SECURITY_HEADERS_ENABLED:
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

            # Content Security Policy
            if self.settings.CSP_ENABLED:
                csp = self.build_csp()
                response.headers["Content-Security-Policy"] = csp

            # Strict Transport Security (for HTTPS)
            if self.settings.HSTS_ENABLED:
                response.headers["Strict-Transport-Security"] = f"max-age={self.settings.HSTS_MAX_AGE}; includeSubDomains"

        return response

    def build_csp(self) -> str:
        """Build Content Security Policy string"""
        directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self'",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        return "; ".join(directives)