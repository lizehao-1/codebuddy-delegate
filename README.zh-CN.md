# codebuddy-delegate

> 一个让 Codex 把重活交给 CodeBuddy CLI 执行的 skill。

Codex 擅长判断和编排，CodeBuddy 有自己独立的模型额度、适合埋头干活。这个 skill 把两者接起来：**Codex 决定做什么，CodeBuddy 负责做完**。

任何能执行 shell 命令的 agent 都能用 —— Codex、Claude Code、Cursor，或者一个普通脚本。

---

## 思路

两个 agent，一份分工：

```
┌─────────────────────────┐
│  Codex（编排者）         │  规划、判断、决定下一步
└───────────┬─────────────┘
            │  shell: codebuddy -p "<任务>" --output-format json
┌───────────▼─────────────┐
│  CodeBuddy（执行者）     │  批量改文件、跑构建测试、长任务
└───────────┬─────────────┘
            │  JSON 结果
┌───────────▼─────────────┐
│  回到编排者继续判断       │
└─────────────────────────┘
```

为什么不直接让 Codex 全干？因为长时间自主循环会吃掉编排者的上下文和额度。把这类活外包出去，主会话更干净也更省。

---

## 前置条件

- **Node.js 18+**
- **Codex CLI**（`npm i -g @openai/codex`）—— 或其他能执行 shell 的 agent
- **CodeBuddy 账号**（免费档即可）

---

## 安装

### 1. 安装 CodeBuddy CLI

```bash
npm install -g @tencent-ai/codebuddy-code
```

想装到默认全局目录以外的地方：

```bash
npm install -g @tencent-ai/codebuddy-code --prefix "<你的 npm 全局目录>"
```

装完记得把该目录加进 `PATH`。

### 2. 放入 skill

```bash
git clone https://github.com/<you>/codebuddy-delegate.git
cp -r codebuddy-delegate ~/.codex/skills/codebuddy-delegate
```

目录名必须和 `SKILL.md` 里的 `name` 字段一致。

### 3. 登录一次

```bash
codebuddy
```

会弹出站点选择，按你需要的模型选：

```
Select login method:
› Log in via Chinese Site          # copilot.tencent.com — 国内模型
  Log in via International Site    # codebuddy.ai — 海外模型
  Log in via Enterprise Domain     # 企业私有化部署
  Log in via iOA                   # 腾讯内部员工
```

**这一步别选错。** 两个站的账号体系和额度互相独立，能用的模型也不一样。而且**没有环境变量可以预设站点**，只能在交互界面里选，没法脚本化。

选完走浏览器授权即可，只需一次，凭证会持久化。

### 4. 打开沙箱网络（重要）

CodeBuddy 是 Codex 派生的子进程，**同样受 Codex 沙箱约束**。默认的 `workspace-write` 模式下网络是**关闭**的 —— CodeBuddy 连不上模型 API，任务必然失败。

在 `~/.codex/config.toml` 里加上：

```toml
[sandbox_workspace_write]
network_access = true
```

---

## 用法

直接用自然语言交代即可：

> 交给 CodeBuddy：把 `src/` 下所有 `.js` 改成 TypeScript，确保 `tsc` 不报错。

或者手动验证接线是否正常：

```bash
codebuddy -p "列出当前目录的文件" \
  --output-format json \
  --dangerously-skip-permissions
```

### 多轮任务

headless 不等于只能单次。复用同一个 session id 就能保住上下文：

```bash
codebuddy --session-id task-001 -p "第一步：梳理 src/ 的模块依赖"
codebuddy --session-id task-001 -p "第二步：把循环依赖拆掉"
codebuddy --session-id task-001 -p "第三步：跑测试确认"
```

### 管道喂数据

```bash
git diff | codebuddy -p "审查这些变更，找出潜在 bug"
cat build.log | codebuddy -p "分析报错原因"
```

---

## 目录结构

```
SKILL.md              skill 本体，先看这个
examples/             可直接复制的片段
README.md             英文说明
```

---

## 容易踩的坑

- **`-p` 模式下动文件或跑命令，必须加 `--dangerously-skip-permissions`**，否则权限检查会直接挡下。不想全放开就用 `--allowedTools` / `--add-dir` 收窄。
- **沙箱网络** —— 见上面第 4 步。这是首次运行失败最常见的原因。
- **目录没有 Git？** Codex 会以 `read-only` 起步，每次写操作都要弹审批。用 `/permissions` 切换。
- **额度** —— CodeBuddy 的任务消耗的是 CodeBuddy 额度，不是 Codex 的。
- **模型列表会变。** `SKILL.md` 里的 id 读自 v2.158.0，以本机 `codebuddy --help` 为准。

---

## 许可

MIT
