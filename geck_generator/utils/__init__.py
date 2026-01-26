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

__all__ = [
    "validate_url",
    "validate_path",
    "validate_project_name",
    "sanitize_filename",
    "create_shortcuts",
    "remove_shortcuts",
    "get_shortcut_info",
    "get_platform",
]
