# Quick Start Guide - Code Review Agent

Get started with the code review agent in under 5 minutes!

## Step 1: Install Dependencies

```bash
# Install review tools
pip install ruff mypy pytest pytest-cov vulture

# Or install all dev dependencies
pip install -e ".[dev]"
```

## Step 2: Run Your First Review

```bash
# From project root
python3 .github/scripts/code_review_agent.py
```

That's it! The agent will:
- Analyze your code for security issues
- Check MCP protocol compliance
- Run linters and type checkers
- Check test coverage
- Verify documentation
- Generate a comprehensive report

## Step 3: Understand the Output

You'll see a report like this:

```
================================================================================
CODE REVIEW REPORT - Apple Mail MCP Server
================================================================================

Timestamp: 2025-10-09T12:34:56
Overall Score: 85.5/100
Status: PASSED ✓

--------------------------------------------------------------------------------
METRICS
--------------------------------------------------------------------------------
test_coverage: 87.5
mcp_tools_count: 5
total_issues: 8

issues_by_severity:
  medium: 5
  low: 3

--------------------------------------------------------------------------------
ISSUES BY SEVERITY
--------------------------------------------------------------------------------

MEDIUM (5 issues):
----------------------------------------

  [security] AppleScript code may not be properly escaped
  File: src/apple_mail_mcp/mail_connector.py
  Recommendation: Ensure all user inputs are escaped using escape_applescript_string()

  ...
```

## Step 4: Address Issues

Focus on issues in this order:

1. **CRITICAL** - Fix immediately (security vulnerabilities)
2. **HIGH** - Fix before release (major bugs, missing tests)
3. **MEDIUM** - Fix if possible (code quality, minor issues)
4. **LOW** - Nice to have (style, minor improvements)
5. **INFO** - Optional (TODOs, suggestions)

## Step 5: Re-run and Verify

After fixing issues:

```bash
python3 .github/scripts/code_review_agent.py
```

Goal: Achieve score ≥ 70 with no CRITICAL issues.

## Common Commands

```bash
# Basic review
python3 .github/scripts/code_review_agent.py

# Verbose output
python3 .github/scripts/code_review_agent.py --verbose

# Save JSON report
python3 .github/scripts/code_review_agent.py --output report.json

# Strict review (for major releases)
python3 .github/scripts/code_review_agent.py --min-score 85 --min-coverage 90

# Lenient review (for development)
python3 .github/scripts/code_review_agent.py --min-score 50 --min-coverage 60
```

## Integration into Workflow

### Before Every Commit

Add to your git pre-commit hook:

```bash
# .git/hooks/pre-commit
#!/bin/bash
python3 .github/scripts/code_review_agent.py --min-score 60 --no-fail
```

### Before Every Release

Add to your release checklist:

```bash
# Run strict review
python3 .github/scripts/code_review_agent.py --min-score 80 --min-coverage 85

# If passed, proceed with release
git tag v0.2.0
git push --tags
```

### In CI/CD

The agent runs automatically via GitHub Actions on every PR and push to main.

Check `.github/workflows/code-review.yml` for configuration.

## Troubleshooting

### "Module not found" errors

```bash
# Install missing dependencies
pip install ruff mypy pytest pytest-cov vulture
```

### "pytest: command not found"

```bash
# Install pytest
pip install pytest pytest-cov
```

### "Coverage report not found"

```bash
# Run tests first to generate coverage
pytest --cov=apple_mail_mcp --cov-report=json
```

### Score too low

Common quick wins:
1. Add docstrings to functions
2. Fix linting errors: `ruff check --fix src/`
3. Add type hints: `mypy src/` shows what's missing
4. Remove unused imports
5. Add more tests

## What Gets Checked?

✅ **Security**: Injection attacks, credentials, input validation
✅ **MCP Compliance**: Tool definitions, error handling, response formats
✅ **Code Quality**: Linting, type checking, code smells
✅ **AppleScript**: Timeouts, error handling, edge cases
✅ **Tests**: Coverage, completeness, edge cases
✅ **Documentation**: README, docstrings, examples
✅ **Dead Code**: Unused functions, imports, variables
✅ **Performance**: Inefficient patterns, blocking operations

## Score Breakdown

- Start: 100 points
- Critical issue: -20 points
- High issue: -10 points
- Medium issue: -5 points
- Low issue: -2 points
- Info issue: -0.5 points
- Coverage ≥ 90%: +5 points
- Coverage ≥ 80%: +2 points

**Pass criteria**: Score ≥ 70 AND no critical issues

## Tips for High Scores

1. **Write tests**: Every public function should have tests
2. **Add docstrings**: Document all public APIs
3. **Fix security issues**: Always use `escape_applescript_string()`
4. **Handle errors**: Wrap tool functions in try-except
5. **Type everything**: Add type hints to all functions
6. **Clean up**: Remove unused code and TODOs

## Next Steps

- 📖 Read the full [README.md](.github/scripts/README.md)
- 🔧 Customize settings in [review_config.json](.github/scripts/review_config.json)
- 🎯 Run example workflows: `.github/scripts/run_review_examples.sh`
- 🚀 Integrate into CI/CD: `.github/workflows/code-review.yml`

## Getting Help

- Check the [full documentation](README.md)
- Review the [configuration options](review_config.json)
- Look at example issues in the report
- Read recommendations for each issue type

Happy reviewing! 🎉
