# Project Instructions for Apple Mail MCP Server

## Core Development Principles

### 1. Test-Driven Development (TDD)
**ALWAYS use TDD throughout the development process.**

- Write tests FIRST (RED phase)
- Implement minimal code to pass (GREEN phase)
- Refactor for quality (REFACTOR phase)
- Never skip writing tests before implementation

### 2. Server and Client Implementation Together
**ALWAYS implement server changes in conjunction with client changes.**

When adding new functionality:
1. Write tests for the connector (mail_connector.py)
2. Implement the connector method
3. Write tests for the server tool (server.py)
4. Implement the FastMCP tool
5. Update documentation

Example flow:
```
1. Write test_get_attachments in test_mail_connector.py
2. Implement get_attachments in mail_connector.py
3. Write test for server tool in test_server.py (or integration test)
4. Implement @mcp.tool() get_attachments in server.py
5. Update TOOLS.md with API documentation
```

**Never implement backend without frontend, or vice versa.**

### 3. Code Review Before Minor Versions
**Use the code review agent prior to minor version changes (0.x.0 -> 0.y.0).**

Before releasing a minor version:
```bash
python .github/scripts/code_review_agent.py --min-score 70 --min-coverage 80
```

The review agent checks:
- Security vulnerabilities
- MCP protocol compliance
- Code quality & maintainability
- AppleScript reliability
- Test coverage
- Documentation quality
- Dead code detection
- Performance issues

### 4. Well-Organized Project Structure
**Keep the project well-organized with clear separation of concerns.**

Structure:
```
src/apple_mail_mcp/
├── mail_connector.py    # AppleScript interface (backend)
├── server.py            # FastMCP tools (frontend/API)
├── security.py          # Security validation
├── utils.py             # Helper functions
└── exceptions.py        # Custom exceptions

tests/
├── unit/                # Unit tests with mocking
└── integration/         # Integration tests with Mail.app
```

### 5. Security First
**Consider security implications for all features.**

For each new feature, assess:
- **Prompt injection risks**: Could malicious email content influence behavior?
- **Data exfiltration**: What data is exposed?
- **Unintended actions**: What could go wrong?
- **Input validation**: Are all inputs sanitized?
- **Path traversal**: Are file paths validated?

Implement mitigations:
- User confirmation for destructive operations
- Rate limiting on sensitive operations
- Comprehensive input validation
- Operation logging for audit trail
- Clear error messages without exposing internals

### 6. Documentation Standards
**Maintain documentation for both humans and LLMs.**

For each new tool/feature:
1. **Docstrings**: Complete with Args, Returns, Raises, Examples
2. **TOOLS.md**: User-facing API documentation with examples
3. **README.md**: Update feature list if user-visible
4. **SECURITY.md**: Document any security implications

### 7. Git Commit Standards
**Use meaningful commits with co-authorship.**

Format:
```
Title: Brief description (max 50 chars)

Detailed explanation of what and why (not how).
Wrap at 72 characters.

- Bullet points for multiple changes
- Reference issues: Fixes #123

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Development Workflow

### Adding a New Feature

1. **Plan** (if complex):
   - Identify use cases
   - Determine security implications
   - Design API

2. **Write Tests** (TDD - RED):
   ```python
   def test_new_feature():
       result = connector.new_feature(params)
       assert result == expected
   ```

3. **Implement Backend** (GREEN):
   ```python
   def new_feature(self, params):
       # Implementation in mail_connector.py
       return result
   ```

4. **Write Server Tests**:
   ```python
   def test_server_tool():
       result = new_feature_tool(params)
       assert result["success"] is True
   ```

5. **Implement Server Tool**:
   ```python
   @mcp.tool()
   def new_feature(params) -> dict[str, Any]:
       """Tool description."""
       result = mail.new_feature(params)
       return {"success": True, "result": result}
   ```

6. **Refactor** (if needed):
   - Improve code quality
   - Extract common patterns
   - Optimize performance

7. **Document**:
   - Update TOOLS.md
   - Add examples
   - Note security considerations

8. **Commit**:
   ```bash
   git add -A
   git commit -m "feat: Add new_feature with full tests

   - Implement backend in mail_connector
   - Add FastMCP tool in server
   - 100% test coverage
   - Security validation included

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

