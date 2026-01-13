"""Unit tests for security module."""

import time
from unittest.mock import patch

import pytest

from apple_mail_mcp.security import (
    OperationLogger,
    RateLimiter,
    rate_limit_check,
    require_confirmation,
    validate_bulk_operation,
    validate_send_operation,
)


class TestOperationLogger:
    """Tests for OperationLogger."""

    def test_logs_operation(self) -> None:
        logger = OperationLogger()
        logger.log_operation("test_op", {"key": "value"}, "success")

        operations = logger.get_recent_operations(limit=1)
        assert len(operations) == 1
        assert operations[0]["operation"] == "test_op"
        assert operations[0]["parameters"] == {"key": "value"}
        assert operations[0]["result"] == "success"

    def test_limits_recent_operations(self) -> None:
        logger = OperationLogger()

        for i in range(20):
            logger.log_operation(f"op_{i}", {}, "success")

        recent = logger.get_recent_operations(limit=5)
        assert len(recent) == 5
        assert recent[-1]["operation"] == "op_19"


class TestValidateSendOperation:
    """Tests for validate_send_operation."""

    def test_valid_single_recipient(self) -> None:
        is_valid, error = validate_send_operation(["user@example.com"])
        assert is_valid is True
        assert error == ""

    def test_valid_multiple_recipients(self) -> None:
        is_valid, error = validate_send_operation(
            to=["user1@example.com"],
            cc=["user2@example.com"],
            bcc=["user3@example.com"]
        )
        assert is_valid is True
        assert error == ""

    def test_no_recipients(self) -> None:
        is_valid, error = validate_send_operation([])
        assert is_valid is False
        assert "required" in error.lower()

    def test_invalid_email(self) -> None:
        is_valid, error = validate_send_operation(["invalid-email"])
        assert is_valid is False
        assert "invalid" in error.lower()

    def test_too_many_recipients(self) -> None:
        recipients = [f"user{i}@example.com" for i in range(150)]
        is_valid, error = validate_send_operation(recipients)
        assert is_valid is False
        assert "too many" in error.lower()


class TestValidateBulkOperation:
    """Tests for validate_bulk_operation."""

    def test_valid_count(self) -> None:
        is_valid, error = validate_bulk_operation(50, max_items=100)
        assert is_valid is True
        assert error == ""

    def test_zero_items(self) -> None:
        is_valid, error = validate_bulk_operation(0)
        assert is_valid is False
        assert "no items" in error.lower()

    def test_too_many_items(self) -> None:
        is_valid, error = validate_bulk_operation(150, max_items=100)
        assert is_valid is False
        assert "too many" in error.lower()

    def test_exactly_max_items(self) -> None:
        is_valid, error = validate_bulk_operation(100, max_items=100)
        assert is_valid is True


class TestRateLimiter:
    """Tests for RateLimiter."""

    def test_allows_operations_within_limit(self) -> None:
        limiter = RateLimiter()

        # Should allow 10 operations within 60 seconds
        for i in range(10):
            result = limiter.check("test_op", window_seconds=60, max_operations=10)
            assert result is True, f"Operation {i+1} should be allowed"

    def test_blocks_operations_exceeding_limit(self) -> None:
        limiter = RateLimiter()

        # Fill up the limit
        for i in range(10):
            limiter.check("test_op", window_seconds=60, max_operations=10)

        # 11th operation should be blocked
        result = limiter.check("test_op", window_seconds=60, max_operations=10)
        assert result is False

    def test_allows_operations_after_window_expires(self) -> None:
        limiter = RateLimiter()

        # Use a 1-second window for faster testing
        for i in range(5):
            limiter.check("test_op", window_seconds=1, max_operations=5)

        # Should be at limit
        result = limiter.check("test_op", window_seconds=1, max_operations=5)
        assert result is False

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again
        result = limiter.check("test_op", window_seconds=1, max_operations=5)
        assert result is True

    def test_tracks_operations_separately(self) -> None:
        limiter = RateLimiter()

        # Fill up limit for operation A
        for i in range(10):
            limiter.check("operation_a", window_seconds=60, max_operations=10)

        # Operation A should be blocked
        assert limiter.check("operation_a", window_seconds=60, max_operations=10) is False

        # Operation B should still be allowed (separate tracking)
        assert limiter.check("operation_b", window_seconds=60, max_operations=10) is True


class TestRateLimitCheck:
    """Tests for rate_limit_check function."""

    def test_global_rate_limiter_works(self) -> None:
        # Reset by creating new test scenario
        # Note: This tests the global instance behavior
        for i in range(10):
            result = rate_limit_check("test_global_op", window_seconds=60, max_operations=10)
            if i < 10:
                assert result is True


class TestRequireConfirmation:
    """Tests for require_confirmation."""

    def test_auto_confirm_mode(self) -> None:
        """Test that auto_confirm mode bypasses dialog for testing."""
        result = require_confirmation(
            "test_operation",
            {"key": "value"},
            auto_confirm=True
        )
        assert result is True

    def test_auto_deny_mode(self) -> None:
        """Test that auto_confirm=False denies for testing."""
        result = require_confirmation(
            "test_operation",
            {"key": "value"},
            auto_confirm=False
        )
        assert result is False

    @patch('subprocess.run')
    def test_user_confirms(self, mock_run) -> None:
        """Test that user clicking Confirm returns True."""
        # Simulate user clicking "Confirm"
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "button returned:Confirm"  # text=True returns string

        result = require_confirmation("send_email", {"to": "test@example.com"})
        assert result is True
        assert mock_run.called

    @patch('subprocess.run')
    def test_user_cancels(self, mock_run) -> None:
        """Test that user clicking Cancel returns False."""
        # Simulate user clicking "Cancel" or closing dialog
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""  # text=True returns string

        result = require_confirmation("send_email", {"to": "test@example.com"})
        assert result is False
        assert mock_run.called

    @patch('subprocess.run')
    def test_confirmation_formats_details(self, mock_run) -> None:
        """Test that confirmation details are properly formatted."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "button returned:Confirm"  # text=True returns string

        details = {
            "subject": "Test Email",
            "to": ["user@example.com"],
            "cc": ["other@example.com"]
        }

        require_confirmation("send_email", details)

        # Check that osascript was called
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert "osascript" in call_args
        assert "send_email" in str(call_args)
