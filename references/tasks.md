# Phase 3 — Tasks

**Trigger:** "create tasks", "breakdown", "task list for [feature]"

**Skip when:** scope is Small or Medium — tasks are implicit in Execute.

## Task format

Path: `.specs/features/[feature-slug]/tasks.md`

Each task must be atomic — completable in one sub-agent call with a verifiable outcome.

```markdown
# Tasks: [Feature Name]

## T-001: [Title]
- **REQ**: REQ-001
- **Graph node**: NodeA
- **What**: [precise description of the change]
- **Where**: [file(s) to create or modify]
- **Depends on**: none (or T-00N)
- **[P]**: (mark if parallelizable with another task — same tag = same wave)
- **Done when**: [verifiable criterion — not "it works", but "test X passes" or "endpoint returns Y"]
- **Gate**: `[test command to run]`

## T-002: [Title]
- **REQ**: REQ-002
- **Graph node**: NodeB → NodeC
- **What**: ...
- **Where**: ...
- **Depends on**: T-001
- **Done when**: ...
- **Gate**: `[command]`
```

## Breakdown rules

1. One task = one atomic change + one gate check
2. Tasks touching God Nodes get their own task (no bundling with other changes)
3. Mark `[P]` on tasks with no shared dependencies — they run in parallel via sub-agents
4. If a task has more than 3 files or more than one conceptual concern → split it
5. Maximum ~15 tasks per feature. More than 15 → the feature should be split.

## Safety valve

If listing tasks reveals > 15 items or 3+ levels of dependencies: stop, discuss
with user whether to split the feature, then revise scope before continuing.

## Update STATE.md

```markdown
## Todos
- [ ] T-001: [title] — Execute phase
- [ ] T-002: [title] — Execute phase
- [ ] T-003: [title] — Execute phase [P]
```
