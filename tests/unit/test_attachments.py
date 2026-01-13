"""Unit tests for attachment functionality."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from apple_mail_mcp.exceptions import (
    MailAppleScriptError,
    MailMessageNotFoundError,
)
from apple_mail_mcp.mail_connector import AppleMailConnector


class TestSendWithAttachments:
    """Tests for sending emails with attachments."""

    @pytest.fixture
    def connector(self) -> AppleMailConnector:
        """Create a connector instance."""
        return AppleMailConnector(timeout=30)

    @pytest.fixture
    def test_file(self, tmp_path: Path) -> Path:
        """Create a test file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")
        return test_file

    @patch.object(AppleMailConnector, "_run_applescript")
    def test_send_with_single_attachment(
        self, mock_run: MagicMock, connector: AppleMailConnector, test_file: Path
    ) -> None:
        """Test sending email with single attachment."""
        mock_run.return_value = "sent"

        result = connector.send_email_with_attachments(
            subject="Test",
            body="Test body",
            to=["recipient@example.com"],
            attachments=[test_file]
        )

        assert result is True
        call_args = mock_run.call_args[0][0]
        assert str(test_file) in call_args
        assert "make new attachment" in call_args

    @patch.object(AppleMailConnector, "_run_applescript")
    def test_send_with_multiple_attachments(
        self, mock_run: MagicMock, connector: AppleMailConnector, tmp_path: Path
    ) -> None:
        """Test sending email with multiple attachments."""
        mock_run.return_value = "sent"

        # Create multiple test files
        file1 = tmp_path / "file1.pdf"
        file2 = tmp_path / "file2.txt"
        file1.write_bytes(b"PDF content")
        file2.write_text("Text content")

        result = connector.send_email_with_attachments(
            subject="Test",
            body="Test body",
            to=["recipient@example.com"],
            attachments=[file1, file2]
        )

        assert result is True
        call_args = mock_run.call_args[0][0]
        assert str(file1) in call_args
        assert str(file2) in call_args

    def test_send_with_nonexistent_file(self, connector: AppleMailConnector) -> None:
        """Test error when attachment file doesn't exist."""
        from apple_mail_mcp.exceptions import MailAppleScriptError

        with pytest.raises((MailAppleScriptError, FileNotFoundError)):
            connector.send_email_with_attachments(
                subject="Test",
                body="Test body",
                to=["recipient@example.com"],
                attachments=[Path("/nonexistent/file.txt")]
            )

    @patch.object(AppleMailConnector, "_run_applescript")
    def test_send_validates_attachment_size(
        self, mock_run: MagicMock, connector: AppleMailConnector, tmp_path: Path
    ) -> None:
        """Test that large attachments are validated."""
        # Create a file larger than the limit
        large_file = tmp_path / "large.bin"
        # We'll implement size checking in the connector
        large_file.write_bytes(b"x" * (26 * 1024 * 1024))  # 26MB

        # Should raise error about file size
        with pytest.raises((ValueError, MailAppleScriptError)):
            connector.send_email_with_attachments(
                subject="Test",
                body="Test",
                to=["test@example.com"],
                attachments=[large_file],
                max_attachment_size=25 * 1024 * 1024  # 25MB limit
            )


class TestGetAttachments:
    """Tests for getting attachment information."""

    @pytest.fixture
    def connector(self) -> AppleMailConnector:
        """Create a connector instance."""
        return AppleMailConnector(timeout=30)

    @patch.object(AppleMailConnector, "_run_applescript")
    def test_get_attachments_list(
        self, mock_run: MagicMock, connector: AppleMailConnector
    ) -> None:
        """Test listing attachments from a message."""
        mock_run.return_value = "document.pdf|application/pdf|524288|true\nimage.jpg|image/jpeg|102400|true"

        result = connector.get_attachments("12345")

        assert len(result) == 2
        assert result[0]["name"] == "document.pdf"
        assert result[0]["mime_type"] == "application/pdf"
        assert result[0]["size"] == 524288
        assert result[0]["downloaded"] is True

    @patch.object(AppleMailConnector, "_run_applescript")
    def test_get_attachments_empty(
        self, mock_run: MagicMock, connector: AppleMailConnector
    ) -> None:
        """Test getting attachments from message with none."""
        mock_run.return_value = ""

        result = connector.get_attachments("12345")

        assert result == []

    @patch.object(AppleMailConnector, "_run_applescript")
    def test_get_attachments_message_not_found(
        self, mock_run: MagicMock, connector: AppleMailConnector
    ) -> None:
        """Test error when message doesn't exist."""
        mock_run.side_effect = MailMessageNotFoundError("Message not found")

        with pytest.raises(MailMessageNotFoundError):
            connector.get_attachments("99999")


