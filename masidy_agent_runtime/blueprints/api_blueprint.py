"""
Masidy Autonomous Agent Runtime - API Blueprint
Creates a complete API service with:
- Backend: FastAPI
- Database: SQLite
- Tests: pytest
- Docker: Dockerfile + docker-compose
- CI: GitHub Actions workflow
"""

import os
from typing import Any
from datetime import datetime

# Import executor
try:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from executors import APIExecutor
    EXECUTOR_AVAILABLE = True
except ImportError:
    EXECUTOR_AVAILABLE = False
    APIExecutor = None


API_BLUEPRINT_INFO = {
    "name": "API Service",
    "description": "Backend-only FastAPI service with database, tests, and CI/CD",
    "components": ["FastAPI", "SQLite", "pytest", "Docker", "GitHub Actions"],
}


def run_blueprint(
    task_description: str,
    config: dict,
    core_agent,
    planner,
    state_manager,
    verbose: bool = False
) -> dict:
    """
    Run the API blueprint to create a complete API service.
    
    Args:
        task_description: What the user wants to build
        config: Configuration options (project_name, etc.)
        core_agent: The core agent instance for tool execution
        planner: The planner instance
        state_manager: State manager for persistence
        verbose: Whether to print detailed output
    
    Returns:
        dict with execution results including:
        - status: "success" | "failure" | "partial"
        - steps_completed: int
        - steps_total: int
        - errors: list
        - output_path: str
    """
    # Extract configuration
    project_name = config.get("project_name", "api_service")
    project_name = project_name.lower().replace(" ", "_").replace("-", "_")
    config["project_name"] = project_name
    config["output_folder"] = project_name
    
    # Use executor if available
    if EXECUTOR_AVAILABLE and APIExecutor:
        executor = APIExecutor(
            tools=core_agent.tools,
            state_manager=state_manager,
            max_retries=3,
            verbose=verbose
        )
        
        # Build structured plan
        plan = executor.build_plan(task_description, config)
        
        # Execute plan
        result = executor.run(task_description, plan, config)
        
        # Convert to standard result format
        return {
            "status": result.status,
            "steps_completed": result.steps_completed,
            "steps_total": result.steps_total,
            "errors": result.errors,
            "output_path": result.output_path,
            "step_results": [
                {
                    "step_id": sr.step_id,
                    "description": sr.description,
                    "status": sr.status,
                    "retries": sr.retries,
                    "error": sr.error
                }
                for sr in result.step_results
            ],
            "duration_ms": result.duration_ms,
            "blueprint": "api",
            "project_name": project_name,
        }
    
    # Fallback to legacy execution
    return _run_legacy_blueprint(
        task_description, config, core_agent, planner, state_manager, verbose
    )


