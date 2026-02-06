"""Git utility functions for GECK Generator."""

import subprocess
from pathlib import Path


def _run_git(path: str, *args: str, timeout: float = 10.0) -> subprocess.CompletedProcess:
    """Run a git command in the given directory."""
    return subprocess.run(
        ["git", "-C", path, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def is_git_repo(path: str) -> bool:
    """Check if a path is inside a git repository."""
    try:
        result = _run_git(str(path), "rev-parse", "--is-inside-work-tree")
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def suggest_repo_url(path: str) -> str | None:
    """Try to get the origin remote URL from a git repo."""
    try:
        result = _run_git(str(path), "remote", "get-url", "origin")
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def get_current_branch(path: str) -> str | None:
    """Return the current branch name, or None if detached/not a repo."""
    try:
        result = _run_git(str(path), "branch", "--show-current")
        if result.returncode == 0:
            branch = result.stdout.strip()
            return branch if branch else None  # empty string = detached HEAD
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def get_branches(path: str, include_remote: bool = True) -> list[str]:
    """List all branches. Returns local branches first, then remote tracking branches."""
    branches = []
    try:
        args = ["branch", "--no-color"]
        if include_remote:
            args.append("-a")
        result = _run_git(str(path), *args)
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                name = line.strip()
                if not name:
                    continue
                # Skip current-branch marker
                if name.startswith("* "):
                    name = name[2:]
                # Skip HEAD pointer
                if " -> " in name:
                    continue
                branches.append(name)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return branches


def has_uncommitted_changes(path: str) -> bool:
    """Check if the working tree has uncommitted changes (staged or unstaged)."""
    try:
        result = _run_git(str(path), "status", "--porcelain")
        if result.returncode == 0:
            return bool(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return False


def checkout_branch(path: str, branch: str) -> tuple[bool, str]:
    """
    Switch to a branch. For remote branches, creates a local tracking branch.

    Returns:
        Tuple of (success, message)
    """
    try:
        # If it's a remote tracking branch like "remotes/origin/foo", extract "foo"
        local_name = branch
        if local_name.startswith("remotes/"):
            local_name = local_name.split("/", 2)[-1]  # "origin/foo"
            # Strip remote name to get just branch name
            parts = local_name.split("/", 1)
            if len(parts) == 2:
                local_name = parts[1]  # "foo"

            # Try to checkout with tracking
            result = _run_git(str(path), "checkout", "-b", local_name, "--track", branch)
            if result.returncode == 0:
                return True, f"Created local branch '{local_name}' tracking '{branch}'"
            # If branch already exists locally, just switch to it
            if "already exists" in result.stderr:
                result = _run_git(str(path), "checkout", local_name)
                if result.returncode == 0:
                    return True, f"Switched to existing branch '{local_name}'"
                return False, result.stderr.strip()
            return False, result.stderr.strip()
        else:
            result = _run_git(str(path), "checkout", local_name)
            if result.returncode == 0:
                return True, f"Switched to branch '{local_name}'"
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Git checkout timed out"
    except (FileNotFoundError, OSError) as e:
        return False, f"Git error: {e}"


def fetch_all(path: str) -> tuple[bool, str]:
    """Run git fetch --all. Returns (success, message)."""
    try:
        result = _run_git(str(path), "fetch", "--all", timeout=30.0)
        if result.returncode == 0:
            return True, result.stderr.strip() or "Fetched all remotes"
        return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Git fetch timed out"
    except (FileNotFoundError, OSError) as e:
        return False, f"Git error: {e}"
