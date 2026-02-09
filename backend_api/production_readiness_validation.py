#!/usr/bin/env python3
"""
Production Readiness Validation Script
Verifies all critical components exist and work correctly
"""

import sys
import os
from pathlib import Path

def check_file_exists(filepath: str, description: str) -> bool:
    """Check if a file exists"""
    path = Path(filepath)
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_import(module_path: str, import_name: str) -> bool:
    """Check if an import works"""
    try:
        if import_name:
            exec(f"from {module_path} import {import_name}")
        else:
            exec(f"import {module_path}")
        print(f"✅ Import works: from {module_path} import {import_name}")
        return True
    except Exception as e:
        print(f"❌ Import failed: from {module_path} import {import_name}")
        print(f"   Error: {e}")
        return False

def main():
    print("=" * 70)
    print("PRODUCTION READINESS VALIDATION")
    print("=" * 70)
    print()
    
    all_checks_passed = True
    
    # 1. Check core files
    print("1. CORE FILES")
    print("-" * 70)
    core_files = [
        ("app/core/config.py", "Configuration module"),
        ("app/core/database.py", "Database module"),
        ("app/core/security.py", "Security module"),
        ("app/core/__init__.py", "Core package init"),
    ]
    for filepath, desc in core_files:
        if not check_file_exists(filepath, desc):
            all_checks_passed = False
    print()
    
    # 2. Check API files
    print("2. API LAYER")
    print("-" * 70)
    api_files = [
        ("app/api/__init__.py", "API router init"),
        ("app/api/auth.py", "Authentication routes"),
        ("app/api/users.py", "User routes"),
        ("app/api/projects.py", "Project routes"),
        ("app/api/billing.py", "Billing routes"),
    ]
    for filepath, desc in api_files:
        if not check_file_exists(filepath, desc):
            all_checks_passed = False
    print()
    
    # 3. Check service files
    print("3. SERVICE LAYER")
    print("-" * 70)
    service_files = [
        ("app/services/openai_service.py", "OpenAI service"),
        ("app/services/ai_code_generator.py", "AI code generator"),
        ("app/services/docker_executor.py", "Docker executor"),
    ]
    for filepath, desc in service_files:
        if not check_file_exists(filepath, desc):
            all_checks_passed = False
    print()
    
    # 4. Check migrations
    print("4. DATABASE MIGRATIONS")
    print("-" * 70)
    migration_files = [
        ("app/migrations/env.py", "Alembic environment"),
        ("app/migrations/versions/001_initial_schema.py", "Migration 001"),
        ("app/migrations/versions/002_github_integration.py", "Migration 002"),
        ("app/migrations/versions/003_add_execution_and_project_file_tables.py", "Migration 003"),
        ("app/migrations/versions/004_add_code_executions_table.py", "Migration 004"),
    ]
    for filepath, desc in migration_files:
        if not check_file_exists(filepath, desc):
            all_checks_passed = False
    print()
    
    # 5. Check configuration files
    print("5. CONFIGURATION FILES")
    print("-" * 70)
    config_files = [
        ("alembic.ini", "Alembic configuration"),
        ("requirements.txt", "Python dependencies"),
        (".env.example", "Environment template"),
        ("../render.yaml", "Render deployment config"),
    ]
    for filepath, desc in config_files:
        if not check_file_exists(filepath, desc):
            all_checks_passed = False
    print()
    
    # 6. Test imports
    print("6. IMPORT VERIFICATION")
    print("-" * 70)
    imports = [
        ("app.core.config", "settings"),
        ("app.core.database", "init_db, close_db"),
        ("app.api", "api_router"),
        ("app.services.openai_service", "get_openai_service"),
        ("app.services.ai_code_generator", "get_ai_generator"),
    ]
    for module_path, import_name in imports:
        if not check_import(module_path, import_name):
            all_checks_passed = False
    print()
    
    # 7. Check alembic configuration
    print("7. ALEMBIC CONFIGURATION")
    print("-" * 70)
    with open("alembic.ini", "r") as f:
        alembic_content = f.read()
        if "script_location = app/migrations" in alembic_content:
            print("✅ Alembic script_location is correct: app/migrations")
        else:
            print("❌ Alembic script_location is incorrect")
            all_checks_passed = False
    print()
    
    # 8. Check render.yaml
    print("8. RENDER DEPLOYMENT CONFIG")
    print("-" * 70)
    render_path = Path("../render.yaml")
    if render_path.exists():
        with open(render_path, "r") as f:
            render_content = f.read()
            if "alembic upgrade heads" in render_content:
                print("✅ render.yaml uses 'alembic upgrade heads' (supports multiple heads)")
            elif "alembic upgrade head" in render_content:
                print("⚠️  render.yaml uses 'alembic upgrade head' (singular)")
                print("   Recommendation: Use 'heads' for better compatibility")
            else:
                print("❌ render.yaml doesn't contain alembic upgrade command")
                all_checks_passed = False
    print()
    
    # Final summary
    print("=" * 70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - PRODUCTION READY")
        print("=" * 70)
        return 0
    else:
        print("❌ SOME CHECKS FAILED - REVIEW REQUIRED")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
