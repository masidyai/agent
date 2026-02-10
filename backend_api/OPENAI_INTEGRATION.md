# OpenAI Integration Documentation

## Overview

The Masidy Agent platform now includes real AI-powered code generation using OpenAI's API. This replaces the previous hardcoded templates with intelligent, context-aware code generation tailored to each project's specific requirements.

## Features

### ✅ Implemented Features

1. **OpenAI Integration**
   - AsyncOpenAI client for non-blocking operations
   - Configurable model selection (GPT-4, GPT-3.5-turbo)
   - Adjustable temperature and max tokens
   - Environment-based configuration

2. **Specialized Prompting System**
   - Backend API generation prompts
   - Database model prompts
   - Authentication system prompts
   - Frontend component prompts
   - Docker/deployment prompts
   - Test generation prompts
   - Documentation prompts
   - CI/CD pipeline prompts

3. **Real Code Generation**
   - SaaS flow: Complete FastAPI backend with React/Next.js frontend
   - API flow: REST API with endpoints, models, and tests
   - Refactor flow: Modernization with Docker and CI/CD

4. **Streaming Support**
   - Server-Sent Events (SSE) for real-time updates
   - Token-by-token streaming (simulated chunking for now)
   - File-by-file progress updates
   - Live code preview as it's generated

5. **Error Handling & Validation**
   - Graceful API error handling
   - Clear error messages when API key is missing (no template fallback)
   - Code validation for completeness
   - Syntax checking (basic)
   - Rate limiting awareness

6. **Security**
   - API key stored in environment variables
   - No hardcoded credentials
   - Secure error messages (no key exposure)

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional (with defaults)
OPENAI_MODEL=gpt-4              # or gpt-3.5-turbo for faster/cheaper
OPENAI_TEMPERATURE=0.7          # 0.0-1.0, higher = more creative
OPENAI_MAX_TOKENS=2000          # max tokens per file generation
```

### Getting an API Key

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Copy it to your `.env` file
4. Restart the server

## Architecture

### Module Structure

```
backend_api/
├── app/
│   └── services/
│       ├── openai_service.py      # OpenAI client & prompting
│       └── ai_code_generator.py   # AI-powered file generation
└── main.py                        # Updated endpoints
```

### Key Components

#### 1. OpenAI Service (`app/services/openai_service.py`)

Handles all OpenAI API interactions:

```python
from app.services.openai_service import get_openai_service

service = get_openai_service()

# Generate code
code = await service.generate_code(
    prompt="Create a FastAPI user model",
    file_type="models",
    context={"project_name": "my_api"}
)

# Streaming generation
async for token in service.generate_code_streaming(
    prompt="Create auth endpoints",
    file_type="api_endpoints"
):
    print(token, end='')

# Validate code
result = service.validate_code(code, "python")
if result["valid"]:
    print("Code is valid!")
else:
    print("Issues:", result["issues"])
```

#### 2. AI Code Generator (`app/services/ai_code_generator.py`)

Orchestrates file generation for complete projects:

```python
from app.services.ai_code_generator import get_ai_generator

generator = get_ai_generator()

# Generate SaaS project files
files = await generator.generate_saas_files(
    project_name="my_saas",
    task_desc="Build a task management app"
)

# Generate API project files
files = await generator.generate_api_files(
    project_name="my_api",
    task_desc="REST API for blog posts"
)

# Generate refactor files
files = await generator.generate_refactor_files(
    project_name="legacy_app",
    task_desc="Modernize deployment"
)
```

#### 3. Updated Main Endpoints (`main.py`)

All code generation endpoints now use AI:

- `POST /api/plan` - Generate execution plan with AI
- `POST /api/plan-and-execute` - Create and execute project
- `GET /api/executions/{id}/stream` - Stream AI code generation via SSE

### API Key Requirement

**IMPORTANT**: OpenAI API key is REQUIRED for code generation. There is NO template or demo fallback:

```python
async def get_project_files_ai(project_name, task_desc, flow):
    """Generate files using AI - requires OpenAI API key"""
    openai_service = get_openai_service()
    
    if openai_service is None:
        raise ValueError(
            "OpenAI API key is required for project generation. "
            "Please set the OPENAI_API_KEY environment variable."
        )
    
    # Generate using real AI
    return await ai_generator.generate_files(...)
```

## Usage Examples

### Example 1: Basic Code Generation

```bash
curl -X POST http://localhost:8000/api/plan-and-execute \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Build a blog API with posts and comments",
    "flow": "api"
  }'
```

Response:
```json
{
  "project_id": "abc123",
  "execution_id": "xyz789",
  "name": "blog_api_posts_comments",
  "steps_total": 17
}
```

### Example 2: Streaming Execution

```bash
curl http://localhost:8000/api/executions/xyz789/stream
```

Server-Sent Events stream:
```
data: {"type":"thinking","message":"Initializing AI code generation..."}

data: {"type":"planning","message":"AI is analyzing your requirements..."}

data: {"type":"step_start","step":1,"total":17,"description":"Generate README.md"}

data: {"type":"code_chunk","step":1,"chunk":"# Blog API\n\n> REST API"}

data: {"type":"step_complete","step":1,"file":"blog_api/README.md","content":"..."}

...

