"""
Masidy Autonomous Agent Runtime - GitHub Tools
Tools for interacting with GitHub repositories and APIs
"""

import os
import subprocess
import json
from typing import Optional
from pathlib import Path


def _run_gh_command(args: list[str], cwd: Optional[str] = None) -> dict:
    """Helper to run gh CLI commands"""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=60
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout.strip()
            }
        else:
            return {
                "success": False,
                "error": result.stderr.strip() or result.stdout.strip()
            }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "GitHub CLI (gh) not installed"
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def _run_git_command(args: list[str], cwd: Optional[str] = None) -> dict:
    """Helper to run git commands"""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=60
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout.strip()
            }
        else:
            return {
                "success": False,
                "error": result.stderr.strip() or result.stdout.strip()
            }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "Git not installed"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def git_clone(repo_url: str, directory: Optional[str] = None, branch: Optional[str] = None) -> dict:
    """
    Clone a Git repository.
    
    Args:
        repo_url: URL of the repository to clone
        directory: Target directory name (optional)
        branch: Branch to clone (optional)
    
    Returns:
        dict with status and path
    """
    args = ["clone"]
    
    if branch:
        args.extend(["-b", branch])
    
    args.append(repo_url)
    
    if directory:
        args.append(directory)
    
    result = _run_git_command(args)
    
    if result["success"]:
        cloned_dir = directory or repo_url.split("/")[-1].replace(".git", "")
        result["path"] = str(Path(cloned_dir).absolute())
        result["message"] = f"Repository cloned to {cloned_dir}"
    
    return result


def git_status(cwd: Optional[str] = None) -> dict:
    """
    Get git status of current repository.
    
    Args:
        cwd: Working directory (optional)
    
    Returns:
        dict with status information
    """
    result = _run_git_command(["status", "--porcelain"], cwd=cwd)
    
    if result["success"]:
        output = result["output"]
        changes = []
        
        for line in output.split("\n"):
            if line.strip():
                status = line[:2]
                file_path = line[3:]
                changes.append({"status": status, "file": file_path})
        
        result["changes"] = changes
        result["has_changes"] = len(changes) > 0
        result["message"] = f"{len(changes)} file(s) changed" if changes else "Working tree clean"
    
    return result


def git_add(files: list[str], cwd: Optional[str] = None) -> dict:
    """
    Stage files for commit.
    
    Args:
        files: List of files to stage (use ["."] for all)
        cwd: Working directory (optional)
    
    Returns:
        dict with status
    """
    result = _run_git_command(["add"] + files, cwd=cwd)
    
    if result["success"]:
        result["message"] = f"Staged {len(files)} file(s)"
    
    return result


def git_commit(message: str, cwd: Optional[str] = None) -> dict:
    """
    Create a git commit.
    
    Args:
        message: Commit message
        cwd: Working directory (optional)
    
    Returns:
        dict with status and commit hash
    """
    result = _run_git_command(["commit", "-m", message], cwd=cwd)
    
    if result["success"]:
        # Get commit hash
        hash_result = _run_git_command(["rev-parse", "HEAD"], cwd=cwd)
        if hash_result["success"]:
            result["commit_hash"] = hash_result["output"]
        result["message"] = f"Created commit: {message}"
    
    return result


def git_push(remote: str = "origin", branch: Optional[str] = None, cwd: Optional[str] = None) -> dict:
    """
    Push commits to remote repository.
    
    Args:
        remote: Remote name (default: origin)
        branch: Branch name (optional, uses current branch)
        cwd: Working directory (optional)
    
    Returns:
        dict with status
    """
    args = ["push", remote]
    if branch:
        args.append(branch)
    
    return _run_git_command(args, cwd=cwd)


def git_pull(remote: str = "origin", branch: Optional[str] = None, cwd: Optional[str] = None) -> dict:
    """
    Pull changes from remote repository.
    
    Args:
        remote: Remote name (default: origin)
        branch: Branch name (optional)
        cwd: Working directory (optional)
    
    Returns:
        dict with status
    """
    args = ["pull", remote]
    if branch:
        args.append(branch)
    
    return _run_git_command(args, cwd=cwd)


def git_branch(name: Optional[str] = None, checkout: bool = False, cwd: Optional[str] = None) -> dict:
    """
    List branches or create a new branch.
    
    Args:
        name: Branch name to create (optional, lists branches if not provided)
        checkout: Switch to the new branch (only if name is provided)
        cwd: Working directory (optional)
    
    Returns:
        dict with status and branch information
    """
    if name:
        if checkout:
            result = _run_git_command(["checkout", "-b", name], cwd=cwd)
        else:
            result = _run_git_command(["branch", name], cwd=cwd)
        
        if result["success"]:
            result["message"] = f"Created branch: {name}"
            result["branch"] = name
    else:
        result = _run_git_command(["branch", "--list"], cwd=cwd)
        if result["success"]:
            branches = [b.strip().lstrip("* ") for b in result["output"].split("\n") if b.strip()]
            result["branches"] = branches
    
    return result


