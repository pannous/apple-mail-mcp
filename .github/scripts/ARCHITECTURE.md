# Code Review Agent - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Code Review Agent System                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   Entry Points   │
├──────────────────┤
│ • CLI            │───┐
│ • GitHub Actions │   │
│ • Git Hooks      │   │
│ • Manual Run     │   │
└──────────────────┘   │
                       │
                       ▼
┌────────────────────────────────────────────────────────┐
│              code_review_agent.py (1113 lines)         │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │           CodeReviewAgent Class                  │ │
│  ├──────────────────────────────────────────────────┤ │
│  │ • Project Configuration                          │ │
│  │ • Issue Tracking                                 │ │
│  │ • Metrics Collection                             │ │
│  │ • Score Calculation                              │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │              Review Modules                      │ │
│  ├──────────────────────────────────────────────────┤ │
│  │ 1. Security Analysis                             │ │
│  │    • AppleScript Injection                       │ │
│  │    • Credential Handling                         │ │
│  │    • Input Validation                            │ │
│  │    • Dangerous Functions                         │ │
│  │                                                   │ │
│  │ 2. MCP Compliance                                │ │
│  │    • Tool Definitions                            │ │
│  │    • Error Handling                              │ │
│  │    • Response Formats                            │ │
│  │                                                   │ │
│  │ 3. Code Quality                                  │ │
│  │    • Ruff Linting                                │ │
│  │    • Mypy Type Checking                          │ │
│  │    • Code Smells                                 │ │
│  │                                                   │ │
│  │ 4. AppleScript Reliability                       │ │
│  │    • Timeout Handling                            │ │
│  │    • Error Parsing                               │ │
│  │    • Edge Cases                                  │ │
│  │                                                   │ │
│  │ 5. Test Coverage                                 │ │
│  │    • Overall Coverage                            │ │
│  │    • File-level Coverage                         │ │
│  │    • pytest-cov Integration                      │ │
│  │                                                   │ │
│  │ 6. Documentation                                 │ │
│  │    • README Completeness                         │ │
│  │    • Docstring Coverage                          │ │
│  │    • API Documentation                           │ │
│  │                                                   │ │
│  │ 7. Dead Code Detection                           │ │
│  │    • Unused Functions                            │ │
│  │    • Unused Imports                              │ │
│  │    • Vulture Integration                         │ │
│  │                                                   │ │
│  │ 8. Performance Analysis                          │ │
│  │    • Inefficient Patterns                        │ │
│  │    • Blocking Operations                         │ │
│  │    • Memory Concerns                             │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │           Reporting & Output                     │ │
│  ├──────────────────────────────────────────────────┤ │
│  │ • Score Calculation                              │ │
│  │ • Issue Aggregation                              │ │
│  │ • Console Formatting                             │ │
│  │ • JSON Serialization                             │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│                   External Tools                      │
├──────────────────────────────────────────────────────┤
│ • ruff        → Linting                              │
│ • mypy        → Type checking                        │
│ • pytest      → Test execution                       │
│ • pytest-cov  → Coverage measurement                 │
│ • vulture     → Dead code detection                  │
└──────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│                      Outputs                          │
├──────────────────────────────────────────────────────┤
│ Console Report  │  JSON Report  │  Exit Code         │
│ (Human-readable)│  (Machine)    │  (0=pass, 1=fail) │
└──────────────────────────────────────────────────────┘
```

## Data Flow

```
┌──────────┐
│  Input   │
│ (Python  │
│  Files)  │
└────┬─────┘
     │
     ├──────────┐
     │          │
     ▼          ▼
┌─────────┐  ┌──────────┐
│ Static  │  │  Test    │
│Analysis │  │ Coverage │
└────┬────┘  └────┬─────┘
     │            │
     ├────────────┤
     │            │
     ▼            ▼
┌──────────────────────┐
│   Issue Collection   │
│                      │
│ {                    │
│   severity: HIGH,    │
│   category: security,│
│   message: ...,      │
│   file: ...,         │
│   line: ...          │
│ }                    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Score Calculation   │
│                      │
│  100 - (issues × w)  │
│      + bonuses       │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Report Generation  │
│                      │
│  ├─ Console          │
│  └─ JSON             │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│   Pass/Fail Decision │
│                      │
│  score >= min        │
│  AND no CRITICAL     │
└──────────────────────┘
```

## Class Hierarchy

```
CodeReviewAgent
├── __init__(project_root, min_score, min_coverage, verbose)
├── Public Methods
│   ├── run_review() → ReviewResult
│   ├── generate_report() → ReviewResult
│   ├── print_console_report(result)
│   └── save_json_report(result, output_file)
│
├── Check Methods
│   ├── check_security()
│   │   ├── _check_applescript_injection()
│   │   ├── _check_credential_handling()
│   │   ├── _check_input_validation()
│   │   └── _check_dangerous_functions()
│   │
│   ├── check_mcp_compliance()
│   │   ├── _check_tool_definitions()
│   │   ├── _check_error_handling()
│   │   └── _check_response_formats()
│   │
│   ├── check_code_quality()
│   │   ├── _run_ruff()
│   │   ├── _run_mypy()
│   │   └── _check_code_smells()
│   │
│   ├── check_applescript_reliability()
│   ├── check_test_coverage()
│   ├── check_documentation()
│   ├── check_dead_code()
│   └── check_performance()
│
├── Utility Methods
│   ├── log(message)
│   ├── run_command(cmd)
│   ├── add_issue(severity, category, message, ...)
│   ├── get_python_files() → list[Path]
│   ├── get_test_files() → list[Path]
│   └── calculate_score() → float
│
└── Internal State
    ├── issues: list[Issue]
    ├── metrics: dict[str, Any]
    ├── project_root: Path
    ├── src_dir: Path
    ├── tests_dir: Path
    ├── min_score: float
    ├── min_coverage: float
    └── verbose: bool
