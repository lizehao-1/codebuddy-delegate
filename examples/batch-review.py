#!/usr/bin/env python3
"""Hand a batch of files to CodeBuddy one at a time and collect the verdicts.

Usage:
    python batch-review.py src/*.py
    python batch-review.py .          # walks the directory
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

TIMEOUT = 300


def ask(prompt: str, cwd: str | None = None) -> dict:
    """Run CodeBuddy headless and return the parsed JSON result."""
    proc = subprocess.run(
        [
            "codebuddy",
            "-p", prompt,
            "--output-format", "json",
            "--dangerously-skip-permissions",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=cwd,
        timeout=TIMEOUT,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"exit code {proc.returncode}")
    return json.loads(proc.stdout)


def targets(args: list[str]) -> list[pathlib.Path]:
    found: list[pathlib.Path] = []
    for raw in args or ["."]:
        p = pathlib.Path(raw)
        if p.is_dir():
            found.extend(sorted(p.rglob("*.py")))
        elif p.is_file():
            found.append(p)
    return found


def main() -> int:
    files = targets(sys.argv[1:])
    if not files:
        print("nothing to review")
        return 1

    print(f"reviewing {len(files)} file(s)\n")
    for path in files:
        try:
            result = ask(
                f"Review {path.name}. In one sentence, name its single biggest problem.",
                cwd=str(path.parent),
            )
            verdict = result.get("response", result)
        except Exception as exc:  # noqa: BLE001
            verdict = f"FAILED: {exc}"
        print(f"{path.name}\n  {verdict}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
