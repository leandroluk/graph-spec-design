# Phase 1 — Specify

**Trigger:** "specify feature", "define requirements", "new feature", "what should X do"

Before writing any requirement, query the index to understand the existing landscape.

## 1.1 — Index-guided discovery

```
nexspec search "[feature area]" --max-tokens 2000   # related modules, budgeted
nexspec trace "CentralComponent"                    # what it connects to
```

Use the results to:
- Identify components the feature will touch (list them in spec.md)
- Flag high-risk components (wide `trace` fan-out) the feature must interact with — note in spec
- Avoid duplicating existing functionality

## 1.2 — Create spec.md

Read `Traceability:` from `.specs/project/PROJECT.md`. When `on` (default), every
requirement gets a stable `REQ-NNN` ID as a list item (`- REQ-001: ...`) — that exact
shape is what nexspec indexes. IDs may carry a feature prefix (`REQ-CTR-001`) — recommended, since
ids are global across the project. Never renumber existing IDs. When `off`, write plain
bullets.

Path: `.specs/features/[feature-slug]/spec.md`

```markdown
# Spec: [Feature Name]

## Summary
One paragraph describing what this feature does and why.

## Requirements
- REQ-001: [description — user-facing or system behavior]
- REQ-002: [description]
- REQ-003: [description]

## Affected Components (from graph)
- `NodeId_A` — [role in this feature]
- `NodeId_B → NodeId_C` — [call path identified via `nexspec trace`]
- `NodeId_X` ⚠️ high fan-in (N dependants via `nexspec trace`) — changes here have wide impact

## Out of Scope
- [explicit exclusion 1]
- [explicit exclusion 2]

## Open Questions
- [anything that needs user decision before Design can start]
```

## 1.3 — Discuss (Complex scope only)

If the spec has open questions or ambiguous gray areas that the agent cannot resolve
without user input, enter discuss mode:

- List each open question clearly
- Offer 2–3 options per question where possible
- Write user decisions to `.specs/features/[slug]/context.md`
- Do not proceed to Design until all blocking questions are resolved

## 1.4 — Update STATE.md

```markdown
## Decisions
- [ISO date] Feature "[name]" specified. Affects modules: [from nexspec search].
  REQ count: N. Index queried: [yes/no].

## Todos
- [ ] Design phase for [feature name]
```

## 1.5 — After saving spec.md

The post-commit hook will run `nexspec sync` automatically on the next commit,
indexing REQ-001 etc. as graph nodes connected to the code that implements them.
No manual action needed.
