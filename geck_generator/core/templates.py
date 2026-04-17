"""Template definitions and rendering for GECK Generator (v1.3)."""

from datetime import datetime
from typing import Any

from jinja2 import Environment, BaseLoader, TemplateNotFound


# Main LLM_init.md template
LLM_INIT_TEMPLATE = """\
# Project: {{ project_name }}

**Repository:** {{ repo_url | default('Not specified', true) }}
**Local Path:** {{ local_path | default('Not specified', true) }}
{% if git_branch %}**Branch:** {{ git_branch }}
{% endif %}**Created:** {{ created_date }}
**GECK Protocol:** v1.3
**Context Budget:** {{ context_budget | default('medium', true) }}

## Goal

{{ goal }}

## Success Criteria

{% for criterion in success_criteria %}
- [ ] {{ criterion }}
{% endfor %}

## Constraints

- **Languages:** {{ languages | default('Not specified', true) }}
- **Frameworks:** {{ frameworks | join(', ') if frameworks else 'Not specified' }}
- **Must use:** {{ must_use | default('None specified', true) }}
- **Must avoid:** {{ must_avoid | default('None specified', true) }}
- **Target platforms:** {{ platforms | join(', ') if platforms else 'Not specified' }}

## Context

{{ context | default('No additional context provided.', true) }}

## Initial Task

{{ initial_task | default('Begin implementation based on the goal and success criteria above.', true) }}
"""

# GECK_Inst.md template (v1.3 — agent operating instructions)
GECK_INST_TEMPLATE = """\
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
"""

# env.md template
ENV_TEMPLATE = """\
# Environment — {{ project_name }}

**Captured:** {{ timestamp }}
**Last Updated:** {{ timestamp }}

## Development Machine

- **OS:** {{ os_info }}
- **Shell:** {{ shell_info }}

## Runtime Versions

| Tool | Version |
|------|---------|
{% for tool, version in runtime_versions.items() %}
| {{ tool }} | {{ version }} |
{% endfor %}

## Package State

- See `requirements.txt` / `package-lock.json` / `Cargo.lock` / etc.

## Environment Variables

| Variable | Purpose |
|----------|---------|
| (Document relevant variables here) |

## Target Platforms

{% for platform in all_platforms %}
- [{{ 'x' if platform in target_platforms else ' ' }}] {{ platform }}
{% endfor %}
"""

# tasks.md template (v1.3 — typed, state-machined)
TASKS_TEMPLATE = """\
# Tasks — {{ project_name }}

**Last Updated:** {{ timestamp }}

## Legend

- `[ ]` proposed/accepted (not started)
- `[~]` active (in progress)
- `[!:reason]` blocked (reason required)
- `[x]` completed (immutable; cite log entry)

State transitions are forward-only (or to blocked). Completed tasks are not re-opened —
file a new task instead.

## Current Sprint

{% if initial_tasks %}
{% for task in initial_tasks %}
- [ ] TASK-{{ '%03d' % (loop.index) }} | TYPE: feature | SCOPE: medium | OWNER: agent
  - {{ task }}
{% endfor %}
{% else %}
- [ ] TASK-001 | TYPE: feature | SCOPE: medium | OWNER: agent
  - Review project goals and begin implementation
{% endif %}

## Backlog

(empty)

## Completed (Recent)

(empty)
"""

# log.md template (v1.3 — tightened per-turn entries)
LOG_TEMPLATE = """\
# Session Log — {{ project_name }}

*Append only. Older entries roll into `log_archive/` once the active log exceeds the
context budget. Full history queryable via `log_index.jsonl`.*

---

## Entry #0 — {{ timestamp }} — touched: (init)
- Did: GECK v1.3 initialized
- Files: GECK/*
- State: WAIT
- Next: Await human confirmation to begin work
"""

# log_index.jsonl template — Entry #0 line, machine-readable
LOG_INDEX_TEMPLATE = """\
{"id":0,"ts":"{{ timestamp }}","tasks":[],"decisions":[],"learnings":[],"files":["GECK/*"],"state":"WAIT","summary":"GECK v1.3 initialized"}
"""

# decisions.md index template
DECISIONS_INDEX_TEMPLATE = """\
# Decisions — {{ project_name }}

*One line per decision record. Drill into the file for rationale.*
*Append-only. Mark superseded decisions with `(superseded by DECISION-NNN)` instead of deleting.*

(no decisions yet)
"""

# learnings.md index template
LEARNINGS_INDEX_TEMPLATE = """\
# Learnings — {{ project_name }}

*One line per learning record. Drill into the file for context.*
*Append-only. Future sessions read this index to avoid re-stepping on the same rakes.*

(no learnings yet)
"""

