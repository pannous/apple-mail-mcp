"""
Utility functions for Apple Mail MCP.
"""

import re
from typing import Any


def escape_applescript_string(s: str) -> str:
    """
    Escape string for safe AppleScript insertion.

    Escapes:
    - Backslashes (\\)
    - Double quotes (")
    - Newlines (\\n, \\r)
    - Tabs (\\t)
    - Null bytes (removed)
    - Control characters (removed)

    Args:
        s: String to escape

    Returns:
        Escaped string safe for AppleScript

    Examples:
        >>> escape_applescript_string('Hello "World"')
        'Hello \\\\"World\\\\"'
        >>> escape_applescript_string('Path\\to\\file')
        'Path\\\\to\\\\file'
        >>> escape_applescript_string('Line1\\nLine2')
        'Line1\\\\nLine2'
    """
    # Remove null bytes first (can't be in AppleScript strings)
    s = s.replace("\x00", "")

    # Remove other control characters (0x01-0x1F except \t, \n, \r)
    # Keep tab (0x09), newline (0x0A), carriage return (0x0D)
    s = ''.join(char for char in s if ord(char) >= 0x20 or char in '\t\n\r')

    # Escape backslashes first (must be first!)
    s = s.replace("\\", "\\\\")

    # Escape quotes
    s = s.replace('"', '\\"')

    # Escape newlines and carriage returns
    s = s.replace("\r", "\\r")
    s = s.replace("\n", "\\n")

    # Escape tabs
    s = s.replace("\t", "\\t")

    return s


def parse_applescript_list(result: str) -> list[str]:
    """
    Parse AppleScript list result into Python list.

    AppleScript returns lists as comma-separated values.

    Args:
        result: AppleScript output

    Returns:
        List of strings
    """
    if not result or result == "":
        return []

    # Handle empty list
    if result.strip() in ["{}", ""]:
        return []

    # Remove braces if present
    result = result.strip()
    if result.startswith("{") and result.endswith("}"):
        result = result[1:-1]

    # Split by comma and clean up
    items = [item.strip() for item in result.split(",") if item.strip()]
    return items


def format_applescript_list(items: list[str]) -> str:
    """
    Format Python list for AppleScript.

    Args:
        items: List of strings

    Returns:
        AppleScript list format

    Examples:
        >>> format_applescript_list(['a', 'b', 'c'])
        '{"a", "b", "c"}'
    """
    escaped_items = [f'"{escape_applescript_string(item)}"' for item in items]
    return "{" + ", ".join(escaped_items) + "}"


def parse_date_filter(date_str: str) -> str:
    """
    Convert human-readable date to AppleScript date expression.

    Args:
        date_str: Date string like "7 days ago", "2024-01-01", "last week"

    Returns:
        AppleScript date expression
    """
    # Handle relative dates
    pattern = r"(\d+)\s+(day|week|month|year)s?\s+ago"
    match = re.match(pattern, date_str.lower())

    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        return f"(current date) - ({amount} * {unit}s)"

    # Handle "last X"
    if date_str.lower().startswith("last "):
        unit = date_str[5:].strip().rstrip("s") + "s"
        return f"(current date) - (1 * {unit})"

    # Handle ISO dates (YYYY-MM-DD)
    if re.match(r"\d{4}-\d{2}-\d{2}", date_str):
        return f'date "{date_str}"'

    # Default: return as is
    return f'date "{date_str}"'


def validate_email(email: str) -> bool:
    """
    Validate email address format per RFC 5321/5322.

    Checks for:
    - Valid length (local ≤64, domain ≤253, total ≤254)
    - No consecutive dots
    - No leading/trailing dots in local part
    - Valid domain format (no leading/trailing dashes)
    - Proper @ separation

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("user..name@example.com")
        False
    """
    # Length check (RFC 5321)
    if not email or len(email) > 254:
        return False

    # Must have exactly one @
    if email.count('@') != 1:
        return False

    # Split into local and domain parts
    try:
        local, domain = email.rsplit('@', 1)
    except ValueError:
        return False

    # Local part: 1-64 chars
    if not local or len(local) > 64:
        return False

    # Domain part: validate format and length
    if not domain or len(domain) > 253:
        return False

    # No consecutive dots anywhere
    if '..' in email:
        return False

    # No leading/trailing dots in local part
    if local.startswith('.') or local.endswith('.'):
        return False

    # Validate local part pattern
    local_pattern = r'^[a-zA-Z0-9._%+-]+$'
    if not re.match(local_pattern, local):
        return False

    # Validate domain part pattern
    # Domain labels can't start/end with dash, must have valid TLD
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
    if not re.match(domain_pattern, domain):
        return False

    return True


