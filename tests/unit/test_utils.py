"""Unit tests for utility functions."""

import pytest

from apple_mail_mcp.utils import (
    escape_applescript_string,
    format_applescript_list,
    parse_applescript_list,
    parse_date_filter,
    sanitize_error_message,
    sanitize_input,
    validate_email,
)


class TestEscapeAppleScriptString:
    """Tests for escape_applescript_string."""

    def test_escapes_backslashes(self) -> None:
        result = escape_applescript_string("path\\to\\file")
        assert result == "path\\\\to\\\\file"

    def test_escapes_double_quotes(self) -> None:
        result = escape_applescript_string('Hello "World"')
        assert result == 'Hello \\"World\\"'

    def test_escapes_both(self) -> None:
        result = escape_applescript_string('Path\\to\\"file"')
        assert result == 'Path\\\\to\\\\\\"file\\"'

    def test_empty_string(self) -> None:
        result = escape_applescript_string("")
        assert result == ""

    def test_no_special_chars(self) -> None:
        result = escape_applescript_string("Hello World")
        assert result == "Hello World"

    def test_escapes_newlines(self) -> None:
        result = escape_applescript_string("Line1\nLine2")
        assert result == "Line1\\nLine2"

        result = escape_applescript_string("Line1\r\nLine2")
        assert result == "Line1\\r\\nLine2"

    def test_escapes_tabs(self) -> None:
        result = escape_applescript_string("Column1\tColumn2")
        assert result == "Column1\\tColumn2"

    def test_escapes_null_bytes(self) -> None:
        result = escape_applescript_string("Hello\x00World")
        assert result == "HelloWorld"

    def test_escapes_control_chars(self) -> None:
        result = escape_applescript_string("Text\x01\x02\x03")
        assert result == "Text"

    def test_escapes_all_combined(self) -> None:
        result = escape_applescript_string('Path\\to\\"file"\nwith\ttabs\x00and\x01control')
        assert result == 'Path\\\\to\\\\\\"file\\"\\nwith\\ttabsandcontrol'


class TestParseAppleScriptList:
    """Tests for parse_applescript_list."""

    def test_empty_list(self) -> None:
        assert parse_applescript_list("{}") == []
        assert parse_applescript_list("") == []

    def test_simple_list(self) -> None:
        result = parse_applescript_list("{a, b, c}")
        assert result == ["a", "b", "c"]

    def test_list_without_braces(self) -> None:
        result = parse_applescript_list("a, b, c")
        assert result == ["a", "b", "c"]

    def test_single_item(self) -> None:
        result = parse_applescript_list("{item}")
        assert result == ["item"]


class TestFormatAppleScriptList:
    """Tests for format_applescript_list."""

    def test_empty_list(self) -> None:
        result = format_applescript_list([])
        assert result == "{}"

    def test_simple_list(self) -> None:
        result = format_applescript_list(["a", "b", "c"])
        assert result == '{"a", "b", "c"}'

    def test_escapes_special_chars(self) -> None:
        result = format_applescript_list(['hello "world"'])
        assert result == '{"hello \\"world\\""}'


class TestParseDateFilter:
    """Tests for parse_date_filter."""

    def test_days_ago(self) -> None:
        result = parse_date_filter("7 days ago")
        assert result == "(current date) - (7 * days)"

    def test_weeks_ago(self) -> None:
        result = parse_date_filter("2 weeks ago")
        assert result == "(current date) - (2 * weeks)"

    def test_last_week(self) -> None:
        result = parse_date_filter("last week")
        assert result == "(current date) - (1 * weeks)"

    def test_iso_date(self) -> None:
        result = parse_date_filter("2024-01-15")
        assert result == 'date "2024-01-15"'


