"""Shared pytest fixtures for GECK Generator tests."""

import pytest
import tempfile
import shutil
from pathlib import Path

from geck_generator.core.generator import GECKGenerator
from geck_generator.core.profiles import ProfileManager, ReporProfileManager
from geck_generator.core.templates import TemplateEngine


@pytest.fixture
def generator():
    """Provide a GECKGenerator instance."""
    return GECKGenerator()


@pytest.fixture
def profile_manager():
    """Provide a ProfileManager instance."""
    return ProfileManager()


@pytest.fixture
def repor_profile_manager():
    """Provide a ReporProfileManager instance."""
    return ReporProfileManager()


@pytest.fixture
def template_engine():
    """Provide a TemplateEngine instance."""
    return TemplateEngine()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    tmpdir = tempfile.mkdtemp(prefix="geck_test_")
    yield Path(tmpdir)
    # Cleanup after test
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def sample_config():
    """Provide a sample valid configuration."""
    return {
        "project_name": "Test Project",
        "repo_url": "https://github.com/example/test",
        "local_path": "/tmp/test_project",
        "goal": "Build a test application that demonstrates GECK functionality",
        "success_criteria": [
            "All tests pass",
            "Documentation is complete",
            "Code coverage above 80%",
        ],
        "languages": "Python 3.11+",
        "must_use": "Type hints, pytest",
        "must_avoid": "Global variables",
        "platforms": ["Linux", "Windows", "macOS"],
        "context": "This is a test project for validation purposes.",
        "initial_task": "Set up project structure",
    }


@pytest.fixture
def minimal_config():
    """Provide a minimal valid configuration."""
    return {
        "project_name": "Minimal Project",
        "goal": "A minimal test goal for validation",
    }


@pytest.fixture
def sample_config_with_profile(sample_config):
    """Provide a sample configuration with a profile."""
    config = sample_config.copy()
    config["profile"] = "cli_tool"
    return config
