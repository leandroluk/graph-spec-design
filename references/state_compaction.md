# State Compaction Protocol

STATE.md must stay below **30 KB** to remain within the session context budget.
When this limit is exceeded, run this protocol automatically — no user prompt needed.

---

## When to Compact

Compact STATE.md when ANY condition is true:

| Condition | Threshold |
|---|---|
| File size | > 30 KB |
| `Recent Progress` entries | > 10 |
| `Recent Decisions` entries | > 15 |
| `Lessons Learned` entries | > 5 |
| `Deferred Ideas` entries | > 10 |

Check these conditions:
1. At session start — before reading STATE.md content.
2. At session end — after updating STATE.md.

**PowerShell (Windows):**
```powershell
$stateFile = ".specs/project/STATE.md"
$sizeKB = [math]::Round((Get-Item $stateFile).Length / 1KB, 1)
if ($sizeKB -gt 30) { # run compaction }
```

**bash (macOS/Linux):**
```bash
state_file=".specs/project/STATE.md"
size_kb=$(du -k "$state_file" | cut -f1)
if [ "$size_kb" -gt 30 ]; then # run compaction; fi
```

---

## Compaction Steps

### Step 1 — Read current STATE.md

Load the full content into memory. Parse all sections.

### Step 2 — Extract "hot" content (what stays in STATE.md)

Keep only the following in STATE.md:

| Section | Keep |
|---|---|
| Header (`# State`, `Last synced commit`, `Last Updated`) | All |
| `Current Work` | All (no limit — this is the critical working context) |
| `Todos` | All active (`[ ]`) items; archive completed (`[x]`) items |
| `Active Blockers` | All (up to 5) |
| `Recent Decisions` | Latest **15** entries by date |
| `Recent Progress` | Latest **10** entries by date |
| `Lessons Learned` | Latest **5** entries by date |
| `Deferred Ideas` | Latest **10** items |

Everything that does not fit within these windows is **archived**.

### Step 3 — Write STATE_ARCHIVE.md

Append a new archive block to `.specs/project/STATE_ARCHIVE.md`:

```markdown
## Archive — <YYYY-MM-DD> (compaction <N>)

### Progress
- [entry 1]
- [entry 2]
...

### Decisions
- [entry 1]
...

### Todos (completed)
- [x] [item]
...

### Lessons Learned
- [entry]
...

### Deferred Ideas (overflow)
- [idea]
...

---
```

If `STATE_ARCHIVE.md` does not exist, create it with this header:

```markdown
# State Archive

<!-- Auto-generated. Never edit manually. Read with: "show state history" -->

```

### Step 4 — Rewrite STATE.md

Replace the full content of STATE.md with the compacted version.

Use this exact template:

```markdown
# State

Last synced commit: <sha>
**Last Updated:** <YYYY-MM-DD>

## Current Work
<full Current Work paragraph — unchanged>

## Todos
- [ ] <next step>

## Active Blockers
- <blocker or "none">

## Recent Decisions (Last 15)
- [YYYY-MM-DD] <decision>

## Recent Progress (Last 10)
- [YYYY-MM-DD] <feature> T-00N complete. Gate: N/N pass. Commit: <sha>.

## Lessons Learned (Last 5)
- [YYYY-MM-DD] <lesson>

## Deferred Ideas
- <idea>
```

### Step 5 — Confirm

Report to the user (inline, not blocking):

```
STATE.md compacted: <before> KB → <after> KB
Archived to STATE_ARCHIVE.md: <N> progress, <M> decisions, <K> lessons entries.
```

---

## Legacy Migration

If STATE.md does not use windowed sections (i.e., `## Progress` instead of
`## Recent Progress (Last 10)`), it is a legacy file. Apply compaction as above,
then rename sections to the new names during the rewrite.

Detection: `## Progress` or `## Decisions` without "(Last N)" in the header.

---

## STATE_ARCHIVE.md is never loaded automatically

The archive file is ONLY read when the user explicitly asks:
- "show state history"
- "what decisions were made before <date>?"
- "show archived progress"

Never preload `STATE_ARCHIVE.md` at session start.
