"""Tests for Google Docs integration."""
import pytest
from unittest.mock import MagicMock, patch

from ctf_bot.integrations.google_docs import GoogleDocsManager, find_doc_in_folder


class TestGoogleDocsManager:
    """Test cases for GoogleDocsManager class."""

    def test_init(self, mock_google_creds, mock_docs_service, mock_drive_service):
        """Test GoogleDocsManager initialization."""
        manager = GoogleDocsManager()
        assert manager.creds is not None
        assert manager.docs_service is not None
        assert manager.drive_service is not None

    def test_add_agenda_item(self, mock_google_creds, mock_docs_service, mock_drive_service):
        """Test adding an agenda item."""
        # Setup mocks
        mock_drive_service.files.return_value.list.return_value.execute.return_value = {
            'files': [{'id': 'test_doc_id', 'name': 'test_doc', 'modifiedTime': '2023-01-01'}]
        }
        
        manager = GoogleDocsManager()
        
        with patch('ctf_bot.integrations.google_docs.add_row_and_fill') as mock_add_row:
            manager.add_agenda_item("Test agenda item")
            mock_add_row.assert_called_once()


class TestGoogleDocsHelpers:
    """Test cases for Google Docs helper functions."""

    def test_find_doc_in_folder_success(self, mock_drive_service):
        """Test successful document finding."""
        mock_drive_service.files.return_value.list.return_value.execute.return_value = {
            'files': [{'id': 'test_doc_id', 'name': 'test_doc', 'modifiedTime': '2023-01-01'}]
        }
        
        doc_id = find_doc_in_folder(mock_drive_service, 'folder_id', 'doc_name')
        assert doc_id == 'test_doc_id'

    def test_find_doc_in_folder_not_found(self, mock_drive_service):
        """Test document not found."""
        mock_drive_service.files.return_value.list.return_value.execute.return_value = {
            'files': []
        }
        
        with pytest.raises(RuntimeError, match="No Google Doc named"):
            find_doc_in_folder(mock_drive_service, 'folder_id', 'doc_name')