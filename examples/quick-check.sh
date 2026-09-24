#!/usr/bin/env bash
# Verify the Codex -> CodeBuddy wiring end to end.
set -euo pipefail

echo "[1/3] CLI present?"
codebuddy --version

echo "[2/3] Logged in? (round-trips to the model)"
codebuddy -p "reply with exactly: ready" \
  --output-format json \
  --dangerously-skip-permissions

echo "[3/3] Can it write files?"
codebuddy -p "create a file named .codebuddy-ok containing the text ok" \
  --dangerously-skip-permissions
cat .codebuddy-ok
rm -f .codebuddy-ok

echo "wiring looks good"
