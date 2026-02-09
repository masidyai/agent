"""
GitHub integration API routes
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from github import GithubException

from app.core.database import get_db
from app.core.security import encrypt_token, decrypt_token
from app.crud import user as crud_user
from app.crud import project as crud_project
from app.schemas.github import (
    GitHubLinkRequest,
    GitHubLinkResponse,
    GitHubStatusResponse,
    PushToGitHubRequest,
    PushToGitHubResponse,
    GitHubRepoResponse,
    AddCollaboratorRequest,
    AddCollaboratorResponse,
)
from app.api.deps import get_current_user
from app.models.user import User
from app.services.github import GitHubService, get_github_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/auth/github", tags=["GitHub Auth"])
async def github_oauth_start(
    state: Optional[str] = Query(None, description="Optional state parameter for CSRF protection"),
):
    """Start GitHub OAuth flow"""
    try:
        oauth_url = GitHubService.get_oauth_url(state=state)
        return {
            "url": oauth_url,
            "message": "Redirect user to this URL to start GitHub OAuth flow",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/auth/github/callback", response_model=GitHubLinkResponse, tags=["GitHub Auth"])
async def github_oauth_callback(
    request: GitHubLinkRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Handle GitHub OAuth callback and link account"""
    try:
        # Exchange code for access token
        token_data = await GitHubService.exchange_code_for_token(request.code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to obtain access token from GitHub",
            )
        
        # Get user info from GitHub
        github_service = GitHubService(access_token=access_token)
        user_info = github_service.get_user_info()
        
        # Encrypt token for storage
        encrypted_token = encrypt_token(access_token)
        
        # Update user with GitHub info
        # Token expires in 60 days (GitHub default for OAuth apps)
        expires_at = datetime.utcnow() + timedelta(days=60)
        
        await crud_user.update(
            db,
            db_obj=current_user,
            obj_in={
                "github_username": user_info["login"],
                "github_token": encrypted_token,
                "github_token_expires_at": expires_at,
                "github_account_linked": True,
                "github_public_repos_count": user_info.get("public_repos", 0),
            }
        )
        
        logger.info(f"User {current_user.email} linked GitHub account: {user_info['login']}")
        
        return GitHubLinkResponse(
            success=True,
            message="GitHub account linked successfully",
            github_username=user_info["login"],
        )
        
    except GithubException as e:
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub API error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error linking GitHub account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to link GitHub account",
        )


