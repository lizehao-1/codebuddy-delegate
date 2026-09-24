# codebuddy-delegate

> A skill that lets Codex hand heavy work to the CodeBuddy CLI agent.

Codex is a sharp orchestrator. CodeBuddy is a capable executor with its own model quota. This skill wires them together: Codex decides *what* needs doing, CodeBuddy grinds through it.

Works with any agent that can run shell commands — Codex, Claude Code, Cursor, or a plain script.

---

## The idea

Two agents, one division of labour:

```
┌─────────────────────────┐
│  Codex (orchestrator)   │  planning, judgement, next steps
└───────────┬─────────────┘
            │  shell: codebuddy -p "<task>" --output-format json
┌───────────▼─────────────┐
│  CodeBuddy (executor)   │  batch edits, build/test loops, long runs
└───────────┬─────────────┘
            │  JSON result
┌───────────▼─────────────┐
│  back to the orchestrator│
└─────────────────────────┘
```

Why not just let Codex do everything? Because long autonomous loops burn the orchestrator's context and quota. Offloading them to a separate agent keeps the main session clean and cheap.

---

## Requirements

- **Node.js 18+**
- **Codex CLI** (`npm i -g @openai/codex`) — or any shell-capable agent
- **A CodeBuddy account** (free tier works)

---

## Install

### 1. Install the CodeBuddy CLI

```bash
npm install -g @tencent-ai/codebuddy-code
```

To install somewhere other than the default global prefix:

```bash
npm install -g @tencent-ai/codebuddy-code --prefix "<your-npm-global-dir>"
```

Then make sure that directory is on your `PATH`.

### 2. Drop in the skill

```bash
git clone https://github.com/<you>/codebuddy-delegate.git
cp -r codebuddy-delegate ~/.codex/skills/codebuddy-delegate
```

The directory name must match the `name` field in `SKILL.md`.

### 3. Log in once

```bash
codebuddy
```

Complete the browser authorization. One time only.

### 4. Open the sandbox network (important)

CodeBuddy runs as a child process of Codex, so **Codex's sandbox applies to it**. Under the default `workspace-write` mode, network access is **off** — CodeBuddy cannot reach its model API and every task will fail.

Add to `~/.codex/config.toml`:

```toml
[sandbox_workspace_write]
network_access = true
```

---

## Usage

Just ask, in plain language:

> Hand this to CodeBuddy: convert every `.js` under `src/` to TypeScript and make `tsc` pass.

Or call it directly to verify the wiring:

```bash
codebuddy -p "list the files in the current directory" \
  --output-format json \
  --dangerously-skip-permissions
```

### Multi-turn work

Headless does not mean single-shot. Reuse a session id to keep context:

```bash
codebuddy --session-id task-001 -p "Step 1: map module dependencies under src/"
codebuddy --session-id task-001 -p "Step 2: break the circular dependency"
codebuddy --session-id task-001 -p "Step 3: run the tests"
```

### Pipe data in

```bash
git diff | codebuddy -p "review these changes for bugs"
cat build.log | codebuddy -p "explain the failure"
```

---

## What's in here

```
SKILL.md              the skill itself — read this first
examples/             copy-pasteable snippets
README.zh-CN.md       中文说明
```

---

## Gotchas

- **`-p` needs `--dangerously-skip-permissions`** for anything that writes files or runs commands. Without it the permission check blocks the call. Scope it down with `--allowedTools` / `--add-dir` if you'd rather not open everything.
- **Sandbox network** — see step 4 above. This is the single most common reason a first run fails.
- **No Git in the directory?** Codex starts in `read-only` and prompts on every write. Switch with `/permissions`.
- **Quota** — CodeBuddy tasks consume your CodeBuddy quota, not Codex's.
- **Model list drifts.** The ids documented in `SKILL.md` were read off v2.158.0. Always trust `codebuddy --help` locally.

---

## License

MIT
