"""Tests for git_utils module using real git repos in temp dirs."""

import subprocess
import pytest
from pathlib import Path

from geck_generator.utils.git_utils import (
    is_git_repo,
    suggest_repo_url,
    get_current_branch,
    get_branches,
    has_uncommitted_changes,
    checkout_branch,
    fetch_all,
)


@pytest.fixture
def git_repo(tmp_path):
    """Create a real git repo with an initial commit."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", str(repo)], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@test.com"], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], capture_output=True, check=True)
    # Create initial commit so we have a branch
    (repo / "README.md").write_text("# Test")
    subprocess.run(["git", "-C", str(repo), "add", "."], capture_output=True, check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-m", "initial"], capture_output=True, check=True)
    return repo


@pytest.fixture
def git_repo_with_branches(git_repo):
    """Create a git repo with multiple branches."""
    # Create branch-a
    subprocess.run(["git", "-C", str(git_repo), "branch", "branch-a"], capture_output=True, check=True)
    # Create branch-b
    subprocess.run(["git", "-C", str(git_repo), "branch", "branch-b"], capture_output=True, check=True)
    return git_repo


class TestIsGitRepo:
    def test_git_repo(self, git_repo):
        assert is_git_repo(str(git_repo)) is True

    def test_not_git_repo(self, tmp_path):
        assert is_git_repo(str(tmp_path)) is False

    def test_subdirectory_of_repo(self, git_repo):
        subdir = git_repo / "subdir"
        subdir.mkdir()
        assert is_git_repo(str(subdir)) is True

    def test_nonexistent_path(self):
        assert is_git_repo("/nonexistent/path/xyz") is False


class TestSuggestRepoUrl:
    def test_no_remote(self, git_repo):
        assert suggest_repo_url(str(git_repo)) is None

    def test_with_remote(self, git_repo):
        subprocess.run(
            ["git", "-C", str(git_repo), "remote", "add", "origin", "https://github.com/test/repo.git"],
            capture_output=True, check=True,
        )
        assert suggest_repo_url(str(git_repo)) == "https://github.com/test/repo.git"

    def test_not_a_repo(self, tmp_path):
        assert suggest_repo_url(str(tmp_path)) is None


class TestGetCurrentBranch:
    def test_on_main(self, git_repo):
        branch = get_current_branch(str(git_repo))
        # Could be "main" or "master" depending on git config
        assert branch in ("main", "master")

    def test_on_other_branch(self, git_repo_with_branches):
        subprocess.run(
            ["git", "-C", str(git_repo_with_branches), "checkout", "branch-a"],
            capture_output=True, check=True,
        )
        assert get_current_branch(str(git_repo_with_branches)) == "branch-a"

    def test_not_a_repo(self, tmp_path):
        assert get_current_branch(str(tmp_path)) is None


class TestGetBranches:
    def test_single_branch(self, git_repo):
        branches = get_branches(str(git_repo), include_remote=False)
        assert len(branches) == 1

    def test_multiple_branches(self, git_repo_with_branches):
        branches = get_branches(str(git_repo_with_branches), include_remote=False)
        assert len(branches) == 3  # main/master + branch-a + branch-b
        # Check branch names are present (one will be main or master)
        assert "branch-a" in branches
        assert "branch-b" in branches

    def test_not_a_repo(self, tmp_path):
        assert get_branches(str(tmp_path)) == []


class TestHasUncommittedChanges:
    def test_clean(self, git_repo):
        assert has_uncommitted_changes(str(git_repo)) is False

    def test_unstaged_changes(self, git_repo):
        (git_repo / "README.md").write_text("# Modified")
        assert has_uncommitted_changes(str(git_repo)) is True

    def test_staged_changes(self, git_repo):
        (git_repo / "new.txt").write_text("new file")
        subprocess.run(["git", "-C", str(git_repo), "add", "new.txt"], capture_output=True, check=True)
        assert has_uncommitted_changes(str(git_repo)) is True

    def test_untracked_file(self, git_repo):
        (git_repo / "untracked.txt").write_text("untracked")
        assert has_uncommitted_changes(str(git_repo)) is True


class TestCheckoutBranch:
    def test_switch_to_existing_branch(self, git_repo_with_branches):
        success, msg = checkout_branch(str(git_repo_with_branches), "branch-a")
        assert success is True
        assert get_current_branch(str(git_repo_with_branches)) == "branch-a"

    def test_switch_to_nonexistent_branch(self, git_repo):
        success, msg = checkout_branch(str(git_repo), "nonexistent")
        assert success is False

    def test_switch_to_remote_branch(self, tmp_path):
        """Test checkout of a remote tracking branch via a local clone."""
        # Create origin repo with a feature branch
        origin = tmp_path / "origin"
        origin.mkdir()
        subprocess.run(["git", "init", "--bare", str(origin)], capture_output=True, check=True)

        # Create a working repo, push to origin
        work = tmp_path / "work"
        subprocess.run(["git", "clone", str(origin), str(work)], capture_output=True, check=True)
        subprocess.run(["git", "-C", str(work), "config", "user.email", "test@test.com"], capture_output=True, check=True)
        subprocess.run(["git", "-C", str(work), "config", "user.name", "Test"], capture_output=True, check=True)
        (work / "README.md").write_text("# Test")
        subprocess.run(["git", "-C", str(work), "add", "."], capture_output=True, check=True)
        subprocess.run(["git", "-C", str(work), "commit", "-m", "initial"], capture_output=True, check=True)
        subprocess.run(["git", "-C", str(work), "push", "-u", "origin", "HEAD"], capture_output=True, check=True)
        # Create feature branch and push
        subprocess.run(["git", "-C", str(work), "checkout", "-b", "feature-x"], capture_output=True, check=True)
        (work / "feature.txt").write_text("feature")
        subprocess.run(["git", "-C", str(work), "add", "."], capture_output=True, check=True)
        subprocess.run(["git", "-C", str(work), "commit", "-m", "feature"], capture_output=True, check=True)
        subprocess.run(["git", "-C", str(work), "push", "-u", "origin", "feature-x"], capture_output=True, check=True)

        # Clone fresh, should only have main locally
        clone = tmp_path / "clone"
        subprocess.run(["git", "clone", str(origin), str(clone)], capture_output=True, check=True)

        # Checkout the remote branch
        success, msg = checkout_branch(str(clone), "remotes/origin/feature-x")
        assert success is True
        assert get_current_branch(str(clone)) == "feature-x"


class TestFetchAll:
    def test_fetch_no_remote(self, git_repo):
        # No remote configured, fetch should still succeed (just nothing to fetch)
        success, msg = fetch_all(str(git_repo))
        assert success is True

    def test_not_a_repo(self, tmp_path):
        success, msg = fetch_all(str(tmp_path))
        assert success is False


# Backward compatibility: validators re-exports
class TestBackwardCompat:
    def test_validators_reexport(self):
        from geck_generator.utils.validators import is_git_repo as v_is_git_repo
        from geck_generator.utils.validators import suggest_repo_url as v_suggest_repo_url
        # They should be the exact same function objects
        assert v_is_git_repo is is_git_repo
        assert v_suggest_repo_url is suggest_repo_url
