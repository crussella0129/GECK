# GECK_Macro v1.1
## Garden of Eden Creation Kit — LLM-Assisted Development Protocol
### Protocol Version: 1.1

---

## Overview

This protocol provides structured memory, task management, and human oversight for LLM-assisted software development. It creates continuity across sessions and maintains an audit trail of all changes.

### Design Principles
1. **Minimal viable overhead** — Documentation should not exceed the work itself
2. **Single source of truth** — One authoritative location for each type of information
3. **Graceful scaling** — Works for small fixes and large projects
4. **Stack agnostic** — Applicable to any technology ecosystem
5. **Git-native** — Integrates cleanly with version control workflows

---

## Project Structure

```
project_root/
├── LLM_init.md          # Project goals and constraints (human-authored)
└── LLM_GECK/
    ├── log.md           # Append-only session log (long-term memory)
    ├── tasks.md         # Current task list (working memory)
    └── env.md           # Environment documentation
```

**Note:** Dependency tracking belongs in code comments, README files, or standard tooling (package.json, requirements.txt, etc.)—not a separate LLM file.

---

## PHASE 0: INITIALIZATION

*Run once per project. Skip to Phase 1 if `LLM_GECK/` folder exists.*

### Step 0.1 — Prerequisites (Human)

1. Create GitHub repository
2. Clone to local directory
3. Create `LLM_init.md` using the template below
4. Instruct LLM: "Clone [REPO_URL] to [TARGET_DIR]. Read LLM_init.md and initialize the GECK."

### Step 0.2 — GECK Initialization (LLM)

1. Create `LLM_GECK/` folder
2. Create `LLM_GECK/env.md`:
   - Run environment detection commands appropriate to the stack
   - Document OS, language versions, package manager state
   - Note any environment variables that exist (names only, not values)
   - Record target platforms from `LLM_init.md`

3. Create `LLM_GECK/tasks.md` with initial tasks derived from `LLM_init.md`

4. Create `LLM_GECK/log.md` with Entry #0:
   - Understood goals (summarized from LLM_init.md)
   - Any ambiguities or questions
   - Proposed first actions

5. **Verify initialization:**
   ```
   - [ ] LLM_GECK/ folder exists
   - [ ] env.md captures current environment
   - [ ] tasks.md has initial task list
   - [ ] log.md has Entry #0
   ```

6. **STOP. State: "GECK initialized. Awaiting confirmation to proceed."**

---

## PHASE 1: EXECUTION LOOP

*Repeat until success criteria are met.*

### Work Modes

Choose the appropriate mode based on task scope:

| Mode | When to Use | Documentation Required |
|------|-------------|----------------------|
| **Light** | Single-file fixes, typos, small bugs | Update tasks.md only |
| **Standard** | Feature work, multi-file changes | Full log entry |
| **Heavy** | Architecture changes, new subsystems | Log entry + decision documentation |

### Step 1.1 — Orient

1. Read the last entry in `log.md`
2. Read `tasks.md` current state
3. Review SUCCESS CRITERIA in `LLM_init.md`

### Step 1.2 — Plan (Standard/Heavy mode only)

Before writing code, state:
1. What you will do this turn
2. What files you expect to modify
3. What success looks like for this turn
4. Any assumptions you're making

### Step 1.3 — Execute

Do the work.

### Step 1.4 — Commit

**Commit after each successful execution cycle:**
```bash
git add [specific files]
git commit -m "[type]: [description]"
```

Commit types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

For experimental/risky work, create a branch first:
```bash
git checkout -b experiment/[description]
```

### Step 1.5 — Update Tasks

Update `tasks.md`:
- Mark completed tasks with `[x]`
- Add new tasks discovered during work
- Note any blocked tasks with `[BLOCKED: reason]`

### Step 1.6 — Log (Standard/Heavy mode only)

Append entry to `log.md` using the template below.

### Step 1.7 — Checkpoint

Evaluate:
- **CONTINUE** — Work is stable, proceed to next task
- **WAIT** — Need human input on decision or encountered blocker
- **ROLLBACK** — Something broke, invoke Rollback Protocol

If WAIT: State what you need and stop.

---

## PHASE 2: COMPLETION

When SUCCESS CRITERIA from `LLM_init.md` are met:

1. Add final log entry summarizing:
   - What was built
   - Known limitations
   - Suggested future improvements

2. Update `tasks.md` to show all tasks complete

3. State: **"SUCCESS CRITERIA MET. Ready for human review."**

---

## PROTOCOLS

### Rollback Protocol

When a turn causes regression:

1. Identify the problem and affected commits
2. Document in log: what broke and why
3. Propose solution:
   - `git revert [commit]` for clean rollback
   - Manual fix if revert is complex
4. State: **"ROLLBACK NEEDED. Awaiting approval."**
5. Wait for human confirmation before executing

### Decision Fork Protocol

When facing non-obvious choices:

1. Document the decision point
2. List 2-3 options with:
   - Brief description
   - Pros
   - Cons
3. State your recommendation with reasoning
4. Mark checkpoint as WAIT