@router.delete("/users/github/unlink", tags=["GitHub"])
async def unlink_github_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Unlink GitHub account from user"""
    if not current_user.github_account_linked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No GitHub account linked",
        )
    
    # Clear GitHub data
    await crud_user.update(
        db,
        db_obj=current_user,
        obj_in={
            "github_username": None,
            "github_token": None,
            "github_token_expires_at": None,
            "github_account_linked": False,
            "github_public_repos_count": 0,
        }
    )
    
    logger.info(f"User {current_user.email} unlinked GitHub account")
    
    return {"success": True, "message": "GitHub account unlinked successfully"}


@router.get("/users/github/status", response_model=GitHubStatusResponse, tags=["GitHub"])
async def get_github_status(
    current_user: User = Depends(get_current_user),
):
    """Get GitHub account link status"""
    return GitHubStatusResponse(
        linked=current_user.github_account_linked,
        username=current_user.github_username,
        public_repos_count=current_user.github_public_repos_count,
    )


@router.post("/projects/{project_id}/push-to-github", response_model=PushToGitHubResponse, tags=["Projects"])
async def push_project_to_github(
    project_id: UUID,
    request: PushToGitHubRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Push project to GitHub repository"""
    # Check if GitHub is linked
    if not current_user.github_account_linked or not current_user.github_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub account not linked. Please link your GitHub account first.",
        )
    
    # Get project
    project = await crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Verify ownership
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to push this project",
        )
    
    # Check if project has output files
    if not project.output_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project has no generated files to push",
        )
    
    try:
        # Get GitHub service
        github_service = get_github_service(current_user.github_token)
        
        # Determine repo name
        repo_name = request.repo_name or project.name
        
        # Check if repo already exists for this project
        repo = None
        is_new_repo = False
        if project.github_repo_name:
            try:
                repo = github_service.get_repository(project.github_repo_name)
                logger.info(f"Using existing repository: {repo.full_name}")
            except GithubException:
                logger.info(f"Repository {project.github_repo_name} not found, creating new one")
        
        # Create repository if it doesn't exist
        if not repo:
            repo = github_service.create_repository(
                name=repo_name,
                description=request.description or project.description,
                private=request.private,
                auto_init=False,  # We'll push files manually
            )
            is_new_repo = True
        
        # Collect files to push
        import os
        from pathlib import Path
        
        files_to_push = {}
        
        # Add README if requested
        if request.include_readme:
            readme_content = github_service.generate_readme(
                project_name=project.name,
                description=project.description or project.prompt or "AI-generated project",
                features=["AI-generated application", "Production-ready code"],
            )
            files_to_push["README.md"] = readme_content
        
        # Add GitHub Actions workflow if requested
        if request.include_ci:
            # Detect project type from output path
            project_type = "node"  # Default
            if project.output_path and os.path.exists(project.output_path):
                if os.path.exists(os.path.join(project.output_path, "package.json")):
                    project_type = "node"
                elif os.path.exists(os.path.join(project.output_path, "requirements.txt")):
                    project_type = "python"
            
            workflow_content = github_service.generate_github_actions_workflow(
                project_type=project_type,
                workflow_name="CI/CD Pipeline",
            )
            files_to_push[".github/workflows/ci.yml"] = workflow_content
        
        # Add project files
        if project.output_path and os.path.exists(project.output_path):
            project_path = Path(project.output_path)
            for file_path in project_path.rglob("*"):
                if file_path.is_file():
                    # Skip certain files/directories
                    relative_path = file_path.relative_to(project_path)
                    path_str = str(relative_path)
                    
                    # Skip node_modules, .git, etc.
                    if any(skip in path_str for skip in ["node_modules", ".git", "__pycache__", ".env"]):
                        continue
                    
                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        files_to_push[path_str] = content
                    except (UnicodeDecodeError, PermissionError):
                        # Skip binary files or files we can't read
                        logger.warning(f"Skipping file {path_str} - cannot read as text")
                        continue
        
        if not files_to_push:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files to push to GitHub",
            )
        
        # Push files to GitHub
        commit_message = f"Initial commit: {project.name}"
        commit_sha = github_service.push_files(
            repo=repo,
            files=files_to_push,
            commit_message=commit_message,
            branch="main",
        )
        
        # Update project with GitHub info
        await crud_project.update(
            db,
            db_obj=project,
            obj_in={
                "github_repo_url": repo.html_url,
                "github_repo_name": repo.name,
                "github_repo_id": repo.id,
                "github_created_at": datetime.utcnow() if is_new_repo else project.github_created_at,
                "github_last_sync": datetime.utcnow(),
                "is_public": not request.private,
            }
        )
        
        # Update user's repo count only if we created a new repository
        if is_new_repo:
            await crud_user.update(
                db,
                db_obj=current_user,
                obj_in={
                    "github_public_repos_count": current_user.github_public_repos_count + 1,
                }
            )
        
        logger.info(f"Pushed project {project.name} to GitHub: {repo.html_url}")
        
        return PushToGitHubResponse(
            success=True,
            message="Project pushed to GitHub successfully",
            repo_url=repo.html_url,
            repo_name=repo.name,
            commit_sha=commit_sha,
        )
        
    except GithubException as e:
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Error pushing to GitHub: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to push project to GitHub: {str(e)}",
        )


@router.get("/projects/{project_id}/github-repo", response_model=GitHubRepoResponse, tags=["Projects"])
async def get_github_repo_info(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get GitHub repository information for a project"""
    # Get project
    project = await crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Verify ownership or team membership
    if project.user_id != current_user.id:
        # TODO: Check team membership
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this project",
        )
    
    if not project.github_repo_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project is not linked to a GitHub repository",
        )
    
    try:
        # Get GitHub service
        if not current_user.github_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub account not linked",
            )
        
        github_service = get_github_service(current_user.github_token)
        repo = github_service.get_repository(project.github_repo_name)
        
        return GitHubRepoResponse(
            url=repo.html_url,
            name=repo.name,
            description=repo.description,
            private=repo.private,
            created_at=project.github_created_at,
            last_sync=project.github_last_sync,
            stars=repo.stargazers_count,
            forks=repo.forks_count,
        )
        
    except GithubException as e:
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub error: {str(e)}",
        )


@router.post("/projects/{project_id}/github/add-collaborator", response_model=AddCollaboratorResponse, tags=["Projects"])
async def add_github_collaborator(
    project_id: UUID,
    request: AddCollaboratorRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a collaborator to the project's GitHub repository"""
    # Get project
    project = await crud_project.get(db, id=project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Verify ownership
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage this project",
        )
    
    if not project.github_repo_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project is not linked to a GitHub repository",
        )
    
    try:
        # Get GitHub service
        if not current_user.github_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub account not linked",
            )
        
        github_service = get_github_service(current_user.github_token)
        repo = github_service.get_repository(project.github_repo_name)
        
        # Add collaborator
        success = github_service.add_collaborator(
            repo=repo,
            username=request.username,
            permission=request.permission,
        )
        
        if success:
            return AddCollaboratorResponse(
                success=True,
                message=f"Collaborator {request.username} added successfully",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add collaborator",
            )
        
    except GithubException as e:
        logger.error(f"GitHub API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GitHub error: {str(e)}",
        )