class TestSaveAttachments:
    """Tests for saving attachments."""

    @pytest.fixture
    def connector(self) -> AppleMailConnector:
        """Create a connector instance."""
        return AppleMailConnector(timeout=30)

    @patch.object(AppleMailConnector, "_run_applescript")
    def test_save_single_attachment(
        self, mock_run: MagicMock, connector: AppleMailConnector, tmp_path: Path
    ) -> None:
        """Test saving a single attachment."""
        mock_run.return_value = "1"

        result = connector.save_attachments(
            message_id="12345",
            save_directory=tmp_path,
            attachment_indices=[0]
        )

        assert result == 1
        call_args = mock_run.call_args[0][0]
        assert str(tmp_path) in call_args

    @patch.object(AppleMailConnector, "_run_applescript")
    def test_save_all_attachments(
        self, mock_run: MagicMock, connector: AppleMailConnector, tmp_path: Path
    ) -> None:
        """Test saving all attachments from a message."""
        mock_run.return_value = "3"

        result = connector.save_attachments(
            message_id="12345",
            save_directory=tmp_path
        )

        assert result == 3

    def test_save_to_invalid_directory(self, connector: AppleMailConnector) -> None:
        """Test error when save directory is invalid."""
        with pytest.raises((ValueError, FileNotFoundError)):
            connector.save_attachments(
                message_id="12345",
                save_directory=Path("/nonexistent/directory")
            )

    @patch.object(AppleMailConnector, "_run_applescript")
    def test_save_validates_path_traversal(
        self, mock_run: MagicMock, connector: AppleMailConnector
    ) -> None:
        """Test that path traversal is prevented."""
        # Attempting path traversal should be blocked
        # Will fail with FileNotFoundError or ValueError depending on path
        with pytest.raises((ValueError, FileNotFoundError)):
            connector.save_attachments(
                message_id="12345",
                save_directory=Path("../../etc")
            )


class TestAttachmentSecurity:
    """Tests for attachment security features."""

    def test_validates_file_type_restrictions(self) -> None:
        """Test that dangerous file types are restricted."""
        from apple_mail_mcp.security import validate_attachment_type

        # Dangerous types should be rejected by default
        assert validate_attachment_type("malware.exe") is False
        assert validate_attachment_type("script.bat") is False
        assert validate_attachment_type("script.sh") is False
        assert validate_attachment_type("document.scr") is False

        # Safe types should be allowed
        assert validate_attachment_type("document.pdf") is True
        assert validate_attachment_type("image.jpg") is True
        assert validate_attachment_type("data.csv") is True

    def test_validates_file_size(self) -> None:
        """Test file size validation."""
        from apple_mail_mcp.security import validate_attachment_size

        # Within limit
        assert validate_attachment_size(1024 * 1024, max_size=10 * 1024 * 1024) is True

        # Exceeds limit
        assert validate_attachment_size(30 * 1024 * 1024, max_size=25 * 1024 * 1024) is False

    def test_sanitizes_filename(self) -> None:
        """Test filename sanitization."""
        from apple_mail_mcp.utils import sanitize_filename

        # Remove dangerous characters and path components
        # Path.name extracts just the filename, so "../../../etc/passwd" -> "passwd"
        assert sanitize_filename("../../../etc/passwd") == "passwd"
        assert sanitize_filename("file:name.txt") == "file_name.txt"
        assert sanitize_filename("file\x00name.txt") == "filename.txt"

        # Preserve safe names
        assert sanitize_filename("document.pdf") == "document.pdf"
        assert sanitize_filename("my-file_v2.txt") == "my-file_v2.txt"


