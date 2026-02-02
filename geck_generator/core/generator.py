"""Main generation logic for GECK Generator."""

import os
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from geck_generator.core.templates import TemplateEngine
from geck_generator.core.profiles import ProfileManager, ReporProfileManager


def _detect_environment() -> dict:
    """
    Detect current environment info: OS, shell, runtime versions.

    Returns:
        Dict with os_info, shell_info, runtime_versions, timestamp
    """
    # Detect OS
    os_name = platform.system()
    os_release = platform.release()
    os_info = f"{os_name} {os_release}"

    # Detect shell
    shell_info = "Unknown"
    if os_name == "Windows":
        # Check for PowerShell or cmd
        shell = os.environ.get("PSModulePath", "")
        if shell:
            shell_info = "PowerShell"
        else:
            shell_info = os.environ.get("COMSPEC", "cmd.exe")
    else:
        shell_info = os.environ.get("SHELL", "/bin/bash")
        # Extract just the shell name
        shell_info = Path(shell_info).name

    # Detect runtime versions
    runtime_versions = {}

    # Python version
    runtime_versions["Python"] = platform.python_version()

    # Try to detect other tools with timeout
    def get_version(cmd: list[str], timeout: float = 2.0) -> str | None:
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=(os_name == "Windows"),
            )
            if result.returncode == 0:
                return result.stdout.strip().split("\n")[0]
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        return None

    # Node.js
    node_version = get_version(["node", "--version"])
    if node_version:
        runtime_versions["Node.js"] = node_version.lstrip("v")

    # npm
    npm_version = get_version(["npm", "--version"])
    if npm_version:
        runtime_versions["npm"] = npm_version

    # git
    git_version = get_version(["git", "--version"])
    if git_version:
        # "git version 2.39.0" -> "2.39.0"
        parts = git_version.split()
        if len(parts) >= 3:
            runtime_versions["git"] = parts[2]

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "os_info": os_info,
        "shell_info": shell_info,
        "runtime_versions": runtime_versions,
        "timestamp": timestamp,
    }


