# Phase 2 — Design

**Trigger:** "design feature", "architecture", "how to implement [feature]"

**Skip when:** scope is Small or Medium with no architectural decisions — design inline in Execute instead.

## 2.1 — Dependency mapping via graph

Before writing any architecture, trace the actual structural paths:

```
graphify path "EntryPoint" "ExitPoint"
graphify explain "ComponentThatWillChange"
graphify query "What depends on [ComponentName]?"
```

Record the paths found — they become the backbone of the design.

## 2.2 — Risk check via GRAPH_REPORT.md

Read `.specs/graph/GRAPH_REPORT.md` and check:

- **God Nodes** the feature must touch — high change radius, document explicitly
- **Low cohesion communities** — fragile groupings that may produce surprises
- **Surprising connections** — unexpected bridges that could be affected

Add findings to `.specs/codebase/CONCERNS.md` if not already there.

## 2.3 — Create design.md

Path: `.specs/features/[feature-slug]/design.md`

```markdown
# Design: [Feature Name]

## Architecture Overview
[diagram or prose — how the feature fits into the existing system]

## Dependency Paths (from graph)
- REQ-001 → NodeA → NodeB → NodeC (graphify path result)
- REQ-002 → NodeD (new component, no existing path)

## New Components
| Component | Responsibility | Location |
|---|---|---|
| [Name] | [what it does] | [file path] |

## Modified Components
| Component | Change | Risk |
|---|---|---|
| [NodeX] | [what changes] | God Node — high impact |

## Risks
- [NodeX] is a God Node (degree N) — any change propagates widely
- [Community Y] has cohesion score 0.3 — fragile, test thoroughly

## Decision Log
- [decision made during design and why]
```

## 2.4 — Update STATE.md

```markdown
## Decisions
- [ISO date] Design complete for "[feature]". Key risk: [God Node name].

## Todos
- [ ] Tasks phase for [feature name]
```
