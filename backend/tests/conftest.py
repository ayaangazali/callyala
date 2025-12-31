"""Pytest configuration and fixtures."""

import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Generator
import pytest

from app.core.config import Settings


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_data_dir() -> Generator[Path, None, None]:
    """Create a temporary data directory for tests."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_settings(temp_data_dir: Path) -> Settings:
    """Create mock settings with temp data directory."""
    return Settings(
        APP_ENV="test",
        DATA_DIR=str(temp_data_dir),
        MOCK_MODE=True,
        GOOGLE_SERVICE_ACCOUNT_FILE="",
        ELEVENLABS_API_KEY="test-api-key",
        ELEVENLABS_AGENT_ID="test-agent-id",
        ELEVENLABS_WEBHOOK_SECRET="test-webhook-secret",
    )


@pytest.fixture
def sample_campaign_data():
    """Sample campaign data for tests."""
    return {
        "id": "test-campaign-123",
        "name": "Test Campaign",
        "sheet_id": "sheet-123",
        "sheet_range": "Leads!A:Z",
        "status": "draft",
        "total_leads": 10,
        "leads_processed": 0,
        "leads_succeeded": 0,
        "leads_failed": 0,
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z",
    }


@pytest.fixture
def sample_call_data():
    """Sample call data for tests."""
    return {
        "id": "call-456",
        "campaign_id": "test-campaign-123",
        "lead_name": "John Doe",
        "phone_e164": "+96512345678",
        "sheet_row_idx": 2,
        "status": "completed",
        "outcome": "success",
        "duration_seconds": 120,
        "transcript": "Hello, this is a test call...",
        "summary": "Customer interested in booking",
        "sentiment": "positive",
        "created_at": "2024-01-15T10:05:00Z",
        "ended_at": "2024-01-15T10:07:00Z",
    }
