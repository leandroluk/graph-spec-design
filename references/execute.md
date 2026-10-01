# Phase 4 — Execute

**Trigger:** "implement", "execute", "build", "do it", "quick fix", "bug fix"

## Quick mode (Small scope)

For ≤3 files with a one-sentence scope:

1. List atomic steps inline (if > 5 steps appear → stop, create `tasks.md`)
2. Implement
3. Run gate check
4. Atomic commit: `git commit -m "type(scope): description [REQ-001]"`
   → post-commit hook runs `nexspec sync` in background
5. Update STATE.md Progress section

## Sub-agent mode (Large/Complex scope)

Each sub-agent receives ONLY:
- The specific task definition from `tasks.md`
- `CONVENTIONS.md` content
- `TESTING.md` content (for gate commands)
- Relevant spec/design context for that task

Sub-agents do NOT receive: full chat history, other tasks, STATE.md.

Sub-agent returns:
```
Status: Complete | Blocked | Partial
Files changed: [list]
Gate check: [command] → [N/N pass / FAIL]
SPEC_DEVIATION: [description or "none"]
Issues: [description or "none"]
```

## Spec Gate (hard rule)

A task is **only complete** when ALL of the following are true:

1. Gate check passes (the command in tasks.md returns success)
2. The following files are updated in the **same atomic commit**:
   - `STATE.md` — Progress entry added
   - `tasks.md` — task marked `[x]` complete
   - `spec.md` — updated if implementation deviated from requirements
3. If `SPEC_DEVIATION` was reported → it must be recorded in STATE.md before commit

## Commit message format

```
type(scope): description [REQ-XXX]

Types: feat | fix | refactor | test | docs | chore
Scope: module or feature slug
```

## Traceability (when `Traceability: on`)

- Put a comment immediately above each function/method/type that implements a
  requirement: `// @spec REQ-001` (use the language's comment syntax; `@adr ADR-001`
  for decisions). It must be the comment directly preceding the symbol, and the ID
  must exist in a spec — nexspec ignores unknown IDs.
- Commit messages carry `[REQ-NNN]` (already in the format below).
- Skip for pure refactors/chores with no requirement.

## Impact check & index update

Before committing, see what the change touches structurally:

```bash
nexspec diff --staged     # symbols changed in the dirty/staged tree + direct dependants
nexspec affected <symbol>  # full transitive dependants for a risky change
```

Dependants outside the task's scope → verify them (or add them to the gate) before
marking the task complete. To understand why a symbol looks the way it does:
`nexspec blame <symbol>` (AST-scoped, cheaper than reading `git log -p`).

If commits were made → the post-commit hook runs `nexspec sync` automatically.
For uncommitted edits (WIP) run `nexspec sync` manually.

## STATE.md update

```markdown
## Recent Progress (Last 10)
- [ISO date] TASK-001 complete. Gate: 42/42 pass. Commit: abc1234. [REQ-001]
- [ISO date] TASK-002 SPEC_DEVIATION: [description]. Gate: 38/42. Commit: def5678.
```
