"""Unit tests for domain models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.core.models import HealthCheckResult, MonitorStats, MonitorTarget


class TestMonitorTarget:
    """Test MonitorTarget domain model."""

    def test_valid_monitor_target(self):
        """Test creating a valid monitor target."""
        target = MonitorTarget(
            name="Google",
            url="https://www.google.com",
            interval=60,
            expected_status=200,
            timeout=10,
            enabled=True,
        )

        assert target.name == "Google"
        assert str(target.url) == "https://www.google.com/"
        assert target.interval == 60
        assert target.expected_status == 200
        assert target.timeout == 10
        assert target.enabled is True

    def test_default_values(self):
        """Test that default values are applied correctly."""
        target = MonitorTarget(
            name="Test",
            url="https://example.com",
        )

        assert target.interval == 60
        assert target.expected_status == 200
        assert target.timeout == 10
        assert target.enabled is True

    def test_name_validation_empty(self):
        """Test that empty name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            MonitorTarget(name="", url="https://example.com")

        errors = exc_info.value.errors()
        assert any("name" in str(e["loc"]) for e in errors)

    def test_name_validation_whitespace(self):
        """Test that whitespace-only name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            MonitorTarget(name="   ", url="https://example.com")

        errors = exc_info.value.errors()
        assert any("name" in str(e["loc"]) for e in errors)

    def test_name_validation_too_long(self):
        """Test that name longer than 100 chars is rejected."""
        long_name = "a" * 101
        with pytest.raises(ValidationError) as exc_info:
            MonitorTarget(name=long_name, url="https://example.com")

        errors = exc_info.value.errors()
        assert any("name" in str(e["loc"]) for e in errors)

    def test_name_trimming(self):
        """Test that name is trimmed of whitespace."""
        target = MonitorTarget(name="  Test  ", url="https://example.com")
        assert target.name == "Test"

    def test_url_validation_invalid(self):
        """Test that invalid URLs are rejected."""
        with pytest.raises(ValidationError):
            MonitorTarget(name="Test", url="not-a-url")

    def test_url_validation_non_http(self):
        """Test that non-HTTP/HTTPS URLs are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            MonitorTarget(name="Test", url="ftp://example.com")

        # Pydantic validates URL scheme before our custom validator
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_interval_validation_too_low(self):
        """Test that interval below 10s is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            MonitorTarget(name="Test", url="https://example.com", interval=5)

        errors = exc_info.value.errors()
        assert any("interval" in str(e["loc"]) for e in errors)

    def test_interval_validation_too_high(self):
        """Test that interval above 3600s is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            MonitorTarget(name="Test", url="https://example.com", interval=3601)

        errors = exc_info.value.errors()
        assert any("interval" in str(e["loc"]) for e in errors)

    def test_expected_status_validation(self):
        """Test that expected_status must be valid HTTP status code."""
        with pytest.raises(ValidationError):
            MonitorTarget(name="Test", url="https://example.com", expected_status=99)

        with pytest.raises(ValidationError):
            MonitorTarget(name="Test", url="https://example.com", expected_status=600)

    def test_timeout_validation(self):
        """Test timeout validation."""
        with pytest.raises(ValidationError):
            MonitorTarget(name="Test", url="https://example.com", timeout=0)

        with pytest.raises(ValidationError):
            MonitorTarget(name="Test", url="https://example.com", timeout=61)

    def test_serialization(self):
        """Test model serialization to dict."""
        target = MonitorTarget(name="Test", url="https://example.com")
        data = target.model_dump()

        assert data["name"] == "Test"
        assert "example.com" in str(data["url"])
        assert data["interval"] == 60

    def test_json_serialization(self):
        """Test model serialization to JSON."""
        target = MonitorTarget(name="Test", url="https://example.com")
        json_str = target.model_dump_json()

        assert "Test" in json_str
        assert "example.com" in json_str


