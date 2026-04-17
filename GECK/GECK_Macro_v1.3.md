# GECK_Macro v1.3
## Garden of Eden Creation Kit — LLM-Assisted Development Protocol
### Protocol Version: 1.3

---

## Overview

GECK gives CLI LLM agents structured memory, task management, and human oversight across sessions. v1.3 reorganizes memory into **episodic** (chronological log) and **semantic** (decisions, learnings) layers, adopts **typed addressable artifacts** (Task IDs, Decision IDs, Learning IDs), and scales the active context to a declared **context budget** so the protocol works for both small-window and frontier-window models.

### Design Principles
1. **Minimal viable overhead** — Documentation should not exceed the work itself
2. **Single source of truth** — One authoritative location for each type of information
3. **Episodic vs. semantic memory** — Logs record *what happened*; decisions and learnings record *what is now true*
4. **Addressable artifacts** — Tasks, decisions, and learnings have stable IDs and are referenced, not re-derived
5. **Drift resistance** — Protocol detects and halts goal erosion at session start
6. **Git-native** — All artifacts are plain text and diff cleanly
7. **Stack agnostic** — Applicable to any technology ecosystem
8. **Scales to context** — Active read set shrinks for small models, expands for large ones

---

## Project Structure

```
project_root/
├── LLM_init.md              # Project goals, constraints, context budget (human-authored)
└── GECK/
    ├── GECK_Inst.md         # Agent instructions (reference doc)
    ├── tasks.md             # Working memory — typed tasks with state
    ├── log.md               # Episodic memory — last N entries (N from context budget)
    ├── log_index.jsonl      # Machine-readable index of every entry, ever
    ├── log_archive/         # log_YYYY-MM.md rollovers
    ├── decisions.md         # Index of decision records (one line each)
    ├── decisions/           # DECISION-NNN-slug.md per decision
    ├── learnings.md         # Index of learning records (one line each)
    ├── learnings/           # LEARNING-NNN-slug.md per learning
    └── env.md               # Environment snapshot
```

**Naming change from v1.2:** the folder is now `GECK/` (was `LLM_GECK/`). The `LLM_` prefix was redundant — the entire repo is for LLM use.

---

## Memory Model (the v1.3 reorganization)

| Layer | File(s) | Read at session start | Write cadence | Purpose |
|-------|---------|----------------------|---------------|---------|
| **Goals** | `LLM_init.md` | Always | Human only | North star |
| **Working memory** | `tasks.md` | Always | Every turn | What to do now |
| **Semantic — decisions** | `decisions.md` + `decisions/` | Index always; files on demand | When a decision is made | Why we chose X |
| **Semantic — learnings** | `learnings.md` + `learnings/` | Index always; files on demand | When something broke or surprised | Don't redo the bad thing |
| **Episodic** | `log.md` (active) | Last N entries | Every turn | Narrative continuity |
| **Episodic archive** | `log_index.jsonl`, `log_archive/` | Index queried on demand | Rollover when active log exceeds budget | Full history for audit & targeted recall |
| **Environment** | `env.md` | As needed | When env changes | Compatibility decisions |

The agent does **not** re-read the full log every session. It reads the index and drills into specific archived entries only when a current task references them.

---

## Per-Record Files (Claude Code memory style, clean-room adapted)

