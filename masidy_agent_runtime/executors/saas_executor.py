"""
Masidy Autonomous Agent Runtime - SaaS Executor
Executes SaaS application generation plans
"""

from typing import Callable
from .base_executor import BaseExecutor


class SaaSExecutor(BaseExecutor):
    """Executor for SaaS application generation"""
    
    @property
    def flow_name(self) -> str:
        return "saas"
    
    def build_plan(self, task_description: str, config: dict) -> list[dict]:
        """
        Build a structured plan for SaaS application generation.
        """
        project_name = config.get("project_name", "saas_app")
        db_type = config.get("database", {}).get("type", "sqlite")
        include_frontend = config.get("include_frontend", True)
        
        plan = []
        
        # Step 1: Create project structure
        dirs = [
            project_name,
            f"{project_name}/backend",
            f"{project_name}/backend/app",
            f"{project_name}/backend/app/api",
            f"{project_name}/backend/app/models",
            f"{project_name}/backend/app/schemas",
            f"{project_name}/backend/app/core",
            f"{project_name}/backend/tests",
        ]
        
        if include_frontend:
            dirs.extend([
                f"{project_name}/frontend",
                f"{project_name}/frontend/src",
                f"{project_name}/frontend/public",
            ])
        
        dirs.append(f"{project_name}/.github/workflows")
        
        for i, d in enumerate(dirs):
            plan.append({
                "id": f"create_dir_{i}",
                "description": f"Create directory: {d.split('/')[-1]}",
                "tool_name": "create_directory",
                "tool_args": {"path": d},
                "verify_instruction": None
            })
        
        # Backend files
        plan.extend([
            {
                "id": "backend_requirements",
                "description": "Create backend requirements.txt",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/requirements.txt",
                    "content": self._get_backend_requirements()
                },
                "verify_instruction": None
            },
            {
                "id": "backend_main",
                "description": "Create FastAPI main.py",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/app/main.py",
                    "content": self._get_main_content(project_name, task_description)
                },
                "verify_instruction": None
            },
            {
                "id": "backend_config",
                "description": "Create config.py",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/app/core/config.py",
                    "content": self._get_config_content(project_name, db_type)
                },
                "verify_instruction": None
            },
            {
                "id": "backend_database",
                "description": "Create database.py",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/app/core/database.py",
                    "content": self._get_database_content()
                },
                "verify_instruction": None
            },
            {
                "id": "backend_security",
                "description": "Create security.py (JWT auth)",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/app/core/security.py",
                    "content": self._get_security_content()
                },
                "verify_instruction": None
            },
            {
                "id": "backend_user_model",
                "description": "Create User model",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/app/models/user.py",
                    "content": self._get_user_model()
                },
                "verify_instruction": None
            },
            {
                "id": "backend_item_model",
                "description": "Create Item model",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/app/models/item.py",
                    "content": self._get_item_model()
                },
                "verify_instruction": None
            },
            {
                "id": "backend_user_schema",
                "description": "Create User schemas",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/app/schemas/user.py",
                    "content": self._get_user_schema()
                },
                "verify_instruction": None
            },
            {
                "id": "backend_item_schema",
                "description": "Create Item schemas",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/app/schemas/item.py",
                    "content": self._get_item_schema()
                },
                "verify_instruction": None
            },
            {
                "id": "backend_auth_routes",
                "description": "Create auth routes",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/app/api/auth.py",
                    "content": self._get_auth_routes()
                },
                "verify_instruction": None
            },
            {
                "id": "backend_users_routes",
                "description": "Create users routes",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/app/api/users.py",
                    "content": self._get_users_routes()
                },
                "verify_instruction": None
            },
            {
                "id": "backend_items_routes",
                "description": "Create items routes",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/app/api/items.py",
                    "content": self._get_items_routes()
                },
                "verify_instruction": None
            },
            {
                "id": "backend_api_init",
                "description": "Create API router",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/app/api/__init__.py",
                    "content": self._get_api_router()
                },
                "verify_instruction": None
            },
            {
                "id": "backend_tests",
                "description": "Create backend tests",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/tests/test_health.py",
                    "content": self._get_test_content()
                },
                "verify_instruction": None
            },
            {
                "id": "backend_dockerfile",
                "description": "Create backend Dockerfile",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/Dockerfile",
                    "content": self._get_backend_dockerfile()
                },
                "verify_instruction": None
            },
        ])
        
        # Frontend files
        if include_frontend:
            plan.extend([
                {
                    "id": "frontend_package",
                    "description": "Create package.json",
                    "tool_name": "write_file",
                    "tool_args": {
                        "path": f"{project_name}/frontend/package.json",
                        "content": self._get_package_json(project_name)
                    },
                    "verify_instruction": None
                },
                {
                    "id": "frontend_vite",
                    "description": "Create vite.config.js",
                    "tool_name": "write_file",
                    "tool_args": {
                        "path": f"{project_name}/frontend/vite.config.js",
                        "content": self._get_vite_config()
                    },
                    "verify_instruction": None
                },
                {
                    "id": "frontend_index",
                    "description": "Create index.html",
                    "tool_name": "write_file",
                    "tool_args": {
                        "path": f"{project_name}/frontend/index.html",
                        "content": self._get_index_html(project_name)
                    },
                    "verify_instruction": None
                },
                {
                    "id": "frontend_app",
                    "description": "Create App.jsx",
                    "tool_name": "write_file",
                    "tool_args": {
                        "path": f"{project_name}/frontend/src/App.jsx",
                        "content": self._get_app_jsx(project_name, task_description)
                    },
                    "verify_instruction": None
                },
                {
                    "id": "frontend_main",
                    "description": "Create main.jsx",
                    "tool_name": "write_file",
                    "tool_args": {
                        "path": f"{project_name}/frontend/src/main.jsx",
                        "content": self._get_main_jsx()
                    },
                    "verify_instruction": None
                },
                {
                    "id": "frontend_css",
                    "description": "Create index.css",
                    "tool_name": "write_file",
                    "tool_args": {
                        "path": f"{project_name}/frontend/src/index.css",
                        "content": self._get_index_css()
                    },
                    "verify_instruction": None
                },
                {
                    "id": "frontend_dockerfile",
                    "description": "Create frontend Dockerfile",
                    "tool_name": "write_file",
                    "tool_args": {
                        "path": f"{project_name}/frontend/Dockerfile",
                        "content": self._get_frontend_dockerfile()
                    },
                    "verify_instruction": None
                },
            ])
        
        # Root files
        plan.extend([
            {
                "id": "docker_compose",
                "description": "Create docker-compose.yml",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/docker-compose.yml",
                    "content": self._get_docker_compose(include_frontend)
                },
                "verify_instruction": None
            },
            {
                "id": "github_ci",
                "description": "Create GitHub Actions CI",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/.github/workflows/ci.yml",
                    "content": self._get_ci_workflow(project_name)
                },
                "verify_instruction": None
            },
            {
                "id": "readme",
                "description": "Create README.md",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/README.md",
                    "content": self._get_readme(project_name, task_description, include_frontend)
                },
                "verify_instruction": None
            },
            {
                "id": "gitignore",
                "description": "Create .gitignore",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/.gitignore",
                    "content": "__pycache__/\n*.py[cod]\n.env\n*.db\nnode_modules/\ndist/\n"
                },
                "verify_instruction": None
            },
        ])
        
        # Init files
        for subdir in ["", "/core", "/api", "/models", "/schemas"]:
            plan.append({
                "id": f"init_{subdir.replace('/', '_') or 'app'}",
                "description": f"Create __init__.py",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{project_name}/backend/app{subdir}/__init__.py",
                    "content": ""
                },
                "verify_instruction": None
            })
        
        plan.append({
            "id": "init_tests",
            "description": "Create tests/__init__.py",
            "tool_name": "write_file",
            "tool_args": {
                "path": f"{project_name}/backend/tests/__init__.py",
                "content": ""
            },
            "verify_instruction": None
        })
        
        return plan
    
    def _get_backend_requirements(self) -> str:
        return """fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
httpx>=0.26.0
pytest>=8.0.0
"""
    
    def _get_main_content(self, project_name: str, task_desc: str) -> str:
        return f'''"""FastAPI SaaS Application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router
from app.core.config import settings
from app.core.database import create_tables

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""{task_desc}""",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
async def root():
    return {{"message": "Welcome to {project_name}", "docs": "/docs"}}

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "version": "0.1.0"}}
'''
    
    def _get_config_content(self, project_name: str, db_type: str) -> str:
        db_url = "sqlite:///./app.db" if db_type == "sqlite" else "postgresql://user:pass@localhost/db"
        return f'''"""Application configuration"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "{project_name}"
    DATABASE_URL: str = "{db_url}"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
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

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {})
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
    
    def _get_security_content(self) -> str:
        return '''"""Security utilities"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user
'''
    
    def _get_user_model(self) -> str:
        return '''"""User model"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
