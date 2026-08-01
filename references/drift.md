# Drift Detection

Run automatically at session start AND before starting Specify or Design phases.
Never block the workflow — report findings, propose fixes, ask before applying.

## When to run

- **Session start** (always, before reading STATE.md)
- **Before Specify** (before writing any spec.md)
- **Before Design** (before writing any design.md)

## Detection steps

### 1. Graph staleness

**PowerShell (Windows):**
```powershell
$graphJson = ".specs/graph/graph.json"
if (Test-Path $graphJson) {
    $graphTime = (Get-Item $graphJson).LastWriteTime
    $stale = Get-ChildItem -Recurse -File |
        Where-Object {
            $_.FullName -notmatch '\\\.specs\\graph\\' -and
            $_.FullName -notmatch '\\node_modules\\' -and
            $_.LastWriteTime -gt $graphTime
        } | Select-Object -First 10
    if ($stale) {
        Write-Host "DRIFT: graph.json is stale. Newer files:"
        $stale | ForEach-Object { Write-Host "  $($_.FullName)" }
    }
}
```

**bash (macOS/Linux):**
```bash
graph_json=".specs/graph/graph.json"
if [ -f "$graph_json" ]; then
    graph_time=$(stat -c %Y "$graph_json" 2>/dev/null || stat -f %m "$graph_json")
    stale=$(find . -not -path '*/.specs/graph/*' -not -path '*/node_modules/*' \
        -newer "$graph_json" -type f | head -10)
    if [ -n "$stale" ]; then
        echo "DRIFT: graph.json is stale. Newer files:"
        echo "$stale"
    fi
fi
```

**Action on stale graph:**
- If stale files include only additions/edits → propose `graphify . --update --no-viz`
- If git log shows `D` (deleted) or `R` (renamed) entries since last graph build → propose full `graphify .` rebuild (phantom nodes from --update over deletes)
- Always ask user before running — do not auto-apply

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
- Summarize commits into STATE.md `## Progress` section
- Ask user to confirm before writing

### 3. Spec vs implementation divergence (before Design/Implement)

Query the graph for nodes tagged with requirement IDs and check if corresponding
spec.md entries still exist:

```
graphify query "Which REQ-IDs appear in the codebase that are not in any spec.md?"
```

Report findings. Never auto-modify spec files.

## Report format

```
DRIFT REPORT
============
Graph: stale (14 files newer than graph.json) → propose: graphify . --update
STATE.md: 3 commits not reflected → propose: update Progress section
Spec drift: none detected

Apply proposed fixes? [y/n]
```

Always wait for user confirmation before applying any fix.
