"""Custom exceptions for health checking."""


class HealthCheckError(Exception):
    """Base exception for health check errors."""

    def __init__(self, message: str, url: str | None = None):
        self.message = message
        self.url = url
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.url:
            return f"{self.message} (URL: {self.url})"
        return self.message


class TimeoutError(HealthCheckError):
    """Raised when health check times out."""

    def __init__(self, url: str, timeout: int):
        super().__init__(f"Health check timed out after {timeout}s", url)
        self.timeout = timeout


class ConnectionError(HealthCheckError):
    """Raised when connection to endpoint fails."""

    def __init__(self, url: str, reason: str):
        super().__init__(f"Connection failed: {reason}", url)
        self.reason = reason


class SSLError(HealthCheckError):
    """Raised when SSL/TLS verification fails."""

    def __init__(self, url: str, reason: str):
        super().__init__(f"SSL verification failed: {reason}", url)
        self.reason = reason


class DNSError(HealthCheckError):
    """Raised when DNS resolution fails."""

    def __init__(self, url: str, hostname: str):
        super().__init__(f"DNS resolution failed for hostname: {hostname}", url)
        self.hostname = hostname
