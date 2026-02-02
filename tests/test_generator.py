"""Tests for geck_generator.core.generator module."""

import pytest
from pathlib import Path

from geck_generator.core.generator import GECKGenerator, _detect_environment


class TestDetectEnvironment:
    """Tests for the _detect_environment function."""

    def test_returns_dict(self):
        """_detect_environment should return a dictionary."""
        result = _detect_environment()
        assert isinstance(result, dict)

    def test_contains_required_keys(self):
        """_detect_environment should contain required keys."""
        result = _detect_environment()
        assert "os_info" in result
        assert "shell_info" in result
        assert "runtime_versions" in result
        assert "timestamp" in result

    def test_os_info_not_empty(self):
        """os_info should not be empty."""
        result = _detect_environment()
        assert result["os_info"]
        assert len(result["os_info"]) > 0

    def test_runtime_versions_includes_python(self):
        """runtime_versions should include Python version."""
        result = _detect_environment()
        assert "Python" in result["runtime_versions"]

    def test_timestamp_is_formatted(self):
        """timestamp should be a formatted string."""
        result = _detect_environment()
        # Should be in format like "2024-01-01 12:00:00"
        assert len(result["timestamp"]) > 10
        assert " " in result["timestamp"]


class TestGECKGenerator:
    """Tests for the GECKGenerator class."""

    def test_init_creates_template_engine(self, generator):
        """GECKGenerator should create a template engine."""
        assert generator.template_engine is not None

    def test_init_creates_profile_manager(self, generator):
        """GECKGenerator should create a profile manager."""
        assert generator.profiles is not None

    def test_generate_returns_string(self, generator, sample_config):
        """generate should return a string."""
        result = generator.generate(sample_config)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_includes_project_name(self, generator, sample_config):
        """generate should include project name in output."""
        result = generator.generate(sample_config)
        assert sample_config["project_name"] in result

    def test_generate_includes_goal(self, generator, sample_config):
        """generate should include goal in output."""
        result = generator.generate(sample_config)
        assert sample_config["goal"] in result

    def test_generate_includes_success_criteria(self, generator, sample_config):
        """generate should include success criteria in output."""
        result = generator.generate(sample_config)
        for criterion in sample_config["success_criteria"]:
            assert criterion in result

    def test_generate_with_minimal_config(self, generator, minimal_config):
        """generate should work with minimal configuration."""
        result = generator.generate(minimal_config)
        assert minimal_config["project_name"] in result
        assert minimal_config["goal"] in result

    def test_generate_with_profile(self, generator, sample_config_with_profile):
        """generate should apply profile when specified."""
        result = generator.generate(sample_config_with_profile)
        # Should still contain project name
        assert sample_config_with_profile["project_name"] in result

    def test_generate_sets_defaults(self, generator):
        """generate should set defaults for missing fields."""
        config = {}  # Empty config
        result = generator.generate(config)
        # Should use default project name
        assert "Untitled Project" in result

    def test_validate_config_returns_empty_for_valid(self, generator, sample_config):
        """validate_config should return empty list for valid config."""
        errors = generator.validate_config(sample_config)
        assert errors == []

    def test_validate_config_catches_missing_project_name(self, generator):
        """validate_config should catch missing project name."""
        config = {"goal": "Test goal"}
        errors = generator.validate_config(config)
        assert len(errors) > 0
        assert any("project name" in e.lower() for e in errors)

    def test_validate_config_catches_missing_goal(self, generator):
        """validate_config should catch missing goal."""
        config = {"project_name": "Test"}
        errors = generator.validate_config(config)
        assert len(errors) > 0
        assert any("goal" in e.lower() for e in errors)

    def test_validate_config_catches_invalid_profile(self, generator):
        """validate_config should catch invalid profile name."""
        config = {
            "project_name": "Test",
            "goal": "Test goal",
            "profile": "nonexistent_profile",
        }
        errors = generator.validate_config(config)
        assert len(errors) > 0

    def test_validate_config_catches_invalid_criteria_type(self, generator):
        """validate_config should catch non-list success_criteria."""
        config = {
            "project_name": "Test",
            "goal": "Test goal",
            "success_criteria": "not a list",
        }
        errors = generator.validate_config(config)
        assert len(errors) > 0

    def test_get_config_template(self, generator):
        """get_config_template should return a template dict."""
        template = generator.get_config_template()
        assert isinstance(template, dict)
        assert "project_name" in template
        assert "goal" in template
        assert "success_criteria" in template


