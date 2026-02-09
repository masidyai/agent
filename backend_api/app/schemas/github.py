"""
GitHub integration schemas
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class GitHubLinkRequest(BaseModel):
    """Schema for linking GitHub account"""
    code: str = Field(..., description="OAuth authorization code from GitHub")


class GitHubLinkResponse(BaseModel):
    """Schema for GitHub link response"""
    success: bool
    message: str
    github_username: Optional[str] = None


class GitHubStatusResponse(BaseModel):
    """Schema for GitHub account status"""
    linked: bool
    username: Optional[str] = None
    public_repos_count: int = 0


class PushToGitHubRequest(BaseModel):
    """Schema for pushing project to GitHub"""
    repo_name: Optional[str] = None
    description: Optional[str] = None
    private: bool = True
    include_readme: bool = True
    include_ci: bool = True


class PushToGitHubResponse(BaseModel):
    """Schema for push to GitHub response"""
    success: bool
    message: str
    repo_url: Optional[str] = None
    repo_name: Optional[str] = None
    commit_sha: Optional[str] = None


class GitHubRepoResponse(BaseModel):
    """Schema for GitHub repository info"""
    url: str
    name: str
    description: Optional[str] = None
    private: bool
    created_at: Optional[datetime] = None
    last_sync: Optional[datetime] = None
    stars: int = 0
    forks: int = 0


class AddCollaboratorRequest(BaseModel):
    """Schema for adding collaborator"""
    username: str = Field(..., min_length=1)
    permission: str = Field(default="push", pattern="^(pull|push|admin)$")


class AddCollaboratorResponse(BaseModel):
    """Schema for add collaborator response"""
    success: bool
    message: str


class GitHubReleaseResponse(BaseModel):
    """Schema for GitHub release"""
    tag: str
    name: str
    body: Optional[str] = None
    draft: bool
    prerelease: bool
    created_at: datetime
    url: str
