#!/usr/bin/env python
"""Run tests with a one-line summary including coverage."""

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

# Find test summary line
test_summary = None
for line in lines:
    if 'passed' in line or 'failed' in line:
        # Clean up the summary
        test_summary = re.sub(r'\s+', ' ', line.strip())
        test_summary = re.sub(r'in [\d.]+s', '', test_summary).strip()
        break

# Find coverage percentage
coverage = None
for line in lines:
    if 'TOTAL' in line:
        parts = line.split()
        if len(parts) >= 4:
            coverage = parts[-1]
        break

# Create one-line summary
if test_summary and coverage:
    print(f"{test_summary} | Coverage: {coverage}")
elif test_summary:
    print(f"{test_summary} | Coverage: N/A")
else:
    print("No test results found")

sys.exit(result.returncode)