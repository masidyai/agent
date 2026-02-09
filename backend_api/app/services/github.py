"""
GitHub integration service
"""
import logging
import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

from github import Github, GithubException, Repository, InputGitAuthor
from github.GithubObject import NotSet

from app.core.config import settings
from app.core.security import encrypt_token, decrypt_token

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for GitHub API integration"""
    
    def __init__(self, access_token: Optional[str] = None):
        """Initialize GitHub service with optional access token"""
        self.access_token = access_token
        self._client: Optional[Github] = None
    
    @property
    def client(self) -> Github:
        """Get or create GitHub client"""
        if not self._client:
            if not self.access_token:
                raise ValueError("GitHub access token is required")
            self._client = Github(self.access_token)
        return self._client
    
    def test_connection(self) -> bool:
        """Test if GitHub connection and token are valid"""
        try:
            user = self.client.get_user()
            user.login  # Access a property to trigger API call
            return True
        except GithubException as e:
            logger.error(f"GitHub connection test failed: {e}")
            return False
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get authenticated user information"""
        try:
            user = self.client.get_user()
            return {
                "login": user.login,
                "name": user.name,
                "email": user.email,
                "avatar_url": user.avatar_url,
                "public_repos": user.public_repos,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            }
        except GithubException as e:
            logger.error(f"Failed to get user info: {e}")
            raise
    
    def create_repository(
        self,
        name: str,
        description: Optional[str] = None,
        private: bool = True,
        auto_init: bool = True,
        gitignore_template: Optional[str] = None,
    ) -> Repository.Repository:
        """
        Create a new GitHub repository
        
        Args:
            name: Repository name
            description: Repository description
            private: Whether the repo should be private
            auto_init: Initialize with README
            gitignore_template: Template for .gitignore (e.g., 'Python', 'Node')
        
        Returns:
            Created repository object
        """
        try:
            user = self.client.get_user()
            
            # Sanitize repository name
            repo_name = self._sanitize_repo_name(name)
            
            # Create repository
            repo = user.create_repo(
                name=repo_name,
                description=description or f"Generated project: {name}",
                private=private,
                auto_init=auto_init,
                gitignore_template=gitignore_template or NotSet,
            )
            
            logger.info(f"Created GitHub repository: {repo.full_name}")
            return repo
            
        except GithubException as e:
            logger.error(f"Failed to create repository: {e}")
            raise
    
    def get_repository(self, repo_name: str) -> Repository.Repository:
        """Get a repository by name"""
        try:
            user = self.client.get_user()
            return user.get_repo(repo_name)
        except GithubException as e:
            logger.error(f"Failed to get repository {repo_name}: {e}")
            raise
    
    def push_files(
        self,
        repo: Repository.Repository,
        files: Dict[str, str],
        commit_message: str = "Initial commit",
        branch: str = "main",
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
    ) -> str:
        """
        Push multiple files to a repository
        
        Args:
            repo: Repository object
            files: Dictionary of {file_path: file_content}
            commit_message: Commit message
            branch: Branch to push to
            author_name: Commit author name (defaults to authenticated user)
            author_email: Commit author email (defaults to authenticated user)
        
        Returns:
            Commit SHA
        """
        try:
            # Get the branch reference
            try:
                ref = repo.get_git_ref(f"heads/{branch}")
                sha = ref.object.sha
            except GithubException:
                # Branch doesn't exist, use default branch
                sha = repo.get_branch(repo.default_branch).commit.sha
                # Create new branch
                repo.create_git_ref(f"refs/heads/{branch}", sha)
                ref = repo.get_git_ref(f"heads/{branch}")
                sha = ref.object.sha
            
            # Get the base tree
            base_tree = repo.get_git_tree(sha)
            
            # Create blobs for each file
            tree_elements = []
            for file_path, content in files.items():
                blob = repo.create_git_blob(content, "utf-8")
                tree_elements.append({
                    "path": file_path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob.sha,
                })
            
            # Create tree
            tree = repo.create_git_tree(tree_elements, base_tree)
            
            # Get author info if not provided
            if not author_name or not author_email:
                user_info = self.get_user_info()
                author_name = author_name or user_info.get("name") or user_info.get("login")
                author_email = author_email or user_info.get("email") or f"{user_info.get('login')}@users.noreply.github.com"
            
            # Create commit
            author = InputGitAuthor(
                name=author_name,
                email=author_email,
            )
            commit = repo.create_git_commit(
                message=commit_message,
                tree=tree,
                parents=[repo.get_git_commit(sha)],
                author=author,
                committer=author,
            )
            
            # Update reference
            ref.edit(commit.sha)
            
            logger.info(f"Pushed files to {repo.full_name} - commit {commit.sha[:7]}")
            return commit.sha
            
        except GithubException as e:
            logger.error(f"Failed to push files: {e}")
            raise
    
    def create_file(
        self,
        repo: Repository.Repository,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str = "main",
    ) -> Dict[str, Any]:
        """Create or update a single file in the repository"""
        try:
            # Check if file exists
            try:
                existing_file = repo.get_contents(file_path, ref=branch)
                # File exists, update it
                result = repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=existing_file.sha,
                    branch=branch,
                )
                logger.info(f"Updated file {file_path} in {repo.full_name}")
            except GithubException as e:
                if e.status == 404:
                    # File doesn't exist, create it
                    result = repo.create_file(
                        path=file_path,
                        message=commit_message,
                        content=content,
                        branch=branch,
                    )
                    logger.info(f"Created file {file_path} in {repo.full_name}")
                else:
                    raise
            
            return {
                "commit_sha": result["commit"].sha,
                "file_path": file_path,
            }
            
        except GithubException as e:
            logger.error(f"Failed to create/update file {file_path}: {e}")
            raise
    
    def generate_readme(
        self,
        project_name: str,
        description: str,
        tech_stack: Optional[List[str]] = None,
        features: Optional[List[str]] = None,
    ) -> str:
        """Generate a professional README for the project"""
        tech_stack = tech_stack or []
        features = features or []
        
        readme = f"""# {project_name}

{description}

## Features

"""
        if features:
            for feature in features:
                readme += f"- {feature}\n"
        else:
            readme += "- AI-generated application\n"
            readme += "- Modern architecture\n"
            readme += "- Production-ready code\n"
        
        readme += "\n## Tech Stack\n\n"
        if tech_stack:
            for tech in tech_stack:
                readme += f"- {tech}\n"
        else:
            readme += "- Auto-detected from project structure\n"
        
        readme += """
## Installation

```bash
# Clone the repository
git clone <repository-url>
cd """ + self._sanitize_repo_name(project_name) + """

# Install dependencies
# (Check package.json, requirements.txt, or other dependency files)
```

## Usage

```bash
# Run the application
# (Check scripts in package.json or main files)
```

## Development

This project was generated by Masidy AI Agent Platform.

## Testing

```bash
# Run tests
# (Check test scripts in your project)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

---

Generated with ❤️ by [Masidy AI](https://masidy.ai)
"""
        return readme
    
    def generate_github_actions_workflow(
        self,
        project_type: str = "node",
        workflow_name: str = "CI/CD",
    ) -> str:
        """Generate GitHub Actions workflow file"""
        
        if project_type.lower() in ["node", "nodejs", "javascript", "typescript"]:
            return self._generate_node_workflow(workflow_name)
        elif project_type.lower() in ["python", "django", "flask", "fastapi"]:
            return self._generate_python_workflow(workflow_name)
        else:
            return self._generate_generic_workflow(workflow_name)
    
    def _generate_node_workflow(self, name: str) -> str:
        """Generate Node.js GitHub Actions workflow"""
        return f"""name: {name}

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Use Node.js ${{{{ matrix.node-version }}}}
      uses: actions/setup-node@v3
      with:
        node-version: ${{{{ matrix.node-version }}}}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run linter
      run: npm run lint --if-present
    
    - name: Run tests
      run: npm test --if-present
    
    - name: Build
      run: npm run build --if-present
"""
    
    def _generate_python_workflow(self, name: str) -> str:
        """Generate Python GitHub Actions workflow"""
        return f"""name: {name}

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{{{ matrix.python-version }}}}
      uses: actions/setup-python@v4
      with:
        python-version: ${{{{ matrix.python-version }}}}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    
    - name: Run linter
      run: |
        pip install flake8
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics || true
    
    - name: Run tests
      run: |
        if [ -f pytest.ini ] || [ -d tests ]; then
          pip install pytest pytest-cov
          pytest --cov || true
        fi
"""
    
    def _generate_generic_workflow(self, name: str) -> str:
        """Generate generic GitHub Actions workflow"""
        return f"""name: {name}

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build
      run: echo "Add your build steps here"
    
    - name: Test
      run: echo "Add your test steps here"
"""
    
    def add_collaborator(
        self,
        repo: Repository.Repository,
        username: str,
        permission: str = "push",
    ) -> bool:
        """Add a collaborator to the repository"""
        try:
            repo.add_to_collaborators(username, permission)
            logger.info(f"Added {username} as collaborator to {repo.full_name}")
            return True
        except GithubException as e:
            logger.error(f"Failed to add collaborator: {e}")
            return False
    
    def create_release(
        self,
        repo: Repository.Repository,
        tag: str,
        name: str,
        message: str,
        draft: bool = False,
        prerelease: bool = False,
    ) -> Any:
        """Create a GitHub release"""
        try:
            release = repo.create_git_release(
                tag=tag,
                name=name,
                message=message,
                draft=draft,
                prerelease=prerelease,
            )
            logger.info(f"Created release {tag} for {repo.full_name}")
            return release
        except GithubException as e:
            logger.error(f"Failed to create release: {e}")
            raise
    
    def _sanitize_repo_name(self, name: str) -> str:
        """Sanitize repository name to meet GitHub requirements"""
        # Remove special characters, replace spaces with hyphens
        sanitized = re.sub(r'[^a-zA-Z0-9\-_.]', '-', name)
        # Remove consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        # Ensure it's not empty
        if not sanitized:
            sanitized = "generated-project"
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        return sanitized.lower()
    
    @staticmethod
    def get_oauth_url(state: Optional[str] = None) -> str:
        """Get GitHub OAuth authorization URL"""
        if not settings.GITHUB_CLIENT_ID:
            raise ValueError("GitHub Client ID not configured")
        
        base_url = "https://github.com/login/oauth/authorize"
        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
            "scope": "repo,user:email",
        }
        
        if state:
            params["state"] = state
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    @staticmethod
    async def exchange_code_for_token(code: str) -> Dict[str, Any]:
        """Exchange OAuth code for access token"""
        import httpx
        
        if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
            raise ValueError("GitHub OAuth credentials not configured")
        
        url = "https://github.com/login/oauth/access_token"
        data = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
        }
        
        headers = {"Accept": "application/json"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise ValueError(f"OAuth error: {result.get('error_description', result['error'])}")
            
            return result


def get_github_service(encrypted_token: str) -> GitHubService:
    """Get GitHub service with decrypted token"""
    if not encrypted_token:
        raise ValueError("No GitHub token provided")
    
    token = decrypt_token(encrypted_token)
    return GitHubService(access_token=token)