'''
    
    def _get_item_model(self) -> str:
        return '''"""Item model"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
'''
    
    def _get_user_schema(self) -> str:
        return '''"""User schemas"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
'''
    
    def _get_item_schema(self) -> str:
        return '''"""Item schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class Item(ItemBase):
    id: int
    owner_id: int
    created_at: datetime
    class Config:
        from_attributes = True
'''
    
    def _get_auth_routes(self) -> str:
        return '''"""Authentication endpoints"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token, verify_password, get_password_hash
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema, Token

router = APIRouter()

@router.post("/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = User(email=user.email, hashed_password=get_password_hash(user.password), full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}
'''
    
    def _get_users_routes(self) -> str:
        return '''"""User endpoints"""
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import User as UserSchema

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user
'''
    
    def _get_items_routes(self) -> str:
        return '''"""Item endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.item import Item
from app.schemas.item import Item as ItemSchema, ItemCreate, ItemUpdate

router = APIRouter()

@router.get("/", response_model=List[ItemSchema])
def list_items(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Item).filter(Item.owner_id == current_user.id).offset(skip).limit(limit).all()

@router.post("/", response_model=ItemSchema)
def create_item(item: ItemCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = Item(**item.model_dump(), owner_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
def delete_item(item_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item deleted"}
'''
    
    def _get_api_router(self) -> str:
        return '''"""API Router"""
from fastapi import APIRouter
from app.api import auth, users, items

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(items.router, prefix="/items", tags=["items"])
'''
    
    def _get_test_content(self) -> str:
        return '''"""Health check tests"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
'''
    
    def _get_backend_dockerfile(self) -> str:
        return '''FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    def _get_package_json(self, project_name: str) -> str:
        return f'''{{"name": "{project_name}-frontend", "version": "0.1.0", "private": true, "scripts": {{"dev": "vite", "build": "vite build"}}, "dependencies": {{"react": "^18.2.0", "react-dom": "^18.2.0"}}, "devDependencies": {{"@vitejs/plugin-react": "^4.2.0", "vite": "^5.0.0"}}}}'''
    
    def _get_vite_config(self) -> str:
        return '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({
  plugins: [react()],
  server: { port: 3000, proxy: { '/api': 'http://localhost:8000' } }
})
'''
    
    def _get_index_html(self, project_name: str) -> str:
        return f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>{project_name}</title></head>
<body><div id="root"></div><script type="module" src="/src/main.jsx"></script></body>
</html>
'''
    
    def _get_main_jsx(self) -> str:
        return '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
