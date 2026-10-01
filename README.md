# graph-spec-design

> Spec-driven AI coding workflow + NexSpec (Rust) = persistent code+spec graph as a token-efficient context index.

[![License: CC-BY-4.0](https://img.shields.io/badge/License-CC--BY--4.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.1.0-green.svg)](SKILL.md)
[![Works with](https://img.shields.io/badge/works%20with-Claude%20Code%20%7C%20Cursor%20%7C%20Gemini%20CLI%20%7C%20Copilot-orange.svg)](#compatibility)

---

## What is this?

**graph-spec-design** is an AI coding agent skill that fuses two powerful workflows:

| Tool                | What it brings                                                                                              |
| ------------------- | ----------------------------------------------------------------------------------------------------------- |
| **tlc-spec-driven** | Spec-driven pipeline: Specify → Design → Tasks → Execute with persistent `.specs/` memory                   |
| **[nexspec](https://github.com/leandroluk/rust-nexspec)** | Rust context engine: code + specs in one graph, hybrid search, token-budgeted output, native Git. Replaces `graphify` |

The result: you get structured planning discipline **and** token-cheap context traversal in a single, unified `.specs/` directory.

### The core insight

```
.specs/features/auth/spec.md   ← source of truth (editable, git-tracked)
         ↓  nexspec sync (Tree-sitter + Markdown markers)
.specs/.index: node "REQ-001"  ← connected to JwtModule, AuthService, UserRepository
         ↓  nexspec trace REQ-001
"What implements REQ-001?"     → returns exact files and functions (~1k tokens)
```

Instead of reading 20–50k tokens of raw source per question, the agent traverses the graph and returns only the relevant subgraph.

---

## Installation

### Option A — Global (all projects)

```bash
# Copy SKILL.md + references/ to your global skills directory
# Claude Code / Antigravity IDE:
cp -r . ~/.gemini/config/skills/graph-spec-design/

# Cursor / Windsurf (CLAUDE.md / .cursorrules path):
cp -r . ~/.cursor/skills/graph-spec-design/
```

### Option B — Project-scoped

```bash
# Copy into your project's .agents directory
cp -r . your-project/.agents/skills/graph-spec-design/
```

### Option C — Clone directly

```bash
cd your-project/.agents/skills
git clone https://github.com/leandroluk/graph-spec-design
```

### Requires nexspec

```bash
cargo install --git https://github.com/leandroluk/rust-nexspec nexspec
# BM25-only, no ONNX/HNSW vector engine:
cargo install --git https://github.com/leandroluk/rust-nexspec nexspec --no-default-features --features lean
```

A single static binary — no Python, no `uv`, no environment variables. The skill installs it automatically on first use when a Rust toolchain is present, and falls back to degraded mode (direct file reads) otherwise.

> **Migrating from v2 (graphify):** delete `.specs/graph/`; `nexspec init && nexspec sync` builds the new index in `.specs/.index/` (git-ignored). The old `graph-spec-design` Python wrapper was removed.

---

## How it works

### One unified directory

Everything lives in `.specs/`:

```
.specs/
├── project/            # PROJECT.md, ROADMAP.md, STATE.md (persistent memory)
├── codebase/           # STACK, ARCHITECTURE, CONVENTIONS, CONCERNS, TESTING
├── features/[name]/    # spec.md, design.md?, tasks.md?
├── quick/NNN-slug/     # quick fixes
└── .index/             # nexspec index (generated, git-ignored)
```

### Session start (every session)

1. Read `.specs/project/STATE.md` — restores memory from last session
2. Run `nexspec sync` (incremental, idempotent — no staleness heuristics)
3. Answer code questions via `nexspec query` / `explain` / `affected` / `path` / `search --max-tokens N` / `trace` / `report` / `diff --staged` — not raw file reads
4. Record outcomes with `nexspec save-result` / `annotate`; load lessons with `nexspec reflect --max-tokens`; optional opt-in `nexspec enrich` improves prose-question recall

### Three hard guarantees

| Guarantee           | Mechanism                                                           |
| ------------------- | ------------------------------------------------------------------- |
| **Spec Gate**       | Task only complete when tests pass AND specs updated in same commit |
| **Drift Detection** | Staleness check at session start and before Specify/Design          |
| **Session Sync**    | STATE.md reconciled with git log + graph on start and end           |

### Auto-sizing

| Scope            | Specify             | Design          | Tasks              | Execute             |
| ---------------- | ------------------- | --------------- | ------------------ | ------------------- |
| Small (≤3 files) | Quick mode          | —               | —                  | Implement + verify  |
| Medium           | Brief spec          | Inline          | Implicit           | Implement + verify  |
| Large            | Full spec + REQ IDs | Architecture    | Full breakdown     | Sub-agents + verify |
| Complex          | Spec + discuss      | Research + arch | Parallel breakdown | Sub-agents + UAT    |

---

## Compatibility

Works with any AI coding agent that supports markdown skill files:

- **Claude Code** (Anthropic)
- **Antigravity IDE** (Google DeepMind)
- **Cursor**
- **Windsurf**
- **GitHub Copilot** (via AGENTS.md)
- **Gemini CLI**
- Any agent supporting `.agents/skills/` or `CLAUDE.md` conventions

---

## Precedence

This skill **supersedes** `tlc-spec-driven` and `graphify` when present. Do not load both alongside this skill — it doubles context for no gain.

---

## License

[CC-BY-4.0](LICENSE) — free to use, modify, and distribute with attribution.
