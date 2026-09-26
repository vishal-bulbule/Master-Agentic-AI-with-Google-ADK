#!/usr/bin/env bash
# Author: Vishal Bulbule
# Date: 2026-09-22

# Run an eval set from the shell with `adk eval`.
#
# Reuses the weather_agent and test file from topic 01 instead of copying them.
# `adk eval` (ADK 2.9) exits 0 even when cases fail, so this script checks the
# "Tests failed" summary line itself and exits 1 on any failure. That makes it
# usable as a CI gate.
#
# Run from any directory:
#   bash run_eval.sh

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOPIC_01="$HERE/../01_test_file_anatomy"
OUTPUT="$(mktemp)"
trap 'rm -f "$OUTPUT"' EXIT

adk eval \
    "$TOPIC_01/weather_agent" \
    "$TOPIC_01/tests/weather.test.json" \
    --print_detailed_results | tee "$OUTPUT"

if grep -Eq "Tests failed: [1-9]" "$OUTPUT"; then
    echo "Eval failed." >&2
    exit 1
fi
echo "All eval cases passed."
