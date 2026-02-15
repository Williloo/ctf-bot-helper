"""Test configuration and fixtures."""
import pytest
import os
from unittest.mock import MagicMock, patch

# Mock environment variables for testing
os.environ.setdefault("DISCORD_TOKEN", "test_token")
os.environ.setdefault("GOOGLE_FOLDER_ID", "test_folder_id")
os.environ.setdefault("GOOGLE_DOC_NAME", "test_doc")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_JSON", "test_service_account.json")


@pytest.fixture
def mock_google_creds():
    """Mock Google credentials."""
    with patch('ctf_bot.integrations.google_docs.make_creds') as mock:
        mock.return_value = MagicMock()
        yield mock


@pytest.fixture
def mock_docs_service():
    """Mock Google Docs service."""
    with patch('ctf_bot.integrations.google_docs.make_docs_service') as mock:
        service = MagicMock()
        mock.return_value = service
        yield service


@pytest.fixture
def mock_drive_service():
    """Mock Google Drive service."""
    with patch('ctf_bot.integrations.google_docs.make_drive_service') as mock:
        service = MagicMock()
        mock.return_value = service
        yield service