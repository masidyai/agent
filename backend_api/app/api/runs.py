"""
Runs API routes - Execution runs for projects
"""
from uuid import UUID
from typing import List, Optional
import json

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.crud import project as crud_project
from app.crud import execution as crud_execution
from app.crud import execution_step as crud_execution_step
from app.crud import project_file as crud_project_file
from app.schemas.execution import (
    ExecutionCreate,
    ExecutionResponse,
    ExecutionStepCreate,
    ExecutionStepResponse,
    ExecutionListResponse,
)
from app.schemas.project_file import ProjectFileResponse, ProjectFileCreate
from app.models.execution import ExecutionStatus, StepStatus
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


# Pydantic models for runs
class RunCreate(BaseModel):
    prompt: str
    config: Optional[dict] = None


class FileNode(BaseModel):
    name: str
    path: str
    type: str  # 'file' or 'directory'
    children: Optional[List['FileNode']] = None


class FileContent(BaseModel):
    path: str
    content: str
    language: Optional[str] = None


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


@router.post("/projects/{project_id}/runs", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
async def create_run(
    project_id: UUID,
    run_in: RunCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new run for a project"""
    # Verify project exists and user has access
    project = await crud_project.get(db, id=project_id)
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    
    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project",
        )
    
    # Generate plan steps
    plan_steps = generate_plan_steps(run_in.prompt)
    
    # Create execution
    execution_create = ExecutionCreate(
        prompt=run_in.prompt,
        plan=json.dumps(plan_steps),
    )
    execution = await crud_execution.create_with_project(
        db, obj_in=execution_create, project_id=project_id
    )
    
    # Create steps
    for i, step_data in enumerate(plan_steps):
        step_create = ExecutionStepCreate(
            step_number=i,
            name=step_data["name"],
            description=step_data.get("description"),
        )
        await crud_execution_step.create_with_execution(
            db, obj_in=step_create, execution_id=execution.id
        )
    
    await db.commit()
    
    # Reload with steps
    execution = await crud_execution.get_with_steps(db, id=execution.id)
    
    return execution


@router.get("/runs/{run_id}", response_model=ExecutionResponse)
async def get_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get run details"""
    execution = await crud_execution.get_with_steps(db, id=run_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    # Check authorization
    project = await crud_project.get(db, id=execution.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this run",
        )
    
    return execution


@router.get("/runs/{run_id}/steps", response_model=List[ExecutionStepResponse])
async def get_run_steps(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all steps for a run"""
    execution = await crud_execution.get(db, id=run_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    # Check authorization
    project = await crud_project.get(db, id=execution.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this run",
        )
    
    steps = await crud_execution_step.get_by_execution(db, execution_id=run_id)
    
    return steps


@router.get("/runs/{run_id}/files", response_model=List[ProjectFileResponse])
async def get_run_files(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get generated files for a run"""
    execution = await crud_execution.get(db, id=run_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    # Check authorization
    project = await crud_project.get(db, id=execution.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this run",
        )
    
    # Get files for the project
    files = await crud_project_file.get_by_project(db, project_id=execution.project_id)
    
    return files


@router.get("/runs/{run_id}/files/{file_path:path}", response_model=FileContent)
async def get_file_content(
    run_id: UUID,
    file_path: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get content of a specific file"""
    execution = await crud_execution.get(db, id=run_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    # Check authorization
    project = await crud_project.get(db, id=execution.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this run",
        )
    
    # Get file from database
    file = await crud_project_file.get_by_path(
        db, project_id=execution.project_id, file_path=file_path
    )
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    
    return FileContent(
        path=file.file_path,
        content=file.content,
        language=file.language,
    )


@router.post("/runs/{run_id}/start")
async def start_run(
    run_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start executing a run"""
    execution = await crud_execution.get(db, id=run_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    # Check authorization
    project = await crud_project.get(db, id=execution.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to start this run",
        )
    
    if execution.status == ExecutionStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Run is already in progress",
        )
    
    # Update status
    await crud_execution.update_status(db, execution=execution, status=ExecutionStatus.IN_PROGRESS)
    
    # Update project status
    await crud_project.update_status(db, project=project, status=ProjectStatus.BUILDING)
    
    await db.commit()
    
    # Add background task to execute the run
    background_tasks.add_task(execute_run, run_id)
    
    return {"message": "Run started", "run_id": str(run_id)}


@router.post("/runs/{run_id}/stop")
async def stop_run(
    run_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stop a running execution"""
    execution = await crud_execution.get(db, id=run_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    # Check authorization
    project = await crud_project.get(db, id=execution.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to stop this run",
        )
    
    await crud_execution.update_status(db, execution=execution, status=ExecutionStatus.STOPPED)
    await db.commit()
    
    return {"message": "Run stopped"}


@router.post("/runs/{run_id}/message")
async def send_message(
    run_id: UUID,
    message: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message to the AI during a run"""
    execution = await crud_execution.get(db, id=run_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )
    
    # Check authorization
    project = await crud_project.get(db, id=execution.project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to send messages to this run",
        )
    
    # In production, this would interact with the AI service
    return {"message": "Message received", "response": "Processing your request..."}


@router.get("/projects/{project_id}/runs", response_model=ExecutionListResponse)
async def list_project_runs(
    project_id: UUID,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all runs for a project"""
    # Verify project access
    project = await crud_project.get(db, id=project_id)
    if not project or project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project",
        )
    
    executions = await crud_execution.get_by_project(
        db, project_id=project_id, skip=skip, limit=limit
    )
    total = await crud_execution.count_by_project(db, project_id=project_id)
    
    return ExecutionListResponse(
        executions=executions,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
    )


async def execute_run(run_id: UUID):
    """Background task to execute a run"""
    import asyncio
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            execution = await crud_execution.get_with_steps(db, id=run_id)
            if not execution:
                return
            
            # Get project
            project = await crud_project.get(db, id=execution.project_id)
            if not project:
                return
            
            # Execute each step
            for step in execution.steps:
                if execution.status == ExecutionStatus.STOPPED:
                    break
                    
                # Update step to in_progress
                await crud_execution_step.update_status(
                    db, step=step, status=StepStatus.IN_PROGRESS
                )
                await db.commit()
                
                await asyncio.sleep(2)  # Simulate work
                
                # Generate sample files for certain steps
                if "structure" in step.name.lower():
                    sample_files = generate_project_files()
                    for file_data in sample_files:
                        if file_data["type"] == "file":
                            file_create = ProjectFileCreate(
                                file_path=file_data["path"],
                                content=file_data.get("content", ""),
                                language=detect_language(file_data["path"]),
                            )
                            await crud_project_file.create_with_project(
                                db, obj_in=file_create, project_id=project.id
                            )
                
                # Update step to completed
                await crud_execution_step.update_status(
                    db, 
                    step=step, 
                    status=StepStatus.COMPLETED,
                    logs=f"Completed: {step.name}",
                )
                await db.commit()
            
            # Mark run as completed
            if execution.status != ExecutionStatus.STOPPED:
                await crud_execution.update_status(
                    db, execution=execution, status=ExecutionStatus.COMPLETED
                )
                await crud_project.update_status(
                    db, project=project, status=ProjectStatus.COMPLETED
                )
            
            await db.commit()
            
        except Exception as e:
            print(f"Error executing run: {e}")
            # Mark as failed
            try:
                execution = await crud_execution.get(db, id=run_id)
                if execution:
                    await crud_execution.update_status(
                        db, execution=execution, status=ExecutionStatus.FAILED
                    )
                    await db.commit()
            except Exception:
                pass


def detect_language(file_path: str) -> Optional[str]:
    """Detect programming language from file extension"""
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
        "yml": "yaml",
        "yaml": "yaml",
    }
    return language_map.get(ext, "text")


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
