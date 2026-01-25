# LLM_Github_Macro.md
## Protocol Version: 1.0

---

## PHASE 0: INITIALIZATION (Run Once Per Project)

### Step 0.1 — Clone Repository
```
Clone the repo at [REPO_URL] to local directory [TARGET_DIR]
```
*Execute in regular mode (not plan mode)*

### Step 0.2 — Environment Snapshot
After cloning, create `LLM_Environment.md` with:
- Python version (`python --version`)
- Node version if applicable (`node --version`)
- OS and shell (`uname -a` or equivalent)
- Package manager state (`pip list` or `pip freeze > requirements_snapshot.txt`)
- Any `.env` variables that are non-secret (document their *existence*, not values)

### Step 0.3 — Read Instructions
```
Read LLM_Initial_Instructions.md in full. Do not execute yet.
```

### Step 0.4 — Create Initial Log Entry
Add Entry #0 to `LLM_Log.md`:
- Timestamp
- Summary: "Project initialized. Instructions parsed."
- Understood Goals: [bullet list of what you understood]
- Ambiguities/Questions: [anything unclear—ASK before assuming]
- Proposed First Action: [what you plan to do in Phase 1]

**STOP. Wait for human confirmation before proceeding.**

---

## PHASE 1: EXECUTION LOOP (Repeat Until Done)

### Step 1.1 — Read Current State
```
Read the LAST 3 entries of LLM_Log.md and the SUCCESS CRITERIA section of LLM_Initial_Instructions.md
```

### Step 1.2 — Plan This Turn
Before writing ANY code:
1. State what you're about to do (1-2 sentences)
2. State what success looks like for THIS turn
3. State any assumptions you're making

### Step 1.3 — Execute
Do the work. Commit logically (small, atomic changes when possible).

### Step 1.4 — Log Entry
Add new entry to `LLM_Log.md`:
```markdown
---
## Entry #[N] — [ISO Timestamp]

### Actions Taken
- [Bullet list of what you did]

### Files Modified
- `path/to/file.py` — [one-line description of change]

### Findings
- [Anything notable: bugs found, design decisions, surprises]

### Issues/Blockers
- [Problems encountered, with severity: MINOR | MAJOR | BLOCKER]

### Checkpoint
- [ ] Working state: YES / NO / PARTIAL
- [ ] Tests passing: YES / NO / N/A
- [ ] Safe to continue: YES / WAIT FOR HUMAN

### Next Steps
1. [Specific next action]
2. [Contingency if #1 fails]

### Questions for Human (if any)
- [Decision points that need human input]
```

### Step 1.5 — Human Review Point
If `Safe to continue: WAIT FOR HUMAN`, STOP and await input.
Otherwise, return to Step 1.1.

---

## PHASE 2: COMPLETION

When SUCCESS CRITERIA from `LLM_Initial_Instructions.md` are met:

1. Add final log entry with:
   - Summary of all major changes
   - Known limitations or technical debt
   - Suggested future improvements

2. Generate `CHANGELOG.md` entry if appropriate

3. State: **"PROJECT GOALS ACHIEVED. Ready for human review."**

---

## ROLLBACK PROTOCOL

If a turn causes regression:
```
Identify the last known-good Entry # from LLM_Log.md.
State what broke and why.
Propose rollback strategy (git revert, manual fix, etc.)
Wait for human approval before reverting.
```

---

## DECISION FORK PROTOCOL

When facing a non-obvious choice (library selection, architecture pattern, etc.):
1. Document the fork in log entry
2. List options with pros/cons (max 3 options)
3. State your recommendation with reasoning
4. Mark `Safe to continue: WAIT FOR HUMAN`

---

## TEMPLATE: LLM_Initial_Instructions.md
```markdown
# Project: [NAME]
# Repo: [URL]
# Date Started: [DATE]

## GOAL
[2-3 sentences describing the end state]

## SUCCESS CRITERIA
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]

## CONSTRAINTS
- Python version: [X.Y]
- Must/Must Not use: [libraries, patterns]
- Platform targets: [Linux/Windows/Both]

## CONTEXT
[Any background the LLM needs: why this exists, who it's for, related projects]

## INITIAL TASK
[The first concrete thing to do after reading this]
```

---

## TEMPLATE: LLM_Log.md
```markdown
# LLM Activity Log — [Project Name]

*Append only. Do not edit existing entries.*

---

## Entry #0 — [Timestamp]
### Actions Taken
- Project initialized

### Understood Goals
- [From Initial Instructions]

### Next Steps
1. [First planned action]
```
