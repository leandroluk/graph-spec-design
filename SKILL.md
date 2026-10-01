---
name: graph-spec-design
description: "Use when starting a work session, initializing or mapping a project, specifying/designing/implementing features, breaking work into tasks, doing quick fixes, pausing or resuming work, or answering any codebase question (how does X work, what calls Y, trace, dependency, impact) in a project containing .specs/. Triggers: initialize project, map codebase, specify feature, design feature, create tasks, implement, quick fix, bug fix, resume work, pause work, graph query."
license: CC-BY-4.0
metadata:
  author: leandroluk
  version: 3.1.0
---

# Graph-Spec-Design

Spec-driven pipeline (Specify → Design → Tasks → Execute) backed by a NexSpec
(`nexspec`, Rust) code+spec graph used as a persistent, token-cheap context index.

**Source of truth:** the `.specs/**/*.md` files. **Index:** `.specs/.index/`. If the index
is deleted or corrupted, `nexspec init && nexspec sync` regenerates it from Git + specs. Never the
other way around.

```
┌──────────┐   ┌──────────┐   ┌─────────┐   ┌─────────┐
│ SPECIFY  │ → │  DESIGN  │ → │  TASKS  │ → │ EXECUTE │
└──────────┘   └──────────┘   └─────────┘   └─────────┘
   required      optional*      optional*     required
* auto-sizing decides (table below)
```

## Precedence

In this project this skill **supersedes** `tlc-spec-driven` and `graphify`. Their
triggers ("specify feature", "graph query", "map codebase", ...) resolve here.
Never load either of them alongside this skill — it doubles context for no gain.

Skill files are en-US; always respond in the user's language.

## Rule #1 — Index before raw files

At the start of EVERY session, before anything else:

1. **Check STATE.md size** — before reading:
   - Windows: `(Get-Item .specs/project/STATE.md).Length / 1KB`
   - macOS/Linux: `wc -c < .specs/project/STATE.md` (bytes; 30 KB = 30720 — never `du -k`, which rounds up to disk blocks and over-reports on Windows/Git Bash)
   - If > 30 KB → run compaction first ([references/state_compaction.md](references/state_compaction.md)). Compaction is automatic — do not ask the user.
2. **Read `.specs/project/STATE.md`** (persistent memory — hot state only).
   - Never read `STATE_ARCHIVE.md` unless the user explicitly asks for history.
3. If `.specs/.index/` exists (NexSpec index):
   - **Refresh** with `nexspec sync` (or `nexspec check-update` first: read-only, ~0.1 s;
     exit 0 = fresh, 3 = stale → run `sync`, 4 = no index → Phase 0). Sync is incremental,
     idempotent and cheap (Git tree diff + dirty tree; ~2 s for 1.3k files cold), so there is
     no mtime comparison — just run it. Deletes and renames are handled natively; a full rebuild is never needed
     (if the index is ever corrupted: `nexspec sync --resume`, then `nexspec doctor`; last
     resort delete `.specs/.index/` and run `nexspec init && nexspec sync`).
   - Answer codebase questions with the graph commands instead of reading raw source
     files (20–50k tokens). All accept `--max-tokens`:

     | Question | Command |
     | --- | --- |
     | free-form ("how does X work", "what relates to Y") | `nexspec query "<q>" --max-tokens 2000` |
     | what is X (location, signature, links, authors) | `nexspec explain <X>` |
     | who depends on X (transitively, by file) | `nexspec affected <X> [--depth N]` |
     | how are A and B connected | `nexspec path <A> <B>` |
     | dependency tree of a symbol / `REQ-ID` | `nexspec trace <X>` |
     | ranked lookup, signature-pruned Markdown | `nexspec search "<q>" --max-tokens 2000` |
     | structure: God nodes, communities, cycles, requirement coverage | `nexspec report --max-tokens 3000` |
     | what my uncommitted change touches | `nexspec diff --staged` |
     | history of a symbol | `nexspec blame <symbol>` |

     Use exact identifiers (class/function names, `REQ-…`) — they resolve directly; vague
     prose falls back to BM25 and may return only files (`nexspec enrich`, below, improves
     prose questions). Add `--no-enrich` / `--no-memory` to see the raw ranking.
   - **Work memory** (`.specs/.memory/`, local): after answering a codebase question, record how
     it went so later sessions rank better:
     `nexspec save-result --question "<q>" --outcome useful|dead_end|corrected --nodes <X> [<Y>…]`
     (`corrected` also needs `--correction "<right answer>"`; no secrets in any field).
     At session start `nexspec reflect --max-tokens 800` prints the short lessons summary
     (read-only); a plain `nexspec reflect` rewrites `LESSONS.md` and the ranking nudge.
     With MCP these are the `save_result` and `reflect` tools.
   - **Annotations**: when exploration reaches a durable conclusion about a node or module,
     persist it: `nexspec annotate <X> --note "<≤500 chars>" [--relation depends_on --to <Y>]`
     (or `community:<n> --label "<name>"` to name a community). Annotations are marked
     `fresh`/`stale`/`dangling` as code moves; `nexspec annotate lint` (exit 8 = findings)
     before committing `annotations.jsonl`. MCP: `annotate_node`.
   - **Optional, opt-in** (ask the user first; neither runs by default):
     `nexspec enrich` — LLM summary per file (Gemini; needs `GEMINI_API_KEY`, **sends code
     snippets to an external API**, secrets masked as `[REDACTED]`, `--omit-secrets` keeps
     flagged files home; `--dry-run` shows the plan and cost, `--status` the state). Raises
     recall on prose questions; cached in `.specs/.cache/`.
     `nexspec sync --embed [--similar]` — real embeddings / `SimilarTo` edges (no clear gain measured).
   - **Other views**: `nexspec export --format json|html|tree|wiki` (`--check` exits 7 if the
     committed export is stale); multi-repo: `nexspec global add|list|remove` then
     `--global` on `query/path/explain/affected`.
   - **Exit codes**: 0 ok · 1 error · 2 import cycle (`report --fail-on-cycle`) · 3 stale /
     4 no index (`check-update`) · 5 `doctor` failure · 6 `enrich` partial failure ·
     7 `export --check` stale · 8 `annotate lint` findings.
     **CRITICAL HEURISTIC:** For behavioral, business logic, or detailed implementation questions, use `search` only to locate the 2-3 relevant files, then read them directly. The graph commands are for locating and for structural/topological questions ("what depends on Y?", "where is X defined?", "what implements REQ-001?" when traceability is on).
