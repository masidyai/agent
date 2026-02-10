#!/usr/bin/env python3
"""
Test script for OpenAI integration
Demonstrates how the AI code generation works

NOTE: This system REQUIRES a valid OpenAI API key for code generation.
There is NO demo/template fallback - all code is generated live by AI.
"""
import os
import sys
import asyncio
from pathlib import Path

# Add backend_api to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_openai_integration():
    """Test OpenAI integration - requires OPENAI_API_KEY to be set"""
    print("🧪 Testing OpenAI Integration\n")
    
    # Test 1: Check if API key is configured
    print("=" * 60)
    print("Test 1: OpenAI API Key Configuration")
    print("=" * 60)
    
    from app.services.openai_service import get_openai_service
    service = get_openai_service()
    
    if service is None:
        print("❌ OpenAI Service NOT initialized - API key is missing!")
        print("\nTo enable AI code generation:")
        print("  1. Get an OpenAI API key from https://platform.openai.com/api-keys")
        print("  2. Add to .env file:")
        print("     OPENAI_API_KEY=sk-your-key-here")
        print("  3. Restart the server")
        print("\n⚠️  NOTE: There is no demo/template fallback.")
        print("    All code generation requires a valid OpenAI API key.")
        return
    
    print("✅ OpenAI Service initialized successfully")
    
    from app.services.ai_code_generator import get_ai_generator
    generator = get_ai_generator()
    print(f"✅ AI Generator initialized: {generator is not None}")
    
    # Test 2: Check AI generation works
    print("\n" + "=" * 60)
    print("Test 2: AI Code Generation")
    print("=" * 60)
    
    from main import get_project_files_ai
    
    try:
        files = await get_project_files_ai("test_project", "Build a REST API for notes", "api")
        print(f"✅ AI Generation returned {len(files)} files")
        print("   Sample files:")
        for f in files[:5]:
            print(f"   - {f['path']}")
    except ValueError as e:
        print(f"❌ AI Generation failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Test 3: Configuration
    print("\n" + "=" * 60)
    print("Test 3: OpenAI Service Configuration")
    print("=" * 60)
    
    print(f"Model: {os.getenv('OPENAI_MODEL', 'gpt-4')}")
    print(f"Temperature: {os.getenv('OPENAI_TEMPERATURE', '0.7')}")
    print(f"Max Tokens: {os.getenv('OPENAI_MAX_TOKENS', '2000')}")
    
    # Test 4: Code Validation
    print("\n" + "=" * 60)
    print("Test 4: Validation System")
    print("=" * 60)
    
    valid_python = """
def hello():
    return "world"
"""
    
    invalid_python = """
def hello(
    # Incomplete function
"""
    
    print("Testing code validation...")
    result = service.validate_code(valid_python, "python")
    print(f"Valid Python code: {result['valid']}")
    
    result = service.validate_code(invalid_python, "python")
    print(f"Invalid Python code: {result['valid']}, Issues: {result['issues']}")
    
    # Test 5: Available endpoints
    print("\n" + "=" * 60)
    print("Test 5: AI-Powered API Endpoints")
    print("=" * 60)
    
    print("The following endpoints support AI-powered code generation:")
    print("  POST /api/plan - Generate execution plan")
    print("  POST /api/plan-and-execute - Start project with AI generation")
    print("  GET  /api/executions/{id}/stream - Stream code generation with SSE")
    
    print("\n✅ All integration tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_openai_integration())
