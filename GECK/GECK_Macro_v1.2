# GECK_Macro v1.2
## Garden of Eden Creation Kit — LLM-Assisted Development Protocol
### Protocol Version: 1.2

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
├── LLM_init.md          # Project goals and constraints (human-authored or generated)
└── LLM_GECK/
    ├── GECK_Inst.md     # AI agent instructions (copy from template)
    ├── log.md           # Append-only session log (long-term memory)
    ├── tasks.md         # Current task list (working memory)
    └── env.md           # Environment documentation
```

---

## FILE SPECIFICATIONS

### LLM_init.md
**Location:** Project root
**Purpose:** Human-defined project goals, constraints, and success criteria
**Created by:** Human (or GECK Generator tool)
**Modified by:** Human only
**AI behavior:** Read-only reference for goals and constraints

### LLM_GECK/GECK_Inst.md
**Location:** LLM_GECK folder
**Purpose:** Instructions for AI agents on how to operate within GECK protocol
**Created by:** Copy from template during Phase 0
**Modified by:** Never (reference document)
**AI behavior:** Read at session start, follow instructions

### LLM_GECK/log.md
**Location:** LLM_GECK folder
**Purpose:** Append-only session history (long-term memory)
**Created by:** AI during Phase 0
**Modified by:** AI (append only, never edit existing entries)
**AI behavior:** Read last entry at session start, append new entry at session end

### LLM_GECK/tasks.md
**Location:** LLM_GECK folder
**Purpose:** Current task list and status (working memory)
**Created by:** AI during Phase 0
**Modified by:** AI (update task statuses, add new tasks)
**AI behavior:** Read and update each session

### LLM_GECK/env.md
**Location:** LLM_GECK folder
**Purpose:** Environment documentation and target platforms
**Created by:** AI during Phase 0
**Modified by:** AI (when environment changes)
**AI behavior:** Reference for compatibility decisions

---

## PHASE 0: INITIALIZATION

*Run once per project. Skip to Phase 1 if `LLM_GECK/` folder exists.*

### Step 0.1 — Prerequisites (Human)

1. Create GitHub repository
2. Clone to local directory
3. Create `LLM_init.md` (manually or via GECK Generator)
4. Instruct AI: "Read LLM_init.md and initialize the GECK."

### Step 0.2 — GECK Initialization (AI)

1. Create `LLM_GECK/` folder

2. Copy `GECK_Inst.md` template into folder (see Templates section)

3. Create `LLM_GECK/env.md`:
   - Run environment detection commands appropriate to the stack
   - Document OS, language versions, package manager state
   - Note any environment variables that exist (names only, not values)
   - Record target platforms from `LLM_init.md`

4. Create `LLM_GECK/tasks.md` with initial tasks derived from `LLM_init.md`

5. Create `LLM_GECK/log.md` with Entry #0:
   - Understood goals (summarized from LLM_init.md)
   - Any ambiguities or questions
   - Proposed first actions

6. **Verify initialization:**
   ```
   - [ ] LLM_GECK/ folder exists
   - [ ] GECK_Inst.md copied from template
   - [ ] env.md captures current environment
   - [ ] tasks.md has initial task list
   - [ ] log.md has Entry #0
   ```

7. **STOP. State: "GECK initialized. Awaiting confirmation to proceed."**

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

1. Read `GECK_Inst.md` (first session only, or if unsure)
2. Read the last entry in `log.md`
3. Read `tasks.md` current state
4. Review SUCCESS CRITERIA in `LLM_init.md`

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

### Log Archival Protocol

When `log.md` exceeds 50 entries:

1. Create `log_archive_[YYYY-MM].md`
2. Move all but last 10 entries to archive
3. Add note in `log.md`: "Earlier entries archived to log_archive_[date].md"

---

## TEMPLATES

### GECK_Inst.md (AI Agent Instructions)

```markdown
# GECK Agent Instructions
## Quick Reference for AI Assistants

**Protocol Version:** 1.2

---

## On Session Start

1. **Check for GECK folder:** Does `LLM_GECK/` exist?
   - NO → Run Phase 0 initialization
   - YES → Continue to step 2

2. **Load context:**
   - Read `LLM_init.md` for goals and constraints
   - Read last entry in `LLM_GECK/log.md`
   - Read `LLM_GECK/tasks.md` for current work

3. **Identify next action** from tasks.md or human instruction

---

## File Responsibilities

| File | Read | Write | Rules |
|------|------|-------|-------|
| `LLM_init.md` | Always | Never | Human-owned, your north star |
| `GECK_Inst.md` | Session start | Never | These instructions |
| `log.md` | Last entry | Append only | Never edit past entries |
| `tasks.md` | Every turn | Update freely | Keep current |
| `env.md` | As needed | When env changes | Document, don't assume |