4. If `.specs/.index/` does not exist → run Phase 0 ([references/init.md](references/init.md)).
5. If `nexspec` is not installed → install it automatically (requires a Rust toolchain):
   ```
   cargo install --git https://github.com/leandroluk/rust-nexspec nexspec
   ```
   Add `--no-default-features --features lean` for a BM25-only build without the ONNX/HNSW vector engine.
   On decline/failure, enter **degraded mode**: the spec-driven flow continues with direct file reads, no phase is ever blocked. Details in [references/init.md](references/init.md).

## The Three Guarantees

What keeps `.specs/` current — each is a hard part of the workflow, not advice:

| Guarantee       | Mechanism                                                                                                                 | Reference                           |
| --------------- | ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| Spec Gate       | A task/commit is only complete when tests pass AND STATE.md/spec.md/tasks.md are updated in the same atomic commit        | [execute.md](references/execute.md) |
| Drift detection | Session start + before Specify/Design: compare git/index against specs, report + propose fixes, ask before applying | [drift.md](references/drift.md)     |
| Session sync    | Start: reconcile STATE.md with git log + `nexspec sync`. End: update STATE.md, refresh index, write handoff              | [session.md](references/session.md) |

## Auto-Sizing

Assess scope before starting any feature:

| Scope       | What                     | Specify             | Design          | Tasks                | Execute             |
| ----------- | ------------------------ | ------------------- | --------------- | -------------------- | ------------------- |
| **Small**   | ≤3 files, one sentence   | Quick mode          | —               | —                    | Implement + verify  |
| **Medium**  | Clear feature, <10 tasks | Brief spec          | Inline          | Implicit             | Implement + verify  |
| **Large**   | Multi-component          | Full spec + REQ IDs | Architecture    | Full breakdown       | Sub-agents + verify |
| **Complex** | Ambiguity, new domain    | Spec + discuss      | Research + arch | Breakdown + parallel | Sub-agents + UAT    |

Safety valve: even when Tasks is skipped, Execute ALWAYS lists atomic steps inline
first. More than 5 steps or complex dependencies → stop, create `tasks.md`.

## Directory Layout

```
.specs/
├── HANDOFF.md                  # ephemeral resumption pointer (see session.md) — may be absent
├── project/
│   ├── PROJECT.md
│   ├── ROADMAP.md
│   ├── STATE.md                # hot state — always < 30 KB (windowed sections)
│   └── STATE_ARCHIVE.md        # historical overflow — never auto-loaded
├── codebase/                   # STACK, ARCHITECTURE, CONVENTIONS, STRUCTURE,
│                               # TESTING, INTEGRATIONS, CONCERNS
├── features/[name]/            # spec.md, context.md?, design.md?, tasks.md?
├── quick/NNN-slug/             # TASK.md, SUMMARY.md
└── .index/                     # generated by nexspec — git-ignored, never read directly
```

The index is created by `nexspec init` in `.specs/.index/` (git-ignored). There is no wrapper, no Python and no environment variable to set; `nexspec --repo <path>` selects another repository.

## Trigger Map

Load ONLY the reference for the active phase:

| Trigger                                      | Reference                                      |
| -------------------------------------------- | ---------------------------------------------- |
| initialize project, map codebase, first run  | [references/init.md](references/init.md)       |
| specify feature, define requirements         | [references/specify.md](references/specify.md) |
| design feature, architecture                 | [references/design.md](references/design.md)   |
| create tasks, breakdown                      | [references/tasks.md](references/tasks.md)     |
| implement, execute, quick fix, bug fix       | [references/execute.md](references/execute.md) |
| resume work, pause work, end session         | [references/session.md](references/session.md) |
| (automatic at session start / pre-Specify)   | [references/drift.md](references/drift.md)     |
| STATE.md > 30 KB (automatic)                 | [references/state_compaction.md](references/state_compaction.md) |
| show state history, archived decisions       | `STATE_ARCHIVE.md` — read on demand only       |
| how does X work, what calls Y, trace, impact | `nexspec query` / `explain` / `affected` / `path` / `trace` / `diff --staged` / `blame` directly |

## Context Budget

- **STATE.md hard limit: 30 KB.** Compact automatically before reading if exceeded.
- Base load per session: STATE.md (≤ 30 KB) + (planning sessions only) PROJECT.md. Target <15k tokens.
- On demand: active feature's spec/design/tasks; index queries replace code reads.
- Never simultaneously: multiple feature specs, multiple architecture docs, raw
  source files when a `nexspec search` answers the question.
- `STATE_ARCHIVE.md` is never preloaded — only on explicit user request.

## Honesty Rules

- Never invent a dependency — confirm via `nexspec trace` or the code itself.
- Never skip Rule #1 (`nexspec sync` before any query).
- Never mark a task complete without its gate check passing.
- Record every spec deviation as `SPEC_DEVIATION` in STATE.md.
- Never hand-edit `.specs/.index/*` — generated artifacts.