class TestValidateEmail:
    """Tests for validate_email."""

    def test_valid_emails(self) -> None:
        assert validate_email("user@example.com") is True
        assert validate_email("first.last@company.co.uk") is True
        assert validate_email("user+tag@example.com") is True

    def test_invalid_emails(self) -> None:
        assert validate_email("invalid") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("user example.com") is False

    def test_invalid_consecutive_dots(self) -> None:
        assert validate_email("user..name@example.com") is False
        assert validate_email("user@example..com") is False

    def test_invalid_leading_trailing_dots(self) -> None:
        assert validate_email(".user@example.com") is False
        assert validate_email("user.@example.com") is False
        assert validate_email("user@.example.com") is False

    def test_invalid_domain_format(self) -> None:
        assert validate_email("user@-example.com") is False
        assert validate_email("user@example-.com") is False

    def test_invalid_length(self) -> None:
        long_local = "a" * 65 + "@example.com"
        assert validate_email(long_local) is False

        long_email = "user@" + "a" * 250 + ".com"
        assert validate_email(long_email) is False


class TestValidateMessageId:
    """Tests for validate_message_id."""

    def test_valid_numeric_id(self) -> None:
        from apple_mail_mcp.utils import validate_message_id
        assert validate_message_id("12345") is True

    def test_valid_alphanumeric_id(self) -> None:
        from apple_mail_mcp.utils import validate_message_id
        assert validate_message_id("ABC-123_def") is True

    def test_invalid_empty_id(self) -> None:
        from apple_mail_mcp.utils import validate_message_id
        assert validate_message_id("") is False

    def test_invalid_too_long(self) -> None:
        from apple_mail_mcp.utils import validate_message_id
        long_id = "a" * 300
        assert validate_message_id(long_id) is False

    def test_invalid_special_chars(self) -> None:
        from apple_mail_mcp.utils import validate_message_id
        assert validate_message_id("id@with!special#chars") is False
        assert validate_message_id("id with spaces") is False
        assert validate_message_id("id/with/slashes") is False

    def test_invalid_path_traversal(self) -> None:
        from apple_mail_mcp.utils import validate_message_id
        assert validate_message_id("../../../etc/passwd") is False
        assert validate_message_id("..\\..\\windows\\system32") is False


class TestSanitizeInput:
    """Tests for sanitize_input."""

    def test_removes_null_bytes(self) -> None:
        result = sanitize_input("hello\x00world")
        assert result == "helloworld"

    def test_handles_none(self) -> None:
        result = sanitize_input(None)
        assert result == ""

    def test_converts_to_string(self) -> None:
        result = sanitize_input(123)
        assert result == "123"

    def test_limits_length(self) -> None:
        long_string = "a" * 20000
        result = sanitize_input(long_string)
        assert len(result) == 10000


class TestSanitizeErrorMessage:
    """Tests for sanitize_error_message."""

    def test_removes_file_paths(self) -> None:
        error = "Error in /Users/me/secrets/config.py: Invalid value"
        result = sanitize_error_message(error)
        assert "/Users/me/secrets/config.py" not in result
        assert "[PATH]" in result

    def test_removes_message_ids(self) -> None:
        error = "Message ABC123XYZ456789 not found"
        result = sanitize_error_message(error)
        assert "ABC123XYZ456789" not in result
        assert "[ID]" in result

    def test_removes_email_addresses(self) -> None:
        error = "Failed to send to user@secret-company.com"
        result = sanitize_error_message(error)
        assert "user@secret-company.com" not in result
        assert "[EMAIL]" in result

    def test_removes_all_combined(self) -> None:
        error = "Error in /path/to/file.py: Message ID1234567890 failed for user@example.com"
        result = sanitize_error_message(error)
        assert "/path/to/file.py" not in result
        assert "ID1234567890" not in result
        assert "user@example.com" not in result
        assert "[PATH]" in result
        assert "[ID]" in result
        assert "[EMAIL]" in result

    def test_preserves_safe_content(self) -> None:
        error = "Connection timeout after 30 seconds"
        result = sanitize_error_message(error)
        assert result == error
