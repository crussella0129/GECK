# GenSys_Macro.md
## Protocol Version: 1.0

---

### **Overall Structure**
- LLM_init.md # Intital instructions, added to the repository before LLM_GenSys is run. See LLM_init.md Template Below.
- LLM_GenSys (Folder)
   - LLM_log.md # Append-only ledger that contains a timestamp of each action taken, as well as a summary of understood goals, and a breif description of next steps. See LLM_Log.md Template Below. 
   - LLM_ckls.md # File that acts as a "current tasks" checklist (almost like a RAM, compared to the Long Term Memory of LLM_log.md).
   - LLM_env.md # File that records the Hw/Fw/Sw environment being developed on, as well as what environment the end product is expected to run on.
   - LLM_dpmp.md # File that records any notable or otherwise unrecorded dependencies of any files or folders added throughout the project.


## PHASE 0: INITIALIZATION (Run Once Per Project - Skip to "Phase 1" if LLM_GenSys Folder Exists)

### Step 0.0 — Create Repository on Github and Establish Local Directory

- Human Instructions:
   - Ensure SSH Keys for GitHub and Local System that Target Directory will exist on are established and shared.
   - Create GitHub Repo for project and record the URL.
   - Create target directory for project and record path.
   - Create LLM_init.md either in the Target Directory, or directly in the GitHub Repo via a browser, according to the template attached at the end of this document.

### Step 0.1 — Instruct Agent to Clone Repository and Read LLM_init.md
```
Clone the repo at [REPO_URL] to local directory [TARGET_DIR]. Read LLM_Init.md in full. Do not execute yet.
```
### Step 0.2 — LLM_GenSys Folder Creation, GenSys "Memory Document" Creation, and Environment Snapshot
- After cloning and reading LLM_Init.md, create the `LLM_Gensys` Folder and create the following files within the folder:
   - `LLM_log.md`
      - Add Entry #0 to `LLM_log.md` in the format of the `LLM_log.md` template at the end of this document:
         - Timestamp
         - Summary: "Project initialized. Instructions parsed."
         - Understood Goals: [bullet list of what you understood]
         - Ambiguities/Questions: [anything unclear—ASK before assuming]
         - Proposed Tasks: [what tasks will be added to `LLM_ckls.md` as the first tasks to handle]
   - `LLM_ckls`
      - Add the proposed tasks 
  
   - `LLM_env.md` with:
      - Python version (`python --version`)
      - Node version if applicable (`node --version`)
      - OS and shell (`uname -a` or equivalent)
      - Package manager state (`pip list` or `pip freeze > requirements_snapshot.txt`)
      - Any `.env` variables that are non-secret (document their *existence*, not values)
      - Desired system compatibility, by indicating what environments this application _should_ run on to consider when developing (Eg. Windows 11, MacOS, Arch, Fedora, Debian, iOS, etc...). *LLM will pull this instruction from LLM_Init.md*
   

### Step 0.3 — Create Initial Log and Checklist Entry
- Add Entry #0 to `LLM_log.md` in the format of the `LLM_log.md` template at the end of this document:
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
- Before writing ANY code:
   1. State what you're about to do (1-2 short paragraphs)
   2. State the dependencies of any files you plan to work on (after searching those dependencies) and explain how your changes will not create dependency errors. 
   3. State what success looks like for THIS turn
   4. State any assumptions you're making
   

### Step 1.3 — Execute
Do the work. Do not Commit or Push yet.

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

When SUCCESS CRITERIA from `LLM_init.md` are met:

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

## TEMPLATE: LLM_init.md
```markdown
# Project: [NAME]
# Repo_URL: [URL]
# Target_Dir: [Path}
# Date Started: [DATE]

## GOAL
[As much detail as possible describing the end state]

## SUCCESS CRITERIA
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]

## CONSTRAINTS + INTENDED ENVIRONMENT
- Python version: [X.Y]
- Must/Must Not use: [libraries, patterns]
- Platform targets: [Linux/Windows/Both]

## CONTEXT
[Any background the LLM needs: why this exists, who it's for, related projects]

## INITIAL TASK
[The first concrete thing to do after reading this]
```

---
## TEMPLATE: LLM_log.md
```markdown
# LLM Checklist — [Project Name]

*Append Only - DO NOT edit existing entries. Post corrections in further entries, referecing the affected entry number and section.

---

## Entry #[Number] — Timestamp: [Date and Time]

### Actions Taken
- Project initialized

### Understood Goals
- [From Initial Instructions]

### Next Steps
1. [First planned action]
```
---
## TEMPLATE: LLM_ckls.md
```markdown
# Project: [NAME]
# Repo_URL: [URL]
# Target_Dir: [Path}
# Date Started: [DATE]

*Create one task per line of document (larger tasks may have more than one line) and delineate each task with a []. When the task is complete, change that symbol to [X], if the task failed, then [Failed] and indicate a reason in the LLM_Log*

## GOAL
[As much detail as possible describing the end state]

## SUCCESS CRITERIA
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]

## CONSTRAINTS + INTENDED ENVIRONMENT
- Python version: [X.Y]
- Must/Must Not use: [libraries, patterns]
- Platform targets: [Linux/Windows/Both]

## CONTEXT
[Any background the LLM needs: why this exists, who it's for, related projects]

## INITIAL TASK
[The first concrete thing to do after reading this]
```
---

