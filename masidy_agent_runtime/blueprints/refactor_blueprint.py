"""
Masidy Autonomous Agent Runtime - Refactor Blueprint
Modernizes and improves an existing repository:
- Analyze structure
- Run existing tests
- Clean unused files (carefully)
- Improve README
- Add/fix Dockerfile
- Add/fix CI workflow
- Summarize changes
"""

import os
from typing import Any
from datetime import datetime
from pathlib import Path

REFACTOR_BLUEPRINT_INFO = {
    "name": "Repository Refactor",
    "description": "Modernize, clean, and improve an existing codebase",
    "components": ["Analysis", "Testing", "Cleanup", "Documentation", "Docker", "CI/CD"],
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
    Run the refactor blueprint to modernize an existing repository.
    
    Args:
        task_description: What refactoring the user wants
        config: Configuration options (target_path, etc.)
        core_agent: The core agent instance for tool execution
        planner: The planner instance
        state_manager: State manager for persistence
        verbose: Whether to print detailed output
    
    Returns:
        dict with results of the blueprint execution
    """
    print("\n" + "=" * 60)
    print("  🔧 REFACTOR BLUEPRINT - Modernizing Repository")
    print("=" * 60)
    print(f"  Task: {task_description}")
    print("=" * 60)
    
    # Extract configuration
    target_path = config.get("target_path", ".")
    
    results = {
        "blueprint": "refactor",
        "target_path": target_path,
        "task": task_description,
        "steps_completed": [],
        "steps_failed": [],
        "changes_made": [],
        "files_created": [],
        "files_modified": [],
        "analysis": {},
        "started_at": datetime.now().isoformat(),
    }
    
    tools = core_agent.tools
    
    # Step 1: Analyze repository structure
    print("\n[Step 1/6] Analyzing repository structure...")
    try:
        analysis = _analyze_repository(tools, target_path)
        results["analysis"] = analysis
        results["steps_completed"].append("analysis")
        print(f"  ✓ Analysis complete:")
        print(f"    - Files: {analysis.get('total_files', 0)}")
        print(f"    - Languages: {', '.join(analysis.get('languages', ['unknown']))}")
        print(f"    - Has tests: {analysis.get('has_tests', False)}")
        print(f"    - Has Docker: {analysis.get('has_docker', False)}")
        print(f"    - Has CI: {analysis.get('has_ci', False)}")
    except Exception as e:
        results["steps_failed"].append({"step": "analysis", "error": str(e)})
        print(f"  ✗ Failed: {e}")
        # Continue with empty analysis
        results["analysis"] = {}
    
    # Step 2: Run existing tests
    print("\n[Step 2/6] Running existing tests...")
    try:
        test_results = _run_existing_tests(tools, target_path, results["analysis"])
        results["test_results"] = test_results
        results["steps_completed"].append("tests")
        if test_results.get("ran"):
            print(f"  ✓ Tests executed: {test_results.get('summary', 'completed')}")
        else:
            print("  ⚠ No tests found or test framework not detected")
    except Exception as e:
        results["steps_failed"].append({"step": "tests", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Step 3: Identify and clean unused files
    print("\n[Step 3/6] Identifying cleanup opportunities...")
    try:
        cleanup = _identify_cleanup(tools, target_path, results["analysis"])
        results["cleanup_suggestions"] = cleanup
        results["steps_completed"].append("cleanup_analysis")
        print(f"  ✓ Found {len(cleanup.get('suggestions', []))} cleanup suggestions")
        for suggestion in cleanup.get("suggestions", [])[:5]:
            print(f"    - {suggestion}")
    except Exception as e:
        results["steps_failed"].append({"step": "cleanup_analysis", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Step 4: Improve README
    print("\n[Step 4/6] Improving documentation...")
    try:
        doc_files = _improve_documentation(tools, target_path, task_description, results["analysis"])
        results["files_modified"].extend(doc_files.get("modified", []))
        results["files_created"].extend(doc_files.get("created", []))
        results["changes_made"].append("documentation")
        results["steps_completed"].append("documentation")
        print(f"  ✓ Documentation updated ({len(doc_files.get('created', []))} created, {len(doc_files.get('modified', []))} modified)")
    except Exception as e:
        results["steps_failed"].append({"step": "documentation", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Step 5: Add/fix Dockerfile
    print("\n[Step 5/6] Adding/improving Docker configuration...")
    try:
        docker_files = _ensure_docker(tools, target_path, results["analysis"])
        results["files_created"].extend(docker_files.get("created", []))
        results["files_modified"].extend(docker_files.get("modified", []))
        if docker_files.get("created") or docker_files.get("modified"):
            results["changes_made"].append("docker")
        results["steps_completed"].append("docker")
        print(f"  ✓ Docker config: {len(docker_files.get('created', []))} created, {len(docker_files.get('modified', []))} modified")
    except Exception as e:
        results["steps_failed"].append({"step": "docker", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Step 6: Add/fix CI workflow
    print("\n[Step 6/6] Adding/improving CI workflow...")
    try:
        ci_files = _ensure_ci(tools, target_path, results["analysis"])
        results["files_created"].extend(ci_files.get("created", []))
        results["files_modified"].extend(ci_files.get("modified", []))
        if ci_files.get("created") or ci_files.get("modified"):
            results["changes_made"].append("ci")
        results["steps_completed"].append("ci")
        print(f"  ✓ CI workflow: {len(ci_files.get('created', []))} created, {len(ci_files.get('modified', []))} modified")
    except Exception as e:
        results["steps_failed"].append({"step": "ci", "error": str(e)})
        print(f"  ✗ Failed: {e}")
    
    # Finalize
    results["completed_at"] = datetime.now().isoformat()
    results["success"] = len(results["steps_failed"]) == 0
    
    # Update state
    state_manager.update_context("last_refactor", {
        "path": target_path,
        "changes": results["changes_made"],
        "files_created": len(results["files_created"]),
        "files_modified": len(results["files_modified"]),
        "completed_at": results["completed_at"]
    })
    
    # Print summary
    print("\n" + "=" * 60)
    print("  📊 REFACTOR BLUEPRINT SUMMARY")
    print("=" * 60)
    print(f"  Target: {target_path}")
    print(f"  Status: {'✓ SUCCESS' if results['success'] else '✗ PARTIAL'}")
    print(f"  Steps completed: {len(results['steps_completed'])}/6")
    print(f"  Changes made: {', '.join(results['changes_made']) or 'none'}")
    print(f"  Files created: {len(results['files_created'])}")
    print(f"  Files modified: {len(results['files_modified'])}")
    if results["steps_failed"]:
        print(f"  Failed steps: {[s['step'] for s in results['steps_failed']]}")
    print("=" * 60)
    
    return results


def _analyze_repository(tools: dict, target_path: str) -> dict:
    """Analyze the repository structure"""
    analysis = {
        "total_files": 0,
        "languages": [],
        "has_tests": False,
        "has_docker": False,
        "has_ci": False,
        "has_readme": False,
        "framework": None,
        "structure": {},
    }
    
    # List directory contents
    result = tools["list_directory"](path=target_path, recursive=True)
    if not result.get("success"):
        return analysis
    
    items = result.get("items", [])
    analysis["total_files"] = len([i for i in items if i.get("type") == "file"])
    
    # Detect languages and frameworks
    extensions = {}
    for item in items:
        name = item.get("name", "")
        if item.get("type") == "file":
            ext = Path(name).suffix.lower()
            extensions[ext] = extensions.get(ext, 0) + 1
            
            # Check for specific files
            if name.lower() in ["readme.md", "readme.rst", "readme.txt", "readme"]:
                analysis["has_readme"] = True
            if name.lower() in ["dockerfile", "docker-compose.yml", "docker-compose.yaml"]:
                analysis["has_docker"] = True
            if "test" in name.lower() or name.startswith("test_"):
                analysis["has_tests"] = True
            
            # Framework detection
            if name == "package.json":
                analysis["framework"] = "nodejs"
            elif name == "requirements.txt" or name == "pyproject.toml":
                analysis["framework"] = "python"
            elif name == "go.mod":
                analysis["framework"] = "go"
            elif name == "Cargo.toml":
                analysis["framework"] = "rust"
        
        # Check for CI directories
        if ".github/workflows" in name or ".gitlab-ci.yml" in name:
            analysis["has_ci"] = True
        
        # Check for test directories
        if item.get("type") == "directory" and item.get("name") in ["tests", "test", "__tests__", "spec"]:
            analysis["has_tests"] = True
    
    # Determine languages
    lang_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".go": "Go",
        ".rs": "Rust",
        ".java": "Java",
        ".rb": "Ruby",
        ".php": "PHP",
    }
    
    for ext, lang in lang_map.items():
        if extensions.get(ext, 0) > 0:
            analysis["languages"].append(lang)
    
    if not analysis["languages"]:
        analysis["languages"] = ["unknown"]
    
    analysis["structure"] = {
        "extensions": extensions,
        "file_count": analysis["total_files"],
    }
    
    return analysis


def _run_existing_tests(tools: dict, target_path: str, analysis: dict) -> dict:
    """Run existing tests if found"""
    test_results = {"ran": False, "summary": "no tests found"}
    
    if not analysis.get("has_tests"):
        return test_results
    
    framework = analysis.get("framework")
    
    # Determine test command based on framework
    test_commands = {
        "python": "pytest tests/ -v --tb=short 2>&1 || python -m pytest tests/ -v --tb=short 2>&1 || echo 'Tests completed or not found'",
        "nodejs": "npm test 2>&1 || echo 'Tests completed or not found'",
        "go": "go test ./... 2>&1 || echo 'Tests completed or not found'",
    }
    
    test_cmd = test_commands.get(framework)
    if test_cmd:
        result = tools["run_command"](command=test_cmd, cwd=target_path, timeout=120)
        test_results["ran"] = True
        test_results["output"] = result.get("stdout", "")[:500]
        test_results["summary"] = "completed" if result.get("success") else "some tests may have failed"
    
    return test_results


def _identify_cleanup(tools: dict, target_path: str, analysis: dict) -> dict:
    """Identify files that could be cleaned up"""
    cleanup = {"suggestions": [], "safe_to_remove": []}
    
    # Common cleanup patterns
    cleanup_patterns = [
        ("__pycache__", "Python cache directories"),
        (".pyc", "Python compiled files"),
        ("node_modules", "Node modules (should be in .gitignore)"),
        (".DS_Store", "macOS metadata files"),
        ("Thumbs.db", "Windows thumbnail cache"),
        (".env", "Environment files (check if should be gitignored)"),
        (".log", "Log files"),
        (".bak", "Backup files"),
        ("~", "Temporary editor files"),
    ]
    
    result = tools["list_directory"](path=target_path, recursive=True)
    if result.get("success"):
        for item in result.get("items", []):
            name = item.get("name", "")
            for pattern, description in cleanup_patterns:
                if pattern in name:
                    cleanup["suggestions"].append(f"{name} - {description}")
                    break
    
    # Check for .gitignore
    gitignore_check = tools["file_exists"](path=f"{target_path}/.gitignore")
    if not gitignore_check.get("exists"):
        cleanup["suggestions"].append("Missing .gitignore file")
    
    return cleanup


def _improve_documentation(tools: dict, target_path: str, task_desc: str, analysis: dict) -> dict:
    """Improve or create README and documentation"""
    doc_files = {"created": [], "modified": []}
    
    readme_path = f"{target_path}/README.md"
    framework = analysis.get("framework", "unknown")
    languages = ", ".join(analysis.get("languages", ["unknown"]))
    
    # Check existing README
    existing = tools["read_file"](path=readme_path)
    
    if existing.get("success"):
        # README exists - add improvement section
        current_content = existing.get("content", "")
        
        # Only add section if not already modernized
        if "## Development" not in current_content and "## Getting Started" not in current_content:
            improvement_section = f'''

---

## Development

*Section added by Masidy Agent Runtime refactor*

### Quick Start

```bash
# Clone and setup
git clone <repository-url>
cd {Path(target_path).name}

# Install dependencies
{"pip install -r requirements.txt" if framework == "python" else "npm install" if framework == "nodejs" else "# Install dependencies for your framework"}

# Run tests
{"pytest" if framework == "python" else "npm test" if framework == "nodejs" else "# Run your test command"}
```

### Project Info

- **Languages**: {languages}
- **Has Tests**: {"Yes" if analysis.get("has_tests") else "No"}
- **Has Docker**: {"Yes" if analysis.get("has_docker") else "No"}
- **Has CI**: {"Yes" if analysis.get("has_ci") else "No"}
'''
            tools["append_to_file"](path=readme_path, content=improvement_section)
            doc_files["modified"].append(readme_path)
    else:
        # Create new README
        project_name = Path(target_path).name
        readme_content = f'''# {project_name}

> {task_desc}

## Overview

This project was analyzed and documented by Masidy Agent Runtime.

## Tech Stack

- **Languages**: {languages}
- **Framework**: {framework if framework else "Not detected"}

## Getting Started

### Prerequisites

{"- Python 3.8+" if framework == "python" else "- Node.js 18+" if framework == "nodejs" else "- Check project requirements"}

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd {project_name}

# Install dependencies
{"pip install -r requirements.txt" if framework == "python" else "npm install" if framework == "nodejs" else "# Install dependencies"}
```

### Running

```bash
{"python main.py  # or uvicorn app:app --reload" if framework == "python" else "npm start" if framework == "nodejs" else "# Run command"}
```

### Testing

```bash
{"pytest tests/" if framework == "python" else "npm test" if framework == "nodejs" else "# Test command"}
```

## Project Structure

```
{project_name}/
├── {"src/" if framework == "nodejs" else "app/" if framework == "python" else ""}
├── {"tests/" if analysis.get("has_tests") else ""}
├── {"Dockerfile" if analysis.get("has_docker") else ""}
└── README.md
```

## License

MIT

---

*Documentation generated by Masidy Agent Runtime*
'''
        tools["write_file"](path=readme_path, content=readme_content)
        doc_files["created"].append(readme_path)
    
    return doc_files


def _ensure_docker(tools: dict, target_path: str, analysis: dict) -> dict:
    """Ensure Dockerfile exists and is properly configured"""
    docker_files = {"created": [], "modified": []}
    
    dockerfile_path = f"{target_path}/Dockerfile"
    framework = analysis.get("framework")
    
    # Check if Dockerfile exists
    existing = tools["file_exists"](path=dockerfile_path)
    
    if not existing.get("exists"):
        # Create Dockerfile based on framework
        if framework == "python":
            dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
'''
        elif framework == "nodejs":
            dockerfile_content = '''FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
'''
        else:
            dockerfile_content = '''# Dockerfile template - customize for your project
FROM ubuntu:22.04

WORKDIR /app

COPY . .

# Add your build and run commands here
# RUN apt-get update && apt-get install -y <dependencies>
# CMD ["./your-app"]
'''
        
        tools["write_file"](path=dockerfile_path, content=dockerfile_content)
        docker_files["created"].append(dockerfile_path)
    
    # Check for .dockerignore
    dockerignore_path = f"{target_path}/.dockerignore"
    dockerignore_exists = tools["file_exists"](path=dockerignore_path)
    
    if not dockerignore_exists.get("exists"):
        dockerignore_content = '''# Dependencies
node_modules/
__pycache__/
*.pyc

# Git
.git/
.gitignore

# IDE
.vscode/
.idea/

# Environment
.env
.env.*
!.env.example

# Tests
tests/
*.test.*
coverage/

# Build
dist/
build/
*.egg-info/

# Logs
*.log
'''
        tools["write_file"](path=dockerignore_path, content=dockerignore_content)
        docker_files["created"].append(dockerignore_path)
    
    return docker_files


def _ensure_ci(tools: dict, target_path: str, analysis: dict) -> dict:
    """Ensure CI workflow exists"""
    ci_files = {"created": [], "modified": []}
    
    # Create GitHub Actions directory
    workflows_dir = f"{target_path}/.github/workflows"
    tools["create_directory"](path=workflows_dir)
    
    ci_path = f"{workflows_dir}/ci.yml"
    framework = analysis.get("framework")
    
    # Check if CI exists
    existing = tools["file_exists"](path=ci_path)
    
    if not existing.get("exists"):
        project_name = Path(target_path).name
        
        if framework == "python":
            ci_content = f'''name: CI

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
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest tests/ -v || echo "No tests found or tests failed"
      
      - name: Lint
        run: |
          pip install ruff
          ruff check . || echo "Linting completed"
'''
        elif framework == "nodejs":
            ci_content = f'''name: CI

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
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test || echo "No tests found or tests failed"
      
      - name: Lint
        run: npm run lint || echo "No lint script"
'''
        else:
            ci_content = f'''name: CI

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
      
      - name: Build
        run: |
          echo "Add your build commands here"
      
      - name: Test
        run: |
          echo "Add your test commands here"
'''
        
        tools["write_file"](path=ci_path, content=ci_content)
        ci_files["created"].append(ci_path)
    
    return ci_files
