# Phase 0 — Init & Graph Build

Run this phase when `.specs/graph/graph.json` does not exist, or when the user
explicitly asks to "initialize project" or "map codebase".

## 0.1 — Create directory structure

```powershell
New-Item -ItemType Directory -Force -Path `
  .specs/project, .specs/codebase, .specs/features, .specs/quick, .specs/graph | Out-Null
```

## 0.2 — Set GRAPHIFY_OUT and build the graph

All graphify invocations MUST set `GRAPHIFY_OUT` so artifacts land in `.specs/graph/`
instead of the default `graphify-out/` at the project root.

```powershell
$env:GRAPHIFY_OUT = ".specs/graph"

# Detect graphify Python interpreter (uv → pipx → active env)
$py = $null
if (Get-Command uv -ErrorAction SilentlyContinue) {
    $uvDir = (uv tool dir 2>$null).Trim()
    $candidate = Join-Path $uvDir "graphifyy\Scripts\python.exe"
    if ((Test-Path $candidate) -and (& $candidate -c "import graphify" 2>$null; $LASTEXITCODE -eq 0)) {
        $py = $candidate
    }
}
if (-not $py) {
    $pyCmd = (Get-Command python -ErrorAction SilentlyContinue)?.Source
    if ($pyCmd -and (& $pyCmd -c "import graphify" 2>$null; $LASTEXITCODE -eq 0)) {
        $py = $pyCmd
    }
}
if (-not $py) {
    Write-Error "graphify not found. Install: uv tool install graphifyy"
    # DEGRADED MODE: continue without graph (spec-driven flow uses direct file reads)
    exit 0
}

# Save interpreter path for future use (commit hook, --update calls)
$py | Out-File -FilePath .specs/graph/.graphify_python -Encoding utf8 -NoNewline

# Run on repo root — scans BOTH source code (AST) AND .specs/*.md (semantic)
# This connects REQ-001 in spec.md to the modules that implement it in the graph.
& $py -m graphify .
```

> **Why scan the root and not just `src/`?**
> Running on `.` makes graphify process source code via AST extraction and
> `.specs/*.md` via semantic extraction. Requirements like `REQ-001` become graph
> nodes connected to the code symbols that implement them — enabling queries like
> "what implements REQ-001?" to return exact file+function references.

## 0.3 — Install post-commit hook (git projects only)

```powershell
if (Test-Path .git) {
    New-Item -ItemType Directory -Force -Path .git/hooks | Out-Null
    @"
#!/bin/sh
# graph-spec-design: update knowledge graph after every commit
export GRAPHIFY_OUT=".specs/graph"
PY=`$(cat .specs/graph/.graphify_python 2>/dev/null || echo "python")
"`$PY" -m graphify . --update --no-viz > /dev/null 2>&1 &
"@ | Out-File -FilePath .git/hooks/post-commit -Encoding utf8 -NoNewline
    Write-Host "Hook installed: graphify --update will run after every commit."
} else {
    Write-Host "No git repo found — hook skipped."
    Write-Host "Remember to run 'graphify . --update' manually after significant changes."
    # Log reminder in STATE.md
}
```

## 0.4 — Read GRAPH_REPORT.md and seed codebase docs

After the build, read `.specs/graph/GRAPH_REPORT.md` and use its output to:

- **God Nodes** section → seed `.specs/codebase/CONCERNS.md` with high-risk components
- **Community Hubs** section → seed `.specs/codebase/ARCHITECTURE.md` with module groupings
- **Token cost** → record in `.specs/project/STATE.md` under `## Cost`

## 0.5 — Degraded mode (graphify unavailable)

If graphify cannot be installed (no Python, restricted environment):

- Skip steps 0.2–0.4
- Record in `.specs/project/STATE.md`:
  ```markdown
  ## Degraded Mode
  - graphify not available. All context loaded from raw files.
  - Token budget: load only the active feature spec + STATE.md per session.
  ```
- Continue with spec-driven flow using direct file reads — no phase is blocked.