Decisions and learnings are stored as one file per record, with a flat-text index pointing to each file. This pattern (borrowed in spirit from Claude Code's auto-memory system) gives:

- Individual addressability (cite by ID, edit in isolation)
- Small diffs (a new decision doesn't churn a 500-line file)
- Cheap session-start reads (the index is one line per record)
- Drill-down on demand (only load the specific file you need)

### `decisions/DECISION-NNN-<slug>.md`

```markdown
---
id: DECISION-001
title: Choose Zustand over React Context for state management
date: 2026-04-17T14:32:00Z
status: active        # active | superseded
related-tasks: [TASK-004]
related-decisions: []
superseded-by: null
---

**Decision:** Use Zustand for client state.

**Why:** App will have complex state interactions across many components.
React Context re-renders too aggressively at scale and adds boilerplate
for cross-cutting state.

**Consequences:**
- New runtime dependency (~1KB gzipped, acceptable)
- Team must learn Zustand idioms (low ramp)
- Refactoring Redux-style slices later is straightforward
```

### `decisions.md` (index)

```markdown
# Decisions — <Project Name>

*One line per decision record. Drill into the file for rationale.*

- [DECISION-001](decisions/DECISION-001-zustand-over-context.md) — Use Zustand for client state. (active)
- [DECISION-002](decisions/DECISION-002-postgres-over-sqlite.md) — Postgres for persistence. (active)
```

### `learnings/LEARNING-NNN-<slug>.md`

```markdown
---
id: LEARNING-001
title: Vite dev server proxy needs explicit Host header rewrite
date: 2026-04-17T16:11:00Z
related-tasks: [TASK-007]
---

**Rule:** When proxying to a backend that validates Host, set
`changeOrigin: true` AND `headers.Host` explicitly in `vite.config.ts`.

**Why:** Backend rejected requests with 421 Misdirected Request because
`changeOrigin: true` alone forwards the upstream Host but leaves cookies
scoped to the dev origin.

**How to apply:** Any new dev-only proxy rule in this project.
```

### `learnings.md` (index)

```markdown
# Learnings — <Project Name>

*One line per learning. Drill into the file for context.*

- [LEARNING-001](learnings/LEARNING-001-vite-proxy-host.md) — Vite proxy needs explicit Host header.
```

---

## Tasks (typed, addressable, state-machined)

### `tasks.md` format

```markdown
# Tasks — <Project Name>

**Last Updated:** <ISO timestamp>

## Legend

- `[ ]` proposed/accepted (not started)
- `[~]` active (in progress)
- `[!:reason]` blocked (reason required)
- `[x]` completed (immutable; cite log entry)

State transitions are forward-only (or to blocked). Completed tasks are not re-opened — file a new task instead.

## Current Sprint

- [~] TASK-001 | TYPE: feature | SCOPE: medium | OWNER: agent
  - Implement user authentication endpoint
  - Subtask: write Pydantic models (nested bullets give the tree shape)
  - Subtask: add JWT middleware
- [!:waiting on DECISION-003] TASK-002 | TYPE: refactor | SCOPE: small | OWNER: agent
  - Extract DB session helper from views

## Backlog

- [ ] TASK-003 | TYPE: research | SCOPE: small | OWNER: human
  - Compare Stripe vs. Lemon Squeezy

## Completed (Recent)

- [x] TASK-000 | TYPE: chore | SCOPE: small — Entry #2
```

### Field semantics

| Field | Allowed values |
|-------|----------------|
| TYPE | `feature` \| `fix` \| `refactor` \| `research` \| `chore` \| `docs` \| `test` |
| SCOPE | `small` \| `medium` \| `large` |
| OWNER | `agent` \| `human` |

### Rules

- Task IDs are sequential and never reused.
- Log entries MUST reference the TASK-IDs they touched.
- A `[x]` completion MUST cite the log entry number (`— Entry #N`).
- A `[!:...]` block MUST include a reason (decision pending, external blocker, etc.).

---

## Log (episodic, tiered, agent-optimized)

### Active `log.md` — tightened per-turn entry

```markdown
# Session Log — <Project Name>

*Append only. Older entries roll to log_archive/. Full history queryable via log_index.jsonl.*

---

## Entry #N — <ISO timestamp> — touched: TASK-001, TASK-004
- Did: <one line summary of what changed>
- Files: <paths, comma-separated>
- State: CONTINUE | WAIT | ROLLBACK
- Refs: DECISION-002, LEARNING-001    (omit line if none)
- Next: <one line — what comes next>
```

That's the whole entry. Long-form audit data, if anyone wants it, lives in commit messages and PR descriptions — not duplicated here.

### `log_index.jsonl` — one line per entry, ever

```jsonl
{"id":1,"ts":"2026-04-17T14:00:00Z","tasks":["TASK-001"],"decisions":[],"learnings":[],"files":["src/auth.py"],"state":"CONTINUE","summary":"Scaffolded auth route"}
{"id":2,"ts":"2026-04-17T15:20:00Z","tasks":["TASK-001"],"decisions":["DECISION-001"],"learnings":[],"files":["src/auth.py","src/state.ts"],"state":"WAIT","summary":"Picked Zustand; awaiting confirmation"}
```

The agent uses this to answer "show me every entry that touched TASK-001" without reading the prose log.

### Rollover

When `log.md` exceeds `LOG_ACTIVE_ENTRIES + 5`:
1. Move all but the most recent `LOG_ACTIVE_ENTRIES` into `log_archive/log_YYYY-MM.md`
2. Add a one-line note at the top of `log.md`: `*Older entries: log_archive/*`
3. `log_index.jsonl` is untouched (it always holds the full timeline)

---

## Context Budget (model-size adaptation)

`LLM_init.md` declares the assumed context budget for the project:

| Budget | Window | LOG_ACTIVE_ENTRIES |
|--------|--------|--------------------|
| `small` | 8k–32k tokens | 3 |
| `medium` | 32k–128k tokens | 10 |
| `large` | 128k+ tokens | 25 |

The agent self-checks at session start: if its actual window is smaller than the declared budget, it downgrades to the smaller-budget rules and warns the human. This avoids needing runtime hardware-detection infrastructure — the human picks at project init, the agent verifies at session start.

---

## PHASE 0: INITIALIZATION

*Run once per project. Skip to Phase 1 if `GECK/` folder exists.*

### Step 0.1 — Prerequisites (Human)

1. Create GitHub repository, clone locally
2. Create `LLM_init.md` (manually or via GECK Generator) — include the `Context Budget` field
3. Instruct agent: "Read LLM_init.md and initialize the GECK."

### Step 0.2 — GECK Initialization (Agent)

1. Create `GECK/` folder
2. Copy `GECK_Inst.md` template into folder
3. Create empty `decisions/` and `learnings/` subfolders
4. Create empty `decisions.md` and `learnings.md` index files (with header only)
5. Create `log_archive/` subfolder
6. Create empty `log_index.jsonl`
7. Create `env.md` with environment detection appropriate to the stack
8. Create `tasks.md` with initial tasks derived from `LLM_init.md` (assigning TASK-001, TASK-002, …)
9. Create `log.md` with Entry #0:
   ```
   ## Entry #0 — <ISO ts> — touched: (init)
   - Did: GECK initialized
   - Files: GECK/*
   - State: WAIT
   - Next: Await confirmation to begin work
   ```
10. Append the matching line to `log_index.jsonl`
11. **Verify** all files exist and state: **"GECK v1.3 initialized. Awaiting confirmation to proceed."**

---

## PHASE 1: EXECUTION LOOP

*Repeat until success criteria are met.*

### Step 1.1 — Drift Check (mandatory, every session)

Before reading the log, restate from `LLM_init.md`:

1. Project Goal (one sentence)
2. Active TASK-IDs (from `tasks.md`)
3. Constraints

Then declare:

```
Drift Detected: YES | NO
If YES: describe discrepancy, set checkpoint to WAIT, stop.
```

### Step 1.2 — Orient

1. Read `decisions.md` (the index) — drill into specific files only as needed
2. Read `learnings.md` (the index) — drill in only as needed
3. Read `tasks.md` (full)
4. Read last `LOG_ACTIVE_ENTRIES` from `log.md`, OR query `log_index.jsonl` for entries touching active TASK-IDs (whichever is more relevant)

### Step 1.3 — Plan (Standard/Heavy mode)

State:
1. What you will do this turn
2. Files you expect to modify
3. What success looks like
4. Assumptions

### Step 1.4 — Execute

Do the work.

### Step 1.5 — Update Working Memory

In order:
1. Update `tasks.md` — transition states, add discovered subtasks
2. If a decision was made: create `decisions/DECISION-NNN-slug.md`, add line to `decisions.md`
3. If a learning emerged: create `learnings/LEARNING-NNN-slug.md`, add line to `learnings.md`
4. Append entry to `log.md`
5. Append matching line to `log_index.jsonl`
6. If `log.md` exceeds `LOG_ACTIVE_ENTRIES + 5`: roll oldest into `log_archive/log_YYYY-MM.md`

### Step 1.6 — Commit

```bash
git add <specific files>
git commit -m "<type>: <description>"
```

Commit types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`. Branch (`experiment/<name>`) for risky work.

### Step 1.7 — Checkpoint

Evaluate and state:

- **CONTINUE** — work stable, proceed to next task
- **WAIT** — need human input or hit a blocker (state what you need)
- **ROLLBACK** — something broke, invoke Rollback Protocol

---

## PHASE 2: COMPLETION

When SUCCESS CRITERIA from `LLM_init.md` are met:

1. Final log entry summarizing build, known limits, suggested improvements
2. All tasks `[x]` or moved to backlog with rationale
3. State: **"SUCCESS CRITERIA MET. Ready for human review."**

---

## Work Modes

| Mode | When | Required updates |
|------|------|------------------|
| **Light** | Single-file fix, typo, trivial chore | tasks.md only |
| **Standard** | Feature work, multi-file changes | Plan + tasks.md + log.md + log_index.jsonl |
| **Heavy** | Architecture changes, new subsystems | All of Standard + DECISION-NNN record |

---

## Protocols

### Rollback Protocol

1. Identify problem and affected commits
2. Log entry documenting what broke and why
3. Propose: `git revert <commit>` for clean cases, manual fix otherwise
4. State: **"ROLLBACK NEEDED. Awaiting approval."**
5. Wait for human confirmation

### Decision Fork Protocol

When facing a non-obvious choice:

1. Identify the fork
2. List 2–3 options with brief pros/cons
3. State recommendation with reasoning
4. Set checkpoint WAIT
5. After human chooses: create `DECISION-NNN-slug.md`

### Learning Capture Protocol

When something breaks unexpectedly OR a non-obvious approach works:

1. Create `LEARNING-NNN-slug.md` with **Rule**, **Why**, **How to apply**
2. Add line to `learnings.md` index
3. Reference `LEARNING-NNN` in the current log entry's `Refs` line

This is the protocol's loss-prevention mechanism. Future sessions read learnings cheaply (the index alone) and avoid re-stepping on the same rakes.

---

## File Responsibilities

| File | Read | Write | Rules |
|------|------|-------|-------|
| `LLM_init.md` | Always | Never | Human-owned; your north star |
| `GECK_Inst.md` | Session start (or as needed) | Never | These instructions |
| `tasks.md` | Every turn | Every turn | Forward-only state transitions |
| `decisions.md` | Index every turn | When decision made | Append-only; supersede via `superseded-by` |
| `decisions/*.md` | On demand | When decision made | One file per decision; never delete |
| `learnings.md` | Index every turn | When learning emerges | Append-only |
| `learnings/*.md` | On demand | When learning emerges | One file per learning; never delete |
| `log.md` | Last N entries | Append every turn | Never edit past entries; rollover when full |
| `log_index.jsonl` | Query as needed | Append every turn | One line per entry, ever |
| `log_archive/*.md` | On demand | Auto-rollover | Append-only |
| `env.md` | As needed | When env changes | Document, don't assume |

---

## Red Lines — Always Stop and Ask

- Deleting files or data
- Changing auth/security code
- Modifying database schemas
- Actions that cannot be undone
- Uncertainty about what user wants
- Significant architectural decisions (use Decision Fork Protocol)
- Drift detected at session start

---

## Quick Reference

### Starting a session
1. Drift Check (restate goal + active TASK-IDs + constraints)
2. Read `decisions.md` index, `learnings.md` index, `tasks.md`
3. Read last N log entries OR query `log_index.jsonl`
4. Pick next task and begin

### Per turn
1. Plan (Standard/Heavy)
2. Execute
3. Update tasks → decisions/learnings (if any) → log.md → log_index.jsonl
4. Commit
5. State checkpoint

---

## Changelog

### v1.3 (Current)
- **Folder rename:** `LLM_GECK/` → `GECK/` (the `LLM_` prefix was redundant)
- **Memory model:** explicit episodic vs. semantic split
- **Per-record files for decisions and learnings**, with index files (Claude Code memory style)
- **`learnings.md` + `learnings/`** added — captures gotchas semantically
- **`log_index.jsonl`** added — machine-readable history; agent queries instead of re-reading prose
- **Tightened per-turn log entry** — narrative bloat moves to commit messages / PRs
- **Tiered log:** active `log.md` holds last N entries, older roll to `log_archive/`
- **Typed tasks:** `TASK-NNN | TYPE | SCOPE | OWNER` syntax with state machine
- **Drift Check:** mandatory at session start
- **Context Budget:** declared in `LLM_init.md`, drives `LOG_ACTIVE_ENTRIES`

### v1.2
- Added `GECK_Inst.md`
- Added file specifications section
- Added GECK_Inst.md template

### v1.1
- Consolidated duplicate templates
- Work modes (Light/Standard/Heavy)
- Standard markdown checkbox syntax
- Log archival protocol

### v1.0
- Initial release
