"""Input validation helpers for GECK Generator."""

import re
import string
from pathlib import Path
from urllib.parse import urlparse


def validate_url(url: str) -> tuple[bool, str]:
    """
    Validate a URL string.

    Args:
        url: URL string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return True, ""  # Empty URLs are allowed (optional field)

    try:
        result = urlparse(url)
        if not result.scheme:
            return False, "URL must include a scheme (e.g., https://)"
        if not result.netloc:
            return False, "URL must include a domain"
        if result.scheme not in ("http", "https", "git", "ssh"):
            return False, f"Unsupported URL scheme: {result.scheme}"
        return True, ""
    except Exception as e:
        return False, f"Invalid URL: {e}"


def validate_path(path: str, must_exist: bool = False, must_be_dir: bool = False) -> tuple[bool, str]:
    """
    Validate a file system path.

    Args:
        path: Path string to validate
        must_exist: Whether the path must exist
        must_be_dir: Whether the path must be a directory

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path:
        return True, ""  # Empty paths are allowed (optional field)

    try:
        p = Path(path)

        # Check for invalid characters (Windows-specific)
        invalid_chars = '<>"|?*'
        if any(c in str(p) for c in invalid_chars):
            return False, f"Path contains invalid characters: {invalid_chars}"

        if must_exist and not p.exists():
            return False, f"Path does not exist: {path}"

        if must_be_dir and p.exists() and not p.is_dir():
            return False, f"Path is not a directory: {path}"

        return True, ""
    except Exception as e:
        return False, f"Invalid path: {e}"


def validate_project_name(name: str) -> tuple[bool, str]:
    """
    Validate a project name.

    Args:
        name: Project name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Project name is required"

    if len(name) > 100:
        return False, "Project name must be 100 characters or less"

    if len(name) < 2:
        return False, "Project name must be at least 2 characters"

    # Allow alphanumeric, spaces, hyphens, underscores
    if not re.match(r'^[\w\s\-]+$', name):
        return False, "Project name can only contain letters, numbers, spaces, hyphens, and underscores"

    return True, ""


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """
    Sanitize a string for use as a filename.

    Args:
        name: String to sanitize
        max_length: Maximum length for the result

    Returns:
        Sanitized filename-safe string
    """
    # Replace spaces with underscores
    result = name.replace(" ", "_")

    # Remove invalid characters
    valid_chars = f"-_.{string.ascii_letters}{string.digits}"
    result = "".join(c for c in result if c in valid_chars)

    # Remove leading/trailing dots and spaces
    result = result.strip("._")

    # Truncate if needed
    if len(result) > max_length:
        result = result[:max_length].rstrip("._")

    # Ensure we have something left
    if not result:
        result = "unnamed"

    return result


def validate_success_criterion(criterion: str) -> tuple[bool, str]:
    """
    Validate a success criterion.

    Args:
        criterion: Success criterion text

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not criterion:
        return False, "Success criterion cannot be empty"

    if len(criterion) > 500:
        return False, "Success criterion must be 500 characters or less"

    if len(criterion) < 5:
        return False, "Success criterion must be at least 5 characters"

    return True, ""


def validate_goal(goal: str) -> tuple[bool, str]:
    """
    Validate a project goal.

    Args:
        goal: Project goal text

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not goal:
        return False, "Project goal is required"

    if len(goal) > 2000:
        return False, "Project goal must be 2000 characters or less"

    if len(goal) < 10:
        return False, "Project goal must be at least 10 characters"

    return True, ""


def validate_context(context: str) -> tuple[bool, str]:
    """
    Validate project context.

    Args:
        context: Context text

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not context:
        return True, ""  # Context is optional

    if len(context) > 5000:
        return False, "Context must be 5000 characters or less"

    return True, ""


# Re-exported from git_utils for backward compatibility
from geck_generator.utils.git_utils import is_git_repo, suggest_repo_url  # noqa: F401