class GECKGenerator:
    """Central class that orchestrates GECK file generation."""

    # Standard list of platforms for env.md
    ALL_PLATFORMS = ["Windows", "macOS", "Linux", "Docker", "iOS", "Android", "Web"]

    def __init__(self):
        """Initialize the generator with template engine and profile manager."""
        self.template_engine = TemplateEngine()
        self.profiles = ProfileManager()

    def generate(self, config: dict[str, Any]) -> str:
        """
        Generate LLM_init.md content from config dict.

        Args:
            config: Configuration dictionary with project details

        Returns:
            Generated LLM_init.md content as string
        """
        # Apply profile if specified
        if "profile" in config and config["profile"]:
            config = self.profiles.apply_profile(config, config["profile"])

        # Ensure required fields have defaults
        config.setdefault("project_name", "Untitled Project")
        config.setdefault("goal", "No goal specified.")
        config.setdefault("success_criteria", [])
        config.setdefault("platforms", [])

        # Render the template
        return self.template_engine.render("llm_init", config)

    def generate_to_file(self, config: dict[str, Any], output_path: Path | str) -> Path:
        """
        Generate and write LLM_init.md to file.

        Args:
            config: Configuration dictionary with project details
            output_path: Path to write the output file

        Returns:
            Path to the written file
        """
        output_path = Path(output_path)

        # Create parent directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate content
        content = self.generate(config)

        # Write to file
        output_path.write_text(content, encoding="utf-8")

        return output_path

    # Default task that is always included
    DEFAULT_INITIAL_TASK = "Compile task list from log and LLM_init entries"

    def _derive_initial_tasks(self, config: dict) -> list[str]:
        """
        Derive initial tasks from config (initial_task + success_criteria).

        The default task "Compile task list from log and LLM_init entries"
        is always included as the first task.

        Args:
            config: Configuration dictionary

        Returns:
            List of task strings
        """
        tasks = []

        # Always include the default task first
        tasks.append(self.DEFAULT_INITIAL_TASK)

        # Add user's initial task if provided
        initial_task = config.get("initial_task", "").strip()
        if initial_task:
            tasks.append(initial_task)

        # Add success criteria as tasks
        for criterion in config.get("success_criteria", []):
            if criterion.strip():
                tasks.append(criterion.strip())

        return tasks

    def _parse_goal_to_bullets(self, goal: str) -> list[str]:
        """
        Parse goal string into bullet point summaries.

        Args:
            goal: Goal string from config

        Returns:
            List of bullet point strings
        """
        if not goal:
            return ["No goal specified"]

        # Split by sentences or newlines
        bullets = []

        # First try splitting by newlines
        lines = goal.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line:
                # Remove leading bullet chars if present
                line = line.lstrip("-*").strip()
                if line:
                    bullets.append(line)

        # If no newline splits, use the whole goal
        if not bullets:
            bullets.append(goal.strip())

        return bullets

    def init_geck_folder(self, project_path: Path | str, config: dict[str, Any]) -> Path:
        """
        Create full GECK folder structure with all files.

        Creates:
        - GECK/LLM_init.md
        - GECK/GECK_Inst.md
        - GECK/env.md
        - GECK/tasks.md
        - GECK/log.md

        Args:
            project_path: Path to the project root
            config: Configuration dictionary with project details

        Returns:
            Path to the created GECK folder
        """
        project_path = Path(project_path)
        geck_folder = project_path / "GECK"

        # Create the GECK folder
        geck_folder.mkdir(parents=True, exist_ok=True)

        # Apply profile if specified
        if "profile" in config and config["profile"]:
            config = self.profiles.apply_profile(config, config["profile"])

        # Ensure required fields have defaults
        config.setdefault("project_name", "Untitled Project")
        config.setdefault("goal", "No goal specified.")
        config.setdefault("success_criteria", [])
        config.setdefault("platforms", [])

        # Detect environment
        env_info = _detect_environment()
        timestamp = env_info["timestamp"]

        # Derive initial tasks and understood goals
        initial_tasks = self._derive_initial_tasks(config)
        understood_goals = self._parse_goal_to_bullets(config.get("goal", ""))

        # 1. Write LLM_init.md inside GECK folder
        init_content = self.template_engine.render("llm_init", config)
        (geck_folder / "LLM_init.md").write_text(init_content, encoding="utf-8")

        # 2. Write GECK_Inst.md (static template, no variables needed)
        geck_inst_content = self.template_engine.render("geck_inst", {})
        (geck_folder / "GECK_Inst.md").write_text(geck_inst_content, encoding="utf-8")

        # 3. Write env.md (with detected environment)
        env_vars = {
            "project_name": config["project_name"],
            "timestamp": timestamp,
            "os_info": env_info["os_info"],
            "shell_info": env_info["shell_info"],
            "runtime_versions": env_info["runtime_versions"],
            "all_platforms": self.ALL_PLATFORMS,
            "target_platforms": config.get("platforms", []),
        }
        env_content = self.template_engine.render("env", env_vars)
        (geck_folder / "env.md").write_text(env_content, encoding="utf-8")

        # 4. Write tasks.md (with initial tasks)
        tasks_vars = {
            "project_name": config["project_name"],
            "timestamp": timestamp,
            "initial_tasks": initial_tasks,
        }
        tasks_content = self.template_engine.render("tasks", tasks_vars)
        (geck_folder / "tasks.md").write_text(tasks_content, encoding="utf-8")

        # 5. Write log.md (Entry #0 format)
        log_vars = {
            "project_name": config["project_name"],
            "timestamp": timestamp,
            "understood_goals": understood_goals,
            "initial_tasks": initial_tasks,
        }
        log_content = self.template_engine.render("log", log_vars)
        (geck_folder / "log.md").write_text(log_content, encoding="utf-8")

        return geck_folder

    def generate_from_profile(
        self,
        profile_name: str,
        project_name: str,
        goal: str,
        output_path: Path | str | None = None,
    ) -> str:
        """
        Quick generation from a profile with minimal config.

        Args:
            profile_name: Name of the preset profile
            project_name: Name of the project
            goal: Project goal description
            output_path: Optional path to write the file

        Returns:
            Generated content (also written to file if output_path provided)
        """
        config = {
            "profile": profile_name,
            "project_name": project_name,
            "goal": goal,
        }

        content = self.generate(config)

        if output_path:
            self.generate_to_file(config, output_path)

        return content

    def generate_from_template_file(
        self,
        template_path: Path | str,
        variables: dict[str, Any],
        output_path: Path | str | None = None,
    ) -> str:
        """
        Generate from a custom template file.

        Args:
            template_path: Path to the Jinja2 template file
            variables: Variables to pass to the template
            output_path: Optional path to write the output

        Returns:
            Generated content
        """
        template_path = Path(template_path)

        # Load the template
        template_content = template_path.read_text(encoding="utf-8")

        # Render
        content = self.template_engine.render_string(template_content, variables)

        # Write if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")

        return content

    def validate_config(self, config: dict[str, Any]) -> list[str]:
        """
        Validate a configuration dictionary.

        Args:
            config: Configuration to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check required fields
        if not config.get("project_name"):
            errors.append("Project name is required")

        if not config.get("goal"):
            errors.append("Project goal is required")

        # Check profile if specified
        if config.get("profile"):
            try:
                self.profiles.get_profile(config["profile"])
            except KeyError as e:
                errors.append(str(e))

        # Validate success criteria is a list
        if "success_criteria" in config:
            if not isinstance(config["success_criteria"], list):
                errors.append("Success criteria must be a list")

        # Validate platforms is a list
        if "platforms" in config:
            if not isinstance(config["platforms"], list):
                errors.append("Platforms must be a list")

        return errors

    def get_config_template(self) -> dict[str, Any]:
        """
        Get a template configuration dictionary with all fields.

        Returns:
            Dictionary with all config fields set to empty/default values
        """
        return {
            "project_name": "",
            "repo_url": "",
            "local_path": "",
            "profile": None,
            "goal": "",
            "success_criteria": [],
            "languages": "",
            "must_use": "",
            "must_avoid": "",
            "platforms": [],
            "context": "",
            "initial_task": "",
        }

    def generate_repor_instructions(
        self,
        working_directory: Path | str,
        repositories: list[str],
        exploration_goals: list[str],
        profile_name: str | None = None,
        output_path: Path | str | None = None,
    ) -> str:
        """
        Generate GECK Repor agent instructions.

        Args:
            working_directory: Path to the working directory
            repositories: List of git repository URLs to explore
            exploration_goals: List of exploration goal strings
            profile_name: Optional exploration profile name
            output_path: Optional path to write the output file

        Returns:
            Generated repor instructions as string
        """
        working_directory = Path(working_directory)

        # Derive project name from working directory
        project_name = working_directory.name

        # GECK folder path
        geck_folder = working_directory / "GECK"

        # Check for existing git repo in working directory
        project_git_repo = None
        git_config = working_directory / ".git" / "config"
        if git_config.exists():
            try:
                config_text = git_config.read_text(encoding="utf-8")
                # Parse remote URL from git config
                for line in config_text.split("\n"):
                    line = line.strip()
                    if line.startswith("url = "):
                        project_git_repo = line[6:].strip()
                        break
            except Exception:
                pass

        # Combine profile goals with custom goals
        all_goals = []
        if profile_name and profile_name != "none":
            repor_profiles = ReporProfileManager()
            profile_goals = repor_profiles.get_goals_for_profile(profile_name)
            all_goals.extend(profile_goals)
        all_goals.extend(exploration_goals)

        # Remove duplicates while preserving order
        seen = set()
        unique_goals = []
        for goal in all_goals:
            if goal not in seen:
                seen.add(goal)
                unique_goals.append(goal)

        # Prepare template variables
        template_vars = {
            "project_name": project_name,
            "working_directory": str(working_directory),
            "geck_folder": str(geck_folder),
            "project_git_repo": project_git_repo,
            "repositories": repositories,
            "exploration_goals": unique_goals if unique_goals else ["General code exploration and analysis"],
        }

        # Render the template
        content = self.template_engine.render("repor", template_vars)

        # Write to file if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")

        return content
