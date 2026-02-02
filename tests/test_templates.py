"""Tests for geck_generator.core.templates module."""

import pytest
from datetime import datetime

from geck_generator.core.templates import (
    TemplateEngine,
    LLM_INIT_TEMPLATE,
    GECK_INST_TEMPLATE,
    ENV_TEMPLATE,
    TASKS_TEMPLATE,
    LOG_TEMPLATE,
    REPOR_TEMPLATE,
)


class TestTemplateEngine:
    """Tests for the TemplateEngine class."""

    def test_init_creates_jinja_environment(self, template_engine):
        """TemplateEngine should create a Jinja2 environment."""
        assert template_engine.env is not None

    def test_list_templates_returns_builtin(self, template_engine):
        """list_templates should return built-in template names."""
        templates = template_engine.list_templates()
        assert "llm_init" in templates
        assert "geck_inst" in templates
        assert "env" in templates
        assert "tasks" in templates
        assert "log" in templates
        assert "repor" in templates

    def test_render_llm_init_template(self, template_engine):
        """render should produce valid LLM_init content."""
        variables = {
            "project_name": "Test Project",
            "goal": "Build something amazing",
            "success_criteria": ["Criterion 1", "Criterion 2"],
            "languages": "Python",
            "platforms": ["Linux", "Windows"],
        }
        result = template_engine.render("llm_init", variables)

        assert "# Project: Test Project" in result
        assert "Build something amazing" in result
        assert "- [ ] Criterion 1" in result
        assert "- [ ] Criterion 2" in result
        assert "Python" in result

    def test_render_adds_default_date(self, template_engine):
        """render should add created_date by default."""
        variables = {"project_name": "Test"}
        result = template_engine.render("llm_init", variables)

        # Should contain today's date
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in result

    def test_render_geck_inst_template(self, template_engine):
        """render should produce valid GECK_Inst content."""
        result = template_engine.render("geck_inst", {})

        assert "GECK Agent Instructions" in result
        assert "Protocol Version" in result
        assert "Session Start" in result

    def test_render_env_template(self, template_engine):
        """render should produce valid env.md content."""
        variables = {
            "project_name": "Test",
            "timestamp": "2024-01-01 12:00:00",
            "os_info": "Windows 11",
            "shell_info": "PowerShell",
            "runtime_versions": {"Python": "3.11.0", "Node.js": "18.0.0"},
            "all_platforms": ["Windows", "Linux", "macOS"],
            "target_platforms": ["Windows"],
        }
        result = template_engine.render("env", variables)

        assert "Environment" in result
        assert "Windows 11" in result
        assert "Python" in result
        assert "3.11.0" in result

    def test_render_tasks_template(self, template_engine):
        """render should produce valid tasks.md content."""
        variables = {
            "project_name": "Test",
            "timestamp": "2024-01-01 12:00:00",
            "initial_tasks": ["Task 1", "Task 2"],
        }
        result = template_engine.render("tasks", variables)

        assert "Tasks" in result
        assert "- [ ] Task 1" in result
        assert "- [ ] Task 2" in result

    def test_render_log_template(self, template_engine):
        """render should produce valid log.md content."""
        variables = {
            "project_name": "Test",
            "timestamp": "2024-01-01 12:00:00",
            "understood_goals": ["Goal 1", "Goal 2"],
            "initial_tasks": ["Task 1"],
        }
        result = template_engine.render("log", variables)

        assert "Session Log" in result
        assert "Entry #0" in result
        assert "Goal 1" in result

    def test_render_repor_template(self, template_engine):
        """render should produce valid repor instructions."""
        variables = {
            "project_name": "Test",
            "working_directory": "/path/to/project",
            "geck_folder": "/path/to/project/GECK",
            "repositories": ["https://github.com/example/repo"],
            "exploration_goals": ["Find patterns", "Identify best practices"],
        }
        result = template_engine.render("repor", variables)

        assert "GECK Repor Agent Instructions" in result
        assert "Test" in result
        assert "https://github.com/example/repo" in result
        assert "Find patterns" in result

    def test_render_string_with_custom_template(self, template_engine):
        """render_string should render arbitrary template strings."""
        template = "Hello {{ name }}! Today is {{ created_date }}."
        result = template_engine.render_string(template, {"name": "World"})

        assert "Hello World!" in result
        # Should have today's date from defaults
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in result

    def test_add_template(self, template_engine):
        """add_template should register a custom template."""
        template_engine.add_template("custom", "Custom: {{ value }}")

        assert "custom" in template_engine.list_templates()
        result = template_engine.render("custom", {"value": "test"})
        assert result == "Custom: test"

    def test_render_handles_missing_optional_variables(self, template_engine):
        """render should handle missing optional variables gracefully."""
        variables = {
            "project_name": "Test",
            "goal": "Test goal",
            "success_criteria": [],
            # Missing: repo_url, local_path, languages, etc.
        }
        # Should not raise an exception
        result = template_engine.render("llm_init", variables)
        assert "Test" in result

    def test_render_with_empty_lists(self, template_engine):
        """render should handle empty lists."""
        variables = {
            "project_name": "Test",
            "goal": "Test goal",
            "success_criteria": [],
            "platforms": [],
        }
        result = template_engine.render("llm_init", variables)
        # Should still render without errors
        assert "Test" in result


