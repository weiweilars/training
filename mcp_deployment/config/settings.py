"""
Settings configuration for MCP Deployment
"""

import os
from typing import List, Dict, Optional
from pathlib import Path


class Settings:
    """Application settings with environment variable support"""

    def __init__(self):
        # Application
        self.APP_NAME = os.getenv("APP_NAME", "MCP Deployment Server")
        self.VERSION = os.getenv("APP_VERSION", "1.0.0")
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"

        # Server
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))
        self.WORKERS = int(os.getenv("WORKERS", "4"))

        # Authentication
        self.AUTH_ENABLED = os.getenv("AUTH_ENABLED", "false").lower() == "true"
        self.AUTH_TYPE = os.getenv("AUTH_TYPE", "bearer")  # bearer, api_key, jwt, basic
        self.SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

        # Bearer tokens (comma-separated)
        bearer_tokens = os.getenv("VALID_BEARER_TOKENS", "")
        self.VALID_BEARER_TOKENS = [t.strip() for t in bearer_tokens.split(",") if t.strip()]

        # API keys (comma-separated)
        api_keys = os.getenv("VALID_API_KEYS", "")
        self.VALID_API_KEYS = [k.strip() for k in api_keys.split(",") if k.strip()]

        # Basic auth users (format: user1:pass1,user2:pass2)
        basic_auth = os.getenv("BASIC_AUTH_USERS", "")
        self.BASIC_AUTH_USERS = self._parse_basic_auth(basic_auth)

        # CORS
        self.CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "*")
        self.CORS_ALLOWED_METHODS = os.getenv(
            "CORS_ALLOWED_METHODS",
            "GET,POST,PUT,DELETE,OPTIONS,PATCH"
        ).split(",")
        self.CORS_ALLOWED_HEADERS = os.getenv(
            "CORS_ALLOWED_HEADERS",
            "Content-Type,Authorization,X-API-Key,X-Request-ID,X-Stream-Response"
        ).split(",")
        self.CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
        self.CORS_MAX_AGE = int(os.getenv("CORS_MAX_AGE", "3600"))

        # Rate Limiting
        self.RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "false").lower() == "true"
        self.RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "100"))
        self.RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

        # Monitoring
        self.MONITORING_ENABLED = os.getenv("MONITORING_ENABLED", "true").lower() == "true"
        self.MONITORING_DETAILED_LOGGING = os.getenv("MONITORING_DETAILED_LOGGING", "false").lower() == "true"
        self.METRICS_EXPORT_FORMAT = os.getenv("METRICS_EXPORT_FORMAT", "prometheus")

        # Security Headers
        self.SECURITY_HEADERS_ENABLED = os.getenv("SECURITY_HEADERS_ENABLED", "true").lower() == "true"
        self.CSP_ENABLED = os.getenv("CSP_ENABLED", "false").lower() == "true"
        self.HSTS_ENABLED = os.getenv("HSTS_ENABLED", "false").lower() == "true"
        self.HSTS_MAX_AGE = int(os.getenv("HSTS_MAX_AGE", "31536000"))

        # Logging
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "info")
        self.LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
        self.LOG_FILE = os.getenv("LOG_FILE", "")

        # MCP Tool Configuration
        self.MCP_TOOL_PATH = os.getenv("MCP_TOOL_PATH", "")
        self.MCP_TOOL_MODULE = os.getenv("MCP_TOOL_MODULE", "")
        self.MCP_STREAMING_ENABLED = os.getenv("MCP_STREAMING_ENABLED", "true").lower() == "true"

        # Timeout settings
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "300"))  # 5 minutes
        self.STREAM_TIMEOUT = int(os.getenv("STREAM_TIMEOUT", "600"))  # 10 minutes

    def _parse_basic_auth(self, auth_string: str) -> Dict[str, str]:
        """Parse basic auth users from environment string"""
        users = {}
        if auth_string:
            for pair in auth_string.split(","):
                if ":" in pair:
                    user, password = pair.split(":", 1)
                    users[user.strip()] = password.strip()
        return users

    def validate(self):
        """Validate settings"""
        errors = []

        if self.AUTH_ENABLED and self.AUTH_TYPE == "jwt" and self.SECRET_KEY == "change-me-in-production":
            errors.append("JWT authentication requires a proper SECRET_KEY")

        if self.AUTH_ENABLED and self.AUTH_TYPE == "bearer" and not self.VALID_BEARER_TOKENS:
            errors.append("Bearer authentication enabled but no tokens configured")

        if self.AUTH_ENABLED and self.AUTH_TYPE == "api_key" and not self.VALID_API_KEYS:
            errors.append("API key authentication enabled but no keys configured")

        if self.AUTH_ENABLED and self.AUTH_TYPE == "basic" and not self.BASIC_AUTH_USERS:
            errors.append("Basic authentication enabled but no users configured")

        if errors:
            raise ValueError(f"Configuration errors: {'; '.join(errors)}")

    def to_dict(self) -> Dict:
        """Export settings as dictionary (excluding sensitive data)"""
        return {
            "app_name": self.APP_NAME,
            "version": self.VERSION,
            "environment": self.ENVIRONMENT,
            "debug": self.DEBUG,
            "host": self.HOST,
            "port": self.PORT,
            "auth_enabled": self.AUTH_ENABLED,
            "auth_type": self.AUTH_TYPE if self.AUTH_ENABLED else None,
            "cors_enabled": True,
            "rate_limit_enabled": self.RATE_LIMIT_ENABLED,
            "monitoring_enabled": self.MONITORING_ENABLED,
            "streaming_enabled": self.MCP_STREAMING_ENABLED
        }


def load_settings() -> Settings:
    """Load and validate settings"""
    settings = Settings()
    settings.validate()
    return settings