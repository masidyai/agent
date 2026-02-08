# Masidy Autonomous Agent Runtime - Premium Edition

🚀 **An ALL-IN-ONE autonomous agent system for creating complete, production-ready projects.**

Uses **OpenAI Swarm** for agent orchestration and **LangGraph** for planning loops.

## ✨ Features

- **Three High-Level Flows**: SaaS, API, and Refactor blueprints
- **Flow Router**: Intelligent routing with auto-detection
- **Configurable**: Full configuration system for each flow
- **End-to-End Execution**: Complete projects autonomously
- **No Mocks**: Everything is runnable and complete
- **33+ Tools**: File operations, commands, Git/GitHub interactions
- **Persistent Memory**: Track task history and execution statistics

## 📦 Available Flows

### 1. SaaS Flow (`--flow saas`)
Creates a complete full-stack SaaS application:
- **Backend**: FastAPI with SQLAlchemy
- **Frontend**: React with Vite
- **Database**: SQLite or PostgreSQL
- **Auth**: JWT-based authentication
- **Docker**: Dockerfile + docker-compose
- **CI/CD**: GitHub Actions workflow
- **Tests**: pytest test suite

### 2. API Flow (`--flow api`)
Creates a backend-only API service:
- **Backend**: FastAPI with full CRUD
- **Database**: SQLite with SQLAlchemy
- **Tests**: pytest test suite
- **Docker**: Dockerfile + docker-compose
- **CI/CD**: GitHub Actions workflow

### 3. Refactor Flow (`--flow refactor`)
Modernizes and improves an existing repository:
- **Analysis**: Detect languages, frameworks, structure
- **Testing**: Run existing tests
- **Cleanup**: Identify unused files
- **Documentation**: Improve or create README
- **Docker**: Add/fix Dockerfile
- **CI/CD**: Add/fix GitHub Actions workflow

## 📁 Project Structure

```
masidy_agent_runtime/
├── agents/
│   ├── core_agent.py      # Core agent with Swarm orchestration
│   └── planner.py         # LangGraph planning + structured plans
├── blueprints/
│   ├── saas_blueprint.py  # Full-stack SaaS generator
│   ├── api_blueprint.py   # Backend API generator
│   └── refactor_blueprint.py  # Repo modernizer
├── executors/             # NEW: Execution layer
│   ├── __init__.py        # Executor registry
│   ├── base_executor.py   # Base class with retry logic
│   ├── api_executor.py    # API service executor
│   ├── saas_executor.py   # SaaS app executor
│   └── refactor_executor.py  # Refactor executor
├── flows/                 # Flow routing system
│   ├── __init__.py
│   └── flow_router.py     # Routes tasks to blueprints
├── config/                # Configuration system
│   ├── __init__.py
│   ├── defaults.py        # Base configuration
│   ├── saas_config.py     # SaaS-specific config
│   ├── api_config.py      # API-specific config
│   └── refactor_config.py # Refactor-specific config
├── tools/
│   ├── file_tools.py      # 10 file system operations
│   ├── command_tools.py   # 10 shell command tools
│   └── github_tools.py    # 13 Git/GitHub operations
├── memory/
│   ├── state.json         # Persistent state storage
│   └── state_manager.py   # State management
├── main.py                # Main entry point
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🛠️ Installation

```bash
cd masidy_agent_runtime
pip install -r requirements.txt
```

Optional: Set OpenAI API key for LLM-based planning:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 🎯 Usage

### Quick Start Examples

```bash
# Create a SaaS application
python main.py --flow saas --task "Build a simple SaaS for managing tasks"

# Create an API service
python main.py --flow api --task "Create an API for notes with CRUD"

# Modernize an existing repo
python main.py --flow refactor --task "Modernize this repo and add CI"

# Auto-detect the right flow
python main.py --task "Build a REST API for user management"

# Interactive mode
python main.py --interactive

# Simple demo (hello world)
python main.py --example
```

### Configuration System

View default configuration for a flow:
```bash
python main.py --show-config api
```

Override configuration via JSON:
```bash
python main.py --flow api --task "Create notes API" \
  --config '{"project_name": "my_notes_api", "database": {"type": "postgresql"}}'
