# Phase 2 — Design

**Trigger:** "design feature", "architecture", "how to implement [feature]"

**Skip when:** scope is Small or Medium with no architectural decisions — design inline in Execute instead.

## 2.1 — Dependency mapping via index

Before writing any architecture, trace the actual structural paths:

```
nexspec explain "ComponentThatWillChange"               # location, signature, links, authors
nexspec affected "ComponentThatWillChange" --depth 2    # who depends on it, grouped by file
nexspec path "EntryPoint" "ExitPoint"                   # shortest chain between two nodes
nexspec trace REQ-001                                   # only when Traceability: on
```

Record the paths found — they become the backbone of the design.

## 2.2 — Risk check

```bash
nexspec report --max-tokens 3000
```

Read and check:

- **God Nodes** the feature must touch — high degree/dependants, document explicitly
- **Low-cohesion communities** (< 0.3 = fragile) and **Surprising Connections** → surprises
- **Import Cycles** near the feature
- **High change radius** — `nexspec affected <symbol>` → document explicitly
- **Fragile history** — `nexspec blame <symbol>` (many authors/hunks, wide co-change list) → note the co-changing files
- **Existing concerns** — check `.specs/codebase/CONCERNS.md`

Add findings to `.specs/codebase/CONCERNS.md` if not already there.

## 2.3 — Create design.md

Path: `.specs/features/[feature-slug]/design.md`

```markdown
# Design: [Feature Name]

## Architecture Overview
[diagram or prose — how the feature fits into the existing system]

## Dependency Paths (from nexspec)
- REQ-001 → NodeA → NodeB → NodeC (`nexspec trace` result)
- REQ-002 → NodeD (new component, no existing path)

## New Components
| Component | Responsibility | Location |
|---|---|---|
| [Name] | [what it does] | [file path] |

## Modified Components
| Component | Change | Risk |
|---|---|---|
| [NodeX] | [what changes] | High fan-in — many dependants in `nexspec trace` |

## Risks
- [NodeX] has N dependants (`nexspec trace`) — any change propagates widely
- [Area Y] co-changes with many unrelated files (`nexspec blame`) — fragile, test thoroughly

## Decision Log
- [decision made during design and why]
```

## 2.4 — Update STATE.md

```markdown
## Decisions
- [ISO date] Design complete for "[feature]". Key risk: [highest fan-in component].

## Todos
- [ ] Tasks phase for [feature name]
```