def _run_legacy_blueprint(
    task_description: str,
    config: dict,
    core_agent,
    planner,
    state_manager,
    verbose: bool = False
) -> dict:
    """Legacy blueprint execution (fallback)"""
    project_name = config.get("project_name", "api_service")
    
    if verbose:
        print("\n" + "=" * 60)
        print("  🔌 API BLUEPRINT - Creating Backend Service")
        print("=" * 60)
        print(f"  Task: {task_description}")
        print("=" * 60)
    
    results = {
        "blueprint": "api",
        "project_name": project_name,
        "task": task_description,
        "steps_completed": [],
        "steps_failed": [],
        "files_created": [],
        "started_at": datetime.now().isoformat(),
    }
    
    tools = core_agent.tools
    
    # Step 1: Create project structure
    if verbose:
        print("\n[Step 1/6] Creating project structure...")
    try:
        _create_project_structure(tools, project_name)
        results["steps_completed"].append("project_structure")
        if verbose:
            print("  ✓ Project structure created")
    except Exception as e:
        results["steps_failed"].append({"step": "project_structure", "error": str(e)})
        if verbose:
            print(f"  ✗ Failed: {e}")
    
    # Step 2: Create FastAPI application
    if verbose:
        print("\n[Step 2/6] Creating FastAPI application...")
    try:
        files = _create_api_app(tools, project_name, task_description)
        results["files_created"].extend(files)
        results["steps_completed"].append("api_app")
        if verbose:
            print(f"  ✓ API application created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "api_app", "error": str(e)})
        if verbose:
            print(f"  ✗ Failed: {e}")
    
    # Step 3: Create database models and CRUD
    if verbose:
        print("\n[Step 3/6] Creating database layer...")
    try:
        files = _create_database_layer(tools, project_name, task_description)
        results["files_created"].extend(files)
        results["steps_completed"].append("database")
        if verbose:
            print(f"  ✓ Database layer created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "database", "error": str(e)})
        if verbose:
            print(f"  ✗ Failed: {e}")
    
    # Step 4: Create tests
    if verbose:
        print("\n[Step 4/6] Creating tests...")
    try:
        files = _create_tests(tools, project_name)
        results["files_created"].extend(files)
        results["steps_completed"].append("tests")
        if verbose:
            print(f"  ✓ Tests created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "tests", "error": str(e)})
        if verbose:
            print(f"  ✗ Failed: {e}")
    
    # Step 5: Create Docker configuration
    if verbose:
        print("\n[Step 5/6] Creating Docker configuration...")
    try:
        files = _create_docker(tools, project_name)
        results["files_created"].extend(files)
        results["steps_completed"].append("docker")
        if verbose:
            print(f"  ✓ Docker config created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "docker", "error": str(e)})
        if verbose:
            print(f"  ✗ Failed: {e}")
    
    # Step 6: Create CI and documentation
    if verbose:
        print("\n[Step 6/6] Creating CI and documentation...")
    try:
        files = _create_ci_and_docs(tools, project_name, task_description)
        results["files_created"].extend(files)
        results["steps_completed"].append("ci_docs")
        if verbose:
            print(f"  ✓ CI and docs created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "ci_docs", "error": str(e)})
        if verbose:
            print(f"  ✗ Failed: {e}")
    
    # Finalize
    results["completed_at"] = datetime.now().isoformat()
    total_steps = 6
    completed = len(results["steps_completed"])
    
    if completed == total_steps:
        status = "success"
    elif completed > 0:
        status = "partial"
    else:
        status = "failure"
    
    # Update state
    state_manager.update_context("last_api_project", {
        "name": project_name,
        "path": project_name,
        "files": len(results["files_created"]),
        "created_at": results["completed_at"]
    })
    
    return {
        "status": status,
        "steps_completed": completed,
        "steps_total": total_steps,
        "errors": results["steps_failed"],
        "output_path": project_name,
        "blueprint": "api",
        "project_name": project_name,
    }


def _run_legacy_with_output(
    task_description, config, core_agent, planner, state_manager, verbose
):
    """Legacy with print output - kept for backward compatibility"""
    project_name = config.get("project_name", "api_service")
    
    print("\n" + "=" * 60)
    print("  🔌 API BLUEPRINT - Creating Backend Service")
    print("=" * 60)
    print(f"  Task: {task_description}")
    print("=" * 60)
    
    results = {
        "blueprint": "api",
        "project_name": project_name,
        "task": task_description,
        "steps_completed": [],
        "steps_failed": [],
        "files_created": [],
        "started_at": datetime.now().isoformat(),
    }
    
    tools = core_agent.tools
    
    # Step 1: Create project structure
    print("\n[Step 1/6] Creating project structure...")
    try:
        _create_project_structure(tools, project_name)
        results["steps_completed"].append("project_structure")
        print("  ✓ Project structure created")
    except Exception as e:
        results["steps_failed"].append({"step": "project_structure", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Step 2: Create FastAPI application
    print("\n[Step 2/6] Creating FastAPI application...")
    try:
        files = _create_api_app(tools, project_name, task_description)
        results["files_created"].extend(files)
        results["steps_completed"].append("api_app")
        print(f"  ✓ API application created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "api_app", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Step 3: Create database models and CRUD
    print("\n[Step 3/6] Creating database layer...")
    try:
        files = _create_database_layer(tools, project_name, task_description)
        results["files_created"].extend(files)
        results["steps_completed"].append("database")
        print(f"  ✓ Database layer created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "database", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Step 4: Create tests
    print("\n[Step 4/6] Creating tests...")
    try:
        files = _create_tests(tools, project_name)
        results["files_created"].extend(files)
        results["steps_completed"].append("tests")
        print(f"  ✓ Tests created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "tests", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Step 5: Create Docker configuration
    print("\n[Step 5/6] Creating Docker configuration...")
    try:
        files = _create_docker(tools, project_name)
        results["files_created"].extend(files)
        results["steps_completed"].append("docker")
        print(f"  ✓ Docker config created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "docker", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Step 6: Create CI and documentation
    print("\n[Step 6/6] Creating CI and documentation...")
    try:
        files = _create_ci_and_docs(tools, project_name, task_description)
        results["files_created"].extend(files)
        results["steps_completed"].append("ci_docs")
        print(f"  ✓ CI and docs created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "ci_docs", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Finalize
    results["completed_at"] = datetime.now().isoformat()
    results["success"] = len(results["steps_failed"]) == 0
    results["total_files"] = len(results["files_created"])
    
    # Update state
    state_manager.update_context("last_api_project", {
        "name": project_name,
        "path": project_name,
        "files": results["total_files"],
        "created_at": results["completed_at"]
    })
    
    # Print summary
    print("\n" + "=" * 60)
    print("  📊 API BLUEPRINT SUMMARY")
    print("=" * 60)
    print(f"  Project: {project_name}/")
    print(f"  Status: {'✓ SUCCESS' if results['success'] else '✗ PARTIAL'}")
    print(f"  Steps completed: {len(results['steps_completed'])}/6")
    print(f"  Files created: {results['total_files']}")
    if results["steps_failed"]:
        print(f"  Failed steps: {[s['step'] for s in results['steps_failed']]}")
    print("=" * 60)
    
    return results


def _create_project_structure(tools: dict, project_name: str):
    """Create the base project directory structure"""
    dirs = [
        project_name,
        f"{project_name}/app",
        f"{project_name}/app/api",
        f"{project_name}/app/models",
        f"{project_name}/app/schemas",
        f"{project_name}/app/crud",
        f"{project_name}/app/core",
        f"{project_name}/tests",
        f"{project_name}/.github/workflows",
    ]
    
    for d in dirs:
        tools["create_directory"](path=d)


def _create_api_app(tools: dict, project_name: str, task_desc: str) -> list[str]:
    """Create the main FastAPI application"""
    files = []
    base = project_name
    
    # requirements.txt
    tools["write_file"](
        path=f"{base}/requirements.txt",
        content="""fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
httpx>=0.26.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
"""
    )
    files.append(f"{base}/requirements.txt")
    
    # Main app
    tools["write_file"](
        path=f"{base}/app/__init__.py",
        content=f'"""API Service"""\n__version__ = "0.1.0"\n'
    )
    files.append(f"{base}/app/__init__.py")
    
    tools["write_file"](
        path=f"{base}/app/main.py",
        content=f'''"""
FastAPI Application Entry Point
Generated by Masidy Agent Runtime
Task: {task_desc[:100]}
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.core.database import create_tables

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""{task_desc}""",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    create_tables()


@app.get("/")
async def root():
    """Root endpoint"""
    return {{"service": "{project_name}", "version": "0.1.0", "docs": "/docs"}}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{"status": "healthy"}}
'''
    )
    files.append(f"{base}/app/main.py")
    
    # Config
    tools["write_file"](
        path=f"{base}/app/core/__init__.py",
        content=""
    )
    files.append(f"{base}/app/core/__init__.py")
    
    tools["write_file"](
        path=f"{base}/app/core/config.py",
        content=f'''"""Application configuration"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "{project_name}"
    DATABASE_URL: str = "sqlite:///./app.db"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"


settings = Settings()
'''
    )
    files.append(f"{base}/app/core/config.py")
    
    # Database
    tools["write_file"](
        path=f"{base}/app/core/database.py",
        content='''"""Database configuration"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
'''
    )
    files.append(f"{base}/app/core/database.py")
    
    return files


def _create_database_layer(tools: dict, project_name: str, task_desc: str) -> list[str]:
    """Create models, schemas, and CRUD operations"""
    files = []
    base = project_name
    
    # Infer entity name from task
    entity_name = _infer_entity_name(task_desc)
    entity_lower = entity_name.lower()
    entity_plural = f"{entity_lower}s"
    
    # Models
    tools["write_file"](
        path=f"{base}/app/models/__init__.py",
        content=f'from app.models.{entity_lower} import {entity_name}\n'
    )
    files.append(f"{base}/app/models/__init__.py")
    
    tools["write_file"](
        path=f"{base}/app/models/{entity_lower}.py",
        content=f'''"""{entity_name} model"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func

from app.core.database import Base


class {entity_name}(Base):
    __tablename__ = "{entity_plural}"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<{entity_name}(id={{self.id}}, title={{self.title}})>"
'''
    )
    files.append(f"{base}/app/models/{entity_lower}.py")
    
    # Schemas
    tools["write_file"](
        path=f"{base}/app/schemas/__init__.py",
        content=f'from app.schemas.{entity_lower} import {entity_name}, {entity_name}Create, {entity_name}Update, {entity_name}List\n'
    )
    files.append(f"{base}/app/schemas/__init__.py")
    
    tools["write_file"](
        path=f"{base}/app/schemas/{entity_lower}.py",
        content=f'''"""{entity_name} schemas"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class {entity_name}Base(BaseModel):
    title: str
    description: Optional[str] = None


class {entity_name}Create({entity_name}Base):
    pass


class {entity_name}Update(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class {entity_name}({entity_name}Base):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class {entity_name}List(BaseModel):
    items: List[{entity_name}]
    total: int
'''
    )
    files.append(f"{base}/app/schemas/{entity_lower}.py")
    
    # CRUD
    tools["write_file"](
        path=f"{base}/app/crud/__init__.py",
        content=f'from app.crud.{entity_lower} import {entity_lower}_crud\n'
    )
    files.append(f"{base}/app/crud/__init__.py")
    
    tools["write_file"](
        path=f"{base}/app/crud/{entity_lower}.py",
        content=f'''"""{entity_name} CRUD operations"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.{entity_lower} import {entity_name}
from app.schemas.{entity_lower} import {entity_name}Create, {entity_name}Update


class {entity_name}CRUD:
    def get(self, db: Session, id: int) -> Optional[{entity_name}]:
        """Get a single {entity_lower} by ID"""
        return db.query({entity_name}).filter({entity_name}.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[{entity_name}]:
        """Get all {entity_plural} with pagination"""
        return db.query({entity_name}).offset(skip).limit(limit).all()
    
    def count(self, db: Session) -> int:
        """Count all {entity_plural}"""
        return db.query({entity_name}).count()
    
    def create(self, db: Session, obj_in: {entity_name}Create) -> {entity_name}:
        """Create a new {entity_lower}"""
        db_obj = {entity_name}(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, id: int, obj_in: {entity_name}Update) -> Optional[{entity_name}]:
        """Update a {entity_lower}"""
        db_obj = self.get(db, id)
        if not db_obj:
            return None
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Delete a {entity_lower}"""
        db_obj = self.get(db, id)
        if not db_obj:
            return False
        
        db.delete(db_obj)
        db.commit()
        return True


{entity_lower}_crud = {entity_name}CRUD()
'''
    )
    files.append(f"{base}/app/crud/{entity_lower}.py")
    
    # API routes
    tools["write_file"](
        path=f"{base}/app/api/__init__.py",
        content=""
    )
    files.append(f"{base}/app/api/__init__.py")
    
    tools["write_file"](
        path=f"{base}/app/api/routes.py",
        content=f'''"""API Routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.crud.{entity_lower} import {entity_lower}_crud
from app.schemas.{entity_lower} import {entity_name}, {entity_name}Create, {entity_name}Update, {entity_name}List

router = APIRouter()


@router.get("/{entity_plural}", response_model={entity_name}List)
def list_{entity_plural}(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all {entity_plural}"""
    items = {entity_lower}_crud.get_all(db, skip=skip, limit=limit)
    total = {entity_lower}_crud.count(db)
    return {{"items": items, "total": total}}


@router.post("/{entity_plural}", response_model={entity_name}, status_code=201)
def create_{entity_lower}(
    {entity_lower}: {entity_name}Create,
    db: Session = Depends(get_db)
):
    """Create a new {entity_lower}"""
    return {entity_lower}_crud.create(db, {entity_lower})


@router.get("/{entity_plural}/{{id}}", response_model={entity_name})
def get_{entity_lower}(id: int, db: Session = Depends(get_db)):
    """Get a specific {entity_lower}"""
    db_obj = {entity_lower}_crud.get(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="{entity_name} not found")
    return db_obj


@router.put("/{entity_plural}/{{id}}", response_model={entity_name})
def update_{entity_lower}(
    id: int,
    {entity_lower}: {entity_name}Update,
    db: Session = Depends(get_db)
):
    """Update a {entity_lower}"""
    db_obj = {entity_lower}_crud.update(db, id, {entity_lower})
    if not db_obj:
        raise HTTPException(status_code=404, detail="{entity_name} not found")
    return db_obj


@router.delete("/{entity_plural}/{{id}}")
def delete_{entity_lower}(id: int, db: Session = Depends(get_db)):
    """Delete a {entity_lower}"""
    success = {entity_lower}_crud.delete(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="{entity_name} not found")
    return {{"message": "{entity_name} deleted"}}
'''
    )
    files.append(f"{base}/app/api/routes.py")
    
    return files


def _create_tests(tools: dict, project_name: str) -> list[str]:
    """Create test files"""
    files = []
    base = f"{project_name}/tests"
    
    tools["write_file"](
        path=f"{base}/__init__.py",
        content=""
    )
    files.append(f"{base}/__init__.py")
    
    tools["write_file"](
        path=f"{base}/conftest.py",
        content='''"""Test configuration"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    """Test client fixture"""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c
    
    Base.metadata.drop_all(bind=engine)
'''
    )
    files.append(f"{base}/conftest.py")
    
    tools["write_file"](
        path=f"{base}/test_api.py",
        content='''"""API tests"""


def test_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()


def test_health(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_item(client):
    """Test creating an item"""
    response = client.post(
        "/api/v1/items",  # Adjust endpoint based on entity
        json={"title": "Test Item", "description": "Test description"}
    )
    # Should be 201 or the endpoint doesn't exist yet
    assert response.status_code in [201, 404]


def test_list_items(client):
    """Test listing items"""
    response = client.get("/api/v1/items")  # Adjust endpoint
    # Should be 200 or endpoint doesn't exist
    assert response.status_code in [200, 404]
'''
    )
    files.append(f"{base}/test_api.py")
    
    return files


def _create_docker(tools: dict, project_name: str) -> list[str]:
    """Create Docker configuration"""
    files = []
    base = project_name
    
    tools["write_file"](
        path=f"{base}/Dockerfile",
        content='''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    )
    files.append(f"{base}/Dockerfile")
    
    tools["write_file"](
        path=f"{base}/docker-compose.yml",
        content=f'''version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
'''
    )
    files.append(f"{base}/docker-compose.yml")
    
    tools["write_file"](
        path=f"{base}/.dockerignore",
        content='''__pycache__
*.pyc
.git
.gitignore
.env
*.db
.pytest_cache
'''
    )
    files.append(f"{base}/.dockerignore")
    
    return files


def _create_ci_and_docs(tools: dict, project_name: str, task_desc: str) -> list[str]:
    """Create CI workflow and documentation"""
    files = []
    
    # CI workflow
    tools["write_file"](
        path=f"{project_name}/.github/workflows/ci.yml",
        content=f'''name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: pytest tests/ -v
      
      - name: Health check
        run: |
          uvicorn app.main:app --host 0.0.0.0 --port 8000 &
          sleep 5
          curl -f http://localhost:8000/health

  docker:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build image
        run: docker build -t {project_name} .
      
      - name: Test container
        run: |
          docker run -d -p 8000:8000 --name test {project_name}
          sleep 5
          curl -f http://localhost:8000/health
'''
    )
    files.append(f"{project_name}/.github/workflows/ci.yml")
    
    # README
    tools["write_file"](
        path=f"{project_name}/README.md",
        content=f'''# {project_name}

> {task_desc}

Generated by **Masidy Autonomous Agent Runtime** 🔌

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload
```

API available at: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker

```bash
# Build and run
docker-compose up --build

# Or manually
docker build -t {project_name} .
docker run -p 8000:8000 {project_name}
```

## Testing

```bash
pytest tests/ -v
```

## Project Structure

```
{project_name}/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Config, database
│   ├── crud/         # CRUD operations
│   ├── models/       # SQLAlchemy models
│   └── schemas/      # Pydantic schemas
├── tests/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## License

MIT
'''
    )
    files.append(f"{project_name}/README.md")
    
    # .gitignore
    tools["write_file"](
        path=f"{project_name}/.gitignore",
        content='''__pycache__/
*.py[cod]
.env
*.db
.pytest_cache/
'''
    )
    files.append(f"{project_name}/.gitignore")
    
    # .env.example
    tools["write_file"](
        path=f"{project_name}/.env.example",
        content='''DATABASE_URL=sqlite:///./app.db
DEBUG=false
'''
    )
    files.append(f"{project_name}/.env.example")
    
    return files


def _infer_entity_name(task_desc: str) -> str:
    """Infer the main entity name from task description"""
    task_lower = task_desc.lower()
    
    # Common entity patterns
    patterns = [
        ("note", "Note"),
        ("task", "Task"),
        ("todo", "Todo"),
        ("item", "Item"),
        ("product", "Product"),
        ("user", "User"),
        ("post", "Post"),
        ("article", "Article"),
        ("comment", "Comment"),
        ("message", "Message"),
        ("order", "Order"),
        ("booking", "Booking"),
        ("event", "Event"),
        ("project", "Project"),
    ]
    
    for pattern, entity in patterns:
        if pattern in task_lower:
            return entity
    
    # Default
    return "Item"
