"""Basic smoke test to verify project setup."""

import pytest

from app import __version__
from app.config import get_settings


def test_version():
    """Test that version is defined."""
    assert __version__ == "0.1.0"


def test_settings_load():
    """Test that settings can be loaded."""
    settings = get_settings()
    assert settings.app_name == "Sentinel"
    assert settings.environment in ["development", "staging", "production"]


def test_settings_validation():
    """Test that settings validation works."""
    settings = get_settings()
    assert settings.check_interval >= 10
    assert settings.check_interval <= 3600
    assert settings.db_pool_size > 0


@pytest.mark.asyncio
async def test_placeholder():
    """Placeholder async test."""
    # TODO: Add real async tests
    assert True