```

### List Available Flows

```bash
python main.py --list-flows
```

### Interactive Mode

```bash
python main.py --interactive
```

Commands in interactive mode:
- `flows` - List available flows
- `config` - Show flow configurations
- `tools` - List available tools
- `stats` - Show execution statistics
- `history` - Show task history
- `quit` - Exit

## ⚙️ Configuration Reference

### Default Configuration (all flows)

```python
{
  "project_name": "project",
  "output_folder": "project",
  "version": "0.1.0",
  "include_docker": True,
  "include_ci": True,
  "include_tests": True,
  "docker": {
    "enabled": True,
    "base_image": "python:3.11-slim",
    "expose_port": 8000
  },
  "ci": {
    "enabled": True,
    "provider": "github",
    "run_tests": True
  },
  "database": {
    "type": "sqlite",
    "name": "app.db"
  }
}
```

### SaaS-Specific Configuration

```python
{
  "include_frontend": True,
  "include_auth": True,
  "frontend": {
    "framework": "react",
    "bundler": "vite",
    "port": 3000
  },
  "auth": {
    "type": "jwt",
    "token_expire_minutes": 30
  }
}
```

### API-Specific Configuration

```python
{
  "api": {
    "prefix": "/api/v1",
    "include_health": True,
    "include_openapi": True,
    "pagination": True
  },
  "testing": {
    "framework": "pytest",
    "async_tests": True
  }
}
```

### Refactor-Specific Configuration

```python
{
  "target_path": ".",
  "cleanup": {
    "enabled": True,
    "safe_mode": True
  },
  "documentation": {
    "improve_readme": True,
    "create_if_missing": True
  }
}
```

## 🔄 Executor Layer

The executor layer provides structured plan execution with retries and result tracking.

### How It Works

1. **Blueprint** creates a structured plan (list of steps)
2. **Executor** iterates over the plan steps
3. **Each step** is executed with retry logic (max 3 retries)
4. **Results** are recorded to memory/state.json
5. **Final result** includes status, steps completed, errors, and output path

### Structured Plan Format

Each plan step includes:
```python
{
  "id": "create_model",
  "description": "Create Item model",
  "tool_name": "write_file",
  "tool_args": {"path": "...", "content": "..."},
  "verify_instruction": "File should exist"
}
```

### Result Format

```python
{
  "status": "success" | "failure" | "partial",
  "steps_completed": 18,
  "steps_total": 18,
  "errors": [],
  "output_path": "api_service",
  "duration_ms": 1234
}
```

### Using --verbose

The `--verbose` flag shows detailed step-by-step execution:

```bash
python main.py --flow api --task "Create a notes API" --verbose
```

Output:
```
============================================================
  Executing API Plan (18 steps)
============================================================

[1/18] Create project directory structure
    ✓ Success

[2/18] Create app directory
    ✓ Success

[3/18] Create API directory
    ↻ Retry 1/3: Directory exists
    ✓ Success
...
```

## 📊 Example Outputs

### API Flow

```bash
$ python main.py --flow api --task "Create a minimal API service"

════════════════════════════════════════════════════════════
  🚀 MASIDY AGENT RUNTIME - EXECUTION SUMMARY
════════════════════════════════════════════════════════════
  Flow:           API
  Task:           Create a minimal API service
  Status:         ✅ SUCCESS
  Steps:          18 / 18 completed
  Duration:       1234ms (1.23s)
  Output:         ./api_service/
════════════════════════════════════════════════════════════
```

### SaaS Flow

```bash
$ python main.py --flow saas --task "Build a task management SaaS"

════════════════════════════════════════════════════════════
  🚀 MASIDY AGENT RUNTIME - EXECUTION SUMMARY
════════════════════════════════════════════════════════════
  Flow:           SAAS
  Task:           Build a task management SaaS
  Status:         ✅ SUCCESS
  Steps:          45 / 45 completed
  Duration:       2345ms (2.35s)
  Output:         ./saas_app/
════════════════════════════════════════════════════════════
```

### Refactor Flow

```bash
$ python main.py --flow refactor --task "Modernize this repo and add CI"

════════════════════════════════════════════════════════════
  🚀 MASIDY AGENT RUNTIME - EXECUTION SUMMARY
════════════════════════════════════════════════════════════
  Flow:           REFACTOR
  Task:           Modernize this repo and add CI
  Status:         ✅ SUCCESS
  Steps:          12 / 12 completed
  Output:         ./