```

## Data Classes

```
Issue
├── severity: Severity (enum)
├── category: str
├── message: str
├── file_path: str | None
├── line_number: int | None
├── recommendation: str | None
└── to_dict() → dict

ReviewResult
├── score: float
├── passed: bool
├── issues: list[Issue]
├── metrics: dict[str, Any]
├── timestamp: str
└── to_dict() → dict

Severity (Enum)
├── CRITICAL = "critical"
├── HIGH = "high"
├── MEDIUM = "medium"
├── LOW = "low"
└── INFO = "info"
```

## File Structure

```
.github/
├── scripts/
│   ├── code_review_agent.py          (1113 lines) - Main script
│   ├── README.md                      ( 393 lines) - Full documentation
│   ├── QUICKSTART.md                  ( 217 lines) - Quick start guide
│   ├── IMPLEMENTATION_SUMMARY.md      ( 300+ lines) - Implementation details
│   ├── ARCHITECTURE.md                (this file) - System architecture
│   ├── review_config.json             (  70 lines) - Configuration
│   └── run_review_examples.sh         ( 120 lines) - Example runner
│
└── workflows/
    └── code-review.yml                ( 147 lines) - GitHub Actions workflow
```

## Configuration Flow

```
┌─────────────────────┐
│  review_config.json │
└──────────┬──────────┘
           │
           ├─ review_settings
           │  ├─ min_score: 70.0
           │  ├─ min_coverage: 80.0
           │  ├─ fail_on_critical: true
           │  └─ fail_on_high: false
           │
           ├─ severity_weights
           │  ├─ critical: -20
           │  ├─ high: -10
           │  ├─ medium: -5
           │  ├─ low: -2
           │  └─ info: -0.5
           │
           ├─ coverage_thresholds
           │  ├─ overall_min: 80.0
           │  ├─ file_min: 70.0
           │  └─ bonus thresholds
           │
           └─ module_settings
              ├─ code_quality {...}
              ├─ security {...}
              ├─ mcp_compliance {...}
              └─ ...
```

## Execution Flow

```
main()
  │
  ├─ Parse arguments
  │  ├─ --project-root
  │  ├─ --min-score
  │  ├─ --min-coverage
  │  ├─ --output
  │  ├─ --verbose
  │  └─ --no-fail
  │
  ├─ Create CodeReviewAgent
  │
  ├─ Run review
  │  │
  │  ├─ check_security()
  │  │  └─ Add issues
  │  │
  │  ├─ check_mcp_compliance()
  │  │  └─ Add issues
  │  │
  │  ├─ check_code_quality()
  │  │  ├─ Run ruff
  │  │  ├─ Run mypy
  │  │  └─ Add issues
  │  │
  │  ├─ check_applescript_reliability()
  │  │  └─ Add issues
  │  │
  │  ├─ check_test_coverage()
  │  │  ├─ Run pytest
  │  │  ├─ Parse coverage
  │  │  └─ Add issues
  │  │
  │  ├─ check_documentation()
  │  │  └─ Add issues
  │  │
  │  ├─ check_dead_code()
  │  │  ├─ Run vulture
  │  │  └─ Add issues
  │  │
  │  └─ check_performance()
  │     └─ Add issues
  │
  ├─ Generate report
  │  ├─ Calculate score
  │  ├─ Determine pass/fail
  │  └─ Create ReviewResult
  │
  ├─ Print console report
  │
  ├─ Save JSON report (if --output)
  │
  └─ Exit with code
     ├─ 0 if passed
     └─ 1 if failed (unless --no-fail)
```

## Integration Points

### GitHub Actions Integration

```
Pull Request / Push
        │
        ▼
┌────────────────────┐
│  GitHub Actions    │
│  Workflow Trigger  │
└────────┬───────────┘
         │
         ├─ Checkout code
         ├─ Setup Python
         ├─ Install dependencies
         │  ├─ pip install -e ".[dev]"
         │  └─ pip install ruff mypy pytest vulture
         │
         ├─ Run tests with coverage
         │  └─ pytest --cov --cov-report=json
         │
         ├─ Run code review agent
         │  └─ python .github/scripts/code_review_agent.py
         │
         ├─ Upload artifacts
         │  └─ code-review-report.json
         │
         ├─ Comment on PR
         │  └─ GitHub API with report summary
         │
         └─ Pass/Fail build
            └─ Based on exit code
