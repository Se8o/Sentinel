"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_monitor_data():
    """Sample monitor data for testing."""
    return {
        "name": "Test Monitor",
        "url": "https://example.com",
        "interval": 60,
        "expected_status": 200,
    }


# TODO: Add database fixtures
# TODO: Add HTTP client fixtures
# TODO: Add mock fixtures for external services
