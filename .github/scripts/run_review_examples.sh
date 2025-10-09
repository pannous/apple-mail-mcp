#!/bin/bash
# Examples of how to run the code review agent

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Code Review Agent - Usage Examples"
echo "===================================="
echo ""

# Example 1: Basic review
echo "Example 1: Basic review (default settings)"
echo "-------------------------------------------"
echo "Command: python code_review_agent.py"
echo ""
read -p "Press Enter to run..."
python "$SCRIPT_DIR/code_review_agent.py" --no-fail
echo ""

# Example 2: Strict review for major release
echo ""
echo "Example 2: Strict review for major release"
echo "-------------------------------------------"
echo "Command: python code_review_agent.py --min-score 85 --min-coverage 90"
echo ""
read -p "Press Enter to run..."
python "$SCRIPT_DIR/code_review_agent.py" --min-score 85 --min-coverage 90 --no-fail
echo ""

# Example 3: Review with JSON output
echo ""
echo "Example 3: Review with JSON output"
echo "-----------------------------------"
echo "Command: python code_review_agent.py --output review.json"
echo ""
read -p "Press Enter to run..."
python "$SCRIPT_DIR/code_review_agent.py" --output "$PROJECT_ROOT/review.json" --no-fail
echo ""
echo "Review saved to: $PROJECT_ROOT/review.json"
echo ""

# Example 4: Verbose review
echo ""
echo "Example 4: Verbose review"
echo "-------------------------"
echo "Command: python code_review_agent.py --verbose"
echo ""
read -p "Press Enter to run..."
python "$SCRIPT_DIR/code_review_agent.py" --verbose --no-fail
echo ""

# Example 5: CI/CD simulation
echo ""
echo "Example 5: CI/CD simulation"
echo "---------------------------"
echo "This simulates how the review runs in CI/CD"
echo ""
read -p "Press Enter to run..."
set +e  # Don't exit on error for this example
python "$SCRIPT_DIR/code_review_agent.py" \
    --project-root "$PROJECT_ROOT" \
    --min-score 70 \
    --min-coverage 80 \
    --output "$PROJECT_ROOT/ci-review.json" \
    --verbose

EXIT_CODE=$?
set -e

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ CI/CD check PASSED - Ready for release"
else
    echo ""
    echo "❌ CI/CD check FAILED - Address issues before release"
fi
echo ""

# Example 6: Quick check (lenient)
echo ""
echo "Example 6: Quick check (lenient settings)"
echo "------------------------------------------"
echo "Command: python code_review_agent.py --min-score 50 --min-coverage 60"
echo "Useful for early development stages"
echo ""
read -p "Press Enter to run..."
python "$SCRIPT_DIR/code_review_agent.py" --min-score 50 --min-coverage 60 --no-fail
echo ""

echo ""
echo "All examples completed!"
echo ""
echo "Next steps:"
echo "1. Review the generated reports"
echo "2. Address any critical or high-priority issues"
echo "3. Re-run the review to verify fixes"
echo "4. Integrate into your CI/CD pipeline"
echo ""
echo "For more information, see: .github/scripts/README.md"
