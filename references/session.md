# Session Management (Resume / Pause / Handoff)

## Session Start — Resume

On every session start, in this exact order:

1. **Run drift detection** ([drift.md](drift.md)) — before loading any context.
2. **Read `.specs/project/STATE.md`** — loads persistent memory:
   - Active feature and current phase
   - Open decisions and blockers
   - Next planned step
3. **Read `.specs/HANDOFF.md`** if it exists — ephemeral resumption pointer written
   at session end. Delete after reading (it's one-shot).
4. **Load feature context on demand** — only read the active feature's spec/design/tasks
   when actually starting work on it. Do not preload all specs.

### Resume prompt to user

After loading STATE.md and HANDOFF.md, summarize in 3–5 lines:

```
Resuming: [feature name], phase [Specify/Design/Tasks/Execute]
Last completed: [last entry in STATE.md Progress]
Next step: [from HANDOFF.md or STATE.md Todos]
Graph: [fresh / stale — N files newer]
Proceed? [or describe what you want to work on]
```

## Session End — Pause / Handoff

Run when the user says "pause work", "end session", "handoff", or when context
is approaching the token budget limit.

### 1. Update STATE.md

Append to the relevant sections using the windowed structure:

- `Recent Progress (Last 10)` — prepend new entry; if count > 10, move oldest to `STATE_ARCHIVE.md`
- `Recent Decisions (Last 15)` — prepend new entry; if count > 15, move oldest to `STATE_ARCHIVE.md`
- `Lessons Learned (Last 5)` — prepend new entry; if count > 5, move oldest to `STATE_ARCHIVE.md`
- `Todos` — append new `[ ]` items; mark finished items `[x]`
- `Active Blockers` — update list
- `Current Work` — rewrite with current status

```markdown
## Recent Progress (Last 10)
- [ISO date] [feature] T-00N complete. Gate: N/N pass. Commit: [sha].

## Recent Decisions (Last 15)
- [ISO date] [decision made this session]

## Active Blockers
- [ISO date] [blocker encountered — or "none"]

## Todos
- [ ] [next atomic step for next session]
```

### 2. Check STATE.md size — compact if needed

After writing STATE.md, check if it exceeds 30 KB:

**PowerShell (Windows):**
```powershell
$sizeKB = [math]::Round((Get-Item .specs/project/STATE.md).Length / 1KB, 1)
if ($sizeKB -gt 30) { Write-Host "STATE.md at $sizeKB KB — running compaction..." }
```

**bash (macOS/Linux):**
```bash
size_kb=$(du -k .specs/project/STATE.md | cut -f1)
if [ "$size_kb" -gt 30 ]; then echo "STATE.md at ${size_kb}KB — running compaction..."; fi
```

If exceeded → run [state_compaction.md](state_compaction.md) protocol before step 3.

### 3. Write HANDOFF.md (ephemeral)

```markdown
# Handoff — [ISO date]

## Active Feature
[feature name] — [spec.md path]

## Current Phase
[Specify / Design / Tasks / Execute]

## Last Action
[what was just done]

## Next Step
[exact first thing to do when resuming — be specific enough that no STATE.md read is needed to know where to start]

## Graph Status
[fresh / stale — last updated: ISO date]

## Open Questions
[anything unresolved that needs user input]
```

### 3. Update the graph

If commits were made, the post-commit hook already handled it. For uncommitted edits (WIP):

**PowerShell (Windows):**
```powershell
$dirty = git status --porcelain 2>$null
if ($dirty) {
    $env:GRAPHIFY_OUT = ".specs/graph"
    $py = Get-Content .specs/graph/.graphify_python -ErrorAction SilentlyContinue
    if ($py) { & $py -m graphify . --update --no-viz }
}
```

**bash (macOS/Linux):**
```bash
dirty=$(git status --porcelain 2>/dev/null)
if [ -n "$dirty" ]; then
    export GRAPHIFY_OUT=".specs/graph"
    py=$(cat .specs/graph/.graphify_python 2>/dev/null || echo "python")
    "$py" -m graphify . --update --no-viz
fi
```

### 4. Confirm to user

```
Session paused.
STATE.md updated ✓
HANDOFF.md written ✓
Graph: [updated / already fresh]

Resume with: "resume work" or "continue [feature name]"
```
