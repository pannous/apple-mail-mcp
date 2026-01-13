"""
Security utilities for Apple Mail MCP.
"""

import logging
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from .exceptions import MailOperationCancelledError
from .utils import escape_applescript_string, validate_email

logger = logging.getLogger(__name__)


class OperationLogger:
    """Log operations for audit trail."""

    def __init__(self) -> None:
        self.operations: list[dict[str, Any]] = []

    def log_operation(
        self, operation: str, parameters: dict[str, Any], result: str = "success"
    ) -> None:
        """
        Log an operation with timestamp.

        Args:
            operation: Operation name
            parameters: Operation parameters
            result: Result status (success/failure/cancelled)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "parameters": parameters,
            "result": result,
        }
        self.operations.append(entry)
        logger.info(f"Operation logged: {operation} - {result}")

    def get_recent_operations(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get recent operations.

        Args:
            limit: Maximum number of operations to return

        Returns:
            List of recent operations
        """
        return self.operations[-limit:]


# Global operation logger instance
operation_logger = OperationLogger()


class RateLimiter:
    """Rate limiter for preventing abuse of operations."""

    def __init__(self) -> None:
        """Initialize rate limiter with empty tracking."""
        self.operation_times: dict[str, list[datetime]] = defaultdict(list)

    def check(
        self, operation: str, window_seconds: int = 60, max_operations: int = 10
    ) -> bool:
        """
        Check if an operation is within rate limits.

        Args:
            operation: Operation name to check
            window_seconds: Time window in seconds
            max_operations: Maximum operations allowed in window

        Returns:
            True if operation is allowed, False if rate limited

        Example:
            >>> limiter = RateLimiter()
            >>> limiter.check("send_email", window_seconds=60, max_operations=10)
            True
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)

        # Remove old operations outside the time window
        self.operation_times[operation] = [
            t for t in self.operation_times[operation] if t > cutoff
        ]

        # Check if limit exceeded
        if len(self.operation_times[operation]) >= max_operations:
            logger.warning(
                f"Rate limit exceeded for {operation}: "
                f"{len(self.operation_times[operation])} operations in {window_seconds}s"
            )
            return False

        # Record this operation
        self.operation_times[operation].append(now)
        return True

    def reset(self, operation: str | None = None) -> None:
        """
        Reset rate limit tracking.

        Args:
            operation: Specific operation to reset, or None to reset all
        """
        if operation:
            self.operation_times[operation] = []
        else:
            self.operation_times.clear()


# Global rate limiter instance
rate_limiter = RateLimiter()


def require_confirmation(
    operation: str, details: dict[str, Any], auto_confirm: bool | None = None
) -> bool:
    """
    Request user confirmation for sensitive operations.

    Shows a macOS dialog box with operation details and waits for user response.

    Args:
        operation: Operation name (e.g., "send_email", "delete_messages")
        details: Operation details to show user (dict will be formatted)
        auto_confirm: Override for testing - True to auto-confirm, False to auto-deny,
                     None (default) to show actual dialog

    Returns:
        True if confirmed, False if denied

    Example:
        >>> require_confirmation("send_email", {"to": "user@example.com"}, auto_confirm=True)
        True
    """
    # Test mode: allow auto-confirm for unit tests
    if auto_confirm is not None:
        logger.info(
            f"Confirmation {'granted' if auto_confirm else 'denied'} (test mode) "
            f"for: {operation}"
        )
        return auto_confirm

    # Format details for display
    details_lines = []
    for key, value in details.items():
        # Handle lists nicely
        if isinstance(value, list):
            value_str = ", ".join(str(v) for v in value[:5])
            if len(value) > 5:
                value_str += f" (and {len(value) - 5} more)"
        else:
            value_str = str(value)
            # Truncate long values
            if len(value_str) > 100:
                value_str = value_str[:100] + "..."

        details_lines.append(f"{key}: {value_str}")

    details_text = "\\n".join(details_lines)
    message = f"Confirm operation: {operation}\\n\\n{details_text}"

    # Escape for AppleScript
    message_safe = escape_applescript_string(message)

    logger.info(f"Requesting user confirmation for: {operation}")
    logger.debug(f"Confirmation details: {details}")

    try:
        # Show macOS confirmation dialog
        result = subprocess.run(
            [
                "osascript",
                "-e",
                f'display dialog "{message_safe}" '
                f'buttons {{"Cancel", "Confirm"}} '
                f'default button "Cancel" '
                f'with title "Apple Mail MCP Confirmation" '
                f'with icon caution',
            ],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        # User clicked "Confirm" if returncode is 0 and output contains "Confirm"
        confirmed = result.returncode == 0 and "Confirm" in result.stdout

        if confirmed:
            logger.info(f"User confirmed operation: {operation}")
        else:
            logger.info(f"User cancelled operation: {operation}")

        return confirmed

    except subprocess.TimeoutExpired:
        logger.warning(f"Confirmation dialog timeout for: {operation}")
        return False
    except Exception as e:
        logger.error(f"Error showing confirmation dialog: {e}")
        # Fail-safe: deny on error
        return False


def validate_send_operation(
    to: list[str], cc: list[str] | None = None, bcc: list[str] | None = None
) -> tuple[bool, str]:
    """
    Validate email sending operation.

    Args:
        to: List of To recipients
        cc: List of CC recipients
        bcc: List of BCC recipients

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for recipients
    if not to:
        return False, "At least one 'to' recipient is required"

    # Validate all email addresses
    all_recipients = to + (cc or []) + (bcc or [])
    invalid_emails = [email for email in all_recipients if not validate_email(email)]

    if invalid_emails:
        return False, f"Invalid email addresses: {', '.join(invalid_emails)}"

    # Check for reasonable limits (prevent spam)
    max_recipients = 100
    if len(all_recipients) > max_recipients:
        return False, f"Too many recipients (max: {max_recipients})"

    return True, ""


