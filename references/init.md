# Phase 0 — Init & Graph Build

Run this phase when `.specs/graph/graph.json` does not exist, or when the user
explicitly asks to "initialize project" or "map codebase".

## 0.1 — Detect OS and shell

Before running any command, detect the operating system:

```
IF Windows  → use PowerShell commands (pwsh / powershell)
IF macOS    → use bash/zsh commands
IF Linux    → use bash commands
```

Detection (the agent reads the environment, not the user):
- Windows: `$env:OS -eq "Windows_NT"` or `[System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform([System.Runtime.InteropServices.OSPlatform]::Windows)`
- macOS/Linux: `uname -s` returns `Darwin` or `Linux`

All commands below are shown in **PowerShell** (Windows) and **bash** (macOS/Linux) variants.
The agent selects the correct one automatically based on the detected OS.

---

## 0.2 — Create directory structure

**PowerShell (Windows):**
```powershell
New-Item -ItemType Directory -Force -Path `
  .specs/project, .specs/codebase, .specs/features, .specs/quick, .specs/graph | Out-Null
```

**bash (macOS/Linux):**
```bash
mkdir -p .specs/project .specs/codebase .specs/features .specs/quick .specs/graph
```

---

## 0.3 — Set GRAPHIFY_OUT and build the graph

All graphify invocations MUST set `GRAPHIFY_OUT` so artifacts land in `.specs/graph/`
instead of the default `graphify-out/` at the project root.

> Running on `.` (repo root) makes graphify process **source code** (AST) AND
> **`.specs/*.md`** (semantic). This connects `REQ-001` in `spec.md` to the modules
> that implement it — enabling `graphify query "what implements REQ-001?"` to return
> exact file+function references.

**PowerShell (Windows):**
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
    exit 0  # degraded mode — see section 0.6
}

# Save interpreter path for future use (commit hook, --update calls)
$py | Out-File -FilePath .specs/graph/.graphify_python -Encoding utf8 -NoNewline

& $py -m graphify .
```

**bash (macOS/Linux):**
```bash
export GRAPHIFY_OUT=".specs/graph"

# Detect graphify Python interpreter (uv → pipx → active env)
py=""
if command -v uv &>/dev/null; then
    uv_dir=$(uv tool dir 2>/dev/null)
    candidate="$uv_dir/graphifyy/bin/python"
    if [ -f "$candidate" ] && "$candidate" -c "import graphify" &>/dev/null; then
        py="$candidate"
    fi
fi
if [ -z "$py" ] && command -v python &>/dev/null; then
    if python -c "import graphify" &>/dev/null; then
        py=$(python -c "import sys; print(sys.executable)")
    fi
fi
if [ -z "$py" ]; then
    echo "graphify not found. Install: uv tool install graphifyy" >&2
    exit 0  # degraded mode — see section 0.6
fi

# Save interpreter path for future use (commit hook, --update calls)
echo -n "$py" > .specs/graph/.graphify_python

"$py" -m graphify .
```

---

## 0.4 — Install post-commit hook (git projects only)

**PowerShell (Windows):**
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
    Write-Host "No .git found — hook skipped. See section 0.6 for manual sync."
}
```

**bash (macOS/Linux):**
```bash
if [ -d .git ]; then
    mkdir -p .git/hooks
    cat > .git/hooks/post-commit << 'EOF'
#!/bin/sh
# graph-spec-design: update knowledge graph after every commit
export GRAPHIFY_OUT=".specs/graph"
PY=$(cat .specs/graph/.graphify_python 2>/dev/null || echo "python")
"$PY" -m graphify . --update --no-viz > /dev/null 2>&1 &
EOF
    chmod +x .git/hooks/post-commit
    echo "Hook installed: graphify --update will run after every commit."
else
    echo "No .git found — hook skipped. See section 0.6 for manual sync."
fi
```

---

## 0.5 — Read GRAPH_REPORT.md and seed codebase docs

After the build, read `.specs/graph/GRAPH_REPORT.md` and use its output to:

- **God Nodes** section → seed `.specs/codebase/CONCERNS.md` with high-risk components
- **Community Hubs** section → seed `.specs/codebase/ARCHITECTURE.md` with module groupings
- **Token cost** → record in `.specs/project/STATE.md` under `## Cost`

---

## 0.5b — Detect legacy STATE.md and migrate

If `.specs/project/STATE.md` already exists, check if it uses the legacy format
(unbounded sections `## Progress`, `## Decisions` without window notation):

**PowerShell (Windows):**
```powershell
$stateContent = Get-Content .specs/project/STATE.md -Raw -ErrorAction SilentlyContinue
$isLegacy = $stateContent -match "^## Progress" -or $stateContent -match "^## Decisions"
$sizeKB = [math]::Round((Get-Item .specs/project/STATE.md -ErrorAction SilentlyContinue)?.Length / 1KB, 1)
```

**bash (macOS/Linux):**
```bash
state_content=$(cat .specs/project/STATE.md 2>/dev/null || echo "")
is_legacy=$(echo "$state_content" | grep -c "^## Progress\|^## Decisions")
size_kb=$(du -k .specs/project/STATE.md 2>/dev/null | cut -f1 || echo 0)
```

If the file is legacy OR if `$sizeKB > 30`:
- Run the compaction protocol: [references/state_compaction.md](state_compaction.md)
- The protocol will migrate legacy section names to windowed names and archive the overflow
- Report to user: `STATE.md migrated to windowed format: <before> KB → <after> KB`

---

## 0.6 — Degraded mode (graphify unavailable)

If graphify cannot be installed (no Python, restricted environment, user declined):

- Skip steps 0.3–0.5
- Record in `.specs/project/STATE.md`:
  ```markdown
  ## Degraded Mode
  - graphify not available. All context loaded from raw files.
  - Token budget: load only the active feature spec + STATE.md per session.
  ```
- Continue with spec-driven flow using direct file reads — no phase is ever blocked.
