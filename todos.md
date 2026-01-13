# Security Improvements To-Do List

Claude may have its own to-do mechanism, but just to be sure. 

  ☐ CRITICAL: Implement require_confirmation() with actual user dialog in security.py
  ☐ CRITICAL: Implement rate_limit_check() with time-based tracking in security.py
  ☐ HIGH: Add confirmation to reply_to_message() in server.py
  ☐ HIGH: Add confirmation to forward_message() in server.py
  ☐ HIGH: Add validate_message_id() function and use in all message operations
  ☐ HIGH: Fix path traversal check in save_attachments() to validate before resolve()
  ☐ MEDIUM: Improve email validation regex to reject consecutive dots and invalid formats
  ☐ MEDIUM: Enhance escape_applescript_string() to escape newlines, tabs, and control chars
  ☐ MEDIUM: Add sanitize_error_message() to prevent information leakage in error responses
  ☐ MEDIUM: Add prompt injection mitigations with content markers in get_message()
  ☐ LOW: Add security contact email to docs/SECURITY.md
  ☐ LOW: Make OperationLogger persist to file for audit trail
  ☐ LOW: Add MAX_EMAIL_BODY_SIZE limit to send_email()
  ☐ Add security test cases for injection attempts, path traversal, and rate limiting