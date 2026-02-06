"""Tests for geck_generator.utils.validators module."""

import pytest
from pathlib import Path

from geck_generator.utils.validators import (
    validate_url,
    validate_path,
    validate_project_name,
    sanitize_filename,
    validate_success_criterion,
    validate_goal,
    validate_context,
    is_git_repo,
)


class TestValidateUrl:
    """Tests for validate_url function."""

    def test_empty_url_is_valid(self):
        """Empty URL should be valid (optional field)."""
        valid, error = validate_url("")
        assert valid is True
        assert error == ""

    def test_valid_https_url(self):
        """Valid HTTPS URL should pass."""
        valid, error = validate_url("https://github.com/example/repo")
        assert valid is True
        assert error == ""

    def test_valid_http_url(self):
        """Valid HTTP URL should pass."""
        valid, error = validate_url("http://example.com/repo")
        assert valid is True
        assert error == ""

    def test_valid_git_url(self):
        """Valid git:// URL should pass."""
        valid, error = validate_url("git://github.com/example/repo.git")
        assert valid is True
        assert error == ""

    def test_valid_ssh_url(self):
        """Valid ssh:// URL should pass."""
        valid, error = validate_url("ssh://git@github.com/example/repo.git")
        assert valid is True
        assert error == ""

    def test_missing_scheme_fails(self):
        """URL without scheme should fail."""
        valid, error = validate_url("github.com/example/repo")
        assert valid is False
        assert "scheme" in error.lower()

    def test_missing_domain_fails(self):
        """URL without domain should fail."""
        valid, error = validate_url("https://")
        assert valid is False
        assert "domain" in error.lower()

    def test_unsupported_scheme_fails(self):
        """URL with unsupported scheme should fail."""
        valid, error = validate_url("ftp://example.com/repo")
        assert valid is False
        assert "unsupported" in error.lower()


class TestValidatePath:
    """Tests for validate_path function."""

    def test_empty_path_is_valid(self):
        """Empty path should be valid (optional field)."""
        valid, error = validate_path("")
        assert valid is True
        assert error == ""

    def test_valid_relative_path(self):
        """Valid relative path should pass."""
        valid, error = validate_path("./some/path")
        assert valid is True
        assert error == ""

    def test_valid_absolute_path(self):
        """Valid absolute path should pass."""
        # Use current directory as it exists
        valid, error = validate_path(str(Path.cwd()))
        assert valid is True
        assert error == ""

    def test_invalid_characters_fails(self):
        """Path with invalid characters should fail."""
        valid, error = validate_path("path/with<invalid>chars")
        assert valid is False
        assert "invalid characters" in error.lower()

    def test_must_exist_fails_for_nonexistent(self, temp_dir):
        """Path that must exist should fail for nonexistent path."""
        valid, error = validate_path(
            str(temp_dir / "nonexistent_dir"),
            must_exist=True,
        )
        assert valid is False
        assert "does not exist" in error.lower()

    def test_must_exist_passes_for_existing(self, temp_dir):
        """Path that must exist should pass for existing path."""
        valid, error = validate_path(str(temp_dir), must_exist=True)
        assert valid is True
        assert error == ""

    def test_must_be_dir_fails_for_file(self, temp_dir):
        """Path that must be dir should fail for file."""
        # Create a file
        test_file = temp_dir / "test_file.txt"
        test_file.write_text("test")

        valid, error = validate_path(
            str(test_file),
            must_exist=True,
            must_be_dir=True,
        )
        assert valid is False
        assert "not a directory" in error.lower()