def validate_bulk_operation(item_count: int, max_items: int = 100) -> tuple[bool, str]:
    """
    Validate bulk operation limits.

    Args:
        item_count: Number of items in operation
        max_items: Maximum allowed items

    Returns:
        Tuple of (is_valid, error_message)
    """
    if item_count == 0:
        return False, "No items specified for operation"

    if item_count > max_items:
        return False, f"Too many items ({item_count}), maximum is {max_items}"

    return True, ""


def rate_limit_check(
    operation: str, window_seconds: int = 60, max_operations: int = 10
) -> bool:
    """
    Check if operation should be rate limited using the global rate limiter.

    Args:
        operation: Operation name
        window_seconds: Time window in seconds (default: 60)
        max_operations: Maximum operations in window (default: 10)

    Returns:
        True if allowed, False if rate limited

    Example:
        >>> rate_limit_check("send_email", window_seconds=60, max_operations=10)
        True
    """
    return rate_limiter.check(operation, window_seconds, max_operations)


def validate_attachment_type(filename: str, allow_executables: bool = False) -> bool:
    """
    Validate attachment file type for security.

    Args:
        filename: Name of the attachment file
        allow_executables: Whether to allow executable files (default: False)

    Returns:
        True if file type is allowed, False otherwise

    Example:
        >>> validate_attachment_type("document.pdf")
        True
        >>> validate_attachment_type("malware.exe")
        False
    """
    # Dangerous executable extensions (block by default)
    dangerous_extensions = {
        '.exe', '.bat', '.cmd', '.com', '.scr', '.pif',
        '.vbs', '.vbe', '.js', '.jse', '.wsf', '.wsh',
        '.msi', '.msp', '.scf', '.lnk', '.inf', '.reg',
        '.ps1', '.psm1', '.app', '.deb', '.rpm', '.sh',
        '.bash', '.csh', '.ksh', '.zsh', '.command'
    }

    filename_lower = filename.lower()

    # Check for dangerous extensions
    for ext in dangerous_extensions:
        if filename_lower.endswith(ext):
            return allow_executables

    # All other types are allowed
    return True


def validate_attachment_size(size_bytes: int, max_size: int = 25 * 1024 * 1024) -> bool:
    """
    Validate attachment file size.

    Args:
        size_bytes: Size of file in bytes
        max_size: Maximum allowed size in bytes (default: 25MB)

    Returns:
        True if within limit, False otherwise

    Example:
        >>> validate_attachment_size(1024 * 1024)  # 1MB
        True
        >>> validate_attachment_size(30 * 1024 * 1024)  # 30MB
        False
    """
    return size_bytes <= max_size
