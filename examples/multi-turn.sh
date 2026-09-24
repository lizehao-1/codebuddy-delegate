#!/usr/bin/env bash
# Multi-turn delegation: reuse one session id so context survives across calls.
# This is the headless equivalent of an interactive conversation.
set -euo pipefail

SID="delegate-$(date +%s)"
echo "session: $SID"

codebuddy --session-id "$SID" \
  -p "Step 1: list every .py file in the current directory. Output filenames only." \
  --output-format json --dangerously-skip-permissions

codebuddy --session-id "$SID" \
  -p "Step 2: of those files, report which one is largest and how many lines it has." \
  --output-format json --dangerously-skip-permissions

codebuddy --session-id "$SID" \
  -p "Step 3: suggest one concrete refactor for that file. Do not modify anything yet." \
  --output-format json --dangerously-skip-permissions
