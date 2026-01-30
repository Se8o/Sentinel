"""Unit tests for custom exceptions."""

import pytest

from app.core.exceptions import (
    ConnectionError,
    DNSError,
    HealthCheckError,
    SSLError,
    TimeoutError,
)


class TestHealthCheckError:
    """Test base HealthCheckError exception."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = HealthCheckError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.url is None

    def test_error_with_url(self):
        """Test error with URL context."""
        error = HealthCheckError("Something went wrong", url="https://example.com")
        assert "https://example.com" in str(error)
        assert error.url == "https://example.com"

    def test_inheritance(self):
        """Test that it inherits from Exception."""
        error = HealthCheckError("Test")
        assert isinstance(error, Exception)


class TestTimeoutError:
    """Test TimeoutError exception."""

    def test_timeout_error(self):
        """Test timeout error creation."""
        error = TimeoutError(url="https://example.com", timeout=10)
        assert error.url == "https://example.com"
        assert error.timeout == 10
        assert "10s" in str(error)
        assert "timed out" in str(error).lower()

    def test_inheritance(self):
        """Test that it inherits from HealthCheckError."""
        error = TimeoutError(url="https://example.com", timeout=5)
        assert isinstance(error, HealthCheckError)
        assert isinstance(error, Exception)


class TestConnectionError:
    """Test ConnectionError exception."""

    def test_connection_error(self):
        """Test connection error creation."""
        error = ConnectionError(url="https://example.com", reason="Network unreachable")
        assert error.url == "https://example.com"
        assert error.reason == "Network unreachable"
        assert "Network unreachable" in str(error)
        assert "Connection failed" in str(error)

    def test_inheritance(self):
        """Test that it inherits from HealthCheckError."""
        error = ConnectionError(url="https://example.com", reason="Test")
        assert isinstance(error, HealthCheckError)


class TestSSLError:
    """Test SSLError exception."""

    def test_ssl_error(self):
        """Test SSL error creation."""
        error = SSLError(url="https://example.com", reason="Certificate expired")
        assert error.url == "https://example.com"
        assert error.reason == "Certificate expired"
        assert "Certificate expired" in str(error)
        assert "SSL verification failed" in str(error)

    def test_inheritance(self):
        """Test that it inherits from HealthCheckError."""
        error = SSLError(url="https://example.com", reason="Test")
        assert isinstance(error, HealthCheckError)


class TestDNSError:
    """Test DNSError exception."""

    def test_dns_error(self):
        """Test DNS error creation."""
        error = DNSError(url="https://nonexistent.example", hostname="nonexistent.example")
        assert error.url == "https://nonexistent.example"
        assert error.hostname == "nonexistent.example"
        assert "nonexistent.example" in str(error)
        assert "DNS resolution failed" in str(error)

    def test_inheritance(self):
        """Test that it inherits from HealthCheckError."""
        error = DNSError(url="https://example.com", hostname="example.com")
        assert isinstance(error, HealthCheckError)


class TestExceptionHierarchy:
    """Test exception hierarchy and catching."""

    def test_catch_base_exception(self):
        """Test that base exception catches all derived exceptions."""
        exceptions = [
            TimeoutError(url="https://example.com", timeout=10),
            ConnectionError(url="https://example.com", reason="Test"),
            SSLError(url="https://example.com", reason="Test"),
            DNSError(url="https://example.com", hostname="example.com"),
        ]

        for exc in exceptions:
            try:
                raise exc
            except HealthCheckError as e:
                assert isinstance(e, HealthCheckError)
            else:
                pytest.fail("Exception was not caught")

    def test_specific_exception_catching(self):
        """Test catching specific exception types."""
        with pytest.raises(TimeoutError) as exc_info:
            raise TimeoutError(url="https://example.com", timeout=5)

        assert exc_info.value.timeout == 5
        assert exc_info.value.url == "https://example.com"
