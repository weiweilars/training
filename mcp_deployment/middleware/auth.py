"""
Authentication middleware for MCP deployment
"""

import json
import time
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import jwt
import hashlib
import hmac


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware with multiple auth strategies"""

    def __init__(self, app, settings):
        super().__init__(app)
        self.settings = settings
        self.auth_type = settings.AUTH_TYPE  # "bearer", "api_key", "jwt", "basic"
        self.secret_key = settings.SECRET_KEY

    async def dispatch(self, request: Request, call_next):
        """Process authentication for each request"""

        # Skip auth for health check and root endpoints
        if request.url.path in ["/health", "/"]:
            return await call_next(request)

        # Skip auth if disabled
        if not self.settings.AUTH_ENABLED:
            return await call_next(request)

        # Perform authentication based on type
        auth_result = await self.authenticate(request)

        if not auth_result["authenticated"]:
            return JSONResponse(
                content={
                    "error": auth_result.get("error", "Authentication failed"),
                    "code": 401
                },
                status_code=401
            )

        # Add user context to request state
        request.state.user = auth_result.get("user", {})
        request.state.auth_method = auth_result.get("method")

        # Process the request
        response = await call_next(request)
        return response

    async def authenticate(self, request: Request) -> dict:
        """Authenticate request based on configured method"""

        if self.auth_type == "bearer":
            return await self.authenticate_bearer(request)
        elif self.auth_type == "api_key":
            return await self.authenticate_api_key(request)
        elif self.auth_type == "jwt":
            return await self.authenticate_jwt(request)
        elif self.auth_type == "basic":
            return await self.authenticate_basic(request)
        else:
            return {"authenticated": False, "error": f"Unknown auth type: {self.auth_type}"}

    async def authenticate_bearer(self, request: Request) -> dict:
        """Bearer token authentication"""
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return {"authenticated": False, "error": "Missing or invalid bearer token"}

        token = auth_header[7:]  # Remove "Bearer " prefix

        # Validate token against configured tokens
        valid_tokens = self.settings.VALID_BEARER_TOKENS
        if token in valid_tokens:
            return {
                "authenticated": True,
                "method": "bearer",
                "user": {"token_id": hashlib.sha256(token.encode()).hexdigest()[:8]}
            }

        return {"authenticated": False, "error": "Invalid bearer token"}

    async def authenticate_api_key(self, request: Request) -> dict:
        """API key authentication via header or query param"""
        # Check header first
        api_key = request.headers.get("X-API-Key")

        # Check query parameters if not in header
        if not api_key:
            api_key = request.query_params.get("api_key")

        if not api_key:
            return {"authenticated": False, "error": "Missing API key"}

        # Validate API key
        valid_keys = self.settings.VALID_API_KEYS
        if api_key in valid_keys:
            return {
                "authenticated": True,
                "method": "api_key",
                "user": {"api_key_id": hashlib.sha256(api_key.encode()).hexdigest()[:8]}
            }

        return {"authenticated": False, "error": "Invalid API key"}

    async def authenticate_jwt(self, request: Request) -> dict:
        """JWT token authentication"""
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return {"authenticated": False, "error": "Missing JWT token"}

        token = auth_header[7:]

        try:
            # Decode and validate JWT
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"]
            )

            # Check expiration
            if payload.get("exp") and payload["exp"] < time.time():
                return {"authenticated": False, "error": "JWT token expired"}

            return {
                "authenticated": True,
                "method": "jwt",
                "user": {
                    "user_id": payload.get("sub"),
                    "email": payload.get("email"),
                    "roles": payload.get("roles", [])
                }
            }

        except jwt.InvalidTokenError as e:
            return {"authenticated": False, "error": f"Invalid JWT: {str(e)}"}

    async def authenticate_basic(self, request: Request) -> dict:
        """Basic authentication"""
        import base64

        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Basic "):
            return {"authenticated": False, "error": "Missing basic auth credentials"}

        try:
            # Decode base64
            encoded = auth_header[6:]
            decoded = base64.b64decode(encoded).decode('utf-8')
            username, password = decoded.split(':', 1)

            # Validate credentials
            valid_users = self.settings.BASIC_AUTH_USERS
            if username in valid_users:
                # In production, use proper password hashing
                stored_password = valid_users[username]
                if self.verify_password(password, stored_password):
                    return {
                        "authenticated": True,
                        "method": "basic",
                        "user": {"username": username}
                    }

        except Exception as e:
            return {"authenticated": False, "error": f"Invalid basic auth: {str(e)}"}

        return {"authenticated": False, "error": "Invalid credentials"}

    def verify_password(self, plain_password: str, stored_password: str) -> bool:
        """Verify password (implement proper hashing in production)"""
        # For demo purposes, using simple comparison
        # In production, use bcrypt or similar
        return plain_password == stored_password


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""

    def __init__(self, app, settings):
        super().__init__(app)
        self.settings = settings
        self.requests = {}  # Simple in-memory store (use Redis in production)
        self.max_requests = settings.RATE_LIMIT_MAX_REQUESTS
        self.window_seconds = settings.RATE_LIMIT_WINDOW_SECONDS

    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting"""
        if not self.settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Get client identifier (IP or user ID)
        client_id = self.get_client_id(request)

        # Check rate limit
        if not self.check_rate_limit(client_id):
            return JSONResponse(
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": self.window_seconds
                },
                status_code=429
            )

        # Process request
        response = await call_next(request)
        return response

    def get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to use authenticated user ID first
        if hasattr(request.state, "user") and request.state.user.get("user_id"):
            return f"user:{request.state.user['user_id']}"

        # Fall back to IP address
        return f"ip:{request.client.host}"

    def check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit"""
        current_time = time.time()

        # Clean old entries
        if client_id in self.requests:
            self.requests[client_id] = [
                t for t in self.requests[client_id]
                if current_time - t < self.window_seconds
            ]

        # Check limit
        if client_id not in self.requests:
            self.requests[client_id] = []

        if len(self.requests[client_id]) >= self.max_requests:
            return False

        # Record request
        self.requests[client_id].append(current_time)
        return True