def validate_message_id(message_id: str) -> bool:
    """
    Validate Apple Mail message ID format.

    Message IDs should be reasonable length alphanumeric strings,
    potentially with dashes and underscores.

    Args:
        message_id: Message ID to validate

    Returns:
        True if valid format, False otherwise

    Example:
        >>> validate_message_id("12345")
        True
        >>> validate_message_id("ABC-123_def")
        True
        >>> validate_message_id("../../../etc/passwd")
        False
    """
    # Empty or None is invalid
    if not message_id:
        return False

    # Length check (reasonable limit for message IDs)
    if len(message_id) > 255:
        return False

    # Should only contain alphanumeric, dash, and underscore
    # No special chars, spaces, or path traversal attempts
    if not re.match(r'^[A-Za-z0-9_-]+$', message_id):
        return False

    # Extra check: no path traversal patterns
    if '..' in message_id or '/' in message_id or '\\' in message_id:
        return False

    return True


def sanitize_input(value: Any) -> str:
    """
    Sanitize user input for safety.

    Args:
        value: User input value

    Returns:
        Sanitized string
    """
    if value is None:
        return ""

    # Convert to string
    s = str(value)

    # Remove null bytes
    s = s.replace("\x00", "")

    # Limit length
    max_length = 10000
    if len(s) > max_length:
        s = s[:max_length]

    return s


def sanitize_error_message(error: Exception | str) -> str:
    """
    Sanitize error messages to prevent information leakage.

    Removes sensitive information such as:
    - File paths
    - Message IDs
    - Email addresses
    - Other potentially sensitive data

    Args:
        error: Exception object or error string

    Returns:
        Sanitized error message

    Example:
        >>> sanitize_error_message("Error in /path/to/file.py")
        'Error in [PATH]'
        >>> sanitize_error_message("Message ID123456 not found")
        'Message [ID] not found'
    """
    error_str = str(error)

    # Remove file paths (anything starting with / or containing :\)
    # Matches: /path/to/file, C:\path\to\file, ~/path/to/file
    error_str = re.sub(r'[~/]?[\w/-]+/[\w/.-]+', '[PATH]', error_str)
    error_str = re.sub(r'[A-Za-z]:\\[\w\\.-]+', '[PATH]', error_str)

    # Remove message IDs (alphanumeric strings 10+ chars with at least one digit)
    # Must contain at least one digit to avoid matching regular words
    error_str = re.sub(r'\b(?=\w*\d)[A-Za-z0-9]{10,}\b', '[ID]', error_str)

    # Remove email addresses
    error_str = re.sub(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        '[EMAIL]',
        error_str
    )

    return error_str


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations.

    Removes path traversal attempts, dangerous characters, and null bytes.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename

    Example:
        >>> sanitize_filename("../../../etc/passwd")
        'etc_passwd'
        >>> sanitize_filename("my-file_v2.txt")
        'my-file_v2.txt'
    """
    import re
    from pathlib import Path

    # Remove null bytes
    filename = filename.replace("\x00", "")

    # Get basename only (no path components)
    filename = Path(filename).name

    # Replace dangerous characters with underscore
    # Keep: letters, numbers, dash, underscore, period
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

    # Remove leading dots (hidden files)
    filename = filename.lstrip('.')

    # Limit length
    max_length = 255
    if len(filename) > max_length:
        # Preserve extension
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        if ext:
            name = name[:max_length - len(ext) - 1]
            filename = f"{name}.{ext}"
        else:
            filename = filename[:max_length]

    # Ensure not empty
    if not filename:
        filename = "unnamed_file"

    return filename


def sanitize_mailbox_name(name: str) -> str:
    """
    Sanitize mailbox/folder name for safe operations.

    Args:
        name: Mailbox name to sanitize

    Returns:
        Sanitized mailbox name

    Example:
        >>> sanitize_mailbox_name("Valid Name")
        'Valid Name'
        >>> sanitize_mailbox_name("../../../etc")
        ''
    """
    import re

    # Remove null bytes
    name = name.replace("\x00", "")

    # Remove path traversal attempts
    name = name.replace("..", "")
    name = name.replace("/", "")
    name = name.replace("\\", "")

    # Remove dangerous characters but keep spaces, dashes, underscores
    name = re.sub(r'[<>:"|?*]', '', name)

    # Trim whitespace
    name = name.strip()

    return name


def validate_flag_color(color: str) -> bool:
    """
    Validate flag color name.

    Args:
        color: Flag color name

    Returns:
        True if valid color, False otherwise

    Example:
        >>> validate_flag_color("red")
        True
        >>> validate_flag_color("invalid")
        False
    """
    valid_colors = {"none", "orange", "red", "yellow", "blue", "green", "purple", "gray"}
    return color.lower() in valid_colors


def get_flag_index(color: str) -> int:
    """
    Get AppleScript flag index for a color name.

    Args:
        color: Flag color name

    Returns:
        Flag index for AppleScript (-1 to 6)

    Raises:
        ValueError: If color is invalid

    Example:
        >>> get_flag_index("red")
        1
        >>> get_flag_index("none")
        -1
    """
    color_map = {
        "none": -1,
        "orange": 0,
        "red": 1,
        "yellow": 2,
        "blue": 3,
        "green": 4,
        "purple": 5,
        "gray": 6,
    }

    color_lower = color.lower()
    if color_lower not in color_map:
        raise ValueError(
            f"Invalid flag color: {color}. "
            f"Valid colors: {', '.join(color_map.keys())}"
        )

    return color_map[color_lower]