class TestTemplateConstants:
    """Tests for template constant definitions."""

    def test_llm_init_template_has_required_sections(self):
        """LLM_INIT_TEMPLATE should have required sections."""
        assert "# Project:" in LLM_INIT_TEMPLATE
        assert "## Goal" in LLM_INIT_TEMPLATE
        assert "## Success Criteria" in LLM_INIT_TEMPLATE
        assert "## Constraints" in LLM_INIT_TEMPLATE

    def test_geck_inst_template_has_required_sections(self):
        """GECK_INST_TEMPLATE should have required sections."""
        assert "GECK Agent Instructions" in GECK_INST_TEMPLATE
        assert "Session Start" in GECK_INST_TEMPLATE
        assert "File Responsibilities" in GECK_INST_TEMPLATE
        assert "Checkpoint Rules" in GECK_INST_TEMPLATE

    def test_env_template_has_required_sections(self):
        """ENV_TEMPLATE should have required sections."""
        assert "Environment" in ENV_TEMPLATE
        assert "Development Machine" in ENV_TEMPLATE
        assert "Runtime Versions" in ENV_TEMPLATE

    def test_tasks_template_has_required_sections(self):
        """TASKS_TEMPLATE should have required sections."""
        assert "Tasks" in TASKS_TEMPLATE
        assert "Legend" in TASKS_TEMPLATE
        assert "Current Sprint" in TASKS_TEMPLATE
        assert "Backlog" in TASKS_TEMPLATE

    def test_log_template_has_required_sections(self):
        """LOG_TEMPLATE should have required sections."""
        assert "Session Log" in LOG_TEMPLATE
        assert "Entry #0" in LOG_TEMPLATE
        assert "Checkpoint" in LOG_TEMPLATE

    def test_repor_template_has_required_sections(self):
        """REPOR_TEMPLATE should have required sections."""
        assert "GECK Repor Agent Instructions" in REPOR_TEMPLATE
        assert "Repositories to Explore" in REPOR_TEMPLATE
        assert "Exploration Goals" in REPOR_TEMPLATE
        assert "Instructions" in REPOR_TEMPLATE

    def test_templates_use_geck_not_llm_geck(self):
        """Templates should reference GECK/ not LLM_GECK/."""
        # Check that we're using the new folder name
        assert "GECK/" in GECK_INST_TEMPLATE
        assert "GECK/" in REPOR_TEMPLATE
        # Make sure old name is not present
        assert "LLM_GECK/" not in GECK_INST_TEMPLATE
        assert "LLM_GECK/" not in REPOR_TEMPLATE
