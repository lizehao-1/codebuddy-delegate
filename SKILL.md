---
name: codebuddy-delegate
description: Delegate substantial work to the CodeBuddy CLI agent from Codex. Use when the user asks to hand a task to CodeBuddy, or when a task involves heavy multi-step file edits, batch refactors, repeated build/test/debug loops, or long autonomous terminal work that is better executed by a dedicated agent.
---

# Delegate work to CodeBuddy CLI

Let CodeBuddy do the heavy lifting. Codex stays the orchestrator.

## When to use this

Reach for CodeBuddy when the task is:

- Batch edits or refactors across many files
- A loop of build / test / debug that needs many iterations
- Long unattended terminal work
- Explicitly requested by the user ("hand this to CodeBuddy")

**Don't** use it for: quick questions, single-file tweaks, anything you can finish in seconds. Doing it yourself is faster.

## Why headless, not interactive

CodeBuddy has two modes. Pick correctly:

| Mode | Command | Who it's for |
|------|---------|--------------|
| Interactive TUI | `codebuddy` | A human watching the terminal |
| Headless | `codebuddy -p "..."` | A program (you) driving it |

**You must use headless.** The interactive TUI needs a TTY, blocks on keyboard input, and emits cursor-control escape sequences instead of parseable text. Spawned as a subprocess it will simply hang.

Headless does *not* mean single-shot. The multi-turn context you'd get from an interactive session is available via `--session-id` — see the next section.

## First-time login

The CLI needs **one interactive login** before any headless call works. Run `codebuddy` with no arguments and pick a site:

```
Select login method:
› Log in via Chinese Site          # copilot.tencent.com — mainland models
  Log in via International Site    # codebuddy.ai — overseas models
  Log in via Enterprise Domain     # private / self-hosted
  Log in via iOA                   # Tencent internal only
```

The choice is **not cosmetic**: the two sites have separate accounts and expose different model sets. Pick the one whose models you actually need, then finish the browser authorization. Credentials persist — it's a one-time step.

There is **no environment variable to preset the site** — the picker only appears in the interactive flow. For fully unattended setups, skip the picker by supplying credentials directly:

```bash
export CODEBUDDY_BASE_URL="https://<site-endpoint>"
export CODEBUDDY_API_KEY="<key>"
codebuddy -p "<task>" --output-format json
```

Under `-p`, `CODEBUDDY_API_KEY` is always used for model calls.

## Basic invocation

```bash
codebuddy -p "<task>" --output-format json --dangerously-skip-permissions
```

- `-p` / `--print` — run non-interactively and exit
- `--output-format` — `text` (default), `json` (single result), `stream-json` (realtime stream)
- `--dangerously-skip-permissions` — **required** under `-p` for any file write or command execution, otherwise the permission check blocks it. `-y` is the short form.

## Multi-turn: the interactive replacement

Reuse a session id to keep context across calls. This is how you get conversational behavior without a TTY:

```bash
codebuddy --session-id task-001 -p "Step 1: map the module dependencies under src/"
codebuddy --session-id task-001 -p "Step 2: break the circular dependency"
codebuddy --session-id task-001 -p "Step 3: run the tests and confirm"
```

Other session controls:

```bash
codebuddy -c -p "continue where we left off"        # most recent conversation
codebuddy -r <sessionId> -p "..."                   # resume a specific one
```

Session ids accept letters, numbers, hyphens, underscores and colons, and must start with a letter or digit.

## Feeding data in

CodeBuddy follows Unix pipe conventions:

```bash
git diff | codebuddy -p "review these changes for bugs"
cat build.log | codebuddy -p "explain the failure"
find . -name "*.py" | head -20 | xargs cat | codebuddy -p "summarize the common patterns"
```

For streaming input, use `--input-format stream-json`.

## Permissions

`--dangerously-skip-permissions` opens everything. Prefer scoping it down when you can:

```bash
codebuddy -p "<task>" --allowedTools "Read Edit Bash" --add-dir "<workspace>"
codebuddy -p "<task>" --disallowedTools "Bash" --permission-mode acceptEdits
```

`--permission-mode` accepts: `acceptEdits`, `bypassPermissions`, `default`, `plan`, `dontAsk`, `auto`.

Even with `-y`, HIGH/CRITICAL-risk commands may still prompt. For genuinely silent runs inside an isolated sandbox:

```bash
CODEBUDDY_IS_SANDBOX=1 codebuddy -p "<task>" -y
```

That is deliberately an env var rather than a flag, and it is never read from `settings.json` — so a repo can't silently grant itself full access. Treat it as high-risk: containers and throwaway VMs only.

## Choosing a model

```bash
codebuddy --model <model-id> -p "<task>"
codebuddy --model <model-id> --fallback-model <backup-id> -p "<task>"
```

Model ids observed on v2.158.0 (`codebuddy --help`). This list drifts between releases — always trust your local `--help` over this document:

```
default-model, fast-model, balanced-model, primary-model, deep-model,
hy4-preview, hy3,
deepseek-v4.1-flash,
gpt-6-astra, gpt-5.6-sol, gpt-5.6-terra, gpt-5.6-luna, gpt-5.5, gpt-5.4,
gemini-3.5-flash,
glm-5.3-flash, glm-5.3, glm-5.2,
kimi-k3, kimi-k2.6, kimi-k2.8-preview
```

Omit `--model` to use the default for the current tier.

## Structured output

Constrain the shape when you need to parse it:

```bash
codebuddy -p "analyze dependency risk in this project" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"risks":{"type":"array","items":{"type":"string"}}},"required":["risks"]}'
```

## Sandbox: the part that bites

CodeBuddy runs as a **child process of Codex**, so Codex's own sandbox applies to it too:

- Under `workspace-write`, **network access is off by default**. CodeBuddy cannot reach its model API and will fail. Fix in `~/.codex/config.toml`:

  ```toml
  [sandbox_workspace_write]
  network_access = true
  ```

- CodeBuddy can only write where Codex can write — the current workspace plus temp dirs. To let it write elsewhere, widen the workspace or pass `--add-dir` explicitly.
- If the directory has **no Git**, Codex starts in `read-only` and every write will prompt for approval. That's not a bug — Codex is waiting for you to trust the directory. Switch with `/permissions`.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Hangs forever | Ran without `-p` | Add `-p` |
| "permission denied" on file writes | Missing bypass flag | Add `--dangerously-skip-permissions` |
| Network errors from inside the task | Sandbox blocks network | Set `network_access = true` |
| `codebuddy: command not found` | PATH not refreshed | Open a new terminal, or use the absolute path |
| Auth errors | Not logged in | Run `codebuddy` once and complete browser auth |

## Notes

- `-p` runs exit when done; a fresh terminal is needed for PATH changes to take effect.
- Consumption counts against the **CodeBuddy** quota, not Codex's.
- Long tasks: mind the timeout, run in the background when needed.
- Full CLI reference: https://www.codebuddy.cn/docs/cli/reference