### Before Releasing a Version

1. **Run all tests**:
   ```bash
   pytest tests/unit/ -v --cov
   ```

2. **Run code review**:
   ```bash
   python .github/scripts/code_review_agent.py
   ```

3. **Update version**:
   - `pyproject.toml`
   - `src/apple_mail_mcp/__init__.py`
   - `ROADMAP.md` (mark phase complete)

4. **Update documentation**:
   - `CHANGELOG.md` (create if needed)
   - `README.md` (current version)

5. **Tag and push**:
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0: Phase 2 complete"
   git push origin v0.2.0
   ```

## Technology Stack

- **Language**: Python 3.10+
- **MCP Framework**: FastMCP
- **AppleScript**: Via subprocess + osascript
- **Testing**: pytest, pytest-cov, pytest-asyncio
- **Code Quality**: black, ruff, mypy
- **CI/CD**: GitHub Actions

## Quality Standards

### Test Coverage
- **Minimum overall**: 80%
- **Minimum per file**: 70%
- **All new features**: 100% coverage

### Code Review Score
- **Minor releases (0.x.0)**: Score ≥ 70
- **Major releases (x.0.0)**: Score ≥ 85
- **Zero critical issues**: Always

### Documentation
- All public functions have docstrings
- All tools documented in TOOLS.md
- Security implications documented
- Examples provided

## Common Patterns

### AppleScript Error Handling
```python
try:
    result = self._run_applescript(script)
except MailAccountNotFoundError as e:
    logger.error(f"Account not found: {e}")
    raise
except MailAppleScriptError as e:
    logger.error(f"AppleScript error: {e}")
    raise
```

### Input Validation
```python
from .utils import sanitize_input, escape_applescript_string

user_input = sanitize_input(user_input)
safe_value = escape_applescript_string(user_input)
```

### Server Tool Pattern
```python
@mcp.tool()
def tool_name(required_param: str, optional_param: str | None = None) -> dict[str, Any]:
    """
    Tool description for Claude.

    Args:
        required_param: Description
        optional_param: Description (optional)

    Returns:
        Dictionary with success status and results

    Example:
        >>> tool_name("value")
        {"success": True, "result": ...}
    """
    try:
        # Validate inputs
        if not required_param:
            return {"success": False, "error": "required_param is required"}

        # Call backend
        result = mail.backend_method(required_param, optional_param)

        # Log operation
        operation_logger.log_operation("tool_name", {"param": required_param}, "success")

        return {
            "success": True,
            "result": result
        }

    except MailError as e:
        logger.error(f"Error in tool_name: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_type": "mail_error"
        }
```

## Security Checklist

For each new feature:
- [ ] All inputs validated and sanitized
- [ ] AppleScript strings properly escaped
- [ ] File paths validated (if applicable)
- [ ] Email addresses validated (if applicable)
- [ ] Size limits enforced (if applicable)
- [ ] Rate limiting considered
- [ ] User confirmation for destructive ops
- [ ] Operation logged
- [ ] Error messages don't leak sensitive info
- [ ] Security tests written

## Repository Maintenance

### GitHub
- **Issues**: Track bugs and feature requests
- **Discussions**: Design discussions and Q&A
- **Pull Requests**: Use PR template
- **Code Review**: Required for all PRs

### When to Update ROADMAP.md
- Phase completion
- Priority changes
- New features identified
- Community feedback incorporated

## Questions?

If you're unsure about any aspect:
1. Check existing code for patterns
2. Refer to this document
3. Look at test examples
4. Review CONTRIBUTING.md

## Remember

**The three golden rules:**
1. **Always TDD** - Tests before implementation
2. **Server + Client together** - Backend and frontend in sync
3. **Security first** - Consider implications for every feature
