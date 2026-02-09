"""
Runs API routes - Execution runs for projects
"""
from uuid import UUID
from typing import List, Optional
import json

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


# Pydantic models for runs
class RunCreate(BaseModel):
    prompt: str
    config: Optional[dict] = None


class StepResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: str
    order: int
    logs: Optional[str] = None

    class Config:
        from_attributes = True


class RunResponse(BaseModel):
    id: str
    project_id: str
    prompt: str
    status: str
    plan: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    steps: List[StepResponse] = []

    class Config:
        from_attributes = True


class FileNode(BaseModel):
    name: str
    path: str
    type: str  # 'file' or 'directory'
    children: Optional[List['FileNode']] = None


class FileContent(BaseModel):
    path: str
    content: str
    language: Optional[str] = None


# In-memory storage for runs (in production, use database)
runs_store = {}
steps_store = {}
files_store = {}


def generate_plan_steps(prompt: str) -> List[dict]:
    """Generate execution plan based on prompt"""
    base_steps = [
        {"name": "Analyze requirements", "description": "Understanding project requirements"},
        {"name": "Create project structure", "description": "Setting up directories and base files"},
        {"name": "Set up backend", "description": "Configuring backend framework and database"},
        {"name": "Implement authentication", "description": "Adding user auth and security"},
        {"name": "Create API endpoints", "description": "Building REST API routes"},
        {"name": "Set up frontend", "description": "Creating UI components"},
        {"name": "Add Docker configuration", "description": "Containerization setup"},
        {"name": "Create CI/CD pipeline", "description": "GitHub Actions workflow"},
        {"name": "Write tests", "description": "Unit and integration tests"},
        {"name": "Generate documentation", "description": "README and API docs"},
    ]
    return base_steps