---

## Work Mode Selection

**Before starting work, select mode:**

- **Light mode** (single file, minor fix):
  - Just do it
  - Update tasks.md
  - No log entry needed

- **Standard mode** (feature, multi-file):
  - State plan first
  - Do work
  - Update tasks.md
  - Add log entry

- **Heavy mode** (architecture, risky):
  - State plan first
  - Consider branching
  - Do work
  - Update tasks.md
  - Add detailed log entry
  - May require WAIT checkpoint

---

## Checkpoint Rules

After each work cycle, evaluate:

| Situation | Checkpoint | Action |
|-----------|------------|--------|
| Work done, tests pass, stable | CONTINUE | Proceed to next task |
| Need human decision | WAIT | State question, stop |
| Unclear requirements | WAIT | Ask for clarification |
| Something broke | ROLLBACK | Document, propose fix, stop |
| Multiple valid approaches | WAIT | Present options, recommend one |

---

## Commit Rules

- Commit after each successful work cycle
- Use semantic commit messages: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`
- Stage specific files, not `git add .`
- Branch for experimental work

---

## Red Lines — Always Stop and Ask

- Deleting files or data
- Changing auth/security code
- Modifying database schemas
- Actions that cannot be undone
- Uncertainty about what user wants
- Significant architectural decisions

---

## Log Entry Format

When logging (Standard/Heavy mode), include:

1. **Summary** — What you did (1-2 sentences)
2. **Actions** — Bullet list of specific actions
3. **Files Changed** — Path and brief description
4. **Commits** — Hash and message
5. **Findings** — Anything notable (or "None")
6. **Issues** — Problems with severity (or "None")
7. **Checkpoint** — CONTINUE / WAIT / ROLLBACK
8. **Next** — What comes next

---

## Common Mistakes to Avoid

1. **Don't edit log.md history** — Append only
2. **Don't assume environment** — Check env.md or detect
3. **Don't skip task updates** — tasks.md is your working memory
4. **Don't make big decisions alone** — Use Decision Fork Protocol
5. **Don't commit without testing** — Verify work before commit
6. **Don't forget to state checkpoint** — Human needs to know status
```

---

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

| Tool | Version |
|------|---------|
| [Language] | x.y.z |
| [Package Manager] | x.y.z |
| [Other] | x.y.z |

## Package State

- See `requirements.txt` / `package-lock.json` / `Cargo.lock` / etc.

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `EXAMPLE_VAR` | Description |

## Target Platforms

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
- `[BLOCKED: reason]` — Cannot proceed
- `[DECISION: topic]` — Awaiting human input

## Current Sprint

- [ ] Task description
- [ ] Task description

## Backlog

- [ ] Future task

## Completed (Recent)

- [x] Task — Entry #N
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
[Bullet summary from LLM_init.md]

### Questions/Ambiguities
[List or "None"]

### Initial Tasks
[What was added to tasks.md]

### Checkpoint
**Status:** WAIT — Awaiting confirmation to begin work.

---
```

**Standard Entry Template:**

```markdown
## Entry #[N] — [ISO TIMESTAMP]

### Summary
[1-2 sentences]

### Actions
- [What you did]

### Files Changed
- `path/to/file` — [description]

### Commits
- `[hash]` — [message]

### Findings
[Notable items or "None"]

### Issues
[MINOR/MAJOR/BLOCKER: description, or "None"]

### Checkpoint
**Status:** CONTINUE / WAIT / ROLLBACK
**Reason:** [If not CONTINUE]

### Next
[Specific next action]
```

---

## Quick Reference

### Starting a Session
```
1. Read GECK_Inst.md (if first time or unsure)
2. Read last log entry
3. Read tasks.md
4. Check LLM_init.md success criteria
5. Pick next task and begin
```

### Ending a Session
```
1. Commit all changes
2. Update tasks.md
3. Add log entry (if Standard/Heavy mode)
4. State checkpoint status
```

---

## Changelog

### v1.2 (Current)
- Added `GECK_Inst.md` — dedicated AI agent instruction file
- Updated project structure to include GECK_Inst.md
- Added file specifications section
- Added GECK_Inst.md template with quick reference tables
- Updated Phase 0 to include GECK_Inst.md setup
- Updated Phase 1 to reference GECK_Inst.md at session start

### v1.1
- Consolidated duplicate templates
- Added work modes (Light/Standard/Heavy)
- Simplified file names
- Removed LLM_dpmp.md
- Added explicit git commit guidance
- Made environment capture stack-agnostic
- Added log archival protocol
- Switched to standard markdown checkbox syntax
- Added Quick Reference section

### v1.0
- Initial protocol release