data: {"type":"complete","message":"Project created successfully with AI-generated code!"}
```

### Example 3: Different Flows

**SaaS Flow** (full-stack app):
```json
{
  "prompt": "Build a SaaS platform for team collaboration",
  "flow": "saas"
}
```
Generates: Backend API + Database + Auth + Frontend + Docker + CI/CD

**API Flow** (backend only):
```json
{
  "prompt": "Create REST API for e-commerce products",
  "flow": "api"
}
```
Generates: FastAPI + Models + Endpoints + Tests + Docker

**Refactor Flow** (modernization):
```json
{
  "prompt": "Modernize legacy Python app with Docker and CI/CD",
  "flow": "refactor"
}
```
Generates: Dockerfile + docker-compose + GitHub Actions + pre-commit hooks

## Specialized Prompts

The system uses specialized prompts for each file type:

| File Type | System Prompt Focus |
|-----------|-------------------|
| `backend_main` | FastAPI app, CORS, health checks, API docs |
| `database` | SQLAlchemy, async support, connection pooling |
| `auth` | JWT, bcrypt, OAuth2, security best practices |
| `models` | SQLAlchemy models, relationships, indexes |
| `api_endpoints` | REST endpoints, CRUD operations, validation |
| `schemas` | Pydantic models, validation, type hints |
| `docker` | Multi-stage builds, optimization, security |
| `tests` | pytest, test coverage, edge cases |
| `documentation` | Clear guides, examples, setup instructions |
| `cicd` | GitHub Actions, testing, deployment |
| `frontend` | React/Next.js, TypeScript, hooks |

## Code Validation

Generated code is validated for:

✅ Minimum length (not empty)  
✅ Balanced parentheses, brackets, braces  
✅ Presence of expected language constructs  
✅ Completeness (no trailing TODO/FIXME)  

Example validation result:
```python
{
  "valid": True,
  "issues": []
}
```

Or with issues:
```python
{
  "valid": False,
  "issues": [
    "Unmatched parentheses",
    "Code appears incomplete"
  ]
}
```

## Performance Considerations

### Cost Optimization

- **Model Selection**: Use `gpt-3.5-turbo` for faster/cheaper generation
- **Max Tokens**: Limit to 2000 tokens per file (configurable)
- **Batch Generation**: Files generated sequentially with small delays

### Rate Limiting

- Small delays (0.1s) between file generations
- Automatic error handling for rate limits
- Clear error messages if rate limited

### Caching

Future enhancement: Cache common patterns to reduce API calls

## Troubleshooting

### Issue: "Warning: OPENAI_API_KEY environment variable is required"

**Solution**: Add your API key to `.env` file

### Issue: API calls failing with authentication error

**Solutions**:
1. Verify API key is correct
2. Check API key has usage credits
3. Ensure no whitespace in API key

### Issue: Generated code is incomplete

**Solutions**:
1. Increase `OPENAI_MAX_TOKENS` (default: 2000)
2. Use `gpt-4` instead of `gpt-3.5-turbo`
3. Check validation warnings in logs

### Issue: Too expensive / slow

**Solutions**:
1. Switch to `gpt-3.5-turbo` (10x cheaper, faster)
2. Reduce `OPENAI_MAX_TOKENS`
3. Start with smaller projects to test

## Future Enhancements

### Planned Features

1. **True Token-by-Token Streaming**
   - Real-time streaming from OpenAI
   - Live code preview as it's typed

2. **Context-Aware Generation**
   - Analyze existing project files
   - Generate consistent code style
   - Cross-reference between files

3. **Intelligent Caching**
   - Cache common patterns
   - Reuse similar code blocks
   - Reduce API costs

4. **Multi-Model Support**
   - Anthropic Claude
   - Google Gemini
   - Local models (Ollama)

5. **Advanced Validation**
   - Syntax checking with AST parsing
   - Import resolution
   - Type checking
   - Security scanning

6. **User Feedback Loop**
   - Rate generated code
   - Provide corrections
   - Improve prompts over time

## Testing

Run the integration test:

```bash
cd backend_api
python test_openai_integration.py
```

Expected output (with API key):
```
🧪 Testing OpenAI Integration

============================================================
Test 1: OpenAI API Key Configuration
============================================================
✅ OpenAI Service initialized successfully
✅ AI Generator initialized: True

============================================================
Test 2: AI Code Generation
============================================================
✅ AI Generation returned 17 files

...

✅ All integration tests passed!
```

If API key is missing:
```
❌ OpenAI Service NOT initialized - API key is missing!
⚠️  NOTE: There is no demo/template fallback.
    All code generation requires a valid OpenAI API key.
```

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive config
3. **Rotate API keys** regularly
4. **Monitor usage** on OpenAI dashboard
5. **Set spending limits** to prevent unexpected costs
6. **Validate all generated code** before deployment

## Cost Estimation

Approximate costs per project (using GPT-4):

- **SaaS Project** (~17 files): $0.50 - $1.00
- **API Project** (~17 files): $0.50 - $1.00
- **Refactor Project** (~5 files): $0.15 - $0.30

Using GPT-3.5-turbo reduces costs by ~90%.

## Support

For issues or questions:
1. Check logs in console output
2. Run test_openai_integration.py
3. Review validation errors
4. Check OpenAI API status

## License

This OpenAI integration is part of the Masidy Agent platform.