class TestGECKGeneratorFileOperations:
    """Tests for GECKGenerator file operations."""

    def test_generate_to_file_creates_file(self, generator, sample_config, temp_dir):
        """generate_to_file should create the output file."""
        output_path = temp_dir / "LLM_init.md"
        result = generator.generate_to_file(sample_config, output_path)

        assert result == output_path
        assert output_path.exists()

    def test_generate_to_file_content_matches(self, generator, sample_config, temp_dir):
        """generate_to_file content should match generate output."""
        output_path = temp_dir / "LLM_init.md"
        generator.generate_to_file(sample_config, output_path)

        expected = generator.generate(sample_config)
        actual = output_path.read_text(encoding="utf-8")

        assert actual == expected

    def test_generate_to_file_creates_parent_dirs(self, generator, sample_config, temp_dir):
        """generate_to_file should create parent directories."""
        output_path = temp_dir / "subdir" / "nested" / "LLM_init.md"
        generator.generate_to_file(sample_config, output_path)

        assert output_path.exists()

    def test_init_geck_folder_creates_structure(self, generator, sample_config, temp_dir):
        """init_geck_folder should create complete GECK structure."""
        geck_path = generator.init_geck_folder(temp_dir, sample_config)

        # Check GECK folder exists
        assert geck_path.exists()
        assert geck_path.is_dir()
        assert geck_path.name == "GECK"

        # Check all required files exist inside GECK folder
        assert (geck_path / "LLM_init.md").exists()
        assert (geck_path / "GECK_Inst.md").exists()
        assert (geck_path / "env.md").exists()
        assert (geck_path / "tasks.md").exists()
        assert (geck_path / "log.md").exists()

    def test_init_geck_folder_llm_init_in_geck_folder(self, generator, sample_config, temp_dir):
        """init_geck_folder should place LLM_init.md inside GECK folder."""
        geck_path = generator.init_geck_folder(temp_dir, sample_config)

        llm_init = geck_path / "LLM_init.md"
        assert llm_init.exists()

        # Verify content
        content = llm_init.read_text(encoding="utf-8")
        assert sample_config["project_name"] in content

    def test_init_geck_folder_env_has_versions(self, generator, sample_config, temp_dir):
        """init_geck_folder should create env.md with runtime versions."""
        geck_path = generator.init_geck_folder(temp_dir, sample_config)

        env_content = (geck_path / "env.md").read_text(encoding="utf-8")
        assert "Python" in env_content

    def test_init_geck_folder_tasks_has_initial_tasks(self, generator, sample_config, temp_dir):
        """init_geck_folder should create tasks.md with initial tasks."""
        geck_path = generator.init_geck_folder(temp_dir, sample_config)

        tasks_content = (geck_path / "tasks.md").read_text(encoding="utf-8")
        # Should have the initial task from config
        assert sample_config["initial_task"] in tasks_content

    def test_init_geck_folder_log_has_entry_zero(self, generator, sample_config, temp_dir):
        """init_geck_folder should create log.md with Entry #0."""
        geck_path = generator.init_geck_folder(temp_dir, sample_config)

        log_content = (geck_path / "log.md").read_text(encoding="utf-8")
        assert "Entry #0" in log_content
        assert "WAIT" in log_content  # Initial checkpoint status


