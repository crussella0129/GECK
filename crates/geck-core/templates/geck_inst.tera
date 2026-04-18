# GECK Agent Instructions
## Quick Reference for AI Assistants

**Protocol Version:** 1.3

---

## On Session Start

1. **Check for `GECK/` folder:** if missing → run Phase 0 initialization, otherwise continue.

2. **Drift Check (mandatory).** Before reading the log, restate from `LLM_init.md`:
   - Project Goal (one sentence)
   - Active TASK-IDs (from `tasks.md`)
   - Constraints
   Then declare: `Drift Detected: YES | NO`. If YES, set checkpoint to WAIT and stop.

3. **Context budget self-check.** `LLM_init.md` declares the assumed budget (small/medium/large).
   If your actual context window is smaller than declared, downgrade to the smaller-budget rules
   and warn the human.

4. **Load context (in this order):**
   - `decisions.md` — read the index; drill into individual `decisions/*.md` files only as needed
   - `learnings.md` — read the index; drill into individual `learnings/*.md` files only as needed
   - `tasks.md` — full
   - `log.md` — last N entries (N from context budget) OR query `log_index.jsonl`
     for entries touching active TASK-IDs

---

## Memory Model

| Layer | File(s) | Purpose |
|-------|---------|---------|
| Goals | `LLM_init.md` | North star; never modify |
| Working memory | `tasks.md` | What to do now (typed, state-machined) |
| Semantic — decisions | `decisions.md` + `decisions/` | Why we chose what we chose |
| Semantic — learnings | `learnings.md` + `learnings/` | What broke before; what works |
| Episodic | `log.md` (active) | Narrative continuity |
| Episodic archive | `log_index.jsonl`, `log_archive/` | Full history; query, don't re-read |
| Environment | `env.md` | Compatibility constraints |

You do **not** re-read the full log every session. The index is your random-access layer.

---

## Context Budget → LOG_ACTIVE_ENTRIES

| Budget | Window | Active log entries |
|--------|--------|-------------------|
| `small` | 8k–32k | 3 |
| `medium` | 32k–128k | 10 |
| `large` | 128k+ | 25 |

When `log.md` exceeds `LOG_ACTIVE_ENTRIES + 5`, roll the oldest entries into
`log_archive/log_YYYY-MM.md`. `log_index.jsonl` always holds the full timeline.

---

## File Responsibilities

| File | Read | Write | Rules |
|------|------|-------|-------|
| `LLM_init.md` | Always | Never | Human-owned, your north star |
| `GECK_Inst.md` | Session start | Never | These instructions |
| `tasks.md` | Every turn | Every turn | Forward-only state transitions |
| `decisions.md` | Index every turn | When decision made | Append-only |
| `decisions/*.md` | On demand | When decision made | One file per decision; never delete |
| `learnings.md` | Index every turn | When learning emerges | Append-only |
| `learnings/*.md` | On demand | When learning emerges | One file per learning; never delete |
| `log.md` | Last N entries | Append every turn | Never edit past entries |
| `log_index.jsonl` | Query as needed | Append every turn | One JSON object per line |
| `log_archive/*.md` | On demand | Auto-rollover | Append-only |
| `env.md` | As needed | When env changes | Document, don't assume |

---

## Tasks

Format:
```
- [<state>] TASK-NNN | TYPE: <type> | SCOPE: <scope> | OWNER: <owner>
  - Description (nested bullets give the tree shape natively)
```

States: `[ ]` proposed/accepted, `[~]` active, `[!:reason]` blocked, `[x]` completed.
State transitions are forward-only (or to blocked). Completed tasks are immutable;
file a new task instead of reopening.

TYPE: `feature | fix | refactor | research | chore | docs | test`
SCOPE: `small | medium | large`
OWNER: `agent | human`

Log entries MUST cite the TASK-IDs they touched. Completing a task MUST cite the log entry.

---

## Decisions

Made a real decision? Create `decisions/DECISION-NNN-<slug>.md` with frontmatter:

```yaml
---
id: DECISION-NNN
title: <short title>
date: <ISO timestamp>
status: active
related-tasks: [TASK-NNN]
related-decisions: []
superseded-by: null
---
```

Body: lead with the decision, then **Why:** and **Consequences:**.

Append a one-line entry to `decisions.md`. Reference the DECISION-ID in the current log entry.
Heavy mode MUST log a DECISION-ID.

---

## Learnings

Something broke? A non-obvious approach worked? Create `learnings/LEARNING-NNN-<slug>.md`:

```yaml
---
id: LEARNING-NNN
title: <short title>
date: <ISO timestamp>
related-tasks: [TASK-NNN]
---
```

Body: lead with the **Rule**, then **Why:** (what broke / what was tried)
and **How to apply:** (when this kicks in).

Append a one-line entry to `learnings.md`. Reference the LEARNING-ID in the current log entry.

This is the protocol's loss-prevention mechanism — future sessions read the index alone
and avoid re-stepping on the same rakes.

---

## Per-Turn Log Entry (tightened)

```
## Entry #N — <ISO timestamp> — touched: TASK-001, TASK-004
- Did: <one line>
- Files: <comma-separated paths>
- State: CONTINUE | WAIT | ROLLBACK
- Refs: DECISION-002, LEARNING-001    (omit line if none)
- Next: <one line>
```

Then append the matching JSON line to `log_index.jsonl`:

```json
{"id":N,"ts":"...","tasks":["TASK-001"],"decisions":[],"learnings":[],"files":[],"state":"CONTINUE","summary":"..."}
```

Long-form context (rationale, code snippets, screenshots) belongs in commit messages
and PR descriptions, not duplicated in the log.

---

## Work Modes

| Mode | When | Required updates |
|------|------|------------------|
| **Light** | Single-file fix, typo, trivial chore | tasks.md only |
| **Standard** | Feature work, multi-file changes | tasks + log + log_index |
| **Heavy** | Architecture changes, new subsystems | All of Standard + DECISION-NNN |

---

## Checkpoint Rules

| Situation | Checkpoint | Action |
|-----------|------------|--------|
| Work done, tests pass, stable | CONTINUE | Proceed to next task |
| Need human decision | WAIT | State question, stop |
| Unclear requirements | WAIT | Ask for clarification |
| Something broke | ROLLBACK | Document, propose fix, stop |
| Multiple valid approaches | WAIT | Present options, recommend one |
| Drift detected at session start | WAIT | Describe discrepancy, stop |

---

## Commit Rules

- Commit after each successful work cycle
- Semantic messages: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`
- Stage specific files, not `git add .`
- Branch (`experiment/<name>`) for risky work

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

## Common Mistakes to Avoid

1. **Don't re-read the full log every session** — query `log_index.jsonl` instead
2. **Don't edit past log entries or completed tasks** — append-only / forward-only
3. **Don't bury decisions in log prose** — promote to `decisions/DECISION-NNN.md`
4. **Don't bury learnings in log prose** — promote to `learnings/LEARNING-NNN.md`
5. **Don't skip the Drift Check** — it's the cognitive checksum that prevents goal mutation
6. **Don't skip the index update** — `log_index.jsonl` is how future sessions navigate
7. **Don't make big decisions alone** — use Decision Fork Protocol
8. **Don't forget to state checkpoint** — human needs to know status
