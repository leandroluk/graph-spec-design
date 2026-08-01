# graph-spec-design

> Spec-driven AI coding workflow + Graphify GraphRAG = persistent knowledge graph as a token-efficient context index.

[![License: CC-BY-4.0](https://img.shields.io/badge/License-CC--BY--4.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-green.svg)](SKILL.md)
[![Works with](https://img.shields.io/badge/works%20with-Claude%20Code%20%7C%20Cursor%20%7C%20Gemini%20CLI%20%7C%20Copilot-orange.svg)](#compatibility)

---

## What is this?

**graph-spec-design** is an AI coding agent skill that fuses two powerful workflows:

| Tool                | What it brings                                                                                              |
| ------------------- | ----------------------------------------------------------------------------------------------------------- |
| **tlc-spec-driven** | Spec-driven pipeline: Specify → Design → Tasks → Execute with persistent `.specs/` memory                   |
| **graphify**        | Knowledge graph (GraphRAG) built from code + specs, queryable at ~1–3k tokens instead of loading full files |

The result: you get structured planning discipline **and** token-cheap context traversal in a single, unified `.specs/` directory.

### The core insight

```
.specs/features/auth/spec.md   ← source of truth (editable, git-tracked)
         ↓  graphify extracts semantically
graph.json: node "REQ-001"     ← connected to JwtModule, AuthService, UserRepository
         ↓  graphify query
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

### Requires graphify

```bash
uv tool install graphifyy   # recommended
# or
pip install graphifyy
```

> **Note:** the PyPI package is `graphifyy` (two y's). The CLI command is `graphify` (one y).

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
└── graph/              # Graphify output — graph.json, GRAPH_REPORT.md, graph.html
```

### Session start (every session)

1. Read `.specs/project/STATE.md` — restores memory from last session
2. Check if `graph.json` is stale → if yes, run `graphify . --update --no-viz`
3. Answer all code questions via `graphify query` / `path` / `explain` — not raw file reads

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
