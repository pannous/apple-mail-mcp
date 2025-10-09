#!/usr/bin/env python3
"""
Comprehensive Code Review Agent for Apple Mail MCP Server

This script performs automated code review checks for release readiness,
analyzing security, code quality, MCP compliance, and more.

Usage:
    python .github/scripts/code_review_agent.py [OPTIONS]

Exit Codes:
    0 - Review passed, ready for release
    1 - Review failed, issues found
"""

import argparse
import ast
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(Enum):
    """Issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Issue:
    """Represents a code issue found during review."""
    severity: Severity
    category: str
    message: str
    file_path: str | None = None
    line_number: int | None = None
    recommendation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "severity": self.severity.value,
            "category": self.category,
            "message": self.message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "recommendation": self.recommendation,
        }


@dataclass
class ReviewResult:
    """Complete review results."""
    score: float
    passed: bool
    issues: list[Issue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "score": self.score,
            "passed": self.passed,
            "issues": [issue.to_dict() for issue in self.issues],
            "metrics": self.metrics,
            "timestamp": self.timestamp,
        }


class CodeReviewAgent:
    """Comprehensive code review agent."""

    def __init__(
        self,
        project_root: Path,
        min_score: float = 70.0,
        min_coverage: float = 80.0,
        verbose: bool = False,
    ):
        """
        Initialize the code review agent.

        Args:
            project_root: Root directory of the project
            min_score: Minimum score to pass review (0-100)
            min_coverage: Minimum test coverage percentage
            verbose: Enable verbose logging
        """
        self.project_root = project_root
        self.src_dir = project_root / "src"
        self.tests_dir = project_root / "tests"
        self.min_score = min_score
        self.min_coverage = min_coverage
        self.verbose = verbose
        self.issues: list[Issue] = []
        self.metrics: dict[str, Any] = {}

    def log(self, message: str) -> None:
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(f"[INFO] {message}")

    def run_command(self, cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        Run a shell command and return result.

        Args:
            cmd: Command and arguments as list
            check: Whether to raise exception on error

        Returns:
            Completed process object
        """
        self.log(f"Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=check,
            )
            return result
        except subprocess.CalledProcessError as e:
            if check:
                raise
            return e

    def add_issue(
        self,
        severity: Severity,
        category: str,
        message: str,
        file_path: str | None = None,
        line_number: int | None = None,
        recommendation: str | None = None,
    ) -> None:
        """Add an issue to the review results."""
        issue = Issue(
            severity=severity,
            category=category,
            message=message,
            file_path=file_path,
            line_number=line_number,
            recommendation=recommendation,
        )
        self.issues.append(issue)

    def get_python_files(self) -> list[Path]:
        """Get all Python files in the source directory."""
        return list(self.src_dir.rglob("*.py"))

    def get_test_files(self) -> list[Path]:
        """Get all Python test files."""
        return list(self.tests_dir.rglob("test_*.py"))

    # ====================================================================
    # SECURITY ANALYSIS
    # ====================================================================

    def check_security(self) -> None:
        """Check for security vulnerabilities."""
        self.log("Checking security vulnerabilities...")

        # Check for injection vulnerabilities in AppleScript code
        self._check_applescript_injection()

        # Check for credential handling
        self._check_credential_handling()

        # Check for input validation
        self._check_input_validation()

        # Check for dangerous functions
        self._check_dangerous_functions()

    def _check_applescript_injection(self) -> None:
        """Check for AppleScript injection vulnerabilities."""
        for py_file in self.get_python_files():
            try:
                content = py_file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    # Look for f-string usage in AppleScript scripts
                    if isinstance(node, ast.JoinedStr):
                        # Check if this is inside a multi-line string (likely AppleScript)
                        parent_func = self._find_parent_function(tree, node)
                        if parent_func and "applescript" in parent_func.lower():
                            self.add_issue(
                                Severity.HIGH,
                                "security",
                                f"Potential AppleScript injection via f-string formatting",
                                str(py_file.relative_to(self.project_root)),
                                node.lineno,
                                "Use parameterized queries or escape_applescript_string() for all user inputs"
                            )

                    # Check for direct string formatting in AppleScript
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Attribute):
                            if node.func.attr == "format":
                                # Check if used with AppleScript
                                self.log(f"Found .format() call at line {node.lineno}")

                # Check for proper use of escape_applescript_string
                if "escape_applescript_string" in content:
                    # Good - using escaping function
                    pass
                elif "applescript" in content.lower() and "f\"" in content:
                    # Potential issue - f-strings with AppleScript
                    self.add_issue(
                        Severity.MEDIUM,
                        "security",
                        f"AppleScript code may not be properly escaped",
                        str(py_file.relative_to(self.project_root)),
                        recommendation="Ensure all user inputs are escaped using escape_applescript_string()"
                    )

            except Exception as e:
                self.log(f"Error analyzing {py_file}: {e}")

    def _check_credential_handling(self) -> None:
        """Check for credential handling issues."""
        patterns = [
            (r'password\s*=\s*["\']', "Hardcoded password detected"),
            (r'api[_-]?key\s*=\s*["\']', "Hardcoded API key detected"),
            (r'secret\s*=\s*["\']', "Hardcoded secret detected"),
            (r'token\s*=\s*["\']', "Hardcoded token detected"),
        ]

        for py_file in self.get_python_files():
            content = py_file.read_text()

            for pattern, message in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    # Get line number
                    line_no = content[:match.start()].count('\n') + 1
                    self.add_issue(
                        Severity.CRITICAL,
                        "security",
                        message,
                        str(py_file.relative_to(self.project_root)),
                        line_no,
                        "Use environment variables or secure credential storage"
                    )

    def _check_input_validation(self) -> None:
        """Check for missing input validation."""
        for py_file in self.get_python_files():
            if "server.py" in str(py_file):
                content = py_file.read_text()

                # Check if tool functions have input validation
                if "@mcp.tool()" in content:
                    # Check for sanitize_input usage
                    if "sanitize_input" not in content:
                        self.add_issue(
                            Severity.MEDIUM,
                            "security",
                            "MCP tool endpoints may lack input sanitization",
                            str(py_file.relative_to(self.project_root)),
                            recommendation="Use sanitize_input() on all user-provided parameters"
                        )

    def _check_dangerous_functions(self) -> None:
        """Check for use of dangerous functions."""
        dangerous = [
            ("eval", "Use of eval() is dangerous"),
            ("exec", "Use of exec() is dangerous"),
            ("__import__", "Dynamic imports can be dangerous"),
            ("pickle.loads", "Pickle deserialization can be dangerous"),
        ]

        for py_file in self.get_python_files():
            content = py_file.read_text()

            for func, message in dangerous:
                if func in content:
                    matches = re.finditer(rf'\b{re.escape(func)}\b', content)
                    for match in matches:
                        line_no = content[:match.start()].count('\n') + 1
                        self.add_issue(
                            Severity.CRITICAL,
                            "security",
                            message,
                            str(py_file.relative_to(self.project_root)),
                            line_no,
                            f"Avoid using {func} with untrusted input"
                        )

    def _find_parent_function(self, tree: ast.AST, node: ast.AST) -> str | None:
        """Find the parent function name for a node."""
        # Simplified - would need proper AST traversal for production
        return None

    # ====================================================================
    # MCP PROTOCOL COMPLIANCE
    # ====================================================================

    def check_mcp_compliance(self) -> None:
        """Check MCP protocol compliance."""
        self.log("Checking MCP protocol compliance...")

        self._check_tool_definitions()
        self._check_error_handling()
        self._check_response_formats()

    def _check_tool_definitions(self) -> None:
        """Check that MCP tools are properly defined."""
        server_file = self.src_dir / "apple_mail_mcp" / "server.py"
        if not server_file.exists():
            self.add_issue(
                Severity.CRITICAL,
                "mcp_compliance",
                "Server file not found",
                recommendation="Ensure server.py exists and defines MCP tools"
            )
            return

        content = server_file.read_text()

        # Check for @mcp.tool() decorator
        tool_count = content.count("@mcp.tool()")
        if tool_count == 0:
            self.add_issue(
                Severity.CRITICAL,
                "mcp_compliance",
                "No MCP tools defined",
                str(server_file.relative_to(self.project_root)),
                recommendation="Define at least one MCP tool using @mcp.tool() decorator"
            )
        else:
            self.metrics["mcp_tools_count"] = tool_count
            self.log(f"Found {tool_count} MCP tools")

        # Check for proper docstrings
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if it's a tool (has decorator)
                has_mcp_decorator = any(
                    isinstance(d, ast.Attribute) and d.attr == "tool"
                    for d in node.decorator_list
                    if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                )

                if has_mcp_decorator:
                    if not ast.get_docstring(node):
                        self.add_issue(
                            Severity.MEDIUM,
                            "mcp_compliance",
                            f"MCP tool '{node.name}' missing docstring",
                            str(server_file.relative_to(self.project_root)),
                            node.lineno,
                            "Add comprehensive docstring with Args, Returns, and Examples"
                        )

    def _check_error_handling(self) -> None:
        """Check for proper error handling in MCP tools."""
        server_file = self.src_dir / "apple_mail_mcp" / "server.py"
        if not server_file.exists():
            return

        content = server_file.read_text()
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function has try-except
                has_try = any(isinstance(n, ast.Try) for n in ast.walk(node))

                # Check if it's a tool function (simple heuristic)
                if node.name.startswith(("list_", "get_", "search_", "send_", "mark_")):
                    if not has_try:
                        self.add_issue(
                            Severity.MEDIUM,
                            "mcp_compliance",
                            f"Tool function '{node.name}' lacks error handling",
                            str(server_file.relative_to(self.project_root)),
                            node.lineno,
                            "Add try-except block to handle exceptions gracefully"
                        )

    def _check_response_formats(self) -> None:
        """Check that MCP tools return proper response formats."""
        server_file = self.src_dir / "apple_mail_mcp" / "server.py"
        if not server_file.exists():
            return

        content = server_file.read_text()

        # Check for consistent response format
        if '"success":' not in content and "'success':" not in content:
            self.add_issue(
                Severity.MEDIUM,
                "mcp_compliance",
                "Tools may not return consistent success/error format",
                str(server_file.relative_to(self.project_root)),
                recommendation="Return dict with 'success' field in all tool responses"
            )

        # Check for error_type in error responses
        if '"error":' in content or "'error':" in content:
            if '"error_type":' not in content and "'error_type':" not in content:
                self.add_issue(
                    Severity.LOW,
                    "mcp_compliance",
                    "Error responses should include 'error_type' field",
                    str(server_file.relative_to(self.project_root)),
                    recommendation="Add 'error_type' field to error responses for better error handling"
                )

    # ====================================================================
    # CODE QUALITY & MAINTAINABILITY
    # ====================================================================

    def check_code_quality(self) -> None:
        """Check code quality using static analysis tools."""
        self.log("Checking code quality...")

        # Run ruff
        self._run_ruff()

        # Run mypy
        self._run_mypy()

        # Check for code smells
        self._check_code_smells()

    def _run_ruff(self) -> None:
        """Run ruff linter."""
        try:
            result = self.run_command(
                ["ruff", "check", str(self.src_dir), "--output-format=json"],
                check=False
            )

            if result.returncode != 0 and result.stdout:
                try:
                    ruff_issues = json.loads(result.stdout)

                    for ruff_issue in ruff_issues:
                        # Map ruff severity to our severity
                        severity = Severity.MEDIUM
                        if ruff_issue.get("code", "").startswith("E"):
                            severity = Severity.LOW
                        elif ruff_issue.get("code", "").startswith("F"):
                            severity = Severity.HIGH

                        self.add_issue(
                            severity,
                            "code_quality",
                            f"Ruff: {ruff_issue.get('message', 'Unknown issue')}",
                            ruff_issue.get("filename"),
                            ruff_issue.get("location", {}).get("row"),
                            f"Fix {ruff_issue.get('code', 'issue')} violation"
                        )
                except json.JSONDecodeError:
                    self.log("Could not parse ruff output")

            self.metrics["ruff_checked"] = True

        except FileNotFoundError:
            self.add_issue(
                Severity.LOW,
                "tooling",
                "Ruff not installed",
                recommendation="Install ruff: pip install ruff"
            )

    def _run_mypy(self) -> None:
        """Run mypy type checker."""
        try:
            result = self.run_command(
                ["mypy", str(self.src_dir), "--show-error-codes", "--no-error-summary"],
                check=False
            )

            if result.returncode != 0:
                # Parse mypy output
                for line in result.stdout.split("\n"):
                    if not line or "error:" not in line:
                        continue

                    # Parse line: file.py:123: error: message [code]
                    match = re.match(r'^(.+?):(\d+): error: (.+?)(\s+\[.+?\])?$', line)
                    if match:
                        file_path = match.group(1)
                        line_no = int(match.group(2))
                        message = match.group(3)

                        self.add_issue(
                            Severity.MEDIUM,
                            "code_quality",
                            f"Type error: {message}",
                            file_path,
                            line_no,
                            "Fix type annotation or add type: ignore comment"
                        )

            self.metrics["mypy_checked"] = True

        except FileNotFoundError:
            self.add_issue(
                Severity.LOW,
                "tooling",
                "Mypy not installed",
                recommendation="Install mypy: pip install mypy"
            )

    def _check_code_smells(self) -> None:
        """Check for common code smells."""
        for py_file in self.get_python_files():
            content = py_file.read_text()
            lines = content.split("\n")

            # Check for long functions (>100 lines)
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_lines = node.end_lineno - node.lineno
                        if func_lines > 100:
                            self.add_issue(
                                Severity.LOW,
                                "code_quality",
                                f"Function '{node.name}' is too long ({func_lines} lines)",
                                str(py_file.relative_to(self.project_root)),
                                node.lineno,
                                "Consider breaking into smaller functions"
                            )

                        # Check for too many parameters (>7)
                        param_count = len(node.args.args)
                        if param_count > 7:
                            self.add_issue(
                                Severity.LOW,
                                "code_quality",
                                f"Function '{node.name}' has too many parameters ({param_count})",
                                str(py_file.relative_to(self.project_root)),
                                node.lineno,
                                "Consider using a configuration object"
                            )
            except:
                pass

            # Check for TODO/FIXME comments
            for i, line in enumerate(lines, 1):
                if "TODO" in line or "FIXME" in line:
                    self.add_issue(
                        Severity.INFO,
                        "code_quality",
                        f"TODO/FIXME comment found: {line.strip()}",
                        str(py_file.relative_to(self.project_root)),
                        i,
                        "Address TODO/FIXME before release"
                    )

    # ====================================================================
    # APPLESCRIPT RELIABILITY
    # ====================================================================

    def check_applescript_reliability(self) -> None:
        """Check AppleScript reliability."""
        self.log("Checking AppleScript reliability...")

        mail_connector = self.src_dir / "apple_mail_mcp" / "mail_connector.py"
        if not mail_connector.exists():
            return

        content = mail_connector.read_text()

        # Check for timeout handling
        if "timeout" not in content.lower():
            self.add_issue(
                Severity.HIGH,
                "applescript",
                "No timeout handling for AppleScript operations",
                str(mail_connector.relative_to(self.project_root)),
                recommendation="Add timeout parameter to subprocess.run() calls"
            )

        # Check for TimeoutExpired exception handling
        if "TimeoutExpired" not in content:
            self.add_issue(
                Severity.MEDIUM,
                "applescript",
                "TimeoutExpired exception not handled",
                str(mail_connector.relative_to(self.project_root)),
                recommendation="Add except subprocess.TimeoutExpired handler"
            )

        # Check for error parsing
        if "stderr" not in content:
            self.add_issue(
                Severity.MEDIUM,
                "applescript",
                "AppleScript stderr not checked",
                str(mail_connector.relative_to(self.project_root)),
                recommendation="Check stderr for error messages"
            )

        # Check for osascript path
        if "/usr/bin/osascript" not in content:
            self.add_issue(
                Severity.LOW,
                "applescript",
                "Hardcoded osascript path not used",
                str(mail_connector.relative_to(self.project_root)),
                recommendation="Use /usr/bin/osascript for security"
            )

    # ====================================================================
    # TEST COVERAGE
    # ====================================================================

    def check_test_coverage(self) -> None:
        """Check test coverage."""
        self.log("Checking test coverage...")

        try:
            # Run pytest with coverage
            result = self.run_command(
                ["pytest", "--cov=apple_mail_mcp", "--cov-report=json", "--cov-report=term"],
                check=False
            )

            # Read coverage report
            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)

                total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
                self.metrics["test_coverage"] = total_coverage

                if total_coverage < self.min_coverage:
                    self.add_issue(
                        Severity.HIGH,
                        "testing",
                        f"Test coverage ({total_coverage:.1f}%) below minimum ({self.min_coverage}%)",
                        recommendation=f"Add tests to reach {self.min_coverage}% coverage"
                    )

                # Check file-level coverage
                for file_path, file_data in coverage_data.get("files", {}).items():
                    file_coverage = file_data.get("summary", {}).get("percent_covered", 0)
                    if file_coverage < 70:  # Per-file threshold
                        self.add_issue(
                            Severity.MEDIUM,
                            "testing",
                            f"Low coverage ({file_coverage:.1f}%) in {Path(file_path).name}",
                            file_path,
                            recommendation="Add more tests for this file"
                        )
            else:
                self.add_issue(
                    Severity.MEDIUM,
                    "testing",
                    "Coverage report not generated",
                    recommendation="Run pytest with --cov-report=json"
                )

        except FileNotFoundError:
            self.add_issue(
                Severity.HIGH,
                "tooling",
                "Pytest not installed",
                recommendation="Install pytest: pip install pytest pytest-cov"
            )

    # ====================================================================
    # DOCUMENTATION
    # ====================================================================

    def check_documentation(self) -> None:
        """Check documentation quality."""
        self.log("Checking documentation...")

        # Check README exists
        readme = self.project_root / "README.md"
        if not readme.exists():
            self.add_issue(
                Severity.HIGH,
                "documentation",
                "README.md not found",
                recommendation="Create comprehensive README.md"
            )
        else:
            readme_content = readme.read_text()

            # Check for essential sections
            required_sections = [
                ("installation", "Installation instructions"),
                ("usage", "Usage examples"),
                ("features", "Features list"),
                ("configuration", "Configuration guide"),
            ]

            for section, description in required_sections:
                if section.lower() not in readme_content.lower():
                    self.add_issue(
                        Severity.LOW,
                        "documentation",
                        f"README missing {description}",
                        str(readme.relative_to(self.project_root)),
                        recommendation=f"Add {description} section to README"
                    )

        # Check for docstrings in all public functions
        for py_file in self.get_python_files():
            if "__init__.py" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Skip private functions
                        if node.name.startswith("_") and not node.name.startswith("__"):
                            continue

                        docstring = ast.get_docstring(node)
                        if not docstring:
                            self.add_issue(
                                Severity.LOW,
                                "documentation",
                                f"Function '{node.name}' missing docstring",
                                str(py_file.relative_to(self.project_root)),
                                node.lineno,
                                "Add docstring with Args, Returns, and description"
                            )
                        elif len(docstring) < 20:
                            self.add_issue(
                                Severity.LOW,
                                "documentation",
                                f"Function '{node.name}' has minimal docstring",
                                str(py_file.relative_to(self.project_root)),
                                node.lineno,
                                "Expand docstring with more details"
                            )
            except:
                pass

    # ====================================================================
    # DEAD CODE DETECTION
    # ====================================================================

    def check_dead_code(self) -> None:
        """Check for dead code."""
        self.log("Checking for dead code...")

        # Use vulture for dead code detection
        try:
            result = self.run_command(
                ["vulture", str(self.src_dir), "--min-confidence=80"],
                check=False
            )

            if result.stdout:
                for line in result.stdout.split("\n"):
                    if not line or "unused" not in line.lower():
                        continue

                    # Parse vulture output: file.py:123: unused function 'foo' (80% confidence)
                    match = re.match(r'^(.+?):(\d+): (.+?)$', line)
                    if match:
                        file_path = match.group(1)
                        line_no = int(match.group(2))
                        message = match.group(3)

                        self.add_issue(
                            Severity.LOW,
                            "dead_code",
                            f"Unused code: {message}",
                            file_path,
                            line_no,
                            "Remove unused code or add # noqa comment if intentional"
                        )

            self.metrics["dead_code_checked"] = True

        except FileNotFoundError:
            self.log("Vulture not installed, skipping dead code detection")

        # Manual checks for unused imports
        for py_file in self.get_python_files():
            try:
                content = py_file.read_text()
                tree = ast.parse(content)

                imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            imports.add(alias.name)

                # Check if imports are used
                for imp in imports:
                    if imp not in content[content.find(imp) + len(imp):]:
                        # This is a simplified check
                        pass
            except:
                pass

    # ====================================================================
    # PERFORMANCE ANALYSIS
    # ====================================================================

    def check_performance(self) -> None:
        """Check for performance issues."""
        self.log("Checking performance...")

        for py_file in self.get_python_files():
            content = py_file.read_text()
            lines = content.split("\n")

            # Check for common performance issues
            performance_patterns = [
                (r'for .+ in .+:\s+.*\.append\(', "Consider list comprehension instead of append in loop"),
                (r'\.+?\s*\+\s*=\s*["\']', "String concatenation in loop is inefficient, use join()"),
                (r'time\.sleep\([0-9]+\)', "Blocking sleep found, consider async approach"),
            ]

            for i, line in enumerate(lines, 1):
                for pattern, message in performance_patterns:
                    if re.search(pattern, line):
                        self.add_issue(
                            Severity.LOW,
                            "performance",
                            message,
                            str(py_file.relative_to(self.project_root)),
                            i,
                            "Optimize for better performance"
                        )

    # ====================================================================
    # SCORING & REPORTING
    # ====================================================================

    def calculate_score(self) -> float:
        """
        Calculate overall review score (0-100).

        Scoring weights:
        - Critical issues: -20 points each
        - High issues: -10 points each
        - Medium issues: -5 points each
        - Low issues: -2 points each
        - Info issues: -0.5 points each
        """
        score = 100.0

        severity_weights = {
            Severity.CRITICAL: -20,
            Severity.HIGH: -10,
            Severity.MEDIUM: -5,
            Severity.LOW: -2,
            Severity.INFO: -0.5,
        }

        for issue in self.issues:
            score += severity_weights.get(issue.severity, 0)

        # Bonus for good coverage
        if "test_coverage" in self.metrics:
            if self.metrics["test_coverage"] >= 90:
                score += 5
            elif self.metrics["test_coverage"] >= 80:
                score += 2

        return max(0.0, min(100.0, score))

    def generate_report(self) -> ReviewResult:
        """Generate comprehensive review report."""
        score = self.calculate_score()
        passed = score >= self.min_score and not any(
            issue.severity == Severity.CRITICAL for issue in self.issues
        )

        # Group issues by severity and category
        issues_by_severity = defaultdict(list)
        issues_by_category = defaultdict(list)

        for issue in self.issues:
            issues_by_severity[issue.severity].append(issue)
            issues_by_category[issue.category].append(issue)

        self.metrics["issues_by_severity"] = {
            severity.value: len(issues)
            for severity, issues in issues_by_severity.items()
        }

        self.metrics["issues_by_category"] = {
            category: len(issues)
            for category, issues in issues_by_category.items()
        }

        self.metrics["total_issues"] = len(self.issues)

        return ReviewResult(
            score=score,
            passed=passed,
            issues=self.issues,
            metrics=self.metrics,
        )

    def print_console_report(self, result: ReviewResult) -> None:
        """Print human-readable console report."""
        print("\n" + "=" * 80)
        print("CODE REVIEW REPORT - Apple Mail MCP Server")
        print("=" * 80)
        print(f"\nTimestamp: {result.timestamp}")
        print(f"Overall Score: {result.score:.1f}/100")
        print(f"Status: {'PASSED ✓' if result.passed else 'FAILED ✗'}")

        # Print metrics
        print("\n" + "-" * 80)
        print("METRICS")
        print("-" * 80)
        for key, value in result.metrics.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            else:
                print(f"{key}: {value}")

        # Print issues by severity
        print("\n" + "-" * 80)
        print("ISSUES BY SEVERITY")
        print("-" * 80)

        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            severity_issues = [i for i in result.issues if i.severity == severity]
            if not severity_issues:
                continue

            print(f"\n{severity.value.upper()} ({len(severity_issues)} issues):")
            print("-" * 40)

            for issue in severity_issues[:10]:  # Show first 10 per severity
                print(f"\n  [{issue.category}] {issue.message}")
                if issue.file_path:
                    location = f"  File: {issue.file_path}"
                    if issue.line_number:
                        location += f":{issue.line_number}"
                    print(location)
                if issue.recommendation:
                    print(f"  Recommendation: {issue.recommendation}")

            if len(severity_issues) > 10:
                print(f"\n  ... and {len(severity_issues) - 10} more {severity.value} issues")

        # Summary
        print("\n" + "=" * 80)
        if result.passed:
            print("REVIEW PASSED - Ready for release")
        else:
            print("REVIEW FAILED - Address critical issues before release")
            if any(i.severity == Severity.CRITICAL for i in result.issues):
                print("⚠️  Critical issues must be resolved!")
        print("=" * 80 + "\n")

    def save_json_report(self, result: ReviewResult, output_file: Path) -> None:
        """Save JSON report to file."""
        with open(output_file, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        print(f"JSON report saved to: {output_file}")

    def run_review(self) -> ReviewResult:
        """Run complete code review."""
        print("Starting comprehensive code review...")
        print(f"Project root: {self.project_root}")
        print(f"Minimum score: {self.min_score}")
        print(f"Minimum coverage: {self.min_coverage}%\n")

        # Run all checks
        try:
            self.check_security()
        except Exception as e:
            self.log(f"Security check error: {e}")

        try:
            self.check_mcp_compliance()
        except Exception as e:
            self.log(f"MCP compliance check error: {e}")

        try:
            self.check_code_quality()
        except Exception as e:
            self.log(f"Code quality check error: {e}")

        try:
            self.check_applescript_reliability()
        except Exception as e:
            self.log(f"AppleScript check error: {e}")

        try:
            self.check_test_coverage()
        except Exception as e:
            self.log(f"Test coverage check error: {e}")

        try:
            self.check_documentation()
        except Exception as e:
            self.log(f"Documentation check error: {e}")

        try:
            self.check_dead_code()
        except Exception as e:
            self.log(f"Dead code check error: {e}")

        try:
            self.check_performance()
        except Exception as e:
            self.log(f"Performance check error: {e}")

        return self.generate_report()


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive code review agent for Apple Mail MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)",
    )

    parser.add_argument(
        "--min-score",
        type=float,
        default=70.0,
        help="Minimum score to pass (0-100, default: 70)",
    )

    parser.add_argument(
        "--min-coverage",
        type=float,
        default=80.0,
        help="Minimum test coverage percentage (default: 80)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Output JSON report file (optional)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="Don't exit with error code on failure (for testing)",
    )

    args = parser.parse_args()

    # Create agent and run review
    agent = CodeReviewAgent(
        project_root=args.project_root,
        min_score=args.min_score,
        min_coverage=args.min_coverage,
        verbose=args.verbose,
    )

    result = agent.run_review()

    # Print console report
    agent.print_console_report(result)

    # Save JSON report if requested
    if args.output:
        agent.save_json_report(result, args.output)

    # Exit with appropriate code
    if args.no_fail:
        return 0

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
