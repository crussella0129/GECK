"""Utility functions for GECK Generator."""

from geck_generator.utils.validators import (
    validate_url,
    validate_path,
    validate_project_name,
    sanitize_filename,
)
from geck_generator.utils.shortcuts import (
    create_shortcuts,
    remove_shortcuts,
    get_shortcut_info,
    get_platform,
)
from geck_generator.utils.git_utils import (
    is_git_repo,
    suggest_repo_url,
    get_current_branch,
    get_branches,
    has_uncommitted_changes,
    checkout_branch,
    fetch_all,
)

__all__ = [
    "validate_url",
    "validate_path",
    "validate_project_name",
    "sanitize_filename",
    "create_shortcuts",
    "remove_shortcuts",
    "get_shortcut_info",
    "get_platform",
    "is_git_repo",
    "suggest_repo_url",
    "get_current_branch",
    "get_branches",
    "has_uncommitted_changes",
    "checkout_branch",
    "fetch_all",
]
