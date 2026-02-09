"""
AI-Powered Code Generator
Generates project files using OpenAI instead of hardcoded templates
"""
import asyncio
from typing import List, Dict, Any, Optional
from app.services.openai_service import get_openai_service


class AICodeGenerator:
    """Generate project code using AI"""
    
    def __init__(self):
        self.openai_service = get_openai_service()
    
    async def generate_saas_files(
        self,
        project_name: str,
        task_desc: str
    ) -> List[Dict[str, Any]]:
        """Generate all files for a SaaS project using AI"""
        
        if not self.openai_service:
            # Fallback to templates if OpenAI not available - return empty to let caller handle
            return []
        
        files = []
        context = {
            "project_name": project_name,
            "task_desc": task_desc,
            "flow": "saas"
        }
        
        # Define files to generate with their specific prompts
        file_specs = [
            {
                "step": 1,
                "description": "Generate README.md",
                "path": f"{project_name}/README.md",
                "file_type": "documentation",
                "prompt": f"Create a comprehensive README.md for a SaaS project named '{project_name}'. Description: {task_desc}. Include quick start, tech stack, API docs link, and setup instructions.",
                "language": "markdown"
            },
            {
                "step": 2,
                "description": "Generate backend main.py",
                "path": f"{project_name}/backend/app/main.py",
                "file_type": "backend_main",
                "prompt": f"Create a FastAPI main.py for '{project_name}'. Description: {task_desc}. Include auth, users, and items routers. Add CORS, health check, and root endpoints.",
                "language": "python"
            },
            {
                "step": 3,
                "description": "Generate database.py",
                "path": f"{project_name}/backend/app/core/database.py",
                "file_type": "database",
                "prompt": f"Create SQLAlchemy database configuration for '{project_name}'. Support both SQLite (dev) and PostgreSQL (prod) with async support.",
                "language": "python"
            },
            {
                "step": 4,
                "description": "Generate config.py",
                "path": f"{project_name}/backend/app/core/config.py",
                "file_type": "config",
                "prompt": f"Create configuration file for '{project_name}' with SECRET_KEY, JWT settings, and other app config.",
                "language": "python"
            },
            {
                "step": 5,
                "description": "Generate security.py",
                "path": f"{project_name}/backend/app/core/security.py",
                "file_type": "auth",
                "prompt": f"Create security utilities for '{project_name}' with JWT token creation/validation, password hashing with bcrypt, and OAuth2 scheme.",
                "language": "python"
            },
            {
                "step": 6,
                "description": "Generate User model",
                "path": f"{project_name}/backend/app/models/user.py",
                "file_type": "models",
                "prompt": f"Create SQLAlchemy User model for '{project_name}' with email, password, full_name, is_active, and timestamps.",
                "language": "python"
            },
            {
                "step": 7,
                "description": "Generate Item model",
                "path": f"{project_name}/backend/app/models/item.py",
                "file_type": "models",
                "prompt": f"Create SQLAlchemy Item model for '{project_name}' appropriate for: {task_desc}. Include relationship to User as owner.",
                "language": "python"
            },
            {
                "step": 8,
                "description": "Generate auth schemas",
                "path": f"{project_name}/backend/app/schemas/auth.py",
                "file_type": "schemas",
                "prompt": f"Create Pydantic schemas for auth: UserCreate, UserResponse, and Token for '{project_name}'.",
                "language": "python"
            },
            {
                "step": 9,
                "description": "Generate item schemas",
                "path": f"{project_name}/backend/app/schemas/item.py",
                "file_type": "schemas",
                "prompt": f"Create Pydantic schemas for items: ItemCreate, ItemUpdate, and ItemResponse for '{project_name}' based on: {task_desc}.",
                "language": "python"
            },
            {
                "step": 10,
                "description": "Generate auth API endpoints",
                "path": f"{project_name}/backend/app/api/auth.py",
                "file_type": "api_endpoints",
                "prompt": f"Create FastAPI auth endpoints for '{project_name}': register and login with JWT tokens.",
                "language": "python"
            },
            {
                "step": 11,
                "description": "Generate users API endpoints",
                "path": f"{project_name}/backend/app/api/users.py",
                "file_type": "api_endpoints",
                "prompt": f"Create FastAPI users endpoints for '{project_name}': get current user (me) endpoint with JWT authentication.",
                "language": "python"
            },
            {
                "step": 12,
                "description": "Generate items API endpoints",
                "path": f"{project_name}/backend/app/api/items.py",
                "file_type": "api_endpoints",
                "prompt": f"Create FastAPI CRUD endpoints for items in '{project_name}' based on: {task_desc}. Include list, create, get, and delete operations.",
                "language": "python"
            },
            {
                "step": 13,
                "description": "Generate requirements.txt",
                "path": f"{project_name}/backend/requirements.txt",
                "file_type": "config",
                "prompt": "Create requirements.txt for a FastAPI project with SQLAlchemy, JWT auth, bcrypt, pytest, and httpx.",
                "language": "text"
            },
            {
                "step": 14,
                "description": "Generate Dockerfile",
                "path": f"{project_name}/backend/Dockerfile",
                "file_type": "docker",
                "prompt": f"Create a production-ready Dockerfile for the FastAPI backend of '{project_name}' using Python 3.11.",
                "language": "dockerfile"
            },
            {
                "step": 15,
                "description": "Generate docker-compose.yml",
                "path": f"{project_name}/docker-compose.yml",
                "file_type": "docker",
                "prompt": f"Create docker-compose.yml for '{project_name}' with backend service on port 8000.",
                "language": "yaml"
            },
            {
                "step": 16,
                "description": "Generate GitHub Actions CI",
                "path": f"{project_name}/.github/workflows/ci.yml",
                "file_type": "cicd",
                "prompt": f"Create GitHub Actions CI workflow for '{project_name}' with testing and Docker build jobs.",
                "language": "yaml"
            },
            {
                "step": 17,
                "description": "Generate tests",
                "path": f"{project_name}/backend/tests/test_api.py",
                "file_type": "tests",
                "prompt": f"Create pytest tests for '{project_name}' FastAPI app: test root endpoint and health check.",
                "language": "python"
            }
        ]
        
        # Generate each file
        for spec in file_specs:
            try:
                context["file_path"] = spec["path"]
                code = await self.openai_service.generate_code(
                    prompt=spec["prompt"],
                    file_type=spec["file_type"],
                    context=context
                )
                
                # Validate the generated code
                validation = self.openai_service.validate_code(code, spec["language"])
                if not validation["valid"]:
                    print(f"Warning: Generated code for {spec['path']} has issues: {validation['issues']}")
                    # Continue anyway - validation is not perfect
                
                files.append({
                    "step": spec["step"],
                    "description": spec["description"],
                    "path": spec["path"],
                    "content": code,
                    "language": spec["language"]
                })
                
                # Small delay to avoid rate limits
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Error generating {spec['path']}: {e}")
                # Add a minimal placeholder to avoid breaking the flow
                files.append({
                    "step": spec["step"],
                    "description": spec["description"],
                    "path": spec["path"],
                    "content": f"# Error generating this file: {str(e)}\n# Please regenerate or edit manually",
                    "language": spec["language"]
                })
        
        # Add __init__.py files
        init_paths = [
            f"{project_name}/backend/app/__init__.py",
            f"{project_name}/backend/app/api/__init__.py",
            f"{project_name}/backend/app/core/__init__.py",
            f"{project_name}/backend/app/models/__init__.py",
            f"{project_name}/backend/app/schemas/__init__.py",
            f"{project_name}/backend/tests/__init__.py",
        ]
        
        for init_path in init_paths:
            files.append({
                "step": len(files) + 1,
                "description": f"Create {init_path.split('/')[-2]}/__init__.py",
                "path": init_path,
                "content": '"""Module init"""',
                "language": "python"
            })
        
        # Add .gitignore and .env.example
        files.append({
            "step": len(files) + 1,
            "description": "Create .gitignore",
            "path": f"{project_name}/.gitignore",
            "content": '''__pycache__/
*.py[cod]
.env
*.db
.pytest_cache/
node_modules/
dist/
.vscode/''',
            "language": "text"
        })
        
        files.append({
            "step": len(files) + 1,
            "description": "Create .env.example",
            "path": f"{project_name}/.env.example",
            "content": '''DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-change-in-production''',
            "language": "text"
        })
        
        return files
    
    async def generate_api_files(
        self,
        project_name: str,
        task_desc: str
    ) -> List[Dict[str, Any]]:
        """Generate files for API-only project using AI"""
        # For API flow, generate similar to SaaS but without frontend
        return await self.generate_saas_files(project_name, task_desc)
    
    async def generate_refactor_files(
        self,
        project_name: str,
        task_desc: str
    ) -> List[Dict[str, Any]]:
        """Generate files for refactoring project using AI"""
        
        if not self.openai_service:
            # Fallback to templates - return empty to let caller handle
            return []
        
        files = []
        context = {
            "project_name": project_name,
            "task_desc": task_desc,
            "flow": "refactor"
        }
        
        file_specs = [
            {
                "step": 1,
                "description": "Generate Dockerfile",
                "path": f"{project_name}/Dockerfile",
                "file_type": "docker",
                "prompt": f"Create a modern Dockerfile for refactoring project '{project_name}'. Description: {task_desc}",
                "language": "dockerfile"
            },
            {
                "step": 2,
                "description": "Generate docker-compose.yml",
                "path": f"{project_name}/docker-compose.yml",
                "file_type": "docker",
                "prompt": f"Create docker-compose.yml for refactored '{project_name}' with volume mounting for development.",
                "language": "yaml"
            },
            {
                "step": 3,
                "description": "Generate GitHub Actions CI",
                "path": f"{project_name}/.github/workflows/ci.yml",
                "file_type": "cicd",
                "prompt": f"Create modern GitHub Actions CI/CD workflow for '{project_name}'. Include testing and deployment steps.",
                "language": "yaml"
            },
            {
                "step": 4,
                "description": "Generate pre-commit config",
                "path": f"{project_name}/.pre-commit-config.yaml",
                "file_type": "config",
                "prompt": "Create pre-commit configuration with basic hooks for code quality.",
                "language": "yaml"
            },
            {
                "step": 5,
                "description": "Generate README",
                "path": f"{project_name}/README.md",
                "file_type": "documentation",
                "prompt": f"Create README.md for modernized project '{project_name}'. Description: {task_desc}. Include quick start with Docker.",
                "language": "markdown"
            }
        ]
        
        for spec in file_specs:
            try:
                context["file_path"] = spec["path"]
                code = await self.openai_service.generate_code(
                    prompt=spec["prompt"],
                    file_type=spec["file_type"],
                    context=context
                )
                
                files.append({
                    "step": spec["step"],
                    "description": spec["description"],
                    "path": spec["path"],
                    "content": code,
                    "language": spec["language"]
                })
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"Error generating {spec['path']}: {e}")
                files.append({
                    "step": spec["step"],
                    "description": spec["description"],
                    "path": spec["path"],
                    "content": f"# Error generating this file: {str(e)}",
                    "language": spec["language"]
                })
        
        return files


# Singleton instance
_ai_generator: Optional[AICodeGenerator] = None

def get_ai_generator() -> AICodeGenerator:
    """
    Get or create AI code generator singleton.
    
    Returns:
        AICodeGenerator instance. Note that the generator's openai_service
        may be None if no API key is configured, in which case generation
        methods will return empty lists and callers should fallback to templates.
    """
    global _ai_generator
    if _ai_generator is None:
        _ai_generator = AICodeGenerator()
    return _ai_generator
