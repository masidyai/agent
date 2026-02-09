"""
OpenAI Service - Real code generation using OpenAI API
"""
import os
import re
from typing import Dict, Any, Optional, AsyncGenerator
from openai import AsyncOpenAI, OpenAIError
import asyncio

class OpenAIService:
    """Service for generating code using OpenAI API"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
        
    async def generate_code_streaming(
        self,
        prompt: str,
        file_type: str = "general",
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate code using OpenAI streaming API.
        Yields tokens as they are generated.
        """
        try:
            full_prompt = self._build_prompt(prompt, file_type, context or {})
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(file_type)},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except OpenAIError as e:
            raise Exception(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Code generation error: {str(e)}")
    
    async def generate_code(
        self,
        prompt: str,
        file_type: str = "general",
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate code using OpenAI API (non-streaming).
        Returns complete code.
        """
        try:
            full_prompt = self._build_prompt(prompt, file_type, context or {})
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(file_type)},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            code = response.choices[0].message.content
            return self._extract_code_from_response(code)
            
        except OpenAIError as e:
            raise Exception(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Code generation error: {str(e)}")
    
    def _get_system_prompt(self, file_type: str) -> str:
        """Get specialized system prompt based on file type"""
        prompts = {
            "backend_main": """You are an expert FastAPI backend developer. Generate production-ready FastAPI applications with:
- Clean, well-structured code
- Proper error handling
- Security best practices
- CORS configuration
- API documentation
- Health check endpoints
Generate only the code, no explanations.""",

            "database": """You are a database architecture expert. Generate SQLAlchemy database configurations with:
- Async support when appropriate
- Proper connection pooling
- Environment-based configuration
- Session management
- Best practices for database setup
Generate only the code, no explanations.""",

            "auth": """You are a security expert. Generate authentication systems with:
- JWT token-based authentication
- Password hashing with bcrypt
- Secure token generation and validation
- OAuth2 password flow
- Proper error handling
Generate only the code, no explanations.""",

            "models": """You are a data modeling expert. Generate SQLAlchemy models with:
- Proper relationships
- Indexes for performance
- Timestamps
- Type hints
- Validation
Generate only the code, no explanations.""",

            "api_endpoints": """You are a REST API expert. Generate FastAPI endpoints with:
- Proper HTTP methods
- Request/response models
- Error handling
- Authentication dependencies
- CRUD operations
Generate only the code, no explanations.""",

            "schemas": """You are a Pydantic expert. Generate Pydantic schemas with:
- Proper validation
- Type hints
- Optional fields
- Config for ORM mode
- Clear naming
Generate only the code, no explanations.""",

            "docker": """You are a Docker expert. Generate Dockerfiles and docker-compose files with:
- Multi-stage builds when appropriate
- Security best practices
- Optimal layer caching
- Production-ready configuration
- Environment variables
Generate only the code, no explanations.""",

            "tests": """You are a testing expert. Generate pytest tests with:
- Test client setup
- Comprehensive test coverage
- Edge cases
- Async support when needed
- Clear test names
Generate only the code, no explanations.""",

            "documentation": """You are a technical writer. Generate clear documentation with:
- Quick start guides
- API documentation
- Setup instructions
- Technology stack description
- Example usage
Use markdown format.""",

            "cicd": """You are a DevOps expert. Generate GitHub Actions workflows with:
- Testing pipeline
- Build steps
- Deployment automation
- Proper job dependencies
- Best practices
Generate only the YAML code, no explanations.""",

            "frontend": """You are a React/Next.js expert. Generate modern frontend components with:
- TypeScript when appropriate
- Hooks for state management
- Clean component structure
- Proper props typing
- Responsive design considerations
Generate only the code, no explanations.""",

            "config": """You are a configuration expert. Generate configuration files with:
- Environment-based settings
- Security best practices
- Clear documentation
- Sensible defaults
- Type safety
Generate only the code, no explanations.""",

            "general": """You are an expert software engineer. Generate clean, production-ready code following best practices.
Generate only the code, no explanations."""
        }
        
        return prompts.get(file_type, prompts["general"])
    
    def _build_prompt(self, user_prompt: str, file_type: str, context: Dict[str, Any]) -> str:
        """Build the full prompt with context"""
        project_name = context.get("project_name", "my_project")
        flow = context.get("flow", "saas")
        task_desc = context.get("task_desc", user_prompt)
        file_path = context.get("file_path", "")
        
        # Add context to the prompt
        prompt_parts = []
        
        if flow:
            prompt_parts.append(f"Flow type: {flow}")
        
        prompt_parts.append(f"Project description: {task_desc}")
        
        if project_name:
            prompt_parts.append(f"Project name: {project_name}")
        
        if file_path:
            prompt_parts.append(f"File path: {file_path}")
        
        prompt_parts.append(f"\n{user_prompt}")
        
        # Add specific requirements based on file type
        if file_type == "backend_main":
            prompt_parts.append("\nInclude: FastAPI app setup, CORS middleware, routers, health check endpoint")
        elif file_type == "database":
            prompt_parts.append("\nInclude: SQLAlchemy setup, async session management, Base model")
        elif file_type == "auth":
            prompt_parts.append("\nInclude: JWT token creation/validation, password hashing, OAuth2 scheme")
        elif file_type == "models":
            prompt_parts.append("\nInclude: SQLAlchemy models with proper relationships, timestamps, indexes")
        elif file_type == "api_endpoints":
            prompt_parts.append("\nInclude: CRUD operations, authentication dependencies, proper error handling")
        elif file_type == "schemas":
            prompt_parts.append("\nInclude: Pydantic models for request/response, validation, ORM config")
        elif file_type == "docker":
            prompt_parts.append("\nInclude: production-ready setup, proper image optimization")
        elif file_type == "tests":
            prompt_parts.append("\nInclude: test client, test cases for main functionality")
        
        return "\n".join(prompt_parts)
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from markdown code blocks if present"""
        # Remove markdown code blocks
        code_block_pattern = r'```(?:\w+)?\n(.*?)```'
        matches = re.findall(code_block_pattern, response, re.DOTALL)
        
        if matches:
            # If there are code blocks, return the first one
            return matches[0].strip()
        
        # Otherwise return the whole response stripped
        return response.strip()
    
    def validate_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Validate generated code for basic completeness.
        Returns dict with 'valid' bool and 'issues' list.
        """
        issues = []
        
        if not code or len(code.strip()) < 10:
            issues.append("Code is too short or empty")
        
        if language == "python":
            # Check for basic Python syntax indicators
            if "def " not in code and "class " not in code and "import " not in code:
                issues.append("No Python functions, classes, or imports found")
            
            # Check for incomplete code
            if code.count("(") != code.count(")"):
                issues.append("Unmatched parentheses")
            
            if code.count("[") != code.count("]"):
                issues.append("Unmatched square brackets")
            
            if code.count("{") != code.count("}"):
                issues.append("Unmatched curly braces")
        
        elif language in ["javascript", "typescript", "jsx", "tsx"]:
            # Check for basic JS/TS syntax
            if "function " not in code and "const " not in code and "let " not in code and "=>" not in code:
                issues.append("No JavaScript functions or variable declarations found")
        
        # Check if code seems incomplete (ends abruptly)
        if code.rstrip().endswith(("...", "TODO", "FIXME")):
            issues.append("Code appears incomplete")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }


# Singleton instance
_openai_service: Optional[OpenAIService] = None

def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service singleton"""
    global _openai_service
    if _openai_service is None:
        try:
            _openai_service = OpenAIService()
        except ValueError as e:
            # If no API key, return None - will fallback to templates
            print(f"Warning: {e}. Will use template fallback.")
            return None
    return _openai_service
