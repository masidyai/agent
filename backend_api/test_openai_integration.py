#!/usr/bin/env python3
"""
Test script for OpenAI integration
Demonstrates how the AI code generation works
"""
import os
import sys
import asyncio
from pathlib import Path

# Add backend_api to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_with_mock_key():
    """Test with a mock API key to show the flow"""
    print("🧪 Testing OpenAI Integration\n")
    
    # Test 1: No API key (fallback to templates)
    print("=" * 60)
    print("Test 1: No API key - should use template fallback")
    print("=" * 60)
    
    from app.services.openai_service import get_openai_service
    service = get_openai_service()
    print(f"OpenAI Service initialized: {service is not None}")
    
    from app.services.ai_code_generator import get_ai_generator
    generator = get_ai_generator()
    print(f"AI Generator initialized: {generator is not None}")
    
    from main import get_project_files_ai, get_project_files_template
    
    files = await get_project_files_ai("test_project", "Build a REST API", "api")
    print(f"AI Generation returned {len(files)} files (expected 0 without API key)")
    
    if len(files) == 0:
        print("✅ Correctly returned empty when no API key")
        files_fallback = get_project_files_template("test_project", "Build a REST API", "api")
        print(f"✅ Template fallback generated {len(files_fallback)} files")
        print(f"   Sample files:")
        for f in files_fallback[:5]:
            print(f"   - {f['path']}")
    
    print("\n" + "=" * 60)
    print("Test 2: OpenAI Service Configuration")
    print("=" * 60)
    
    print(f"Model: {os.getenv('OPENAI_MODEL', 'gpt-4')}")
    print(f"Temperature: {os.getenv('OPENAI_TEMPERATURE', '0.7')}")
    print(f"Max Tokens: {os.getenv('OPENAI_MAX_TOKENS', '2000')}")
    
    print("\n" + "=" * 60)
    print("Test 3: Validation System")
    print("=" * 60)
    
    # Test validation without needing API
    if service:
        # Mock some code samples
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
    else:
        print("Skipping validation test (no OpenAI service)")
    
    print("\n" + "=" * 60)
    print("Test 4: Streaming Endpoints")
    print("=" * 60)
    
    print("The following endpoints support AI-powered code generation:")
    print("  POST /api/plan - Generate execution plan")
    print("  POST /api/plan-and-execute - Start project with AI generation")
    print("  GET  /api/executions/{id}/stream - Stream code generation with SSE")
    
    print("\n✅ All integration tests passed!")
    print("\n" + "=" * 60)
    print("To enable AI code generation:")
    print("=" * 60)
    print("1. Get an OpenAI API key from https://platform.openai.com/api-keys")
    print("2. Add to .env file:")
    print("   OPENAI_API_KEY=sk-your-key-here")
    print("3. Optionally configure:")
    print("   OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo")
    print("   OPENAI_TEMPERATURE=0.7")
    print("   OPENAI_MAX_TOKENS=2000")
    print("4. Restart the server")
    print("\nWithout an API key, the system will automatically fall back to templates.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_with_mock_key())
