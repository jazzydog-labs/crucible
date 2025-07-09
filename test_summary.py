#!/usr/bin/env python
"""Run tests with a comprehensive one-line summary including coverage."""

import subprocess
import re
import sys

# Run tests with coverage
result = subprocess.run(
    ['python', '-m', 'pytest', 'tests/', '--cov=src', '--cov-report=term', '-q'],
    capture_output=True,
    text=True
)

# Parse output
output = result.stdout
lines = output.strip().split('\n')

# Initialize stats
passed = 0
failed = 0
skipped = 0
errors = 0
warnings = 0
coverage = "N/A"
missing_lines = 0
total_lines = 0

# Parse test results
for line in lines:
    # Look for test summary line with counts
    if 'passed' in line or 'failed' in line or 'error' in line:
        # Extract numbers from patterns like "70 passed", "2 failed", etc.
        passed_match = re.search(r'(\d+)\s+passed', line)
        failed_match = re.search(r'(\d+)\s+failed', line)
        skipped_match = re.search(r'(\d+)\s+skipped', line)
        error_match = re.search(r'(\d+)\s+error', line)
        warning_match = re.search(r'(\d+)\s+warning', line)
        
        if passed_match:
            passed = int(passed_match.group(1))
        if failed_match:
            failed = int(failed_match.group(1))
        if skipped_match:
            skipped = int(skipped_match.group(1))
        if error_match:
            errors = int(error_match.group(1))
        if warning_match:
            warnings = int(warning_match.group(1))
    
    # Look for coverage info in TOTAL line
    if 'TOTAL' in line:
        parts = line.split()
        if len(parts) >= 4:
            try:
                total_lines = int(parts[1])  # Total statements
                missing_lines = int(parts[2])  # Missing statements
                coverage = parts[-1]  # Coverage percentage
            except (ValueError, IndexError):
                pass

# Build comprehensive summary
total_tests = passed + failed + skipped + errors
status_parts = []

if passed > 0:
    status_parts.append(f"{passed} passed")
if failed > 0:
    status_parts.append(f"{failed} failed")
if skipped > 0:
    status_parts.append(f"{skipped} skipped")
if errors > 0:
    status_parts.append(f"{errors} errors")
if warnings > 0:
    status_parts.append(f"{warnings} warnings")

# Create status string
if status_parts:
    status_str = ", ".join(status_parts)
else:
    status_str = "No tests found"

# Create coverage details
if coverage != "N/A" and total_lines > 0:
    covered_lines = total_lines - missing_lines
    coverage_detail = f"{coverage} ({covered_lines}/{total_lines} lines)"
else:
    coverage_detail = coverage

# Output comprehensive one-line summary
print(f"{status_str} | Coverage: {coverage_detail}")

sys.exit(result.returncode)