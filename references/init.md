# Phase 0 — Init & Index Build

Run this phase when `.specs/.index/` does not exist, or when the user explicitly
asks to "initialize project" or "map codebase".

`nexspec` is a single static binary: no Python interpreter to detect, no environment
variable to set, and no OS-specific branches — the same commands work on every OS.

---

## 0.1 — Verify the binary

```bash
nexspec --version
```

If missing, install (requires a Rust toolchain):

```bash
cargo install --git https://github.com/leandroluk/rust-nexspec nexspec
# BM25-only build, without the ONNX/HNSW vector engine:
cargo install --git https://github.com/leandroluk/rust-nexspec nexspec --no-default-features --features lean
```

If that fails or is declined → degraded mode (section 0.6).

The default `full` build also uses an embedding model (`all-MiniLM-L6-v2`, INT8, in
`.models/`) for semantic search. Without it, search degrades to BM25 — it never fails.

---

## 0.2 — Create directory structure

**PowerShell (Windows):**
```powershell
New-Item -ItemType Directory -Force -Path `
  .specs/project, .specs/codebase, .specs/features, .specs/quick | Out-Null
```

**bash (macOS/Linux):**
```bash
mkdir -p .specs/project .specs/codebase .specs/features .specs/quick
```

Ensure `.specs/.index/` is git-ignored (append it to `.gitignore` if missing). The existing file may not end with a newline — add one first, or the entry gets glued to the last line and silently ignores nothing:

```bash
grep -qxF '.specs/.index' .gitignore || { [ -n "$(tail -c1 .gitignore)" ] && echo >> .gitignore; echo '.specs/.index' >> .gitignore; }
```

---

## 0.2b — Ask about requirement traceability (once)

Ask the user (in their language):

> Use requirement traceability? Specs get `REQ-001`-style IDs, code gets `@spec REQ-001`
> comments and commits carry `[REQ-001]`, so `nexspec trace REQ-001` answers "what
> implements this?" and drift/impact checks can find unimplemented or orphaned
> requirements. Costs a few tokens per spec/commit, saves far more per query.
> **Recommended: yes.**

Record the answer in `.specs/project/PROJECT.md` as `Traceability: on` (default if the
user has no preference) or `Traceability: off`. Every later phase reads this flag; when
`off`, skip all REQ/`@spec` steps and use symbol-based `search`/`trace` only. Never re-ask.

For a project that already has specs, default to `on` only if they already contain
`REQ-` IDs; otherwise ask.

---

## 0.3 — Build the index

```bash
nexspec init     # creates .specs/.index/ (idempotent)
nexspec sync     # indexes code (Tree-sitter) + .specs/*.md (REQ/TASK/ADR markers)
```

> The index covers **source code** (TS/JS, Python, Go, Rust) AND **`.specs/*.md`** in
> one graph. Symbol search/trace work with no markers at all. With traceability on (0.2b),
> `REQ-XXX`/`TASK-XXX`/`ADR-XXX` markers in specs, `@spec` code comments and commit
> messages become linked nodes, and `nexspec trace REQ-001` returns exact
> file+symbol references.

`nexspec` syncs from **Git history**, so the project must be a Git repository.

Optional — register the MCP server so the agent gets `query_context`,
`trace_requirement`, `find_impacted_code`, `get_symbol_history` and `sync_workspace`
as native tools:

```json
{ "mcpServers": { "nexspec": { "command": "nexspec", "args": ["--repo", ".", "mcp"] } } }
```

---

## 0.4 — Install post-commit hook (git projects only)

```bash
mkdir -p .git/hooks
printf '#!/bin/sh\n# graph-spec-design: refresh the NexSpec index after every commit\nnexspec sync > /dev/null 2>&1 &\n' > .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

On Windows, run this in Git Bash (git executes hooks through its bundled `sh`).
If a `post-commit` hook already exists, append the `nexspec sync` line instead of overwriting.

---

## 0.5 — Seed codebase docs

There is no generated report to read. Seed `.specs/codebase/` with targeted, budgeted
queries instead of walking the tree:

```bash
nexspec search "entry point main architecture modules" --max-tokens 2000   # → ARCHITECTURE.md
nexspec search "error handling retry fallback risk" --max-tokens 1500      # → CONCERNS.md
```

Read at most the 2–3 files the results point to. Record the first `nexspec sync`
summary line (added/modified counts) in `.specs/project/STATE.md` under `## Cost`.

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
size_bytes=$(wc -c < .specs/project/STATE.md 2>/dev/null || echo 0)   # bytes, not du -k (block-rounded)
```

If the file is legacy OR if `$sizeKB > 30` (bash: `$size_bytes -gt 30720`):
- Run the compaction protocol: [references/state_compaction.md](state_compaction.md)
- The protocol will migrate legacy section names to windowed names and archive the overflow
- Report to user: `STATE.md migrated to windowed format: <before> KB → <after> KB`

## 0.5c — Migrating from graphify

If `.specs/graph/` exists from a previous graphify-based install: delete it (it is
generated), remove any `GRAPHIFY_OUT` / `.graphify_python` lines from
`.git/hooks/post-commit` (0.4 replaces the hook), and continue at 0.3.

---

## 0.6 — Degraded mode (nexspec unavailable)

If nexspec cannot be installed (no Rust toolchain, no Git repo, restricted
environment, user declined):

- Skip steps 0.3–0.5
- Record in `.specs/project/STATE.md`:
  ```markdown
  ## Degraded Mode
  - nexspec not available. All context loaded from raw files.
  - Token budget: load only the active feature spec + STATE.md per session.
  ```
- Continue with spec-driven flow using direct file reads — no phase is ever blocked.
