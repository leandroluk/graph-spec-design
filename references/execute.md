# Phase 4 — Execute

**Trigger:** "implement", "execute", "build", "do it", "quick fix", "bug fix"

## Quick mode (Small scope)

For ≤3 files with a one-sentence scope:

1. List atomic steps inline (if > 5 steps appear → stop, create `tasks.md`)
2. Implement
3. Run gate check
4. Atomic commit: `git commit -m "type(scope): description [REQ-001]"`
   → post-commit hook runs `graphify --update` in background
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

## Graph update after execute

If commits were made → the post-commit hook handles `graphify --update` automatically.

If edits are uncommitted (WIP):
```powershell
$env:GRAPHIFY_OUT = ".specs/graph"
$py = Get-Content .specs/graph/.graphify_python
& $py -m graphify . --update --no-viz
```

## STATE.md update

```markdown
## Progress
- [ISO date] T-001 complete. Gate: 42/42 pass. Commit: abc1234. [REQ-001]
- [ISO date] T-002 SPEC_DEVIATION: [description]. Gate: 38/42. Commit: def5678.
```
