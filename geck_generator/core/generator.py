"""Main generation logic for GECK Generator."""

import os
from pathlib import Path
from typing import Any

from geck_generator.core.templates import TemplateEngine
from geck_generator.core.profiles import ProfileManager


class GECKGenerator:
    """Central class that orchestrates GECK file generation."""

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

    def init_geck_folder(self, project_path: Path | str, config: dict[str, Any]) -> Path:
        """
        Create full LLM_GECK folder structure with all files.

        Creates:
        - LLM_GECK/LLM_init.md
        - LLM_GECK/README.md
        - LLM_GECK/context.md
        - LLM_GECK/history.md

        Args:
            project_path: Path to the project root
            config: Configuration dictionary with project details

        Returns:
            Path to the created LLM_GECK folder
        """
        project_path = Path(project_path)
        geck_folder = project_path / "LLM_GECK"

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

        # Generate and write LLM_init.md
        init_content = self.template_engine.render("llm_init", config)
        (geck_folder / "LLM_init.md").write_text(init_content, encoding="utf-8")

        # Generate and write README.md
        readme_content = self.template_engine.render("geck_readme", config)
        (geck_folder / "README.md").write_text(readme_content, encoding="utf-8")

        # Generate and write context.md
        context_content = self.template_engine.render("context", config)
        (geck_folder / "context.md").write_text(context_content, encoding="utf-8")

        # Generate and write history.md
        history_content = self.template_engine.render("history", config)
        (geck_folder / "history.md").write_text(history_content, encoding="utf-8")

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
