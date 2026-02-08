"""
Masidy Autonomous Agent Runtime - SaaS Blueprint
Creates a complete SaaS application with:
- Backend: FastAPI
- Frontend: React (minimal)
- Database: SQLite/PostgreSQL
- Auth: JWT-based
- Docker: Dockerfile + docker-compose
- CI: GitHub Actions workflow
"""

import os
from typing import Any
from datetime import datetime

SAAS_BLUEPRINT_INFO = {
    "name": "SaaS Application",
    "description": "Full-stack SaaS with FastAPI backend, React frontend, auth, and CI/CD",
    "components": ["FastAPI", "React", "SQLite/PostgreSQL", "JWT Auth", "Docker", "GitHub Actions"],
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
    Run the SaaS blueprint to create a complete SaaS application.
    
    Args:
        task_description: What the user wants to build
        config: Configuration options (project_name, db_type, etc.)
        core_agent: The core agent instance for tool execution
        planner: The planner instance
        state_manager: State manager for persistence
        verbose: Whether to print detailed output
    
    Returns:
        dict with results of the blueprint execution
    """
    print("\n" + "=" * 60)
    print("  🚀 SaaS BLUEPRINT - Starting Full Stack Generation")
    print("=" * 60)
    print(f"  Task: {task_description}")
    print("=" * 60)
    
    # Extract configuration
    project_name = config.get("project_name", "saas_app")
    db_type = config.get("db_type", "sqlite")
    include_frontend = config.get("include_frontend", True)
    
    # Clean project name
    project_name = project_name.lower().replace(" ", "_").replace("-", "_")
    
    results = {
        "blueprint": "saas",
        "project_name": project_name,
        "task": task_description,
        "steps_completed": [],
        "steps_failed": [],
        "files_created": [],
        "started_at": datetime.now().isoformat(),
    }
    
    tools = core_agent.tools
    
    # Step 1: Create project structure
    print("\n[Step 1/8] Creating project structure...")
    try:
        _create_project_structure(tools, project_name)
        results["steps_completed"].append("project_structure")
        print("  ✓ Project structure created")
    except Exception as e:
        results["steps_failed"].append({"step": "project_structure", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Step 2: Create backend
    print("\n[Step 2/8] Creating FastAPI backend...")
    try:
        files = _create_backend(tools, project_name, db_type, task_description)
        results["files_created"].extend(files)
        results["steps_completed"].append("backend")
        print(f"  ✓ Backend created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "backend", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Step 3: Create frontend
    if include_frontend:
        print("\n[Step 3/8] Creating React frontend...")
        try:
            files = _create_frontend(tools, project_name, task_description)
            results["files_created"].extend(files)
            results["steps_completed"].append("frontend")
            print(f"  ✓ Frontend created ({len(files)} files)")
        except Exception as e:
            results["steps_failed"].append({"step": "frontend", "error": str(e)})
            print(f"  ✗ Failed: {e}")
    else:
        print("\n[Step 3/8] Skipping frontend (disabled in config)")
        results["steps_completed"].append("frontend_skipped")
    
    # Step 4: Create auth module
    print("\n[Step 4/8] Creating JWT authentication...")
    try:
        files = _create_auth(tools, project_name)
        results["files_created"].extend(files)
        results["steps_completed"].append("auth")
        print(f"  ✓ Auth module created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "auth", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Step 5: Create Docker configuration
    print("\n[Step 5/8] Creating Docker configuration...")
    try:
        files = _create_docker(tools, project_name, include_frontend)
        results["files_created"].extend(files)
        results["steps_completed"].append("docker")
        print(f"  ✓ Docker config created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "docker", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Step 6: Create CI workflow
    print("\n[Step 6/8] Creating GitHub Actions CI...")
    try:
        files = _create_ci(tools, project_name)
        results["files_created"].extend(files)
        results["steps_completed"].append("ci")
        print(f"  ✓ CI workflow created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "ci", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Step 7: Create tests
    print("\n[Step 7/8] Creating tests...")
    try:
        files = _create_tests(tools, project_name)
        results["files_created"].extend(files)
        results["steps_completed"].append("tests")
        print(f"  ✓ Tests created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "tests", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Step 8: Create README
    print("\n[Step 8/8] Creating README and documentation...")
    try:
        files = _create_readme(tools, project_name, task_description, db_type, include_frontend)
        results["files_created"].extend(files)
        results["steps_completed"].append("readme")
        print(f"  ✓ README created ({len(files)} files)")
    except Exception as e:
        results["steps_failed"].append({"step": "readme", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Finalize
    results["completed_at"] = datetime.now().isoformat()
    results["success"] = len(results["steps_failed"]) == 0
    results["total_files"] = len(results["files_created"])
    
    # Update state
    state_manager.update_context("last_saas_project", {
        "name": project_name,
        "path": project_name,
        "files": results["total_files"],
        "created_at": results["completed_at"]
    })
    
    # Print summary
    print("\n" + "=" * 60)
    print("  📊 SAAS BLUEPRINT SUMMARY")
    print("=" * 60)
    print(f"  Project: {project_name}/")
    print(f"  Status: {'✓ SUCCESS' if results['success'] else '✗ PARTIAL'}")
    print(f"  Steps completed: {len(results['steps_completed'])}/8")
    print(f"  Files created: {results['total_files']}")
    if results["steps_failed"]:
        print(f"  Failed steps: {[s['step'] for s in results['steps_failed']]}")
    print("=" * 60)
    
    return results


def _create_project_structure(tools: dict, project_name: str):
    """Create the base project directory structure"""
    dirs = [
        project_name,
        f"{project_name}/backend",
        f"{project_name}/backend/app",
        f"{project_name}/backend/app/api",
        f"{project_name}/backend/app/models",
        f"{project_name}/backend/app/schemas",
        f"{project_name}/backend/app/core",
        f"{project_name}/backend/tests",
        f"{project_name}/frontend",
        f"{project_name}/frontend/src",
        f"{project_name}/frontend/public",
        f"{project_name}/.github/workflows",
    ]
    
    for d in dirs:
        tools["create_directory"](path=d)


def _create_backend(tools: dict, project_name: str, db_type: str, task_desc: str) -> list[str]:
    """Create FastAPI backend files"""
    files = []
    base = f"{project_name}/backend"
    
    # requirements.txt
    tools["write_file"](
        path=f"{base}/requirements.txt",
        content="""fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
httpx>=0.26.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
"""
    )
    files.append(f"{base}/requirements.txt")
    
    # Main app
    tools["write_file"](
        path=f"{base}/app/__init__.py",
        content='"""SaaS Application Backend"""\n__version__ = "0.1.0"\n'
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

from app.api import router as api_router
from app.core.config import settings
from app.core.database import create_tables

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="{task_desc[:200]}",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    create_tables()


@app.get("/")
async def root():
    """Root endpoint"""
    return {{"message": "Welcome to {project_name}", "docs": "/docs"}}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {{"status": "healthy", "version": "0.1.0"}}
'''
    )
    files.append(f"{base}/app/main.py")
    
    # Config
    tools["write_file"](
        path=f"{base}/app/core/__init__.py",
        content=""
    )
    files.append(f"{base}/app/core/__init__.py")
    
    db_url = "sqlite:///./app.db" if db_type == "sqlite" else "postgresql://user:pass@localhost/db"
    tools["write_file"](
        path=f"{base}/app/core/config.py",
        content=f'''"""Application configuration"""

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
    
    # Models
    tools["write_file"](
        path=f"{base}/app/models/__init__.py",
        content='from app.models.user import User\nfrom app.models.item import Item\n'
    )
    files.append(f"{base}/app/models/__init__.py")
    
    tools["write_file"](
        path=f"{base}/app/models/user.py",
        content='''"""User model"""

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
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
'''
    )
    files.append(f"{base}/app/models/user.py")
    
    tools["write_file"](
        path=f"{base}/app/models/item.py",
        content='''"""Item model - customize for your SaaS"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
'''
    )
    files.append(f"{base}/app/models/item.py")
    
    # Schemas
    tools["write_file"](
        path=f"{base}/app/schemas/__init__.py",
        content='from app.schemas.user import User, UserCreate, UserUpdate, Token\nfrom app.schemas.item import Item, ItemCreate, ItemUpdate\n'
    )
    files.append(f"{base}/app/schemas/__init__.py")
    
    tools["write_file"](
        path=f"{base}/app/schemas/user.py",
        content='''"""User schemas"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
'''
    )
    files.append(f"{base}/app/schemas/user.py")
    
    tools["write_file"](
        path=f"{base}/app/schemas/item.py",
        content='''"""Item schemas"""

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
    )
    files.append(f"{base}/app/schemas/item.py")
    
    # API routes
    tools["write_file"](
        path=f"{base}/app/api/__init__.py",
        content='''"""API Router"""

from fastapi import APIRouter

from app.api import auth, users, items

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(items.router, prefix="/items", tags=["items"])
'''
    )
    files.append(f"{base}/app/api/__init__.py")
    
    tools["write_file"](
        path=f"{base}/app/api/auth.py",
        content='''"""Authentication endpoints"""

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
    """Register a new user"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token"""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
'''
    )
    files.append(f"{base}/app/api/auth.py")
    
    tools["write_file"](
        path=f"{base}/app/api/users.py",
        content='''"""User endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserSchema)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user


@router.put("/me", response_model=UserSchema)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user"""
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    db.commit()
    db.refresh(current_user)
    return current_user
'''
    )
    files.append(f"{base}/app/api/users.py")
    
    tools["write_file"](
        path=f"{base}/app/api/items.py",
        content='''"""Item endpoints - customize for your SaaS"""

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
def list_items(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List items for current user"""
    items = db.query(Item).filter(Item.owner_id == current_user.id).offset(skip).limit(limit).all()
    return items


@router.post("/", response_model=ItemSchema)
def create_item(
    item: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new item"""
    db_item = Item(**item.model_dump(), owner_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=ItemSchema)
def get_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific item"""
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=ItemSchema)
def update_item(
    item_id: int,
    item_update: ItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an item"""
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for field, value in item_update.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an item"""
    item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return {"message": "Item deleted"}
'''
    )
    files.append(f"{base}/app/api/items.py")
    
    return files


def _create_auth(tools: dict, project_name: str) -> list[str]:
    """Create authentication/security module"""
    files = []
    base = f"{project_name}/backend/app/core"
    
    tools["write_file"](
        path=f"{base}/security.py",
        content='''"""Security utilities"""

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
from app.schemas.user import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    
    return user
'''
    )
    files.append(f"{base}/security.py")
    
    return files


def _create_frontend(tools: dict, project_name: str, task_desc: str) -> list[str]:
    """Create minimal React frontend"""
    files = []
    base = f"{project_name}/frontend"
    
    # package.json
    tools["write_file"](
        path=f"{base}/package.json",
        content=f'''{{
  "name": "{project_name}-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {{
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }},
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }},
  "devDependencies": {{
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  }}
}}
'''
    )
    files.append(f"{base}/package.json")
    
    # vite.config.js
    tools["write_file"](
        path=f"{base}/vite.config.js",
        content='''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
'''
    )
    files.append(f"{base}/vite.config.js")
    
    # index.html
    tools["write_file"](
        path=f"{base}/index.html",
        content=f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
'''
    )
    files.append(f"{base}/index.html")
    
    # src/main.jsx
    tools["write_file"](
        path=f"{base}/src/main.jsx",
        content='''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
'''
    )
    files.append(f"{base}/src/main.jsx")
    
    # src/App.jsx
    tools["write_file"](
        path=f"{base}/src/App.jsx",
        content=f'''import {{ useState, useEffect }} from 'react'

function App() {{
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {{
    fetch('/api/v1/../health')
      .then(res => res.json())
      .then(data => {{
        setHealth(data)
        setLoading(false)
      }})
      .catch(() => setLoading(false))
  }}, [])

  return (
    <div className="app">
      <header>
        <h1>🚀 {project_name}</h1>
        <p>{task_desc[:100]}</p>
      </header>
      
      <main>
        <section className="status">
          <h2>API Status</h2>
          {{loading ? (
            <p>Checking...</p>
          ) : health ? (
            <p className="success">✓ Backend is {{health.status}}</p>
          ) : (
            <p className="error">✗ Backend not reachable</p>
          )}}
        </section>
        
        <section className="links">
          <h2>Quick Links</h2>
          <ul>
            <li><a href="/api/v1/docs" target="_blank">📖 API Docs</a></li>
            <li><a href="/api/v1/redoc" target="_blank">📋 ReDoc</a></li>
          </ul>
        </section>
      </main>
      
      <footer>
        <p>Generated by Masidy Autonomous Agent Runtime</p>
      </footer>
    </div>
  )
}}

export default App
'''
    )
    files.append(f"{base}/src/App.jsx")
    
    # src/index.css
    tools["write_file"](
        path=f"{base}/src/index.css",
        content='''* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  color: #333;
}

.app {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
}

header {
  text-align: center;
  color: white;
  margin-bottom: 2rem;
}

header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

main {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

section {
  margin-bottom: 2rem;
}

section h2 {
  color: #667eea;
  margin-bottom: 1rem;
  border-bottom: 2px solid #eee;
  padding-bottom: 0.5rem;
}

.success {
  color: #28a745;
  font-weight: bold;
}

.error {
  color: #dc3545;
  font-weight: bold;
}

ul {
  list-style: none;
}

li {
  margin: 0.5rem 0;
}

a {
  color: #667eea;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

footer {
  text-align: center;
  color: rgba(255,255,255,0.8);
  margin-top: 2rem;
  font-size: 0.9rem;
}
'''
    )
    files.append(f"{base}/src/index.css")
    
    return files


def _create_docker(tools: dict, project_name: str, include_frontend: bool) -> list[str]:
    """Create Docker configuration"""
    files = []
    base = project_name
    
    # Backend Dockerfile
    tools["write_file"](
        path=f"{base}/backend/Dockerfile",
        content='''FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    )
    files.append(f"{base}/backend/Dockerfile")
    
    if include_frontend:
        # Frontend Dockerfile
        tools["write_file"](
            path=f"{base}/frontend/Dockerfile",
            content='''FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
'''
        )
        files.append(f"{base}/frontend/Dockerfile")
        
        # nginx.conf
        tools["write_file"](
            path=f"{base}/frontend/nginx.conf",
            content='''server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
'''
        )
        files.append(f"{base}/frontend/nginx.conf")
    
    # docker-compose.yml
    compose_content = f'''version: '3.8'

services:
  backend:
    build: ./backend
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
    
    if include_frontend:
        compose_content += '''
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
'''
    
    tools["write_file"](
        path=f"{base}/docker-compose.yml",
        content=compose_content
    )
    files.append(f"{base}/docker-compose.yml")
    
    # .dockerignore
    tools["write_file"](
        path=f"{base}/.dockerignore",
        content='''__pycache__
*.pyc
*.pyo
.git
.gitignore
.env
*.db
node_modules
dist
.vite
'''
    )
    files.append(f"{base}/.dockerignore")
    
    return files


def _create_ci(tools: dict, project_name: str) -> list[str]:
    """Create GitHub Actions CI workflow"""
    files = []
    
    tools["write_file"](
        path=f"{project_name}/.github/workflows/ci.yml",
        content=f'''name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        working-directory: ./backend
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run tests
        working-directory: ./backend
        run: |
          pytest tests/ -v --tb=short
      
      - name: Check app starts
        working-directory: ./backend
        run: |
          timeout 10 uvicorn app.main:app --host 0.0.0.0 --port 8000 &
          sleep 5
          curl -f http://localhost:8000/health || exit 1

  build-docker:
    runs-on: ubuntu-latest
    needs: test-backend
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build backend image
        run: docker build -t {project_name}-backend ./backend
      
      - name: Test backend container
        run: |
          docker run -d -p 8000:8000 --name test-backend {project_name}-backend
          sleep 5
          curl -f http://localhost:8000/health
          docker stop test-backend
'''
    )
    files.append(f"{project_name}/.github/workflows/ci.yml")
    
    return files


def _create_tests(tools: dict, project_name: str) -> list[str]:
    """Create test files"""
    files = []
    base = f"{project_name}/backend/tests"
    
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

# Test database
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
        path=f"{base}/test_health.py",
        content='''"""Health check tests"""


def test_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
'''
    )
    files.append(f"{base}/test_health.py")
    
    tools["write_file"](
        path=f"{base}/test_auth.py",
        content='''"""Authentication tests"""


def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_login(client):
    """Test user login"""
    # First register
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "testpass123"
        }
    )
    
    # Then login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
'''
    )
    files.append(f"{base}/test_auth.py")
    
    return files


def _create_readme(tools: dict, project_name: str, task_desc: str, db_type: str, include_frontend: bool) -> list[str]:
    """Create project README"""
    files = []
    
    frontend_section = ""
    if include_frontend:
        frontend_section = """
## Frontend

React-based frontend with Vite.

```bash
cd frontend
npm install
npm run dev
```

Access at: http://localhost:3000
"""
    
    tools["write_file"](
        path=f"{project_name}/README.md",
        content=f'''# {project_name}

> {task_desc}

Generated by **Masidy Autonomous Agent Runtime** 🚀

## Stack

- **Backend**: FastAPI + SQLAlchemy
- **Database**: {db_type.upper()}
- **Auth**: JWT-based authentication
- **Frontend**: {'React + Vite' if include_frontend else 'Not included'}
- **CI/CD**: GitHub Actions

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API available at: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
{frontend_section}
## Docker

```bash
# Build and run all services
docker-compose up --build

# Or just backend
docker build -t {project_name}-backend ./backend
docker run -p 8000:8000 {project_name}-backend
```

## Testing

```bash
cd backend
pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get token |
| GET | `/api/v1/users/me` | Get current user |
| GET | `/api/v1/items/` | List items |
| POST | `/api/v1/items/` | Create item |
| GET | `/api/v1/items/{{id}}` | Get item |
| PUT | `/api/v1/items/{{id}}` | Update item |
| DELETE | `/api/v1/items/{{id}}` | Delete item |

## Project Structure

```
{project_name}/
├── backend/
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Config, DB, security
│   │   ├── models/       # SQLAlchemy models
│   │   └── schemas/      # Pydantic schemas
│   ├── tests/            # Pytest tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # React app
├── .github/workflows/    # CI/CD
├── docker-compose.yml
└── README.md
```

## License

MIT
'''
    )
    files.append(f"{project_name}/README.md")
    
    # .env.example
    tools["write_file"](
        path=f"{project_name}/.env.example",
        content=f'''# Environment Configuration
DATABASE_URL={db_type}:///./app.db
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
'''
    )
    files.append(f"{project_name}/.env.example")
    
    # .gitignore
    tools["write_file"](
        path=f"{project_name}/.gitignore",
        content='''# Python
__pycache__/
*.py[cod]
*$py.class
.env
*.db
.pytest_cache/
.coverage

# Node
node_modules/
dist/
.vite/

# IDE
.vscode/
.idea/

# Docker
*.log
'''
    )
    files.append(f"{project_name}/.gitignore")
    
    return files
