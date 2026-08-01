# Drift Detection

Run automatically at session start AND before starting Specify or Design phases.
Never block the workflow — report findings, propose fixes, ask before applying.

## When to run

- **Session start** (always, before reading STATE.md)
- **Before Specify** (before writing any spec.md)
- **Before Design** (before writing any design.md)

## Detection steps

### 1. Graph staleness

```powershell
$graphJson = ".specs/graph/graph.json"
if (Test-Path $graphJson) {
    $graphTime = (Get-Item $graphJson).LastWriteTime

    # Find any source or spec file newer than the graph
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

**Action on stale graph:**
- If stale files include only additions/edits → propose `graphify . --update --no-viz`
- If git log shows `D` (deleted) or `R` (renamed) entries since last graph build → propose full `graphify .` rebuild (phantom nodes from --update over deletes)
- Always ask user before running — do not auto-apply

### 2. Git vs STATE.md divergence

```powershell
# Get commits since last STATE.md update
$stateTime = (Get-Item ".specs/project/STATE.md" -ErrorAction SilentlyContinue)?.LastWriteTime
if ($stateTime) {
    $newCommits = git log --oneline --since="$stateTime" 2>$null
    if ($newCommits) {
        Write-Host "DRIFT: $($newCommits.Count) commits since STATE.md was last updated:"
        $newCommits | Select-Object -First 5 | ForEach-Object { Write-Host "  $_" }
    }
}
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