class TestExtractAttachmentText:
    """Tests for extracting text from attachments."""

    @pytest.fixture
    def connector(self) -> AppleMailConnector:
        """Create a connector instance."""
        return AppleMailConnector(timeout=30)

    def test_extract_text_from_txt_file(self, tmp_path: Path) -> None:
        """Test extracting text from a .txt file."""
        from apple_mail_mcp.mail_connector import extract_text_from_file

        # Create a test text file
        test_file = tmp_path / "test.txt"
        test_content = "This is a test document.\nIt has multiple lines."
        test_file.write_text(test_content)

        # Extract text
        result = extract_text_from_file(test_file)

        assert result == test_content

    def test_extract_text_from_pdf_file(self, tmp_path: Path) -> None:
        """Test extracting text from a .pdf file."""
        from apple_mail_mcp.mail_connector import extract_text_from_file

        # Create a dummy PDF file
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4\nTest content")

        # Should either extract text or raise an error for invalid PDF
        try:
            result = extract_text_from_file(test_file)
            # If it succeeds, it should return a string
            assert isinstance(result, str)
        except (NotImplementedError, ValueError):
            # Expected - either PDF support not installed or invalid PDF format
            pass

    def test_extract_text_unsupported_format(self, tmp_path: Path) -> None:
        """Test that unsupported formats raise an error."""
        from apple_mail_mcp.mail_connector import extract_text_from_file

        # Create a file with unsupported extension
        test_file = tmp_path / "image.jpg"
        test_file.write_bytes(b"\xff\xd8\xff\xe0")  # JPEG header

        with pytest.raises((ValueError, NotImplementedError)):
            extract_text_from_file(test_file)

    def test_extract_text_file_not_found(self) -> None:
        """Test error when file doesn't exist."""
        from apple_mail_mcp.mail_connector import extract_text_from_file

        with pytest.raises(FileNotFoundError):
            extract_text_from_file(Path("/nonexistent/file.txt"))

    @patch.object(AppleMailConnector, "get_attachments")
    @patch.object(AppleMailConnector, "save_attachments")
    def test_extract_attachment_text_integration(
        self, mock_save: MagicMock, mock_get: MagicMock, connector: AppleMailConnector, tmp_path: Path
    ) -> None:
        """Test extracting text from a message attachment."""
        # Setup: Create a temp file that save_attachments will "save"
        test_file = tmp_path / "attachment.txt"
        test_content = "Email attachment content"
        test_file.write_text(test_content)

        # Mock get_attachments to return attachment info
        mock_get.return_value = [
            {
                "name": "attachment.txt",
                "mime_type": "text/plain",
                "size": len(test_content),
                "downloaded": True
            }
        ]

        # Mock save_attachments to create our test file
        def mock_save_attachment(message_id: str, save_directory: Path, attachment_indices: list[int] | None = None) -> int:
            # Copy our test file to the save directory
            dest = save_directory / "attachment.txt"
            dest.write_text(test_content)
            return 1

        mock_save.side_effect = mock_save_attachment

        # Extract text from attachment
        result = connector.extract_attachment_text(
            message_id="12345",
            attachment_index=0,
            attachment_name="attachment.txt"
        )

        assert result == test_content

    def test_extract_text_from_large_file(self, tmp_path: Path) -> None:
        """Test that large files are handled properly."""
        from apple_mail_mcp.mail_connector import extract_text_from_file

        # Create a large text file
        test_file = tmp_path / "large.txt"
        large_content = "Line of text.\n" * 10000  # ~140KB
        test_file.write_text(large_content)

        result = extract_text_from_file(test_file, max_size=1024 * 1024)  # 1MB limit

        assert len(result) > 0
        assert len(result) <= 1024 * 1024

    def test_extract_text_size_limit(self, tmp_path: Path) -> None:
        """Test that extraction respects size limits."""
        from apple_mail_mcp.mail_connector import extract_text_from_file

        # Create a file larger than the limit
        test_file = tmp_path / "huge.txt"
        huge_content = "x" * (2 * 1024 * 1024)  # 2MB
        test_file.write_text(huge_content)

        # Should raise error or truncate
        try:
            result = extract_text_from_file(test_file, max_size=1024 * 1024)  # 1MB limit
            # If it doesn't raise, it should truncate
            assert len(result) <= 1024 * 1024
        except ValueError as e:
            # Should mention size limit
            assert "size" in str(e).lower()