@router.post("/projects/{project_id}/runs", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
async def create_run(
    project_id: UUID,
    run_in: RunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new run for a project"""
    # Verify project exists and user has access
    result = await db.execute(
        select(Project).where(
            and_(Project.id == project_id, Project.user_id == current_user.id)
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    # Create run
    run_id = str(UUID(int=len(runs_store) + 1).hex[:8]) + "-" + str(project_id)[:8]
    
    # Generate plan steps
    plan_steps = generate_plan_steps(run_in.prompt)
    
    run = {
        "id": run_id,
        "project_id": str(project_id),
        "prompt": run_in.prompt,
        "status": "pending",
        "plan": json.dumps(plan_steps),
        "created_at": datetime.utcnow(),
        "updated_at": None,
    }
    runs_store[run_id] = run
    
    # Create steps
    steps = []
    for i, step_data in enumerate(plan_steps):
        step_id = f"{run_id}-step-{i}"
        step = {
            "id": step_id,
            "run_id": run_id,
            "name": step_data["name"],
            "description": step_data.get("description"),
            "status": "pending",
            "order": i,
            "logs": None,
        }
        steps_store[step_id] = step
        steps.append(step)
    
    # Initialize files for this run
    files_store[run_id] = []
    
    return {**run, "steps": steps}


@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get run details"""
    run = runs_store.get(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    # Get steps for this run
    steps = [s for s in steps_store.values() if s.get("run_id") == run_id]
    steps.sort(key=lambda x: x["order"])
    
    return {**run, "steps": steps}


@router.get("/runs/{run_id}/steps", response_model=List[StepResponse])
async def get_run_steps(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all steps for a run"""
    run = runs_store.get(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    steps = [s for s in steps_store.values() if s.get("run_id") == run_id]
    steps.sort(key=lambda x: x["order"])
    
    return steps


@router.get("/runs/{run_id}/files", response_model=List[FileNode])
async def get_run_files(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get generated files for a run"""
    run = runs_store.get(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    return files_store.get(run_id, [])


@router.get("/runs/{run_id}/files/{file_path:path}", response_model=FileContent)
async def get_file_content(
    run_id: str,
    file_path: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get content of a specific file"""
    run = runs_store.get(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    # Find file in files store
    files = files_store.get(run_id, [])
    
    def find_file(nodes: List[dict], path: str) -> Optional[dict]:
        for node in nodes:
            if node["path"] == path:
                return node
            if node.get("children"):
                found = find_file(node["children"], path)
                if found:
                    return found
        return None
    
    file_node = find_file(files, file_path)
    if not file_node or file_node["type"] != "file":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    
    # Return file content (in production, read from disk/storage)
    content = file_node.get("content", "// File content would be here")
    
    # Detect language from extension
    ext = file_path.split(".")[-1] if "." in file_path else ""
    language_map = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "tsx": "typescript",
        "jsx": "javascript",
        "json": "json",
        "md": "markdown",
        "html": "html",
        "css": "css",
    }
    
    return FileContent(
        path=file_path,
        content=content,
        language=language_map.get(ext, "text"),
    )


@router.post("/runs/{run_id}/start")
async def start_run(
    run_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start executing a run"""
    run = runs_store.get(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    if run["status"] == "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Run is already in progress",
        )
    
    # Update status
    run["status"] = "in_progress"
    run["updated_at"] = datetime.utcnow()
    
    # Add background task to execute the run
    background_tasks.add_task(execute_run, run_id)
    
    return {"message": "Run started", "run_id": run_id}


@router.post("/runs/{run_id}/stop")
async def stop_run(
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stop a running execution"""
    run = runs_store.get(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    run["status"] = "stopped"
    run["updated_at"] = datetime.utcnow()
    
    return {"message": "Run stopped"}


@router.post("/runs/{run_id}/message")
async def send_message(
    run_id: str,
    message: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message to the AI during a run"""
    run = runs_store.get(run_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    # In production, this would interact with the AI service
    return {"message": "Message received", "response": "Processing your request..."}


@router.get("/projects/{project_id}/runs", response_model=List[RunResponse])
async def list_project_runs(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all runs for a project"""
    project_runs = [
        {**run, "steps": [s for s in steps_store.values() if s.get("run_id") == run["id"]]}
        for run in runs_store.values()
        if run.get("project_id") == str(project_id)
    ]
    return project_runs


async def execute_run(run_id: str):
    """Background task to execute a run"""
    import asyncio
    
    run = runs_store.get(run_id)
    if not run:
        return
    
    # Get steps
    steps = [s for s in steps_store.values() if s.get("run_id") == run_id]
    steps.sort(key=lambda x: x["order"])
    
    # Execute each step
    for step in steps:
        if run["status"] == "stopped":
            break
            
        step["status"] = "in_progress"
        await asyncio.sleep(2)  # Simulate work
        
        # Generate sample files for certain steps
        if "structure" in step["name"].lower():
            files_store[run_id] = generate_project_files()
        
        step["status"] = "completed"
        step["logs"] = f"Completed: {step['name']}"
    
    # Mark run as completed
    if run["status"] != "stopped":
        run["status"] = "completed"
    run["updated_at"] = datetime.utcnow()


def generate_project_files() -> List[dict]:
    """Generate sample project file structure"""
    return [
        {
            "name": "src",
            "path": "src",
            "type": "directory",
            "children": [
                {
                    "name": "app",
                    "path": "src/app",
                    "type": "directory",
                    "children": [
                        {"name": "page.tsx", "path": "src/app/page.tsx", "type": "file", "content": "'use client'\n\nexport default function Home() {\n  return <div>Hello World</div>\n}"},
                        {"name": "layout.tsx", "path": "src/app/layout.tsx", "type": "file", "content": "export default function RootLayout({ children }) {\n  return (\n    <html>\n      <body>{children}</body>\n    </html>\n  )\n}"},
                    ],
                },
                {
                    "name": "components",
                    "path": "src/components",
                    "type": "directory",
                    "children": [
                        {"name": "Button.tsx", "path": "src/components/Button.tsx", "type": "file", "content": "export function Button({ children, onClick }) {\n  return <button onClick={onClick}>{children}</button>\n}"},
                    ],
                },
            ],
        },
        {"name": "package.json", "path": "package.json", "type": "file", "content": '{\n  "name": "my-app",\n  "version": "1.0.0",\n  "dependencies": {\n    "react": "^18.0.0",\n    "next": "^14.0.0"\n  }\n}'},
        {"name": "README.md", "path": "README.md", "type": "file", "content": "# My App\n\nGenerated by Masidy AI"},
        {"name": ".gitignore", "path": ".gitignore", "type": "file", "content": "node_modules/\n.next/\n.env"},
    ]
