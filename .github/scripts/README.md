# Code Review Agent

Comprehensive automated code review tool for the Apple Mail MCP Server project.

## Overview

This agent performs thorough code analysis before minor version releases (0.x.0 -> 0.y.0), checking:

1. **Security Vulnerabilities**
   - AppleScript injection attacks
   - Credential handling issues
   - Missing input validation
   - Dangerous function usage

2. **MCP Protocol Compliance**
   - Proper tool definitions
   - Error handling patterns
   - Response format consistency

3. **Code Quality & Maintainability**
   - Linting (ruff)
   - Type checking (mypy)
   - Code smells and complexity
   - SOLID principles

4. **AppleScript Reliability**
   - Timeout handling
   - Error parsing
   - Edge case handling

5. **Test Coverage**
   - Unit test completeness
   - Integration test coverage
   - File-level coverage analysis

6. **Documentation Quality**
   - README completeness
   - Docstring coverage
   - API documentation

7. **Dead Code Detection**
   - Unused functions
   - Unused imports
   - Unreachable code

8. **Performance Issues**
   - Inefficient patterns
   - Blocking operations
   - Memory concerns

## Installation

### Required Tools

Install the review dependencies:

```bash
pip install ruff mypy pytest pytest-cov vulture
```

Or install all dev dependencies:

```bash
pip install -e ".[dev]"
```

### Optional Tools

For enhanced dead code detection:

```bash
pip install vulture
```

## Usage

### Basic Usage

Run from project root:

```bash
python .github/scripts/code_review_agent.py
```

### With Options

```bash
# Specify project root
python .github/scripts/code_review_agent.py --project-root /path/to/project

# Set custom thresholds
python .github/scripts/code_review_agent.py --min-score 80 --min-coverage 85

# Enable verbose logging
python .github/scripts/code_review_agent.py --verbose

# Save JSON report
python .github/scripts/code_review_agent.py --output review_report.json

# Don't fail on issues (for testing)
python .github/scripts/code_review_agent.py --no-fail
```

### Command-Line Options

```
--project-root PATH     Project root directory (default: current directory)
--min-score FLOAT       Minimum score to pass (0-100, default: 70)
--min-coverage FLOAT    Minimum test coverage % (default: 80)
--output PATH           Output JSON report file (optional)
--verbose, -v           Enable verbose logging
--no-fail               Don't exit with error code on failure
```

## Exit Codes

- `0` - Review passed, ready for release
- `1` - Review failed, issues found

## Scoring System

The agent calculates a score from 0-100 based on issues found:

- **Critical issues**: -20 points each
- **High issues**: -10 points each
- **Medium issues**: -5 points each
- **Low issues**: -2 points each
- **Info issues**: -0.5 points each

**Bonuses:**
- Test coverage ≥ 90%: +5 points
- Test coverage ≥ 80%: +2 points

**Pass Criteria:**
- Score ≥ minimum score (default: 70)
- No critical issues

## Output Format

### Console Output

Human-readable report with:
- Overall score and pass/fail status
- Metrics summary
- Issues grouped by severity
- Recommendations for each issue

### JSON Output

Machine-readable format with:
- Score and pass/fail status
- Detailed metrics
- Complete issue list with file locations
- Timestamp

Example:

```json
{
  "score": 85.5,
  "passed": true,
  "issues": [
    {
      "severity": "high",
      "category": "security",
      "message": "Potential AppleScript injection",
      "file_path": "src/apple_mail_mcp/mail_connector.py",
      "line_number": 123,
      "recommendation": "Use escape_applescript_string() for all inputs"
    }
  ],
  "metrics": {
    "test_coverage": 87.5,
    "mcp_tools_count": 5,
    "total_issues": 12
  },
  "timestamp": "2025-10-09T12:34:56"
}
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/code-review.yml`:

```yaml
name: Code Review

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  review:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          pip install ruff mypy pytest pytest-cov vulture

      - name: Run code review
        run: python .github/scripts/code_review_agent.py --output review.json

      - name: Upload review report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: code-review-report
          path: review.json
```

### Pre-Release Hook

Create `.github/scripts/pre-release.sh`:

```bash
#!/bin/bash
set -e

echo "Running pre-release code review..."
python .github/scripts/code_review_agent.py \
  --min-score 80 \
  --min-coverage 85 \
  --output pre-release-review.json

echo "Code review passed! Ready for release."
```

## Issue Categories

### Security
- AppleScript injection vulnerabilities
- Hardcoded credentials
- Missing input validation
- Dangerous function usage (eval, exec, etc.)

### MCP Compliance
- Missing or improper tool definitions
- Inconsistent error handling
- Non-standard response formats
- Missing docstrings

### Code Quality
- Linting violations (ruff)
- Type errors (mypy)
- Long functions (>100 lines)
- Too many parameters (>7)
- TODO/FIXME comments

### AppleScript
- Missing timeout handling
- No TimeoutExpired exception handling
- Stderr not checked
- Non-absolute osascript path

### Testing
- Low overall coverage (<80%)
- Low file-level coverage (<70%)
- Missing test files

### Documentation
- Missing README
- Incomplete README sections
- Missing docstrings
- Minimal docstrings

### Dead Code
- Unused functions
- Unused variables
- Unused imports
- Unreachable code

### Performance
- Inefficient loops
- String concatenation in loops
- Blocking sleep operations

## Customization

### Adjusting Thresholds

Modify scoring weights in `code_review_agent.py`:

```python
severity_weights = {
    Severity.CRITICAL: -20,  # Adjust as needed
    Severity.HIGH: -10,
    Severity.MEDIUM: -5,
    Severity.LOW: -2,
    Severity.INFO: -0.5,
}
```

### Adding Custom Checks

Add new check methods to the `CodeReviewAgent` class:

```python
def check_custom_rule(self) -> None:
    """Check for custom rule violations."""
    for py_file in self.get_python_files():
        # Your custom logic
        if violation_found:
            self.add_issue(
                Severity.MEDIUM,
                "custom",
                "Custom rule violation",
                str(py_file.relative_to(self.project_root)),
                line_number,
                "Fix the violation"
            )
```

Then call it in `run_review()`:

```python
def run_review(self) -> ReviewResult:
    # ... existing checks ...
    try:
        self.check_custom_rule()
    except Exception as e:
        self.log(f"Custom check error: {e}")
    # ...
```

## Troubleshooting

### "Tool not found" errors

Install missing tools:

```bash
pip install ruff mypy pytest pytest-cov vulture
```

### Coverage report not generated

Ensure pytest-cov is installed and run tests first:

```bash
pip install pytest-cov
pytest --cov=apple_mail_mcp --cov-report=json
```

### Permission denied

Make the script executable:

```bash
chmod +x .github/scripts/code_review_agent.py
```

### False positives

For intentional issues, add comments:

```python
# noqa: <rule>  # For ruff
# type: ignore  # For mypy
# vulture: ignore  # For vulture
```

## Best Practices

1. **Run before every release**: Make it part of your release checklist
2. **Address critical issues immediately**: Don't ignore security issues
3. **Track trends**: Save JSON reports to monitor code quality over time
4. **Customize for your team**: Adjust thresholds based on project needs
5. **Combine with manual review**: Automated tools complement human review

## Support

For issues or questions about the code review agent:

1. Check the troubleshooting section
2. Review the code for customization options
3. Open an issue in the project repository

## License

This tool is part of the Apple Mail MCP Server project and shares the same license.
