---
name: graph-spec-design
description: "Use when starting a work session, initializing or mapping a project, specifying/designing/implementing features, breaking work into tasks, doing quick fixes, pausing or resuming work, or answering any codebase question (how does X work, what calls Y, trace, dependency, impact) in a project containing .specs/. Triggers: initialize project, map codebase, specify feature, design feature, create tasks, implement, quick fix, bug fix, resume work, pause work, graph query."
license: CC-BY-4.0
metadata:
  author: leandroluk
  version: 2.0.0
---

# Graph-Spec-Design

Spec-driven pipeline (Specify → Design → Tasks → Execute) backed by a Graphify
knowledge graph used as a persistent, token-cheap context index.

**Source of truth:** the `.specs/**/*.md` files. **Index:** the graph. If the graph
is deleted or corrupted, a full rebuild regenerates it from code + specs. Never the
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
triggers ("specify feature", "graphify query", "map codebase", ...) resolve here.
Never load either of them alongside this skill — it doubles context for no gain.

Skill files are en-US; always respond in the user's language.

## Rule #1 — Graph before raw files

At the start of EVERY session, before anything else:

1. Read `.specs/project/STATE.md` (persistent memory).
2. If `.specs/graph/graph.json` exists:
   - Staleness check: any code or `.specs/**/*.md` newer than `graph.json`
     (`(Get-Item .specs/graph/graph.json).LastWriteTime`)? → run
     `graphify . --update --no-viz` first.
   - Answer codebase questions with `graphify query` / `path` / `explain`
     (~1–3k tokens) instead of reading raw source files (20–50k tokens).
   - Full rebuild (`graphify .`) only when files were deleted/moved — detect via
     `git diff --name-status <anchor>..HEAD` containing `D`/`R` entries;
     `--update` over deletes/renames leaves phantom nodes.
3. If it does not exist → run Phase 0 ([references/init.md](references/init.md)).
4. If graphify is not installed → offer to install; on decline/failure, enter
   **degraded mode**: the spec-driven flow continues with direct file reads, no
   phase is ever blocked. Details in [references/init.md](references/init.md).

## The Three Guarantees

What keeps `.specs/` current — each is a hard part of the workflow, not advice:

| Guarantee       | Mechanism                                                                                                                 | Reference                           |
| --------------- | ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| Spec Gate       | A task/commit is only complete when tests pass AND STATE.md/spec.md/tasks.md are updated in the same atomic commit        | [execute.md](references/execute.md) |
| Drift detection | Session start + before Specify/Design: compare git/graph/mtime against specs, report + propose fixes, ask before applying | [drift.md](references/drift.md)     |
| Session sync    | Start: reconcile STATE.md with git log + graph staleness. End: update STATE.md, refresh graph, write handoff              | [session.md](references/session.md) |

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
├── HANDOFF.md          # ephemeral resumption pointer (see session.md) — may be absent
├── project/            # PROJECT.md, ROADMAP.md, STATE.md
├── codebase/           # STACK, ARCHITECTURE, CONVENTIONS, STRUCTURE,
│                       # TESTING, INTEGRATIONS, CONCERNS
├── features/[name]/    # spec.md, context.md?, design.md?, tasks.md?
├── quick/NNN-slug/     # TASK.md, SUMMARY.md
└── graph/              # generated — graph.json, GRAPH_REPORT.md, cache/ ...
```

No `graphify-out/` directory exists. Every graphify invocation (CLI or library)
MUST set the env var `GRAPHIFY_OUT=.specs/graph` first — PowerShell:
`$env:GRAPHIFY_OUT = ".specs/graph"` — so all artifacts land in `.specs/graph/`
directly. Forgetting the var silently recreates `graphify-out/` at the root.

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
| how does X work, what calls Y, trace, impact | `graphify query` / `path` / `explain` directly |

## Context Budget

- Base load per session: STATE.md + (planning sessions only) PROJECT.md. Target <15k tokens.
- On demand: active feature's spec/design/tasks; graph queries replace code reads.
- Never simultaneously: multiple feature specs, multiple architecture docs, raw
  source files when the graph is fresh.

## Honesty Rules

- Never invent a dependency — confirm via `graphify path` or the code itself.
- Never skip Rule #1 (staleness check before any query).
- Never mark a task complete without its gate check passing.
- Record every spec deviation as `SPEC_DEVIATION` in STATE.md.
- Never hand-edit `.specs/graph/*` — generated artifacts.