# GECK Repor agent instructions template
REPOR_TEMPLATE = """\
# GECK Repor Agent Instructions

## Project Information

- **Project Name:** {{ project_name }}
- **Working Directory:** {{ working_directory }}
- **GECK Folder:** {{ geck_folder }}
{% if project_git_repo %}
- **Project Git Repo:** {{ project_git_repo }}
{% endif %}

## Repositories to Explore

{% for repo in repositories %}
- {{ repo }}
{% endfor %}

## Exploration Goals

{% for goal in exploration_goals %}
- {{ goal }}
{% endfor %}

## Instructions

You are an AI exploration agent tasked with analyzing external repositories to find improvements, patterns, and ideas that can be applied to the project above.

### Your Mission

1. **Clone and Explore** each repository listed above
2. **Search for** implementations, patterns, and techniques related to the exploration goals
3. **Document Findings** in the GECK folder with:
   - Code snippets that demonstrate useful patterns
   - Links to specific files/lines in the source repos
   - Explanations of how each finding could apply to this project

### Output Format

Create a file `GECK/repor_findings.md` with:

```markdown
# Repor Findings — {{ project_name }}

**Generated:** [timestamp]

## Summary
[Brief overview of what was found]

## Findings by Goal

### [Goal 1]
- **Finding:** [description]
- **Source:** [repo/file:line]
- **Relevance:** [how it applies to this project]
- **Code Example:**
  ```
  [relevant code snippet]
  ```

[Repeat for each finding]

## Recommendations
[Prioritized list of improvements to implement]

## Next Steps
[Suggested actions based on findings]
```

### Guidelines

- Focus on patterns that match the project's technology stack
- Prioritize findings that address the exploration goals
- Include enough context for each finding to be actionable
- Note any dependencies or prerequisites for implementing findings
- Flag any potential conflicts with existing project architecture
"""


class DictLoader(BaseLoader):
    """Jinja2 loader that loads templates from a dictionary."""

    def __init__(self, templates: dict[str, str]):
        self.templates = templates

    def get_source(self, environment: Environment, template: str) -> tuple[str, str, callable]:
        if template not in self.templates:
            raise TemplateNotFound(template)
        source = self.templates[template]
        return source, template, lambda: True


class TemplateEngine:
    """Jinja2-based template rendering engine."""

    # Built-in templates
    TEMPLATES = {
        "llm_init": LLM_INIT_TEMPLATE,
        "geck_inst": GECK_INST_TEMPLATE,
        "env": ENV_TEMPLATE,
        "tasks": TASKS_TEMPLATE,
        "log": LOG_TEMPLATE,
        "log_index": LOG_INDEX_TEMPLATE,
        "decisions_index": DECISIONS_INDEX_TEMPLATE,
        "learnings_index": LEARNINGS_INDEX_TEMPLATE,
        "repor": REPOR_TEMPLATE,
    }

    def __init__(self):
        """Initialize the template engine with built-in templates."""
        self.env = Environment(
            loader=DictLoader(self.TEMPLATES),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._custom_templates: dict[str, str] = {}

    def render(self, template_name: str, variables: dict[str, Any]) -> str:
        """
        Render a template with the given variables.

        Args:
            template_name: Name of the template to render
            variables: Dictionary of variables to pass to the template

        Returns:
            Rendered template string
        """
        # Add default variables
        defaults = {
            "created_date": datetime.now().strftime("%Y-%m-%d"),
        }
        merged_vars = {**defaults, **variables}

        # Try custom templates first, then built-in
        if template_name in self._custom_templates:
            template = self.env.from_string(self._custom_templates[template_name])
        else:
            template = self.env.get_template(template_name)

        return template.render(**merged_vars)

    def render_string(self, template_string: str, variables: dict[str, Any]) -> str:
        """
        Render a template string directly.

        Args:
            template_string: Jinja2 template string
            variables: Dictionary of variables to pass to the template

        Returns:
            Rendered template string
        """
        defaults = {
            "created_date": datetime.now().strftime("%Y-%m-%d"),
        }
        merged_vars = {**defaults, **variables}

        template = self.env.from_string(template_string)
        return template.render(**merged_vars)

    def list_templates(self) -> list[str]:
        """
        List all available template names.

        Returns:
            List of template names
        """
        built_in = list(self.TEMPLATES.keys())
        custom = list(self._custom_templates.keys())
        return built_in + custom

    def add_template(self, name: str, template_string: str) -> None:
        """
        Add a custom template.

        Args:
            name: Name for the template
            template_string: Jinja2 template string
        """
        self._custom_templates[name] = template_string

    def load_template_from_file(self, name: str, filepath: str) -> None:
        """
        Load a custom template from a file.

        Args:
            name: Name for the template
            filepath: Path to the template file
        """
        with open(filepath, "r", encoding="utf-8") as f:
            template_string = f.read()
        self.add_template(name, template_string)
