"""Template definitions and rendering for GECK Generator."""

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

# GECK_Inst.md template (static - AI agent instructions from v1.2 spec)
GECK_INST_TEMPLATE = """\
# GECK Agent Instructions
## Quick Reference for AI Assistants

**Protocol Version:** 1.2

---

## On Session Start

1. **Check for GECK folder:** Does `GECK/` exist?
   - NO → Run Phase 0 initialization
   - YES → Continue to step 2

2. **Load context:**
   - Read `LLM_init.md` for goals and constraints
   - Read last entry in `GECK/log.md`
   - Read `GECK/tasks.md` for current work

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

# tasks.md template
TASKS_TEMPLATE = """\
# Tasks — {{ project_name }}

**Last Updated:** {{ timestamp }}

## Legend

- `[ ]` — Not started
- `[x]` — Complete
- `[BLOCKED: reason]` — Cannot proceed
- `[DECISION: topic]` — Awaiting human input

## Current Sprint

{% if initial_tasks %}
{% for task in initial_tasks %}
- [ ] {{ task }}
{% endfor %}
{% else %}
- [ ] Review project goals and begin implementation
{% endif %}

## Backlog

(empty)

## Completed (Recent)

(empty)
"""

# log.md template
LOG_TEMPLATE = """\
# Session Log — {{ project_name }}

*Append only. Do not edit existing entries.*

---

## Entry #0 — {{ timestamp }}

### Summary
Project initialized. GECK structure created.

### Understood Goals
{% for goal_item in understood_goals %}
- {{ goal_item }}
{% endfor %}

### Questions/Ambiguities
None

### Initial Tasks
{% for task in initial_tasks %}
- {{ task }}
{% endfor %}

### Checkpoint
**Status:** WAIT — Awaiting confirmation to begin work.

---
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
