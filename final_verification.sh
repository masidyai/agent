#!/bin/bash

echo "🎯 Final Verification of OpenAI Integration"
echo "=============================================="
echo ""

cd backend_api

echo "1. Checking Python syntax..."
python -m py_compile app/services/openai_service.py app/services/ai_code_generator.py main.py
if [ $? -eq 0 ]; then
    echo "   ✅ All Python files compile successfully"
else
    echo "   ❌ Syntax errors found"
    exit 1
fi

echo ""
echo "2. Verifying imports..."
python -c "from app.services.openai_service import get_openai_service; from app.services.ai_code_generator import get_ai_generator; print('   ✅ All imports successful')"

echo ""
echo "3. Checking FastAPI app..."
python -c "from main import app; print(f'   ✅ FastAPI app loaded: {app.title} v{app.version}')"

echo ""
echo "4. Running integration tests..."
python test_openai_integration.py > /tmp/test_output.txt 2>&1
if grep -q "All integration tests passed" /tmp/test_output.txt; then
    echo "   ✅ Integration tests passed"
else
    echo "   ❌ Integration tests failed"
    cat /tmp/test_output.txt
    exit 1
fi

echo ""
echo "5. Verifying file structure..."
for file in \
    "app/services/openai_service.py" \
    "app/services/ai_code_generator.py" \
    "OPENAI_INTEGRATION.md" \
    "test_openai_integration.py" \
    ".env.example"
do
    if [ -f "$file" ]; then
        echo "   ✅ $file exists"
    else
        echo "   ❌ $file missing"
        exit 1
    fi
done

echo ""
echo "6. Checking environment configuration..."
if grep -q "OPENAI_API_KEY" .env.example; then
    echo "   ✅ OPENAI_API_KEY in .env.example"
else
    echo "   ❌ OPENAI_API_KEY not in .env.example"
    exit 1
fi

if grep -q "OPENAI_MODEL" .env.example; then
    echo "   ✅ OPENAI_MODEL in .env.example"
else
    echo "   ❌ OPENAI_MODEL not in .env.example"
    exit 1
fi

echo ""
echo "7. Checking dependencies..."
if grep -q "openai>=1.0.0" requirements.txt; then
    echo "   ✅ openai>=1.0.0 in requirements.txt"
else
    echo "   ❌ openai dependency missing"
    exit 1
fi

echo ""
echo "8. Verifying documentation..."
if [ -f "OPENAI_INTEGRATION.md" ] && [ $(wc -l < OPENAI_INTEGRATION.md) -gt 100 ]; then
    echo "   ✅ Comprehensive documentation exists ($(wc -l < OPENAI_INTEGRATION.md) lines)"
else
    echo "   ❌ Documentation incomplete"
    exit 1
fi

echo ""
echo "=============================================="
echo "🎉 All Verifications Passed!"
echo "=============================================="
echo ""
echo "📝 Summary:"
echo "   • OpenAI integration implemented"
echo "   • All files created and verified"
echo "   • Tests passing"
echo "   • Documentation complete"
echo "   • Configuration ready"
echo ""
echo "🚀 Next Steps:"
echo "   1. Add OPENAI_API_KEY to .env file"
echo "   2. Start server: uvicorn main:app --reload"
echo "   3. Test API generation!"
echo ""
