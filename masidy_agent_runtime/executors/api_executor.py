"""
Masidy Autonomous Agent Runtime - API Executor
Executes API service generation plans
"""

from typing import Callable
from .base_executor import BaseExecutor


class APIExecutor(BaseExecutor):
    """Executor for API service generation"""
    
    @property
    def flow_name(self) -> str:
        return "api"
    
    def build_plan(self, task_description: str, config: dict) -> list[dict]:
        """
        Build a structured plan for API service generation.
        """
        project_name = config.get("project_name", "api_service")
        db_type = config.get("database", {}).get("type", "sqlite")
        
        # Infer entity name from task
        entity = self._infer_entity(task_description)
        entity_lower = entity.lower()
        entity_plural = f"{entity_lower}s"
        
        plan = [
            # Step 1: Create project structure
            {
                "id": "create_structure",
                "description": "Create project directory structure",
                "tool_name": "create_directory",
                "tool_args": {"path": project_name},
                "verify_instruction": "Directory should exist"
            },
            {
                "id": "create_app_dir",
                "description": "Create app directory",
                "tool_name": "create_directory",
                "tool_args": {"path": f"{project_name}/app"},
                "verify_instruction": None
            },
            {
                "id": "create_api_dir",
                "description": "Create API directory",
                "tool_name": "create_directory",
                "tool_args": {"path": f"{project_name}/app/api"},
                "verify_instruction": None
            },
            {
                "id": "create_models_dir",
                "description": "Create models directory",
                "tool_name": "create_directory",
                "tool_args": {"path": f"{project_name}/app/models"},
                "verify_instruction": None
            },
            {
                "id": "create_schemas_dir",
                "description": "Create schemas directory",
                "tool_name": "create_directory",
                "tool_args": {"path": f"{project_name}/app/schemas"},
                "verify_instruction": None
            },
            {
                "id": "create_crud_dir",
                "description": "Create CRUD directory",
                "tool_name": "create_directory",
                "tool_args": {"path": f"{project_name}/app/crud"},
                "verify_instruction": None
            },
            {
                "id": "create_core_dir",
                "description": "Create core directory",
                "tool_name": "create_directory",
                "tool_args": {"path": f"{project_name}/app/core"},
                "verify_instruction": None
            },
            {
                "id": "create_tests_dir",
                "description": "Create tests directory",
                "tool_name": "create_directory",
                "tool_args": {"path": f"{project_name}/tests"},
                "verify_instruction": None
            },
            {
                "id": "create_github_dir",
                "description": "Create GitHub workflows directory",
                "tool_name": "create_directory",
                "tool_args": {"path": f"{project_name}/.github/workflows"},
                "verify_instruction": None
            },
            
            # Step 2: Create requirements.txt
            {
                "id": "create_requirements",
                "description": "Create requirements.txt",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/requirements.txt",
                    "content": self._get_requirements_content()
                },
                "verify_instruction": None
            },
            
            # Step 3: Create app __init__.py
            {
                "id": "create_app_init",
                "description": "Create app/__init__.py",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/app/__init__.py",
                    "content": f'"""API Service"""\n__version__ = "0.1.0"\n'
                },
                "verify_instruction": None
            },
            
            # Step 4: Create main.py
            {
                "id": "create_main",
                "description": "Create FastAPI main.py",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/app/main.py",
                    "content": self._get_main_content(project_name, task_description)
                },
                "verify_instruction": None
            },
            
            # Step 5: Create config
            {
                "id": "create_config",
                "description": "Create core/config.py",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/app/core/config.py",
                    "content": self._get_config_content(project_name, db_type)
                },
                "verify_instruction": None
            },
            {
                "id": "create_core_init",
                "description": "Create core/__init__.py",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/app/core/__init__.py",
                    "content": ""
                },
                "verify_instruction": None
            },
            
            # Step 6: Create database
            {
                "id": "create_database",
                "description": "Create core/database.py",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/app/core/database.py",
                    "content": self._get_database_content()
                },
                "verify_instruction": None
            },
            
            # Step 7: Create model
            {
                "id": "create_model",
                "description": f"Create {entity} model",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/app/models/{entity_lower}.py",
                    "content": self._get_model_content(entity, entity_plural)
                },
                "verify_instruction": None
            },
            {
                "id": "create_models_init",
                "description": "Create models/__init__.py",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/app/models/__init__.py",
                    "content": f"from app.models.{entity_lower} import {entity}\n"
                },
                "verify_instruction": None
            },
            
            # Step 8: Create schema
            {
                "id": "create_schema",
                "description": f"Create {entity} schema",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/app/schemas/{entity_lower}.py",
                    "content": self._get_schema_content(entity)
                },
                "verify_instruction": None
            },
            {
                "id": "create_schemas_init",
                "description": "Create schemas/__init__.py",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/app/schemas/__init__.py",
                    "content": f"from app.schemas.{entity_lower} import {entity}, {entity}Create, {entity}Update, {entity}List\n"
                },
                "verify_instruction": None
            },
            
            # Step 9: Create CRUD
            {
                "id": "create_crud",
                "description": f"Create {entity} CRUD operations",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/app/crud/{entity_lower}.py",
                    "content": self._get_crud_content(entity, entity_lower, entity_plural)
                },
                "verify_instruction": None
            },
            {
                "id": "create_crud_init",
                "description": "Create crud/__init__.py",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/app/crud/__init__.py",
                    "content": f"from app.crud.{entity_lower} import {entity_lower}_crud\n"
                },
                "verify_instruction": None
            },
            
            # Step 10: Create API routes
            {
                "id": "create_routes",
                "description": "Create API routes",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/app/api/routes.py",
                    "content": self._get_routes_content(entity, entity_lower, entity_plural)
                },
                "verify_instruction": None
            },
            {
                "id": "create_api_init",
                "description": "Create api/__init__.py",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/app/api/__init__.py",
                    "content": ""
                },
                "verify_instruction": None
            },
            
            # Step 11: Create tests
            {
                "id": "create_tests_init",
                "description": "Create tests/__init__.py",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/tests/__init__.py",
                    "content": ""
                },
                "verify_instruction": None
            },
            {
                "id": "create_conftest",
                "description": "Create test conftest.py",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/tests/conftest.py",
                    "content": self._get_conftest_content()
                },
                "verify_instruction": None
            },
            {
                "id": "create_test_api",
                "description": "Create API tests",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/tests/test_api.py",
                    "content": self._get_test_content(entity_plural)
                },
                "verify_instruction": None
            },
            
            # Step 12: Create Dockerfile
            {
                "id": "create_dockerfile",
                "description": "Create Dockerfile",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/Dockerfile",
                    "content": self._get_dockerfile_content()
                },
                "verify_instruction": None
            },
            
            # Step 13: Create docker-compose.yml
            {
                "id": "create_compose",
                "description": "Create docker-compose.yml",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/docker-compose.yml",
                    "content": self._get_compose_content()
                },
                "verify_instruction": None
            },
            
            # Step 14: Create .dockerignore
            {
                "id": "create_dockerignore",
                "description": "Create .dockerignore",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/.dockerignore",
                    "content": "__pycache__\n*.pyc\n.git\n.env\n*.db\n.pytest_cache\n"
                },
                "verify_instruction": None
            },
            
            # Step 15: Create CI workflow
            {
                "id": "create_ci",
                "description": "Create GitHub Actions CI",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/.github/workflows/ci.yml",
                    "content": self._get_ci_content(project_name)
                },
                "verify_instruction": None
            },
            
            # Step 16: Create README
            {
                "id": "create_readme",
                "description": "Create README.md",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/README.md",
                    "content": self._get_readme_content(project_name, task_description, entity)
                },
                "verify_instruction": None
            },
            
            # Step 17: Create .gitignore
            {
                "id": "create_gitignore",
                "description": "Create .gitignore",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/.gitignore",
                    "content": "__pycache__/\n*.py[cod]\n.env\n*.db\n.pytest_cache/\n"
                },
                "verify_instruction": None
            },
            
            # Step 18: Create .env.example
            {
                "id": "create_env_example",
                "description": "Create .env.example",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/.env.example",
                    "content": f"DATABASE_URL=sqlite:///./app.db\nDEBUG=false\n"
                },
                "verify_instruction": None
            },
        ]
        
        return plan
    
    def _infer_entity(self, task_desc: str) -> str:
        """Infer entity name from task description"""
        task_lower = task_desc.lower()
        
        patterns = [
            ("note", "Note"), ("task", "Task"), ("todo", "Todo"),
            ("item", "Item"), ("product", "Product"), ("user", "User"),
            ("post", "Post"), ("article", "Article"), ("comment", "Comment"),
            ("message", "Message"), ("order", "Order"), ("booking", "Booking"),
        ]
        
        for pattern, entity in patterns:
            if pattern in task_lower:
                return entity
        
        return "Item"
    
    def _get_requirements_content(self) -> str:
        return """fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
httpx>=0.26.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
"""
    
    def _get_main_content(self, project_name: str, task_desc: str) -> str:
        return f'''"""
FastAPI Application - {project_name}
Generated by Masidy Agent Runtime
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    create_tables()


@app.get("/")
async def root():
    return {{"service": "{project_name}", "version": "0.1.0", "docs": "/docs"}}


@app.get("/health")
async def health_check():
    return {{"status": "healthy"}}
'''
    
    def _get_config_content(self, project_name: str, db_type: str) -> str:
        db_url = "sqlite:///./app.db" if db_type == "sqlite" else "postgresql://user:pass@localhost/db"
        return f'''"""Application configuration"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "{project_name}"
    DATABASE_URL: str = "{db_url}"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"


settings = Settings()
'''
    
    def _get_database_content(self) -> str:
        return '''"""Database configuration"""

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
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
'''
    
    def _get_model_content(self, entity: str, entity_plural: str) -> str:
        return f'''"""{entity} model"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func

from app.core.database import Base


class {entity}(Base):
    __tablename__ = "{entity_plural}"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
'''
    
    def _get_schema_content(self, entity: str) -> str:
        return f'''"""{entity} schemas"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class {entity}Base(BaseModel):
    title: str
    description: Optional[str] = None


class {entity}Create({entity}Base):
    pass


class {entity}Update(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class {entity}({entity}Base):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class {entity}List(BaseModel):
    items: List[{entity}]
    total: int
'''
    
    def _get_crud_content(self, entity: str, entity_lower: str, entity_plural: str) -> str:
        return f'''"""{entity} CRUD operations"""

from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.{entity_lower} import {entity}
from app.schemas.{entity_lower} import {entity}Create, {entity}Update


class {entity}CRUD:
    def get(self, db: Session, id: int) -> Optional[{entity}]:
        return db.query({entity}).filter({entity}.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[{entity}]:
        return db.query({entity}).offset(skip).limit(limit).all()
    
    def count(self, db: Session) -> int:
        return db.query({entity}).count()
    
    def create(self, db: Session, obj_in: {entity}Create) -> {entity}:
        db_obj = {entity}(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, id: int, obj_in: {entity}Update) -> Optional[{entity}]:
        db_obj = self.get(db, id)
        if not db_obj:
            return None
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, id: int) -> bool:
        db_obj = self.get(db, id)
        if not db_obj:
            return False
        db.delete(db_obj)
        db.commit()
        return True


{entity_lower}_crud = {entity}CRUD()
'''
    
    def _get_routes_content(self, entity: str, entity_lower: str, entity_plural: str) -> str:
        return f'''"""API Routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.crud.{entity_lower} import {entity_lower}_crud
from app.schemas.{entity_lower} import {entity}, {entity}Create, {entity}Update, {entity}List

router = APIRouter()


@router.get("/{entity_plural}", response_model={entity}List)
def list_{entity_plural}(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = {entity_lower}_crud.get_all(db, skip=skip, limit=limit)
    total = {entity_lower}_crud.count(db)
    return {{"items": items, "total": total}}


@router.post("/{entity_plural}", response_model={entity}, status_code=201)
def create_{entity_lower}({entity_lower}: {entity}Create, db: Session = Depends(get_db)):
    return {entity_lower}_crud.create(db, {entity_lower})


@router.get("/{entity_plural}/{{id}}", response_model={entity})
def get_{entity_lower}(id: int, db: Session = Depends(get_db)):
    db_obj = {entity_lower}_crud.get(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="{entity} not found")
    return db_obj


@router.put("/{entity_plural}/{{id}}", response_model={entity})
def update_{entity_lower}(id: int, {entity_lower}: {entity}Update, db: Session = Depends(get_db)):
    db_obj = {entity_lower}_crud.update(db, id, {entity_lower})
    if not db_obj:
        raise HTTPException(status_code=404, detail="{entity} not found")
    return db_obj


@router.delete("/{entity_plural}/{{id}}")
def delete_{entity_lower}(id: int, db: Session = Depends(get_db)):
    success = {entity_lower}_crud.delete(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="{entity} not found")
    return {{"message": "{entity} deleted"}}
'''
    
    def _get_conftest_content(self) -> str:
        return '''"""Test configuration"""

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
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
'''
    
    def _get_test_content(self, entity_plural: str) -> str:
        return f'''"""API tests"""


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_{entity_plural}(client):
    response = client.get("/api/v1/{entity_plural}")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
'''
    
    def _get_dockerfile_content(self) -> str:
        return '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    def _get_compose_content(self) -> str:
        return '''version: '3.8'

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
    
    def _get_ci_content(self, project_name: str) -> str:
        return f'''name: CI

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
        run: pip install -r requirements.txt
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
'''
    
    def _get_readme_content(self, project_name: str, task_desc: str, entity: str) -> str:
        entity_lower = entity.lower()
        entity_plural = f"{entity_lower}s"
        return f'''# {project_name}

> {task_desc}

Generated by **Masidy Autonomous Agent Runtime**

## Quick Start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/{entity_plural} | List all {entity_plural} |
| POST | /api/v1/{entity_plural} | Create {entity_lower} |
| GET | /api/v1/{entity_plural}/{{id}} | Get {entity_lower} |
| PUT | /api/v1/{entity_plural}/{{id}} | Update {entity_lower} |
| DELETE | /api/v1/{entity_plural}/{{id}} | Delete {entity_lower} |

## Docker

```bash
docker-compose up --build
```

## Testing

```bash
pytest tests/ -v
```
'''