class TestValidateProjectName:
    """Tests for validate_project_name function."""

    def test_empty_name_fails(self):
        """Empty project name should fail."""
        valid, error = validate_project_name("")
        assert valid is False
        assert "required" in error.lower()

    def test_valid_name(self):
        """Valid project name should pass."""
        valid, error = validate_project_name("My Project")
        assert valid is True
        assert error == ""

    def test_name_with_hyphens(self):
        """Project name with hyphens should pass."""
        valid, error = validate_project_name("my-cool-project")
        assert valid is True
        assert error == ""

    def test_name_with_underscores(self):
        """Project name with underscores should pass."""
        valid, error = validate_project_name("my_cool_project")
        assert valid is True
        assert error == ""

    def test_name_with_numbers(self):
        """Project name with numbers should pass."""
        valid, error = validate_project_name("Project123")
        assert valid is True
        assert error == ""

    def test_too_short_fails(self):
        """Project name that's too short should fail."""
        valid, error = validate_project_name("A")
        assert valid is False
        assert "at least 2" in error.lower()

    def test_too_long_fails(self):
        """Project name that's too long should fail."""
        valid, error = validate_project_name("A" * 101)
        assert valid is False
        assert "100 characters" in error.lower()

    def test_special_characters_fail(self):
        """Project name with special characters should fail."""
        valid, error = validate_project_name("Project@#$!")
        assert valid is False
        assert "only contain" in error.lower()


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_replaces_spaces(self):
        """sanitize_filename should replace spaces with underscores."""
        result = sanitize_filename("my project name")
        assert " " not in result
        assert "my_project_name" == result

    def test_removes_invalid_chars(self):
        """sanitize_filename should remove invalid characters."""
        result = sanitize_filename("file@#$name")
        assert "@" not in result
        assert "#" not in result
        assert "$" not in result

    def test_truncates_long_names(self):
        """sanitize_filename should truncate long names."""
        result = sanitize_filename("a" * 100, max_length=20)
        assert len(result) <= 20

    def test_strips_leading_dots(self):
        """sanitize_filename should strip leading dots."""
        result = sanitize_filename("...hidden")
        assert not result.startswith(".")

    def test_returns_unnamed_for_empty(self):
        """sanitize_filename should return 'unnamed' for empty result."""
        result = sanitize_filename("@#$%")  # All invalid chars
        assert result == "unnamed"

    def test_preserves_hyphens(self):
        """sanitize_filename should preserve hyphens."""
        result = sanitize_filename("my-project")
        assert result == "my-project"

    def test_preserves_underscores(self):
        """sanitize_filename should preserve underscores."""
        result = sanitize_filename("my_project")
        assert result == "my_project"


class TestValidateSuccessCriterion:
    """Tests for validate_success_criterion function."""

    def test_empty_criterion_fails(self):
        """Empty success criterion should fail."""
        valid, error = validate_success_criterion("")
        assert valid is False
        assert "cannot be empty" in error.lower()

    def test_valid_criterion(self):
        """Valid success criterion should pass."""
        valid, error = validate_success_criterion("All tests pass successfully")
        assert valid is True
        assert error == ""

    def test_too_short_fails(self):
        """Criterion that's too short should fail."""
        valid, error = validate_success_criterion("Test")
        assert valid is False
        assert "at least 5" in error.lower()

    def test_too_long_fails(self):
        """Criterion that's too long should fail."""
        valid, error = validate_success_criterion("A" * 501)
        assert valid is False
        assert "500 characters" in error.lower()


class TestValidateGoal:
    """Tests for validate_goal function."""

    def test_empty_goal_fails(self):
        """Empty goal should fail."""
        valid, error = validate_goal("")
        assert valid is False
        assert "required" in error.lower()

    def test_valid_goal(self):
        """Valid goal should pass."""
        valid, error = validate_goal("Build a REST API for user management")
        assert valid is True
        assert error == ""

    def test_too_short_fails(self):
        """Goal that's too short should fail."""
        valid, error = validate_goal("Build")
        assert valid is False
        assert "at least 10" in error.lower()

    def test_too_long_fails(self):
        """Goal that's too long should fail."""
        valid, error = validate_goal("A" * 2001)
        assert valid is False
        assert "2000 characters" in error.lower()


class TestValidateContext:
    """Tests for validate_context function."""

    def test_empty_context_is_valid(self):
        """Empty context should be valid (optional field)."""
        valid, error = validate_context("")
        assert valid is True
        assert error == ""

    def test_valid_context(self):
        """Valid context should pass."""
        valid, error = validate_context("This project builds on previous work...")
        assert valid is True
        assert error == ""

    def test_too_long_fails(self):
        """Context that's too long should fail."""
        valid, error = validate_context("A" * 5001)
        assert valid is False
        assert "5000 characters" in error.lower()


class TestIsGitRepo:
    """Tests for is_git_repo function."""

    def test_non_git_dir_returns_false(self, temp_dir):
        """Non-git directory should return False."""
        result = is_git_repo(str(temp_dir))
        assert result is False

    def test_git_dir_returns_true(self, temp_dir):
        """Real git repo should return True."""
        import subprocess
        subprocess.run(["git", "init", str(temp_dir)], capture_output=True, check=True)

        result = is_git_repo(str(temp_dir))
        assert result is True

    def test_subdirectory_of_git_repo(self, temp_dir):
        """Subdirectory of git repo should return True."""
        import subprocess
        subprocess.run(["git", "init", str(temp_dir)], capture_output=True, check=True)

        subdir = temp_dir / "src" / "lib"
        subdir.mkdir(parents=True)

        result = is_git_repo(str(subdir))
        assert result is True

    def test_nonexistent_path_returns_false(self):
        """Nonexistent path should return False."""
        result = is_git_repo("/nonexistent/path/that/does/not/exist")
        assert result is False