Example:
```markdown
### Decision: State Management Approach

**Option A: React Context**
- Pros: No additional dependencies, simple for small state
- Cons: Performance issues at scale, boilerplate for complex state

**Option B: Zustand**
- Pros: Minimal boilerplate, good performance, small bundle
- Cons: Additional dependency, team unfamiliarity

**Recommendation:** Option B (Zustand) — The app will have complex state interactions, and Zustand's simplicity will reduce bugs.

**WAIT FOR HUMAN INPUT**
```

### Log Archival Protocol

When `log.md` exceeds 50 entries:

1. Create `log_archive_[YYYY-MM].md`
2. Move all but last 10 entries to archive
3. Add note in `log.md`: "Earlier entries archived to log_archive_[date].md"

---

## TEMPLATES

### LLM_init.md

```markdown
# Project: [NAME]

**Repository:** [URL]
**Local Path:** [PATH]
**Created:** [DATE]

## Goal

[Clear description of what this project should accomplish. Be specific about the end state.]

## Success Criteria

- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]

## Constraints

- **Languages/Frameworks:** [e.g., Python 3.11+, FastAPI]
- **Must use:** [required libraries or patterns]
- **Must avoid:** [forbidden approaches]
- **Target platforms:** [e.g., Linux, Windows, macOS]

## Context

[Background information: why this exists, who it's for, related systems]

## Initial Task

[The first concrete thing to do after GECK initialization]
```

---

### LLM_GECK/env.md

```markdown
# Environment — [Project Name]

**Captured:** [TIMESTAMP]
**Last Updated:** [TIMESTAMP]

## Development Machine

- **OS:** [e.g., Windows 11, Ubuntu 22.04, macOS 14]
- **Shell:** [e.g., PowerShell, bash, zsh]

## Runtime Versions

[Adjust based on project stack]

| Tool | Version |
|------|---------|
| Python | x.y.z |
| Node | x.y.z |
| npm/yarn | x.y.z |
| [Other] | x.y.z |

## Package State

[Reference to lockfile or snapshot]
- See `requirements.txt` / `package-lock.json` / `Cargo.lock`

## Environment Variables

[List variable names that must be set, not values]

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Database connection |
| `API_KEY` | External service auth |

## Target Platforms

[From LLM_init.md constraints]

- [ ] Windows
- [ ] macOS
- [ ] Linux
- [ ] [Other]
```

---

### LLM_GECK/tasks.md

```markdown
# Tasks — [Project Name]

**Last Updated:** [TIMESTAMP]

## Legend

- `[ ]` — Not started
- `[x]` — Complete
- `[BLOCKED: reason]` — Cannot proceed until dependency resolved
- `[DECISION: topic]` — Awaiting human input

## Current Sprint

- [ ] Task description
- [ ] Task description
- [x] Completed task

## Backlog

- [ ] Future task
- [ ] Future task

## Completed (Recent)

- [x] Task that was done — Entry #N
- [x] Task that was done — Entry #N
```

---

### LLM_GECK/log.md

```markdown
# Session Log — [Project Name]

*Append only. Do not edit existing entries.*

---

## Entry #0 — [ISO TIMESTAMP]

### Summary
Project initialized. GECK structure created.

### Understood Goals
[Bullet summary of project goals from LLM_init.md]

### Questions/Ambiguities
[List anything unclear — or "None"]

### Initial Tasks
[What was added to tasks.md]

### Checkpoint
**Status:** WAIT — Awaiting confirmation to begin work.

---

## Entry #[N] — [ISO TIMESTAMP]

### Summary
[1-2 sentence description of what this turn accomplished]

### Actions
- [What you did]
- [What you did]

### Files Changed
- `path/to/file` — [brief description]
- `path/to/file` — [brief description]

### Commits
- `[hash]` — [commit message]

### Findings
[Anything notable: bugs discovered, design insights, surprises]
[Or "None"]

### Issues
[Problems encountered, with severity]
- MINOR: [description]
- MAJOR: [description]
- BLOCKER: [description]
[Or "None"]

### Checkpoint
**Status:** CONTINUE / WAIT / ROLLBACK
**Reason:** [If WAIT or ROLLBACK, explain why]

### Next
[Specific next action]
```

---

## Quick Reference

### Starting a Session
```
1. Read last log entry
2. Read tasks.md
3. Check LLM_init.md success criteria
4. Pick next task and begin
```

### Ending a Session
```
1. Commit all changes
2. Update tasks.md
3. Add log entry (if Standard/Heavy mode)
4. State session status
```

### Red Flags — Stop and Ask Human
- About to delete files or data
- Changing authentication/security code
- Modifying database schemas
- Uncertainty about requirements
- Multiple valid approaches with significant tradeoffs
- Any action that cannot be easily undone

---

## Changelog from v1.0

- Consolidated duplicate templates
- Added work modes (Light/Standard/Heavy) to reduce overhead
- Simplified file names (`LLM_log.md` → `log.md`, etc.)
- Removed `LLM_dpmp.md` (dependency tracking belongs in standard tooling)
- Added explicit git commit guidance
- Made environment capture stack-agnostic
- Added log archival protocol
- Switched to standard markdown checkbox syntax
- Added Quick Reference section
- Clarified checkpoint states (CONTINUE/WAIT/ROLLBACK)