class TestGECKGeneratorReporFeature:
    """Tests for GECK Repor functionality."""

    def test_generate_repor_instructions_returns_string(self, generator, temp_dir):
        """generate_repor_instructions should return a string."""
        result = generator.generate_repor_instructions(
            working_directory=temp_dir,
            repositories=["https://github.com/example/repo"],
            exploration_goals=["Find patterns"],
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_repor_instructions_includes_repos(self, generator, temp_dir):
        """generate_repor_instructions should include repository URLs."""
        repos = [
            "https://github.com/example/repo1",
            "https://github.com/example/repo2",
        ]
        result = generator.generate_repor_instructions(
            working_directory=temp_dir,
            repositories=repos,
            exploration_goals=["Find patterns"],
        )
        for repo in repos:
            assert repo in result

    def test_generate_repor_instructions_includes_goals(self, generator, temp_dir):
        """generate_repor_instructions should include exploration goals."""
        goals = ["Find authentication patterns", "Identify caching strategies"]
        result = generator.generate_repor_instructions(
            working_directory=temp_dir,
            repositories=["https://github.com/example/repo"],
            exploration_goals=goals,
        )
        for goal in goals:
            assert goal in result

    def test_generate_repor_instructions_with_profile(self, generator, temp_dir):
        """generate_repor_instructions should merge profile goals."""
        result = generator.generate_repor_instructions(
            working_directory=temp_dir,
            repositories=["https://github.com/example/repo"],
            exploration_goals=["Custom goal"],
            profile_name="security_audit",
        )
        # Should include profile goals
        assert "authentication" in result.lower()
        # Should also include custom goal
        assert "Custom goal" in result

    def test_generate_repor_instructions_writes_file(self, generator, temp_dir):
        """generate_repor_instructions should write to file when path given."""
        output_path = temp_dir / "repor_instructions.md"
        generator.generate_repor_instructions(
            working_directory=temp_dir,
            repositories=["https://github.com/example/repo"],
            exploration_goals=["Find patterns"],
            output_path=output_path,
        )
        assert output_path.exists()

    def test_generate_repor_instructions_derives_project_name(self, generator, temp_dir):
        """generate_repor_instructions should derive project name from directory."""
        result = generator.generate_repor_instructions(
            working_directory=temp_dir,
            repositories=["https://github.com/example/repo"],
            exploration_goals=["Find patterns"],
        )
        # Project name should be derived from temp_dir name
        assert temp_dir.name in result

    def test_generate_repor_instructions_uses_geck_folder(self, generator, temp_dir):
        """generate_repor_instructions should reference GECK/ folder."""
        result = generator.generate_repor_instructions(
            working_directory=temp_dir,
            repositories=["https://github.com/example/repo"],
            exploration_goals=["Find patterns"],
        )
        # Should use GECK, not LLM_GECK
        assert "GECK" in result
        assert "LLM_GECK" not in result


class TestGECKGeneratorHelperMethods:
    """Tests for GECKGenerator helper methods."""

    def test_derive_initial_tasks_always_includes_default(self, generator):
        """_derive_initial_tasks should always include default task first."""
        config = {"initial_task": "Set up project", "success_criteria": []}
        tasks = generator._derive_initial_tasks(config)
        # Default task should be first
        assert tasks[0] == generator.DEFAULT_INITIAL_TASK
        # User's task should also be included
        assert "Set up project" in tasks

    def test_derive_initial_tasks_from_criteria(self, generator):
        """_derive_initial_tasks should include success criteria."""
        config = {
            "initial_task": "",
            "success_criteria": ["Criterion 1", "Criterion 2"],
        }
        tasks = generator._derive_initial_tasks(config)
        # Default task should be first
        assert tasks[0] == generator.DEFAULT_INITIAL_TASK
        assert "Criterion 1" in tasks
        assert "Criterion 2" in tasks

    def test_derive_initial_tasks_empty_config(self, generator):
        """_derive_initial_tasks should include default task even with empty config."""
        config = {"initial_task": "", "success_criteria": []}
        tasks = generator._derive_initial_tasks(config)
        assert len(tasks) == 1
        assert tasks[0] == generator.DEFAULT_INITIAL_TASK

    def test_parse_goal_to_bullets_single_line(self, generator):
        """_parse_goal_to_bullets should handle single line goals."""
        goal = "Build a web application"
        bullets = generator._parse_goal_to_bullets(goal)
        assert bullets == ["Build a web application"]

    def test_parse_goal_to_bullets_multiline(self, generator):
        """_parse_goal_to_bullets should split multiline goals."""
        goal = "First goal\nSecond goal\nThird goal"
        bullets = generator._parse_goal_to_bullets(goal)
        assert len(bullets) == 3
        assert "First goal" in bullets
        assert "Second goal" in bullets

    def test_parse_goal_to_bullets_strips_bullets(self, generator):
        """_parse_goal_to_bullets should strip existing bullet chars."""
        goal = "- First goal\n* Second goal"
        bullets = generator._parse_goal_to_bullets(goal)
        assert "First goal" in bullets
        assert "Second goal" in bullets
        # Should not have leading dashes/asterisks
        assert not any(b.startswith("-") or b.startswith("*") for b in bullets)

    def test_parse_goal_to_bullets_empty(self, generator):
        """_parse_goal_to_bullets should handle empty goal."""
        bullets = generator._parse_goal_to_bullets("")
        assert bullets == ["No goal specified"]
