# Session Management (Resume / Pause / Handoff)

## Session Start — Resume

On every session start, in this exact order:

1. **Run drift detection** ([drift.md](drift.md)) — before loading any context.
2. **Read `.specs/project/STATE.md`** — loads persistent memory:
   - Active feature and current phase
   - Open decisions and blockers
   - Next planned step
3. **Load work memory** (if `.specs/.memory/` exists): `nexspec reflect --max-tokens 800`
   — read-only lessons from past questions (what helped, dead ends, corrections).
4. **Read `.specs/HANDOFF.md`** if it exists — ephemeral resumption pointer written
   at session end. Delete after reading (it's one-shot).
5. **Load feature context on demand** — only read the active feature's spec/design/tasks
   when actually starting work on it. Do not preload all specs.

### Resume prompt to user

After loading STATE.md and HANDOFF.md, summarize in 3–5 lines:

```
Resuming: [feature name], phase [Specify/Design/Tasks/Execute]
Last completed: [last entry in STATE.md Progress]
Next step: [from HANDOFF.md or STATE.md Todos]
Index: [nexspec sync summary]
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
- [ISO date] [feature] TASK-00N complete. Gate: N/N pass. Commit: [sha].

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
size_bytes=$(wc -c < .specs/project/STATE.md)   # bytes, not du -k (block-rounded)
if [ "$size_bytes" -gt 30720 ]; then echo "STATE.md at ${size_bytes}B — running compaction..."; fi
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

## Index Status
[nexspec sync output — last run: ISO date]

## Open Questions
[anything unresolved that needs user input]
```

### 4. Persist what was learned

- Record the questions that mattered:
  `nexspec save-result --question "<q>" --outcome useful|dead_end|corrected --nodes <X>`
- Persist durable conclusions about code: `nexspec annotate <X> --note "<short>"`, then
  `nexspec annotate lint` (exit 8 = stale/dangling/duplicate findings to fix first).
- `nexspec reflect` rewrites `.specs/.memory/LESSONS.md` from the saved results.

### 5. Refresh the index

The post-commit hook covers commits. For uncommitted edits (WIP), sync manually
(it includes the dirty tree):

```bash
nexspec sync
```

### 6. Confirm to user

```
Session paused.
STATE.md updated ✓
HANDOFF.md written ✓
Index: [synced / nothing to sync]

Resume with: "resume work" or "continue [feature name]"
```
