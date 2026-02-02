"""Integration tests for GECK Generator."""

import pytest
import subprocess
import sys
from pathlib import Path


class TestCLICommands:
    """Integration tests for CLI commands."""

    def test_version_flag(self):
        """--version should print version and exit cleanly."""
        result = subprocess.run(
            [sys.executable, "-m", "geck_generator", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "GECK Generator" in result.stdout

    def test_help_flag(self):
        """--help should print help text."""
        result = subprocess.run(
            [sys.executable, "-m", "geck_generator", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "geck_generator" in result.stdout.lower() or "usage" in result.stdout.lower()

    def test_list_profiles(self):
        """--list-profiles should list available profiles."""
        result = subprocess.run(
            [sys.executable, "-m", "geck_generator", "--list-profiles"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "web_app" in result.stdout
        assert "cli_tool" in result.stdout

    def test_list_templates(self):
        """--list-templates should list available templates."""
        result = subprocess.run(
            [sys.executable, "-m", "geck_generator", "--list-templates"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "llm_init" in result.stdout
        assert "geck_inst" in result.stdout

    def test_shortcut_info(self):
        """--shortcut-info should print shortcut information."""
        result = subprocess.run(
            [sys.executable, "-m", "geck_generator", "--shortcut-info"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "Shortcut Information" in result.stdout

    def test_profile_generation_stdout(self):
        """--profile should generate to stdout."""
        result = subprocess.run(
            [
                sys.executable, "-m", "geck_generator",
                "--profile", "cli_tool",
                "--project-name", "TestCLI",
                "--goal", "A test CLI tool for integration testing",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "TestCLI" in result.stdout
        assert "test CLI tool" in result.stdout

    def test_profile_generation_to_file(self, temp_dir):
        """--profile with -o should generate to file."""
        output_file = temp_dir / "test_output.md"

        result = subprocess.run(
            [
                sys.executable, "-m", "geck_generator",
                "--profile", "cli_tool",
                "--project-name", "TestCLI",
                "--goal", "A test CLI tool for integration testing",
                "-o", str(output_file),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert output_file.exists()

        content = output_file.read_text(encoding="utf-8")
        assert "TestCLI" in content

    def test_invalid_profile_fails(self):
        """--profile with invalid name should fail."""
        result = subprocess.run(
            [
                sys.executable, "-m", "geck_generator",
                "--profile", "nonexistent_profile",
                "--project-name", "Test",
                "--goal", "Test goal here",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode != 0
        assert "error" in result.stdout.lower() or "error" in result.stderr.lower()


class TestGECKFolderCreation:
    """Integration tests for GECK folder creation."""

    def test_full_geck_folder_structure(self, generator, sample_config, temp_dir):
        """Full GECK folder creation should create all required files."""
        geck_path = generator.init_geck_folder(temp_dir, sample_config)

        # Verify folder structure
        assert geck_path.exists()
        assert geck_path.name == "GECK"

        # All required files should be inside GECK folder
        required_files = [
            "LLM_init.md",
            "GECK_Inst.md",
            "env.md",
            "tasks.md",
            "log.md",
        ]
        for filename in required_files:
            filepath = geck_path / filename
            assert filepath.exists(), f"Missing file: {filename}"
            # Each file should have content
            assert filepath.stat().st_size > 0, f"Empty file: {filename}"

    def test_geck_folder_idempotent(self, generator, sample_config, temp_dir):
        """Creating GECK folder twice should not fail."""
        # First creation
        geck_path1 = generator.init_geck_folder(temp_dir, sample_config)
        assert geck_path1.exists()

        # Second creation (should overwrite)
        geck_path2 = generator.init_geck_folder(temp_dir, sample_config)
        assert geck_path2.exists()
        assert geck_path1 == geck_path2

    def test_geck_folder_content_consistency(self, generator, sample_config, temp_dir):
        """GECK folder files should have consistent content."""
        geck_path = generator.init_geck_folder(temp_dir, sample_config)

        # LLM_init.md should contain project name (now inside GECK folder)
        llm_init = (geck_path / "LLM_init.md").read_text(encoding="utf-8")
        assert sample_config["project_name"] in llm_init

        # tasks.md should reference the initial task
        tasks = (geck_path / "tasks.md").read_text(encoding="utf-8")
        if sample_config.get("initial_task"):
            assert sample_config["initial_task"] in tasks

        # log.md should have Entry #0
        log = (geck_path / "log.md").read_text(encoding="utf-8")
        assert "Entry #0" in log

        # env.md should have Python version
        env = (geck_path / "env.md").read_text(encoding="utf-8")
        assert "Python" in env

    def test_geck_folder_with_profile(self, generator, temp_dir):
        """GECK folder with profile should apply profile settings."""
        config = {
            "project_name": "Profile Test",
            "goal": "Test profile application in GECK folder",
            "profile": "web_app",
        }
        geck_path = generator.init_geck_folder(temp_dir, config)

        # LLM_init.md should have profile-suggested criteria (now inside GECK folder)
        llm_init = (geck_path / "LLM_init.md").read_text(encoding="utf-8")
        # web_app profile suggests these criteria
        assert "API" in llm_init or "endpoint" in llm_init.lower()


class TestReporIntegration:
    """Integration tests for GECK Repor feature."""

    def test_repor_instructions_complete(self, generator, temp_dir):
        """Repor instructions should be complete and valid."""
        repos = [
            "https://github.com/example/repo1",
            "https://github.com/example/repo2",
        ]
        goals = ["Find authentication patterns", "Identify best practices"]

        result = generator.generate_repor_instructions(
            working_directory=temp_dir,
            repositories=repos,
            exploration_goals=goals,
            profile_name="security_audit",
        )

        # Should have all required sections
        assert "GECK Repor Agent Instructions" in result
        assert "Project Information" in result
        assert "Repositories to Explore" in result
        assert "Exploration Goals" in result
        assert "Instructions" in result

        # Should include all repos
        for repo in repos:
            assert repo in result

        # Should include custom goals
        for goal in goals:
            assert goal in result

        # Should include profile goals (security_audit)
        assert "authentication" in result.lower()

    def test_repor_file_output(self, generator, temp_dir):
        """Repor instructions should write to file correctly."""
        output_path = temp_dir / "repor_test.md"

        generator.generate_repor_instructions(
            working_directory=temp_dir,
            repositories=["https://github.com/example/repo"],
            exploration_goals=["Test goal"],
            output_path=output_path,
        )

        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")
        assert "GECK Repor" in content


class TestModuleImports:
    """Tests for module imports and public API."""

    def test_core_imports(self):
        """Core modules should import successfully."""
        from geck_generator.core.generator import GECKGenerator
        from geck_generator.core.profiles import ProfileManager, ReporProfileManager
        from geck_generator.core.templates import TemplateEngine

        assert GECKGenerator is not None
        assert ProfileManager is not None
        assert ReporProfileManager is not None
        assert TemplateEngine is not None

    def test_utils_imports(self):
        """Utils modules should import successfully."""
        from geck_generator.utils.validators import (
            validate_url,
            validate_path,
            validate_project_name,
        )

        assert validate_url is not None
        assert validate_path is not None
        assert validate_project_name is not None

    def test_version_available(self):
        """Package version should be available."""
        from geck_generator import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""

    def test_complete_bootstrapper_workflow(self, generator, temp_dir):
        """Complete bootstrapper workflow should work."""
        # 1. Create config
        config = {
            "project_name": "E2E Test Project",
            "repo_url": "https://github.com/test/e2e",
            "local_path": str(temp_dir),
            "goal": "Test the complete bootstrapper workflow end to end",
            "success_criteria": [
                "All GECK files are created",
                "Content is correct",
                "No errors occur",
            ],
            "languages": "Python 3.11+",
            "platforms": ["Linux", "Windows"],
            "initial_task": "Verify GECK structure",
        }

        # 2. Validate config
        errors = generator.validate_config(config)
        assert errors == []

        # 3. Create GECK folder
        geck_path = generator.init_geck_folder(temp_dir, config)

        # 4. Verify all files exist inside GECK folder
        assert (geck_path / "LLM_init.md").exists()
        assert (geck_path / "GECK_Inst.md").exists()
        assert (geck_path / "env.md").exists()
        assert (geck_path / "tasks.md").exists()
        assert (geck_path / "log.md").exists()

        # 5. Verify content correctness
        llm_init = (geck_path / "LLM_init.md").read_text(encoding="utf-8")
        assert config["project_name"] in llm_init
        assert config["goal"] in llm_init
        for criterion in config["success_criteria"]:
            assert criterion in llm_init

        tasks = (geck_path / "tasks.md").read_text(encoding="utf-8")
        assert config["initial_task"] in tasks

    def test_complete_repor_workflow(self, generator, temp_dir):
        """Complete repor workflow should work."""
        # 1. Set up working directory (simulate existing project)
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "main.py").write_text("# Main file")

        # 2. Generate repor instructions
        output_path = temp_dir / "GECK_Repor_Instructions.md"
        content = generator.generate_repor_instructions(
            working_directory=temp_dir,
            repositories=[
                "https://github.com/pallets/flask",
                "https://github.com/fastapi/fastapi",
            ],
            exploration_goals=[
                "Find middleware patterns",
                "Identify error handling approaches",
            ],
            profile_name="architecture_review",
            output_path=output_path,
        )

        # 3. Verify output
        assert output_path.exists()
        assert "flask" in content.lower()
        assert "fastapi" in content.lower()
        assert "middleware" in content.lower()
        # Profile goals should be included
        assert "architectural patterns" in content.lower() or "architecture" in content.lower()
