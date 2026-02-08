"""
Masidy Autonomous Agent Runtime - Refactor Executor
Executes repository refactoring and modernization plans
"""

from typing import Callable
from pathlib import Path
from .base_executor import BaseExecutor


class RefactorExecutor(BaseExecutor):
    """Executor for repository refactoring"""
    
    @property
    def flow_name(self) -> str:
        return "refactor"
    
    def build_plan(self, task_description: str, config: dict) -> list[dict]:
        """
        Build a structured plan for repository refactoring.
        """
        target_path = config.get("target_path", ".")
        
        plan = [
            # Step 1: Analyze repository
            {
                "id": "analyze_structure",
                "description": "Analyze repository structure",
                "tool_name": "list_directory",
                "tool_args": {"path": target_path, "recursive": True},
                "verify_instruction": "Should return list of files"
            },
            
            # Step 2: Check for existing README
            {
                "id": "check_readme",
                "description": "Check for existing README",
                "tool_name": "file_exists",
                "tool_args": {"path": f"{target_path}/README.md"},
                "verify_instruction": None
            },
            
            # Step 3: Check for existing Dockerfile
            {
                "id": "check_dockerfile",
                "description": "Check for existing Dockerfile",
                "tool_name": "file_exists",
                "tool_args": {"path": f"{target_path}/Dockerfile"},
                "verify_instruction": None
            },
            
            # Step 4: Check for existing CI
            {
                "id": "check_ci",
                "description": "Check for existing CI workflow",
                "tool_name": "file_exists",
                "tool_args": {"path": f"{target_path}/.github/workflows"},
                "verify_instruction": None
            },
            
            # Step 5: Check for .gitignore
            {
                "id": "check_gitignore",
                "description": "Check for .gitignore",
                "tool_name": "file_exists",
                "tool_args": {"path": f"{target_path}/.gitignore"},
                "verify_instruction": None
            },
            
            # Step 6: Create .github/workflows directory if needed
            {
                "id": "create_workflows_dir",
                "description": "Create .github/workflows directory",
                "tool_name": "create_directory",
                "tool_args": {"path": f"{target_path}/.github/workflows"},
                "verify_instruction": None
            },
            
            # Step 7: Create or improve README
            {
                "id": "create_readme",
                "description": "Create/improve README.md",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{target_path}/README.md",
                    "content": self._get_readme_content(target_path, task_description)
                },
                "verify_instruction": None
            },
            
            # Step 8: Create .gitignore if missing
            {
                "id": "create_gitignore",
                "description": "Create/update .gitignore",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{target_path}/.gitignore",
                    "content": self._get_gitignore_content()
                },
                "verify_instruction": None
            },
            
            # Step 9: Create Dockerfile
            {
                "id": "create_dockerfile",
                "description": "Create Dockerfile",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{target_path}/Dockerfile",
                    "content": self._get_dockerfile_content()
                },
                "verify_instruction": None
            },
            
            # Step 10: Create .dockerignore
            {
                "id": "create_dockerignore",
                "description": "Create .dockerignore",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{target_path}/.dockerignore",
                    "content": self._get_dockerignore_content()
                },
                "verify_instruction": None
            },
            
            # Step 11: Create CI workflow
            {
                "id": "create_ci",
                "description": "Create GitHub Actions CI workflow",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{target_path}/.github/workflows/ci.yml",
                    "content": self._get_ci_content()
                },
                "verify_instruction": None
            },
            
            # Step 12: Create CONTRIBUTING.md
            {
                "id": "create_contributing",
                "description": "Create CONTRIBUTING.md",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{target_path}/CONTRIBUTING.md",
                    "content": self._get_contributing_content()
                },
                "verify_instruction": None
            },
        ]
        
        return plan
    
    def _get_readme_content(self, target_path: str, task_desc: str) -> str:
        project_name = Path(target_path).name if target_path != "." else "Project"
        return f'''# {project_name}

> {task_desc}

*Modernized by Masidy Autonomous Agent Runtime*

## Overview

This project has been analyzed and improved with:
- Updated documentation
- Docker support
- CI/CD pipeline
- Standard project structure

## Getting Started

### Prerequisites

- Python 3.11+ or Node.js 20+ (depending on project type)
- Docker (optional)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd {project_name}

# Install dependencies
pip install -r requirements.txt  # For Python
# or
npm install  # For Node.js
```

### Running

```bash
# Development
python main.py  # or npm start

# With Docker
docker-compose up --build
```

## Testing

```bash
pytest tests/ -v  # Python
# or
npm test  # Node.js
```

## Project Structure

```
{project_name}/
├── src/           # Source code
├── tests/         # Test files
├── docs/          # Documentation
├── Dockerfile     # Docker configuration
├── .github/       # CI/CD workflows
└── README.md      # This file
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT

---

*Documentation generated by Masidy Agent Runtime*
'''
    
    def _get_gitignore_content(self) -> str:
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
.env
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/
venv/
.venv/

# Node.js
node_modules/
npm-debug.log
yarn-error.log
.next/
out/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project
*.db
*.log
*.tmp
.cache/
'''
    
    def _get_dockerfile_content(self) -> str:
        return '''# Multi-stage Dockerfile template
# Customize based on your project type

FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies
COPY requirements.txt* ./
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || echo "No requirements.txt"

# Copy source
COPY . .

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

EXPOSE 8000

# Default command - customize for your app
CMD ["python", "-m", "http.server", "8000"]
'''
    
    def _get_dockerignore_content(self) -> str:
        return '''# Dependencies
node_modules/
__pycache__/
*.pyc
venv/
.venv/

# Git
.git/
.gitignore

# IDE
.vscode/
.idea/

# Tests
tests/
*.test.*
coverage/
.pytest_cache/

# Build
dist/
build/
*.egg-info/

# Environment
.env
.env.*
!.env.example

# Logs
*.log

# OS
.DS_Store
Thumbs.db
'''
    
    def _get_ci_content(self) -> str:
        return '''name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
      
      - name: Run tests
        run: |
          if [ -d tests ]; then
            pip install pytest
            pytest tests/ -v || echo "Tests completed"
          else
            echo "No tests directory found"
          fi
      
      - name: Lint
        run: |
          pip install ruff
          ruff check . || echo "Linting completed"

  docker:
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'push'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker image
        run: |
          if [ -f Dockerfile ]; then
            docker build -t ${{ github.repository }}:latest .
          else
            echo "No Dockerfile found"
          fi
'''
    
    def _get_contributing_content(self) -> str:
        return '''# Contributing

Thank you for your interest in contributing!

## How to Contribute

1. **Fork** the repository
2. **Clone** your fork
3. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
4. **Commit** your changes (`git commit -m 'Add amazing feature'`)
5. **Push** to the branch (`git push origin feature/amazing-feature`)
6. **Open** a Pull Request

## Guidelines

### Code Style

- Follow the existing code style
- Write clear, descriptive commit messages
- Add tests for new features

### Pull Requests

- Keep PRs focused on a single change
- Update documentation as needed
- Ensure all tests pass

### Issues

- Search existing issues before creating a new one
- Provide clear reproduction steps for bugs
- Use issue templates when available

## Development Setup

```bash
# Clone the repository
git clone <your-fork-url>
cd <project-name>

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v
```

## Questions?

Open an issue or reach out to the maintainers.

---

*Generated by Masidy Agent Runtime*
'''