ReactDOM.createRoot(document.getElementById('root')).render(<React.StrictMode><App /></React.StrictMode>)
'''
    
    def _get_app_jsx(self, project_name: str, task_desc: str) -> str:
        return f'''import {{ useState, useEffect }} from 'react'
function App() {{
  const [health, setHealth] = useState(null)
  useEffect(() => {{
    fetch('/api/v1/../health').then(res => res.json()).then(setHealth).catch(() => {{}})
  }}, [])
  return (
    <div className="app">
      <h1>🚀 {project_name}</h1>
      <p>{task_desc[:80]}</p>
      <p>Status: {{health ? '✓ ' + health.status : 'Checking...'}}</p>
      <p><a href="/docs">API Docs</a></p>
    </div>
  )
}}
export default App
'''
    
    def _get_index_css(self) -> str:
        return '''body { font-family: system-ui, sans-serif; margin: 0; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
.app { max-width: 600px; margin: 0 auto; background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
h1 { color: #667eea; }
a { color: #667eea; }
'''
    
    def _get_frontend_dockerfile(self) -> str:
        return '''FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
'''
    
    def _get_docker_compose(self, include_frontend: bool) -> str:
        content = '''version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
'''
        if include_frontend:
            content += '''  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
'''
        return content
    
    def _get_ci_workflow(self, project_name: str) -> str:
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
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
        working-directory: .
      - run: pytest tests/ -v
        working-directory: ./backend
'''
    
    def _get_readme(self, project_name: str, task_desc: str, include_frontend: bool) -> str:
        frontend_section = "## Frontend\\n\\n```bash\\ncd frontend && npm install && npm run dev\\n```\\n\\n" if include_frontend else ""
        return f'''# {project_name}

> {task_desc}

Generated by **Masidy Autonomous Agent Runtime**

## Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

{frontend_section}## Docker

```bash
docker-compose up --build
```
'''
