"""Preset profile definitions for GECK Generator."""

from typing import Any


# Preset profiles for common project types
PROFILES: dict[str, dict[str, Any]] = {
    "web_app": {
        "name": "Web Application",
        "description": "Full-stack web application with frontend and backend",
        "languages": "Python 3.11+, JavaScript/TypeScript",
        "frameworks": ["FastAPI", "Flask", "Django", "React", "Vue"],
        "platforms": ["Linux", "Windows", "macOS", "Docker"],
        "suggested_criteria": [
            "API endpoints return correct responses",
            "Frontend renders without errors",
            "Authentication works correctly",
            "Database operations complete successfully",
            "Application handles errors gracefully",
        ],
        "suggested_must_use": "Type hints, async/await where appropriate",
        "suggested_must_avoid": "Hardcoded credentials, synchronous blocking calls in async context",
    },
    "cli_tool": {
        "name": "CLI Tool",
        "description": "Command-line interface application",
        "languages": "Python 3.11+",
        "frameworks": ["Click", "Typer", "argparse"],
        "platforms": ["Linux", "Windows", "macOS"],
        "suggested_criteria": [
            "All commands execute without errors",
            "Help text is accurate and complete",
            "Exit codes are correct",
            "Input validation works properly",
            "Error messages are clear and actionable",
        ],
        "suggested_must_use": "Type hints, proper exit codes",
        "suggested_must_avoid": "Hardcoded paths, platform-specific assumptions",
    },
    "data_science": {
        "name": "Data Science / ML",
        "description": "Data analysis, machine learning, or AI project",
        "languages": "Python 3.11+",
        "frameworks": ["pandas", "numpy", "scikit-learn", "pytorch", "tensorflow"],
        "platforms": ["Linux", "Windows", "macOS"],
        "suggested_criteria": [
            "Data pipeline runs end-to-end",
            "Model achieves target metrics",
            "Results are reproducible",
            "Data preprocessing handles edge cases",
            "Visualizations render correctly",
        ],
        "suggested_must_use": "Virtual environments, requirements.txt or pyproject.toml",
        "suggested_must_avoid": "Absolute paths to data, training on test data",
    },
    "api_backend": {
        "name": "API Backend",
        "description": "REST or GraphQL API service",
        "languages": "Python 3.11+",
        "frameworks": ["FastAPI", "Flask", "Django REST Framework"],
        "platforms": ["Linux", "Docker"],
        "suggested_criteria": [
            "All endpoints respond correctly",
            "Error handling returns proper status codes",
            "Database operations complete successfully",
            "Authentication/authorization works correctly",
            "API documentation is accurate",
        ],
        "suggested_must_use": "OpenAPI/Swagger documentation, proper HTTP status codes",
        "suggested_must_avoid": "SQL injection vulnerabilities, exposing sensitive data in responses",
    },
    "automation_script": {
        "name": "Automation Script",
        "description": "Scripts for task automation and batch processing",
        "languages": "Python 3.11+",
        "frameworks": [],
        "platforms": ["Linux", "Windows", "macOS"],
        "suggested_criteria": [
            "Script completes without errors",
            "Output is in expected format",
            "Edge cases are handled",
            "Logging provides useful information",
            "Script is idempotent where appropriate",
        ],
        "suggested_must_use": "Logging, error handling, clear documentation",
        "suggested_must_avoid": "Destructive operations without confirmation, hardcoded secrets",
    },
    "library": {
        "name": "Python Library/Package",
        "description": "Reusable Python library or package",
        "languages": "Python 3.11+",
        "frameworks": [],
        "platforms": ["Linux", "Windows", "macOS"],
        "suggested_criteria": [
            "All public APIs have docstrings",
            "Unit tests pass with good coverage",
            "Package installs correctly via pip",
            "Type hints are complete and accurate",
            "Documentation is clear and complete",
        ],
        "suggested_must_use": "Type hints, docstrings, pyproject.toml",
        "suggested_must_avoid": "Breaking changes without version bump, circular imports",
    },
    "microservice": {
        "name": "Microservice",
        "description": "Containerized microservice for distributed systems",
        "languages": "Python 3.11+",
        "frameworks": ["FastAPI", "Flask", "gRPC"],
        "platforms": ["Docker", "Kubernetes"],
        "suggested_criteria": [
            "Service starts and responds to health checks",
            "All endpoints function correctly",
            "Service handles failures gracefully",
            "Logging and metrics are properly configured",
            "Container builds and runs successfully",
        ],
        "suggested_must_use": "Health check endpoints, structured logging, environment variables for config",
        "suggested_must_avoid": "Storing state locally, hardcoded service URLs",
    },
}


class ProfileManager:
    """Manager for preset project profiles."""

    def __init__(self):
        """Initialize the profile manager with built-in profiles."""
        self._profiles = PROFILES.copy()
        self._custom_profiles: dict[str, dict[str, Any]] = {}

    def get_profile(self, name: str) -> dict[str, Any]:
        """
        Get a profile by name.

        Args:
            name: Profile name (e.g., 'web_app', 'cli_tool')

        Returns:
            Profile dictionary

        Raises:
            KeyError: If profile doesn't exist
        """
        if name in self._custom_profiles:
            return self._custom_profiles[name]
        if name in self._profiles:
            return self._profiles[name]
        raise KeyError(f"Profile '{name}' not found. Available: {self.list_profiles()}")

    def list_profiles(self) -> list[str]:
        """
        List all available profile names.

        Returns:
            List of profile names
        """
        return list(self._profiles.keys()) + list(self._custom_profiles.keys())

    def get_profile_names_with_descriptions(self) -> list[tuple[str, str, str]]:
        """
        Get profile names with their display names and descriptions.

        Returns:
            List of tuples: (key, display_name, description)
        """
        result = []
        for key, profile in self._profiles.items():
            result.append((key, profile["name"], profile.get("description", "")))
        for key, profile in self._custom_profiles.items():
            result.append((key, profile["name"], profile.get("description", "")))
        return result

    def apply_profile(self, base_config: dict[str, Any], profile_name: str) -> dict[str, Any]:
        """
        Apply a profile to a base configuration.

        Profile values fill in missing fields but don't override existing values.

        Args:
            base_config: Base configuration dictionary
            profile_name: Name of the profile to apply

        Returns:
            Merged configuration dictionary
        """
        profile = self.get_profile(profile_name)
        result = base_config.copy()

        # Map profile fields to config fields
        mappings = {
            "languages": "languages",
            "platforms": "platforms",
            "suggested_criteria": "success_criteria",
            "suggested_must_use": "must_use",
            "suggested_must_avoid": "must_avoid",
        }

        for profile_key, config_key in mappings.items():
            if profile_key in profile:
                if config_key not in result or not result[config_key]:
                    result[config_key] = profile[profile_key]

        # Add profile metadata
        result["_profile_name"] = profile_name
        result["_profile_display_name"] = profile.get("name", profile_name)

        return result

    def add_profile(self, name: str, profile: dict[str, Any]) -> None:
        """
        Add a custom profile.

        Args:
            name: Profile name/key
            profile: Profile configuration dictionary
        """
        if "name" not in profile:
            profile["name"] = name.replace("_", " ").title()
        self._custom_profiles[name] = profile

    def get_frameworks_for_profile(self, profile_name: str) -> list[str]:
        """
        Get the list of frameworks for a profile.

        Args:
            profile_name: Name of the profile

        Returns:
            List of framework names
        """
        profile = self.get_profile(profile_name)
        return profile.get("frameworks", [])