def git_current_branch(cwd: Optional[str] = None) -> dict:
    """
    Get the current branch name.
    
    Args:
        cwd: Working directory (optional)
    
    Returns:
        dict with current branch name
    """
    result = _run_git_command(["branch", "--show-current"], cwd=cwd)
    
    if result["success"]:
        result["branch"] = result["output"]
    
    return result


def github_create_issue(
    title: str,
    body: str,
    labels: Optional[list[str]] = None,
    repo: Optional[str] = None
) -> dict:
    """
    Create a GitHub issue.
    
    Args:
        title: Issue title
        body: Issue body/description
        labels: List of labels (optional)
        repo: Repository in format owner/repo (optional, uses current repo)
    
    Returns:
        dict with status and issue URL
    """
    args = ["issue", "create", "--title", title, "--body", body]
    
    if labels:
        for label in labels:
            args.extend(["--label", label])
    
    if repo:
        args.extend(["--repo", repo])
    
    result = _run_gh_command(args)
    
    if result["success"]:
        result["issue_url"] = result["output"]
        result["message"] = f"Created issue: {title}"
    
    return result


def github_list_issues(
    state: str = "open",
    labels: Optional[list[str]] = None,
    limit: int = 30,
    repo: Optional[str] = None
) -> dict:
    """
    List GitHub issues.
    
    Args:
        state: Issue state (open, closed, all)
        labels: Filter by labels (optional)
        limit: Maximum number of issues to return
        repo: Repository in format owner/repo (optional)
    
    Returns:
        dict with list of issues
    """
    args = ["issue", "list", "--state", state, "--limit", str(limit), "--json", 
            "number,title,state,labels,createdAt,url"]
    
    if labels:
        args.extend(["--label", ",".join(labels)])
    
    if repo:
        args.extend(["--repo", repo])
    
    result = _run_gh_command(args)
    
    if result["success"]:
        try:
            result["issues"] = json.loads(result["output"])
        except json.JSONDecodeError:
            result["issues"] = []
    
    return result


def github_create_pr(
    title: str,
    body: str,
    base: str = "main",
    head: Optional[str] = None,
    draft: bool = False,
    repo: Optional[str] = None
) -> dict:
    """
    Create a GitHub pull request.
    
    Args:
        title: PR title
        body: PR description
        base: Base branch (default: main)
        head: Head branch (optional, uses current branch)
        draft: Create as draft PR
        repo: Repository in format owner/repo (optional)
    
    Returns:
        dict with status and PR URL
    """
    args = ["pr", "create", "--title", title, "--body", body, "--base", base]
    
    if head:
        args.extend(["--head", head])
    
    if draft:
        args.append("--draft")
    
    if repo:
        args.extend(["--repo", repo])
    
    result = _run_gh_command(args)
    
    if result["success"]:
        result["pr_url"] = result["output"]
        result["message"] = f"Created PR: {title}"
    
    return result


def github_list_prs(
    state: str = "open",
    limit: int = 30,
    repo: Optional[str] = None
) -> dict:
    """
    List GitHub pull requests.
    
    Args:
        state: PR state (open, closed, merged, all)
        limit: Maximum number of PRs to return
        repo: Repository in format owner/repo (optional)
    
    Returns:
        dict with list of PRs
    """
    args = ["pr", "list", "--state", state, "--limit", str(limit), "--json",
            "number,title,state,headRefName,baseRefName,createdAt,url"]
    
    if repo:
        args.extend(["--repo", repo])
    
    result = _run_gh_command(args)
    
    if result["success"]:
        try:
            result["prs"] = json.loads(result["output"])
        except json.JSONDecodeError:
            result["prs"] = []
    
    return result


def github_repo_info(repo: Optional[str] = None) -> dict:
    """
    Get repository information.
    
    Args:
        repo: Repository in format owner/repo (optional, uses current repo)
    
    Returns:
        dict with repository information
    """
    args = ["repo", "view", "--json", "name,owner,description,url,defaultBranchRef,stargazerCount"]
    
    if repo:
        args.append(repo)
    
    result = _run_gh_command(args)
    
    if result["success"]:
        try:
            result["repo"] = json.loads(result["output"])
        except json.JSONDecodeError:
            pass
    
    return result


# Tool registry for easy access
GITHUB_TOOLS = {
    "git_clone": git_clone,
    "git_status": git_status,
    "git_add": git_add,
    "git_commit": git_commit,
    "git_push": git_push,
    "git_pull": git_pull,
    "git_branch": git_branch,
    "git_current_branch": git_current_branch,
    "github_create_issue": github_create_issue,
    "github_list_issues": github_list_issues,
    "github_create_pr": github_create_pr,
    "github_list_prs": github_list_prs,
    "github_repo_info": github_repo_info,
}
