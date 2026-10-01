# Drift Detection

Run automatically at session start AND before starting Specify or Design phases.
Never block the workflow — report findings, propose fixes, ask before applying.

## When to run

- **Session start** (always, before reading STATE.md)
- **Before Specify** (before writing any spec.md)
- **Before Design** (before writing any design.md)

## Detection steps

### 1. Index freshness

No mtime comparison is needed: `nexspec sync` diffs Git trees plus the dirty working
tree, so it is the freshness check and the fix in one cheap command.

```bash
nexspec check-update   # read-only: "up-to-date" | "stale: <reason>" | "no-index" (exit 0 / 3 / 4)
nexspec sync           # prints: added=N modified=N deleted=N dirty=N
```

If it fails with `Database already open. Cannot acquire lock`, the post-commit hook's background sync is
still running — wait for it to finish and retry (do not delete the index).

**Action:** run it automatically (it only writes the generated `.specs/.index/`, never
user files) and report the counts. Renames/deletes need no special handling — they are
applied incrementally. If `sync` errors, try `nexspec sync --resume` (replays the WAL);
as a last resort delete `.specs/.index/` and run `nexspec init && nexspec sync`.

### 2. Git vs STATE.md divergence

**PowerShell (Windows):**
```powershell
$stateTime = (Get-Item ".specs/project/STATE.md" -ErrorAction SilentlyContinue)?.LastWriteTime
if ($stateTime) {
    $newCommits = git log --oneline --since="$stateTime" 2>$null
    if ($newCommits) {
        Write-Host "DRIFT: $($newCommits.Count) commits since STATE.md was last updated:"
        $newCommits | Select-Object -First 5 | ForEach-Object { Write-Host "  $_" }
    }
}
```

**bash (macOS/Linux):**
```bash
state_file=".specs/project/STATE.md"
if [ -f "$state_file" ]; then
    state_time=$(stat -c %Y "$state_file" 2>/dev/null || stat -f %m "$state_file")
    state_date=$(date -d "@$state_time" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || \
                 date -r "$state_time" '+%Y-%m-%d %H:%M:%S')
    new_commits=$(git log --oneline --since="$state_date" 2>/dev/null)
    if [ -n "$new_commits" ]; then
        count=$(echo "$new_commits" | wc -l)
        echo "DRIFT: $count commits since STATE.md was last updated:"
        echo "$new_commits" | head -5
    fi
fi
```

**Action on STATE.md divergence:**
- Summarize commits into STATE.md `## Recent Progress` section
- Ask user to confirm before writing

### 3. Spec vs implementation divergence (before Design/Implement)

Run the requirement checks only when `Traceability: on` in `.specs/project/PROJECT.md`:

```bash
nexspec report --format md --max-tokens 1500   # read "Requirement Coverage": requirements with
                                               # no code/task, tasks with no REQ, @spec → missing REQ
nexspec trace REQ-001                          # drill into one requirement
nexspec diff --staged                          # changed symbols + dependants → do their REQs still hold?
```

Report findings. Never auto-modify spec files.

## Report format

```
DRIFT REPORT
============
Index: synced (added=2 modified=5 deleted=1 dirty=3)
STATE.md: 3 commits not reflected → propose: update Progress section
Spec drift: none detected

Apply remaining proposed fixes? [y/n]
```

Always wait for user confirmation before applying any fix.