════════════════════════════════════════════════════════════
```

## 🔧 Available Tools

### File Tools
| Tool | Description |
|------|-------------|
| `create_directory` | Create a new directory |
| `write_file` | Write content to a file |
| `read_file` | Read content from a file |
| `append_to_file` | Append content to a file |
| `delete_file` | Delete a file |
| `delete_directory` | Delete a directory |
| `list_directory` | List directory contents |
| `copy_file` | Copy a file |
| `move_file` | Move a file |
| `file_exists` | Check if file/directory exists |

### Command Tools
| Tool | Description |
|------|-------------|
| `run_command` | Execute a shell command |
| `run_python_script` | Run a Python script |
| `run_pip_install` | Install Python packages |
| `get_environment_variable` | Get an environment variable |
| `set_environment_variable` | Set an environment variable |
| `get_current_directory` | Get current working directory |
| `change_directory` | Change working directory |
| `which_command` | Find command path |
| `get_system_info` | Get system information |
| `run_background_command` | Run command in background |

### GitHub Tools
| Tool | Description |
|------|-------------|
| `git_clone` | Clone a repository |
| `git_status` | Get git status |
| `git_add` | Stage files |
| `git_commit` | Create a commit |
| `git_push` | Push to remote |
| `git_pull` | Pull from remote |
| `git_branch` | List/create branches |
| `git_current_branch` | Get current branch |
| `github_create_issue` | Create GitHub issue |
| `github_list_issues` | List GitHub issues |
| `github_create_pr` | Create pull request |
| `github_list_prs` | List pull requests |
| `github_repo_info` | Get repository info |

## 🏗️ Architecture

### Core Components

1. **Core Agent** (`agents/core_agent.py`)
   - Uses OpenAI Swarm for agent orchestration
   - Manages task context and execution flow
   - Implements retry logic for failed steps

2. **Task Planner** (`agents/planner.py`)
   - Uses LangGraph for stateful planning workflows
   - Blueprint selection and inference
   - Creates execution plans from natural language tasks

3. **Blueprints** (`blueprints/`)
   - High-level flows for complete projects
   - SaaS, API, and Refactor blueprints
   - Each generates real, runnable code

4. **State Manager** (`memory/state_manager.py`)
   - Thread-safe persistent state storage
   - Tracks task history and execution statistics

### Flow Execution

```
Task → Blueprint Selection → Multi-Step Execution → Verification → Memory Update
          ↓                        ↓
     (saas/api/refactor)    (tools + retry logic)
```

## 📊 Example: SaaS Flow Output

```bash
$ python main.py --flow saas --task "Create a minimal SaaS app skeleton"

============================================================
  🚀 Masidy Autonomous Agent Runtime - Premium Edition
============================================================
  Available tools: 33
  Available flows: saas, api, refactor
============================================================

🎯 Selected flow: SAAS
   Full-stack SaaS with FastAPI backend, React frontend, auth, and CI/CD

============================================================
  🚀 SAAS BLUEPRINT - Starting Full Stack Generation
============================================================
  Task: Create a minimal SaaS app skeleton
============================================================

[Step 1/8] Creating project structure...
  ✓ Project structure created

[Step 2/8] Creating FastAPI backend...
  ✓ Backend created (15 files)

[Step 3/8] Creating React frontend...
  ✓ Frontend created (6 files)

[Step 4/8] Creating JWT authentication...
  ✓ Auth module created (1 files)

[Step 5/8] Creating Docker configuration...
  ✓ Docker config created (4 files)

[Step 6/8] Creating GitHub Actions CI...
  ✓ CI workflow created (1 files)

[Step 7/8] Creating tests...
  ✓ Tests created (4 files)

[Step 8/8] Creating README and documentation...
  ✓ README created (3 files)

============================================================
  📊 SAAS BLUEPRINT SUMMARY
============================================================
  Project: saas_app/
  Status: ✓ SUCCESS
  Steps completed: 8/8
  Files created: 34
============================================================
```

### Generated SaaS Structure

```
saas_app/
├── backend/
│   ├── app/
│   │   ├── api/          # Auth, users, items endpoints
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # User, Item models
│   │   └── schemas/      # Pydantic schemas
│   ├── tests/            # pytest tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/              # React components
│   ├── Dockerfile
│   └── package.json
├── .github/workflows/    # CI pipeline
├── docker-compose.yml
└── README.md
```

## 🔮 Extending the Runtime

### Adding New Tools

1. Create a new tool function in the appropriate tools file:

```python
def my_new_tool(param1: str, param2: int = 10) -> dict:
    """Description of what the tool does"""
    try:
        # Tool implementation
        return {"success": True, "result": "..."}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

2. Add it to the tool registry:

```python
MY_TOOLS = {
    "my_new_tool": my_new_tool,
}
```

3. Import and register in `main.py`:

```python
from tools.my_tools import MY_TOOLS
self.tools.update(MY_TOOLS)
```

### Custom Planners

Implement a custom planner by extending the planning interface:

```python
class CustomPlanner:
    def create_plan(self, task: str) -> list[dict]:
        # Your planning logic here
        return [
            {"step": 1, "tool": "...", "args": {...}, "description": "..."}
        ]
```

## 📝 License

MIT License - Feel free to use and modify for your projects.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.
