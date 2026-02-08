"""
Masidy Backend API

FastAPI server that wraps the Masidy Agent Runtime for the web IDE.
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Add masidy_agent_runtime to path
sys.path.insert(0, str(Path(__file__).parent.parent / "masidy_agent_runtime"))

app = FastAPI(
    title="Masidy API",
    description="Backend API for the Masidy AI Agent Platform",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:12000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for projects (would be database in production)
projects_db: dict = {}
executions_db: dict = {}

# State file path
STATE_FILE = Path(__file__).parent.parent / "masidy_agent_runtime" / "memory" / "state.json"


class ProjectCreate(BaseModel):
    prompt: str
    flow: str = "saas"
    name: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    prompt: str
    flow: str
    status: str
    created_at: str
    steps_completed: int
    steps_total: int
    output_path: Optional[str] = None


class ExecutionStatus(BaseModel):
    id: str
    project_id: str
    status: str
    current_step: int
    total_steps: int
    current_step_description: str
    files_created: list[str]
    errors: list[str]


class PlanStep(BaseModel):
    id: int
    description: str
    tool_name: str
    status: str = "pending"


class ExecutionPlan(BaseModel):
    project_id: str
    flow: str
    steps: list[PlanStep]
    estimated_time: str


def load_state() -> dict:
    """Load state from file."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"projects": [], "executions": []}


def save_state(state: dict):
    """Save state to file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


def generate_plan(prompt: str, flow: str) -> list[PlanStep]:
    """Generate execution plan based on flow type."""
    plans = {
        "saas": [
            PlanStep(id=1, description="Create project directory structure", tool_name="create_directory"),
            PlanStep(id=2, description="Initialize FastAPI backend application", tool_name="write_file"),
            PlanStep(id=3, description="Set up database models with SQLAlchemy", tool_name="write_file"),
            PlanStep(id=4, description="Implement user authentication", tool_name="write_file"),
            PlanStep(id=5, description="Create API endpoints", tool_name="write_file"),
            PlanStep(id=6, description="Build React frontend components", tool_name="write_file"),
            PlanStep(id=7, description="Create main dashboard page", tool_name="write_file"),
            PlanStep(id=8, description="Add Docker configuration", tool_name="write_file"),
            PlanStep(id=9, description="Write unit tests", tool_name="write_file"),
            PlanStep(id=10, description="Add CI/CD pipeline", tool_name="write_file"),
            PlanStep(id=11, description="Generate README documentation", tool_name="write_file"),
            PlanStep(id=12, description="Create requirements.txt", tool_name="write_file"),
        ],
        "api": [
            PlanStep(id=1, description="Create project directory structure", tool_name="create_directory"),
            PlanStep(id=2, description="Initialize FastAPI application", tool_name="write_file"),
            PlanStep(id=3, description="Set up database models", tool_name="write_file"),
            PlanStep(id=4, description="Create CRUD endpoints", tool_name="write_file"),
            PlanStep(id=5, description="Add input validation with Pydantic", tool_name="write_file"),
            PlanStep(id=6, description="Implement error handling", tool_name="write_file"),
            PlanStep(id=7, description="Write comprehensive unit tests", tool_name="write_file"),
            PlanStep(id=8, description="Add Docker setup", tool_name="write_file"),
            PlanStep(id=9, description="Generate OpenAPI documentation", tool_name="write_file"),
            PlanStep(id=10, description="Create GitHub Actions CI/CD", tool_name="write_file"),
        ],
        "refactor": [
            PlanStep(id=1, description="Analyze existing codebase structure", tool_name="list_directory"),
            PlanStep(id=2, description="Add type hints to Python files", tool_name="write_file"),
            PlanStep(id=3, description="Restructure project layout", tool_name="create_directory"),
            PlanStep(id=4, description="Create Dockerfile", tool_name="write_file"),
            PlanStep(id=5, description="Add docker-compose.yml", tool_name="write_file"),
            PlanStep(id=6, description="Generate test suite", tool_name="write_file"),
            PlanStep(id=7, description="Configure pre-commit hooks", tool_name="write_file"),
            PlanStep(id=8, description="Set up GitHub Actions workflow", tool_name="write_file"),
        ],
    }
    return plans.get(flow, plans["api"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Masidy API",
        "version": "1.0.0",
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "runtime_available": True,
        "flows_available": ["saas", "api", "refactor"],
    }


@app.get("/api/projects", response_model=list[ProjectResponse])
async def list_projects():
    """List all projects."""
    state = load_state()
    return state.get("projects", [])


@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate):
    """Create a new project."""
    project_id = str(uuid.uuid4())[:8]
    
    # Generate name from prompt if not provided
    name = project.name
    if not name:
        name = project.prompt.lower()
        for word in ["build", "create", "make", "a", "an", "the"]:
            name = name.replace(word, "")
        name = "_".join(name.split()[:3]).strip("_")
        name = "".join(c for c in name if c.isalnum() or c == "_")
        name = name or "my_project"
    
    plan = generate_plan(project.prompt, project.flow)
    
    new_project = {
        "id": project_id,
        "name": name,
        "prompt": project.prompt,
        "flow": project.flow,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "steps_completed": 0,
        "steps_total": len(plan),
        "output_path": f"./{name}/",
    }
    
    # Save to state
    state = load_state()
    state.setdefault("projects", []).insert(0, new_project)
    save_state(state)
    
    projects_db[project_id] = new_project
    
    return ProjectResponse(**new_project)


@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Get project details."""
    state = load_state()
    for project in state.get("projects", []):
        if project["id"] == project_id:
            return ProjectResponse(**project)
    raise HTTPException(status_code=404, detail="Project not found")


