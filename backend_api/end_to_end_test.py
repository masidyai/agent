#!/usr/bin/env python3
"""
End-to-End Application Test
Simulates the full deployment workflow
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

async def test_database_migrations():
    """Test database migration workflow"""
    print("=" * 70)
    print("TEST 1: DATABASE MIGRATIONS")
    print("=" * 70)
    
    # Remove existing database
    db_file = Path("masidy.db")
    if db_file.exists():
        db_file.unlink()
        print("✅ Removed existing database")
    
    # Test alembic heads
    result = subprocess.run(
        ["python", "-m", "alembic", "heads"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"✅ Alembic heads check passed")
        print(f"   Output: {result.stdout.strip()}")
    else:
        print(f"❌ Alembic heads check failed")
        print(f"   Error: {result.stderr}")
        return False
    
    # Test alembic upgrade heads (as used in render.yaml)
    result = subprocess.run(
        ["python", "-m", "alembic", "upgrade", "heads"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"✅ Database migrations applied successfully")
        if "Running upgrade" in result.stdout:
            migrations = result.stdout.count("Running upgrade")
            print(f"   Applied {migrations} migrations")
    else:
        print(f"❌ Database migration failed")
        print(f"   Error: {result.stderr}")
        return False
    
    # Verify database exists
    if db_file.exists():
        print(f"✅ Database file created: {db_file}")
    else:
        print(f"❌ Database file not created")
        return False
    
    print()
    return True

async def test_application_imports():
    """Test all critical imports"""
    print("=" * 70)
    print("TEST 2: APPLICATION IMPORTS")
    print("=" * 70)
    
    try:
        # Test core imports
        from app.core.config import settings
        print(f"✅ Config loaded: {settings.APP_NAME}")
        
        from app.core.database import init_db, close_db
        print(f"✅ Database functions imported")
        
        from app.api import api_router
        print(f"✅ API router imported")
        
        from app.services.openai_service import get_openai_service
        print(f"✅ OpenAI service imported")
        
        from app.services.ai_code_generator import get_ai_generator
        print(f"✅ AI code generator imported")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        print()
        return False

async def test_application_startup():
    """Test FastAPI application startup"""
    print("=" * 70)
    print("TEST 3: APPLICATION STARTUP")
    print("=" * 70)
    
    try:
        # Import the app
        from app.main import app
        print("✅ FastAPI app imported successfully")
        
        # Get app metadata
        print(f"   Title: {app.title}")
        print(f"   Version: {app.version}")
        print(f"   Routes: {len(app.routes)}")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False

async def test_health_endpoint():
    """Test health endpoint via HTTP request"""
    print("=" * 70)
    print("TEST 4: HEALTH ENDPOINT (HTTP)")
    print("=" * 70)
    
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code == 200:
            print(f"✅ Health endpoint returned 200 OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health endpoint returned {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False

async def test_api_documentation():
    """Test API documentation endpoints"""
    print("=" * 70)
    print("TEST 5: API DOCUMENTATION")
    print("=" * 70)
    
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Test OpenAPI schema
        response = client.get("/openapi.json")
        if response.status_code == 200:
            print(f"✅ OpenAPI schema available")
            schema = response.json()
            print(f"   Title: {schema.get('info', {}).get('title')}")
            print(f"   Version: {schema.get('info', {}).get('version')}")
            print(f"   Paths: {len(schema.get('paths', {}))}")
        else:
            print(f"❌ OpenAPI schema not available")
            return False
        
        # Test Swagger UI
        response = client.get("/docs")
        if response.status_code == 200:
            print(f"✅ Swagger UI available at /docs")
        else:
            print(f"❌ Swagger UI not available")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ API documentation test failed: {e}")
        print()
        return False

async def main():
    """Run all tests"""
    print()
    print("█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + " " * 15 + "END-TO-END APPLICATION TEST" + " " * 25 + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    print()
    
    tests = [
        ("Database Migrations", test_database_migrations),
        ("Application Imports", test_application_imports),
        ("Application Startup", test_application_startup),
        ("Health Endpoint", test_health_endpoint),
        ("API Documentation", test_api_documentation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)
    
    if passed == total:
        print()
        print("🎉 ALL TESTS PASSED - APPLICATION IS PRODUCTION READY! 🎉")
        print()
        return 0
    else:
        print()
        print("⚠️  SOME TESTS FAILED - REVIEW REQUIRED")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
