# Phase 2 — Design

**Trigger:** "design feature", "architecture", "how to implement [feature]"

**Skip when:** scope is Small or Medium with no architectural decisions — design inline in Execute instead.

## 2.1 — Dependency mapping via index

Before writing any architecture, trace the actual structural paths:

```
nexspec trace "ComponentThatWillChange"                 # what it depends on / is defined in
nexspec trace REQ-001                                   # only if the specs use REQ markers
nexspec search "[ComponentName] usage" --max-tokens 2000  # budgeted context on callers
```

Record the paths found — they become the backbone of the design.

## 2.2 — Risk check

`nexspec` has no generated report; derive risk from targeted queries:

- **High change radius** — `nexspec trace <symbol>` with many hops/dependants → document explicitly
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
