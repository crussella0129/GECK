"""Preset profile definitions for GECK Generator."""

from typing import Any


# Exploration profiles for GECK Repor feature
REPOR_PROFILES: dict[str, dict[str, Any]] = {
    "feature_discovery": {
        "name": "Feature Discovery",
        "description": "Find reusable components and patterns",
        "goals": [
            "Identify reusable utility functions",
            "Find well-documented APIs",
            "Locate configurable components",
            "Discover extensible patterns",
        ],
    },
    "performance_optimization": {
        "name": "Performance Optimization",
        "description": "Identify performance patterns",
        "goals": [
            "Find caching implementations",
            "Locate async/concurrent patterns",
            "Identify optimization techniques",
            "Discover efficient algorithms",
        ],
    },
    "security_audit": {
        "name": "Security Audit",
        "description": "Look for security patterns and practices",
        "goals": [
            "Find authentication implementations",
            "Locate input validation patterns",
            "Identify secure configuration practices",
            "Discover access control mechanisms",
        ],
    },
    "testing_patterns": {
        "name": "Testing Patterns",
        "description": "Find testing strategies and coverage",
        "goals": [
            "Identify testing frameworks used",
            "Find mock/stub patterns",
            "Locate integration test setups",
            "Discover test organization patterns",
        ],
    },
    "architecture_review": {
        "name": "Architecture Review",
        "description": "Analyze code organization",
        "goals": [
            "Identify architectural patterns (MVC, etc.)",
            "Find module organization patterns",
            "Locate dependency injection usage",
            "Discover error handling strategies",
        ],
    },
}


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
    "game": {
        "name": "Game Development",
        "description": "Video game or interactive entertainment project",
        "languages": "Python, C#, C++, GDScript, Lua",
        "frameworks": ["Pygame", "Godot", "Unity", "Unreal Engine", "Phaser", "LÖVE"],
        "platforms": ["Windows", "macOS", "Linux", "Web", "iOS", "Android"],
        "suggested_criteria": [
            "Game launches without errors",
            "Core gameplay loop functions correctly",
            "Player input is responsive and accurate",
            "Game state saves and loads correctly",
            "Performance meets target frame rate",
            "Audio plays correctly and synchronizes with visuals",
        ],
        "suggested_must_use": "Delta time for frame-independent movement, asset management, input abstraction layer",
        "suggested_must_avoid": "Frame-rate dependent physics, blocking operations in game loop, memory leaks in asset loading",
    },
    "os_development": {
        "name": "OS / Systems Development",
        "description": "Operating system, kernel, driver, or low-level systems programming",
        "languages": "C, C++, Rust, Assembly",
        "frameworks": ["UEFI", "GRUB", "Limine", "seL4", "Zephyr RTOS"],
        "platforms": ["Linux", "Windows", "macOS", "Custom/Bare Metal"],
        "suggested_criteria": [
            "Kernel boots successfully on target hardware/emulator",
            "Memory management operates correctly without leaks",
            "Interrupt handlers respond within timing requirements",
            "System calls function correctly",
            "Hardware drivers initialize and operate properly",
            "System remains stable under load",
        ],
        "suggested_must_use": "Memory-safe patterns, proper synchronization primitives, hardware abstraction layers",
        "suggested_must_avoid": "Undefined behavior, unhandled interrupts, unbounded loops in kernel space, memory corruption",
    },
    "blockchain": {
        "name": "Blockchain / DeFi",
        "description": "Cryptocurrency, smart contracts, or decentralized application development",
        "languages": "Solidity, Rust, Python, TypeScript, Move",
        "frameworks": ["Hardhat", "Foundry", "Anchor", "ethers.js", "web3.py", "OpenZeppelin"],
        "platforms": ["Ethereum", "Solana", "Polygon", "Arbitrum", "Linux", "Docker"],
        "suggested_criteria": [
            "Smart contracts compile without errors",
            "All contract tests pass",
            "No reentrancy vulnerabilities detected",
            "Gas optimization meets targets",
            "Contract upgrades work correctly",
            "Integration with wallets functions properly",
        ],
        "suggested_must_use": "Audited libraries (OpenZeppelin), comprehensive test coverage, formal verification where possible",
        "suggested_must_avoid": "Reentrancy patterns, unchecked external calls, floating pragma versions, storing sensitive data on-chain",
    },
    "embedded": {
        "name": "Embedded / Maker",
        "description": "Arduino, Raspberry Pi, Jetson, ESP32, or other dev board projects",
        "languages": "C, C++, Python, MicroPython, CircuitPython, Rust",
        "frameworks": ["Arduino", "PlatformIO", "ESP-IDF", "Raspberry Pi OS", "NVIDIA JetPack", "Zephyr"],
        "platforms": ["Arduino", "Raspberry Pi", "NVIDIA Jetson", "ESP32", "STM32", "Linux"],
        "suggested_criteria": [
            "Firmware compiles and uploads successfully",
            "Hardware peripherals initialize correctly",
            "Sensor readings are accurate within tolerance",
            "Communication protocols work reliably",
            "Power consumption meets requirements",
            "System recovers gracefully from errors",
        ],
        "suggested_must_use": "Watchdog timers, proper pin initialization, interrupt-safe code, hardware abstraction",
        "suggested_must_avoid": "Blocking delays in critical loops, floating inputs, unbounded memory allocation, ignoring hardware errata",
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


class ReporProfileManager:
    """Manager for GECK Repor exploration profiles."""

    def __init__(self):
        """Initialize with built-in exploration profiles."""
        self._profiles = REPOR_PROFILES.copy()

    def get_profile(self, name: str) -> dict[str, Any]:
        """
        Get an exploration profile by name.

        Args:
            name: Profile name (e.g., 'feature_discovery')

        Returns:
            Profile dictionary

        Raises:
            KeyError: If profile doesn't exist
        """
        if name in self._profiles:
            return self._profiles[name]
        raise KeyError(f"Repor profile '{name}' not found. Available: {self.list_profiles()}")

    def list_profiles(self) -> list[str]:
        """
        List all available exploration profile names.

        Returns:
            List of profile names
        """
        return list(self._profiles.keys())

    def get_profile_choices(self) -> list[tuple[str, str, str]]:
        """
        Get profile choices for dropdown.

        Returns:
            List of tuples: (key, display_name, description)
        """
        result = [("none", "Custom / No Profile", "Enter your own exploration goals")]
        for key, profile in self._profiles.items():
            result.append((key, profile["name"], profile.get("description", "")))
        return result

    def get_goals_for_profile(self, profile_name: str) -> list[str]:
        """
        Get the exploration goals for a profile.

        Args:
            profile_name: Name of the profile

        Returns:
            List of goal strings
        """
        if profile_name == "none" or not profile_name:
            return []
        profile = self.get_profile(profile_name)
        return profile.get("goals", [])
