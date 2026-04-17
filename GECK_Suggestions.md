```markdown
# What Would Make GECK a 10/10
## Concrete, Actionable Steps to Reach Protocol Maturity

**Current Version:** GECK v1.2  
**Current Rating:** ~8.8 / 10  
**Target:** 10 / 10 (Protocol-complete, evolution-capable, still minimal)

This document outlines *specific, low-bloat, high-leverage changes* that would elevate GECK from an excellent protocol to a reference-grade system for long-running, agentic, and evolutionary CLI workflows.

The guiding constraint throughout:  
**Do not add tools unless the protocol itself demands them.**

---

## Principle of the 10/10 Version

A 10/10 GECK must satisfy all of the following:

1. **Deterministic authority** — No ambiguity about who decides what
2. **Typed cognition** — Tasks and decisions have stable identities and states
3. **Drift resistance** — Protocol detects and halts goal erosion
4. **Evolution readiness** — Fitness and mutation boundaries are explicit
5. **Human auditability** — All reasoning remains inspectable via text + Git

Everything below maps directly to one of these criteria.

---

## 1. Add Stable Identity to Tasks (High Impact, Low Cost)

### Problem
Tasks are currently prose + checkboxes. This limits:
- cross-referencing
- long-term reasoning
- agent-to-agent handoff
- fitness attribution

### Action
Introduce **Task IDs and lightweight typing** in `tasks.md`.

### Implementation
Update task format to:

```

* [ ] TASK-001 | TYPE: feature | SCOPE: medium | OWNER: agent
  Description of the task.

```

**Required fields:**
- `TASK-###` — Stable identifier
- `TYPE` — feature | fix | refactor | research | chore
- `SCOPE` — small | medium | large
- `OWNER` — agent | human

### Protocol Rule to Add
- Log entries **must reference Task IDs**
- Completed tasks **must cite the log entry number**

### Result
Tasks become addressable entities instead of transient prose.

---

## 2. Promote Decisions to First-Class Artifacts

### Problem
Decisions currently live implicitly inside logs. This obscures:
- rationale
- alternatives
- long-term consequences

### Action
Add an optional but canonical file: `GECK/decisions.md`

### File Purpose
- Immutable record of architectural and strategic decisions
- Separate *what was decided* from *what was done*

### Minimal Template
```

# Decisions — [Project Name]

## DECISION-001 — [Title]

**Date:** [ISO timestamp]
**Context:** Why this decision was needed
**Options Considered:**

1. Option A — Pros / Cons
2. Option B — Pros / Cons
   **Decision:** Chosen option
   **Rationale:** Why
   **Consequences:** What this enables or constrains

```

### Protocol Rule to Add
- Heavy mode **must** log a Decision ID when one is made
- Logs reference decisions, not re-explain them

### Result
GECK gains architectural memory without increasing verbosity.

---

## 3. Formalize Task State Transitions (Implicit → Explicit)

### Problem
Task status exists, but transitions are informal.

### Action
Define allowed task state transitions in the protocol.

### Allowed States
```

proposed → accepted → active → blocked → completed → archived

```

### Protocol Rule to Add
- Tasks may only move forward or to `blocked`
- `completed` tasks are immutable
- `blocked` tasks must include a reason

### Optional (Still Markdown)
```

* [BLOCKED: waiting on DECISION-003]

```

### Result
GECK now behaves like a **state machine**, not a checklist.

---

## 4. Add a Drift Check at Session Start (Critical for Agent Evolution)

### Problem
Agents can slowly reinterpret goals across sessions.

### Action
Add a mandatory **Drift Check** step to Phase 1.1 (Orient).

### Drift Check Requirements
At session start, the agent must explicitly restate:
1. Project Goal (from `LLM_init.md`)
2. Active Tasks (by ID)
3. Constraints

And then state:
```

Drift Detected: YES / NO
If YES: describe discrepancy and STOP.

```

### Protocol Rule to Add
- If drift is detected, checkpoint must be `WAIT`

### Result
GECK gains a cognitive checksum that prevents silent goal mutation.

---

## 5. Introduce a Minimal Fitness Specification (Evolution Enabler)

### Problem
GECK governs behavior but not evaluation.

### Action
Add an **optional Fitness Specification section** to `LLM_init.md`.

### Example
```

## Fitness Criteria (If Applicable)

* Accuracy of task completion
* Time-to-completion
* Token or compute efficiency
* Constraint violations (penalty)
* Human intervention frequency

```

### Protocol Rule to Add
- When GECK is used for agent iteration, agents **may not modify fitness criteria**
- Fitness evaluation is human- or harness-owned

### Result
GECK becomes a valid substrate for controlled evolution.

---

## 6. Explicitly Freeze the Genotype (Anti-Runaway Rule)

### Problem
Recursive agent systems fail when they mutate their own rules.

### Action
Add a **Genotype Freeze Rule** to GECK_Inst.md.

### Rule Text
```

The GECK protocol, fitness criteria, and success definitions
are immutable unless explicitly modified by a human.
Agents may optimize behavior, not rules.

```

### Result
Clear separation between:
- **Genotype** — GECK + goals
- **Phenotype** — agent behavior

This is the difference between evolution and corruption.

---

## 7. Add a Single Meta-Rule (The “Explain Yourself” Rule)

### Action
Add this invariant to the protocol:

> Any agent proposing a significant change must be able to explain,
> in plain language, why it believes the change improves outcomes,
> and cite evidence from logs, tasks, or measurements.

### Result
This prevents:
- deceptive optimization
- hallucinated improvement
- silent regressions

It also aligns GECK with scientific reasoning norms.

---

## What This Achieves

With these additions, GECK becomes:

- A **typed cognitive protocol**
- A **human-auditable memory system**
- A **safe substrate for agent iteration**
- A **filesystem-native evolutionary framework**

All without:
- databases
- vector stores
- orchestration frameworks
- autonomy theater

---

## Final Assessment

These changes would move GECK to:

**9.8–10.0 / 10**, depending on execution quality

Not because it does more —  
but because everything it does becomes *explicit, constrained, and durable*.

This is how serious systems age well.

---

## Closing Note

If GECK ever feels boring, you are doing it right.

Boring protocols are the ones that survive.
```