```

### Git Hook Integration

```
git commit
    │
    ▼
┌────────────────────┐
│  pre-commit hook   │
└────────┬───────────┘
         │
         ├─ Run quick review
         │  └─ python .github/scripts/code_review_agent.py \
         │        --min-score 60 --no-fail
         │
         ├─ Show summary
         │
         └─ Continue commit
            (hook doesn't block)
```

### Release Process Integration

```
Release Checklist
        │
        ▼
┌────────────────────┐
│  Pre-release       │
│  Review            │
└────────┬───────────┘
         │
         ├─ Run strict review
         │  └─ python .github/scripts/code_review_agent.py \
         │        --min-score 85 --min-coverage 90
         │
         ├─ Review report
         │
         ├─ Fix critical issues
         │
         ├─ Re-run review
         │
         └─ If passed:
            ├─ Tag version
            └─ Push release
```

## Error Handling Strategy

```
run_review()
    │
    ├─ try: check_security()
    │  └─ except: log error, continue
    │
    ├─ try: check_mcp_compliance()
    │  └─ except: log error, continue
    │
    ├─ try: check_code_quality()
    │  └─ except: log error, continue
    │
    └─ ... (all checks protected)

Rationale: Individual check failures don't prevent
           other checks from running. Agent always
           produces a report, even if some checks fail.
```

## Scoring Algorithm

```python
def calculate_score() -> float:
    score = 100.0

    # Deduct for issues
    for issue in issues:
        score += severity_weights[issue.severity]

    # Add bonuses
    if test_coverage >= 90:
        score += 5
    elif test_coverage >= 80:
        score += 2

    # Clamp to [0, 100]
    return max(0.0, min(100.0, score))

def is_passed(score: float) -> bool:
    # Must meet minimum score
    if score < min_score:
        return False

    # Must have no critical issues
    if any(issue.severity == CRITICAL for issue in issues):
        return False

    return True
```

## Extension Points

### Adding New Check Modules

1. Add method to `CodeReviewAgent`:
   ```python
   def check_new_criteria(self) -> None:
       # Implementation
       self.add_issue(...)
   ```

2. Call in `run_review()`:
   ```python
   try:
       self.check_new_criteria()
   except Exception as e:
       self.log(f"New check error: {e}")
   ```

### Adding New Severity Levels

1. Update `Severity` enum
2. Update `severity_weights`
3. Update documentation

### Adding New Output Formats

1. Add method to `CodeReviewAgent`:
   ```python
   def save_html_report(self, result: ReviewResult, output: Path) -> None:
       # Generate HTML report
   ```

2. Add CLI argument:
   ```python
   parser.add_argument("--html-output", type=Path)
   ```

3. Call in `main()`:
   ```python
   if args.html_output:
       agent.save_html_report(result, args.html_output)
   ```

## Performance Characteristics

**Typical Execution Time:**
- Small project (<1000 LOC): 10-30 seconds
- Medium project (1000-5000 LOC): 30-90 seconds
- Large project (>5000 LOC): 90-180 seconds

**Main Performance Factors:**
1. Test execution time (pytest)
2. Coverage calculation (pytest-cov)
3. Type checking (mypy)
4. Linting (ruff)
5. File system I/O

**Optimization Opportunities:**
- Parallel check execution
- Incremental analysis (only changed files)
- Caching of tool results
- Faster AST parsing

## Testing Strategy

The agent itself should be tested with:

1. **Unit Tests:**
   - Issue creation
   - Score calculation
   - Report generation
   - Configuration parsing

2. **Integration Tests:**
   - Full review execution
   - Tool integration (ruff, mypy, etc.)
   - File system operations

3. **End-to-End Tests:**
   - CLI interface
   - CI/CD workflows
   - Output formats

## Maintenance Considerations

**Regular Updates:**
- Tool versions (ruff, mypy, etc.)
- Python version compatibility
- Check logic refinements
- Threshold adjustments

**Monitoring:**
- Average execution time
- Issue detection rates
- False positive rates
- Team feedback

**Documentation:**
- Keep README in sync
- Update examples
- Document new checks
- Maintain changelog

## Summary

The Code Review Agent is a comprehensive, modular system that:

✅ Analyzes 8 critical areas of code quality
✅ Integrates with standard Python tools
✅ Provides flexible configuration
✅ Generates actionable reports
✅ Integrates with CI/CD pipelines
✅ Supports multiple use cases
✅ Maintains extensibility
✅ Follows best practices

**Architecture Benefits:**
- **Modular:** Each check is independent
- **Extensible:** Easy to add new checks
- **Robust:** Errors in one check don't affect others
- **Configurable:** Thresholds and weights adjustable
- **Well-documented:** Multiple documentation levels
- **Production-ready:** Error handling, logging, CI/CD integration