class TestHealthCheckResult:
    """Test HealthCheckResult domain model."""

    def test_successful_result(self):
        """Test creating a successful health check result."""
        result = HealthCheckResult(
            monitor_name="Google",
            url="https://www.google.com",
            status="UP",
            status_code=200,
            latency_ms=45.2,
        )

        assert result.monitor_name == "Google"
        assert result.url == "https://www.google.com"
        assert result.status == "UP"
        assert result.status_code == 200
        assert result.latency_ms == 45.2
        assert result.error_message is None
        assert isinstance(result.timestamp, datetime)

    def test_failed_result(self):
        """Test creating a failed health check result."""
        result = HealthCheckResult(
            monitor_name="Test",
            url="https://example.com",
            status="DOWN",
            status_code=500,
            latency_ms=100.0,
            error_message="Internal Server Error",
        )

        assert result.status == "DOWN"
        assert result.status_code == 500
        assert result.error_message == "Internal Server Error"

    def test_timeout_result(self):
        """Test creating a timeout result."""
        result = HealthCheckResult(
            monitor_name="Test",
            url="https://example.com",
            status="TIMEOUT",
            error_message="Request timed out after 10s",
        )

        assert result.status == "TIMEOUT"
        assert result.status_code is None
        assert result.latency_ms is None
        assert "timed out" in result.error_message.lower()

    def test_error_result(self):
        """Test creating an error result."""
        result = HealthCheckResult(
            monitor_name="Test",
            url="https://example.com",
            status="ERROR",
            error_message="DNS resolution failed",
        )

        assert result.status == "ERROR"
        assert result.status_code is None

    def test_is_healthy_property(self):
        """Test is_healthy property."""
        up_result = HealthCheckResult(
            monitor_name="Test",
            url="https://example.com",
            status="UP",
            status_code=200,
        )
        assert up_result.is_healthy is True

        down_result = HealthCheckResult(
            monitor_name="Test",
            url="https://example.com",
            status="DOWN",
            status_code=500,
        )
        assert down_result.is_healthy is False

    def test_latency_seconds_property(self):
        """Test latency_seconds conversion."""
        result = HealthCheckResult(
            monitor_name="Test",
            url="https://example.com",
            status="UP",
            latency_ms=1500.0,
        )

        assert result.latency_seconds == 1.5

    def test_latency_seconds_none(self):
        """Test latency_seconds when latency_ms is None."""
        result = HealthCheckResult(
            monitor_name="Test",
            url="https://example.com",
            status="TIMEOUT",
        )

        assert result.latency_seconds is None

    def test_to_log_dict(self):
        """Test conversion to log dictionary."""
        result = HealthCheckResult(
            monitor_name="Test",
            url="https://example.com",
            status="UP",
            status_code=200,
            latency_ms=45.2,
        )

        log_dict = result.to_log_dict()

        assert log_dict["monitor"] == "Test"
        assert log_dict["url"] == "https://example.com"
        assert log_dict["status"] == "UP"
        assert log_dict["status_code"] == 200
        assert log_dict["latency_ms"] == 45.2
        assert log_dict["error"] is None
        assert "timestamp" in log_dict

    def test_latency_validation(self):
        """Test that negative latency is rejected."""
        with pytest.raises(ValidationError):
            HealthCheckResult(
                monitor_name="Test",
                url="https://example.com",
                status="UP",
                latency_ms=-10.0,
            )

    def test_status_validation(self):
        """Test that invalid status is rejected."""
        with pytest.raises(ValidationError):
            HealthCheckResult(
                monitor_name="Test",
                url="https://example.com",
                status="INVALID",  # type: ignore
            )


class TestMonitorStats:
    """Test MonitorStats domain model."""

    def test_valid_stats(self):
        """Test creating valid monitor stats."""
        stats = MonitorStats(
            monitor_name="Google",
            total_checks=100,
            successful_checks=98,
            failed_checks=2,
            average_latency_ms=42.5,
            uptime_percentage=98.0,
        )

        assert stats.monitor_name == "Google"
        assert stats.total_checks == 100
        assert stats.successful_checks == 98
        assert stats.failed_checks == 2
        assert stats.average_latency_ms == 42.5
        assert stats.uptime_percentage == 98.0

    def test_success_rate_property(self):
        """Test success_rate calculation."""
        stats = MonitorStats(
            monitor_name="Test",
            total_checks=100,
            successful_checks=95,
            failed_checks=5,
            uptime_percentage=95.0,
        )

        assert stats.success_rate == 95.0

    def test_success_rate_zero_checks(self):
        """Test success_rate when no checks performed."""
        stats = MonitorStats(
            monitor_name="Test",
            total_checks=0,
            successful_checks=0,
            failed_checks=0,
            uptime_percentage=0.0,
        )

        assert stats.success_rate == 0.0

    def test_validation_negative_values(self):
        """Test that negative values are rejected."""
        with pytest.raises(ValidationError):
            MonitorStats(
                monitor_name="Test",
                total_checks=-1,
                successful_checks=0,
                failed_checks=0,
                uptime_percentage=0.0,
            )

    def test_uptime_percentage_validation(self):
        """Test uptime percentage bounds."""
        with pytest.raises(ValidationError):
            MonitorStats(
                monitor_name="Test",
                total_checks=100,
                successful_checks=100,
                failed_checks=0,
                uptime_percentage=101.0,
            )

        with pytest.raises(ValidationError):
            MonitorStats(
                monitor_name="Test",
                total_checks=100,
                successful_checks=100,
                failed_checks=0,
                uptime_percentage=-1.0,
            )