@app.post("/api/projects/{project_id}/plan", response_model=ExecutionPlan)
async def get_execution_plan(project_id: str):
    """Generate execution plan for a project."""
    state = load_state()
    project = None
    for p in state.get("projects", []):
        if p["id"] == project_id:
            project = p
            break
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    steps = generate_plan(project["prompt"], project["flow"])
    
    return ExecutionPlan(
        project_id=project_id,
        flow=project["flow"],
        steps=steps,
        estimated_time=f"{len(steps) * 2}-{len(steps) * 4} seconds",
    )


@app.post("/api/projects/{project_id}/execute")
async def execute_project(project_id: str, background_tasks: BackgroundTasks):
    """Start project execution."""
    state = load_state()
    project = None
    for p in state.get("projects", []):
        if p["id"] == project_id:
            project = p
            break
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    execution_id = str(uuid.uuid4())[:8]
    
    execution = {
        "id": execution_id,
        "project_id": project_id,
        "status": "running",
        "current_step": 0,
        "total_steps": project["steps_total"],
        "current_step_description": "Starting...",
        "files_created": [],
        "errors": [],
    }
    
    executions_db[execution_id] = execution
    
    # Update project status
    project["status"] = "in_progress"
    save_state(state)
    
    return {"execution_id": execution_id, "status": "started"}


@app.get("/api/executions/{execution_id}/stream")
async def stream_execution(execution_id: str):
    """Stream execution progress via Server-Sent Events."""
    
    async def generate():
        execution = executions_db.get(execution_id)
        if not execution:
            yield f"data: {json.dumps({'error': 'Execution not found'})}\n\n"
            return
        
        project_id = execution["project_id"]
        state = load_state()
        project = None
        for p in state.get("projects", []):
            if p["id"] == project_id:
                project = p
                break
        
        if not project:
            yield f"data: {json.dumps({'error': 'Project not found'})}\n\n"
            return
        
        plan = generate_plan(project["prompt"], project["flow"])
        
        # Simulate execution
        for i, step in enumerate(plan):
            execution["current_step"] = i + 1
            execution["current_step_description"] = step.description
            step.status = "executing"
            
            yield f"data: {json.dumps({'type': 'step_start', 'step': i + 1, 'total': len(plan), 'description': step.description})}\n\n"
            
            # Simulate work
            await asyncio.sleep(0.5 + (0.3 * (i % 3)))
            
            # Generate mock file
            mock_file = f"project/{step.description.lower().replace(' ', '_')}.py"
            execution["files_created"].append(mock_file)
            step.status = "completed"
            
            yield f"data: {json.dumps({'type': 'step_complete', 'step': i + 1, 'file': mock_file})}\n\n"
        
        # Update project status
        project["status"] = "completed"
        project["steps_completed"] = len(plan)
        save_state(state)
        
        execution["status"] = "completed"
        
        yield f"data: {json.dumps({'type': 'complete', 'files_created': execution['files_created']})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/api/executions/{execution_id}", response_model=ExecutionStatus)
async def get_execution_status(execution_id: str):
    """Get current execution status."""
    execution = executions_db.get(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return ExecutionStatus(**execution)


@app.get("/api/flows")
async def list_flows():
    """List available flows."""
    return {
        "flows": [
            {
                "id": "saas",
                "name": "SaaS Application",
                "description": "Full-stack SaaS with auth, database, and UI",
                "steps": 12,
            },
            {
                "id": "api",
                "name": "API Service",
                "description": "REST API with CRUD, tests, and docs",
                "steps": 10,
            },
            {
                "id": "refactor",
                "name": "Repository Refactor",
                "description": "Modernize with Docker, CI/CD, and tests",
                "steps": 8,
            },
        ]
    }


@app.get("/api/tools")
async def list_tools():
    """List available tools."""
    return {
        "tools": [
            {"name": "write_file", "description": "Write content to a file"},
            {"name": "read_file", "description": "Read content from a file"},
            {"name": "create_directory", "description": "Create a directory"},
            {"name": "list_directory", "description": "List directory contents"},
            {"name": "delete_file", "description": "Delete a file"},
            {"name": "run_command", "description": "Execute shell command"},
            {"name": "git_init", "description": "Initialize git repository"},
            {"name": "git_commit", "description": "Commit changes"},
            {"name": "git_push", "description": "Push to remote"},
            # ... more tools
        ],
        "total": 33,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
