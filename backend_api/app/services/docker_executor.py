"""
Docker-based code execution service
Provides isolated container execution with resource limits and timeout handling
"""
import asyncio
import logging
import os
from typing import Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

try:
    import docker
    from docker.errors import DockerException, ContainerError, ImageNotFound, APIError
    from docker.models.containers import Container
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    docker = None

logger = logging.getLogger(__name__)

# Constants
MAX_LINT_WARNINGS = 10  # Maximum number of lint warnings to store
DEFAULT_TEST_COVERAGE = 0.0  # Default coverage when not available


class ExecutionPhase(str, Enum):
    """Execution pipeline phases"""
    VALIDATION = "validation"
    BUILD = "build"
    LINT = "lint"
    TEST = "test"
    EXECUTION = "execution"
    CLEANUP = "cleanup"


class ExecutionStatus(str, Enum):
    """Execution status states"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class DockerExecutionConfig:
    """Configuration for Docker-based execution"""
    # Resource limits
    timeout_seconds: int = 300  # 5 minutes default
    max_memory_mb: int = 512
    max_cpu_cores: float = 1.0
    
    # Docker settings
    docker_image: Optional[str] = None  # Auto-detect based on language
    keep_container: bool = False  # Debug mode
    network_disabled: bool = False  # Disable network for security
    
    # Environment
    env_vars: Dict[str, str] = field(default_factory=dict)
    working_dir: str = "/workspace"
    
    # Language-specific
    language: str = "python"  # python, javascript, docker-compose
    
    @property
    def memory_limit(self) -> str:
        """Get memory limit in Docker format"""
        return f"{self.max_memory_mb}m"
    
    @property
    def nano_cpus(self) -> int:
        """Get CPU limit in Docker format (1 CPU = 1e9 nano CPUs)"""
        return int(self.max_cpu_cores * 1e9)


@dataclass
class DockerExecutionResult:
    """Result of a Docker execution"""
    status: ExecutionStatus
    output: str = ""
    error: str = ""
    exit_code: int = -1
    duration_ms: int = 0
    memory_used_mb: Optional[int] = None
    container_id: Optional[str] = None
    
    # Phase-specific results
    build_output: str = ""
    build_error: str = ""
    lint_output: str = ""
    lint_issues: Dict[str, Any] = field(default_factory=dict)
    test_output: str = ""
    tests_passed: int = 0
    tests_failed: int = 0
    test_coverage: float = 0.0
    
    # Timestamps
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class DockerExecutor:
    """
    Docker-based code execution engine.
    Executes code in isolated containers with resource limits and timeout handling.
    """
    
    # Base images for different languages
    BASE_IMAGES = {
        "python": "python:3.11-slim",
        "javascript": "node:20-alpine",
        "node": "node:20-alpine",
        "typescript": "node:20-alpine",
        "docker-compose": "docker/compose:latest",
    }
    
    def __init__(self):
        if not DOCKER_AVAILABLE:
            raise RuntimeError(
                "Docker SDK not available. Install with: pip install docker"
            )
        
        try:
            self.client = docker.from_env()
            # Test Docker connection
            self.client.ping()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise RuntimeError(
                f"Cannot connect to Docker daemon: {e}. "
                "Make sure Docker is installed and running."
            )
        
        self.active_containers: Dict[str, Container] = {}
        self._lock = asyncio.Lock()
    
    def _get_image_for_language(self, language: str) -> str:
        """Get the Docker image for a given language"""
        return self.BASE_IMAGES.get(language.lower(), self.BASE_IMAGES["python"])
    
    async def _ensure_image(self, image: str) -> bool:
        """Ensure Docker image is available, pull if needed"""
        try:
            self.client.images.get(image)
            logger.debug(f"Image {image} already exists")
            return True
        except ImageNotFound:
            logger.info(f"Pulling image {image}...")
            try:
                # Run in executor to avoid blocking
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, 
                    lambda: self.client.images.pull(image)
                )
                logger.info(f"Successfully pulled image {image}")
                return True
            except Exception as e:
                logger.error(f"Failed to pull image {image}: {e}")
                return False
    
    async def execute_pipeline(
        self,
        project_path: str,
        config: DockerExecutionConfig,
        stream_callback: Optional[callable] = None,
    ) -> DockerExecutionResult:
        """
        Execute a complete pipeline: build, lint, test, run
        
        Args:
            project_path: Path to the project directory on host
            config: Execution configuration
            stream_callback: Optional callback for streaming output
        
        Returns:
            DockerExecutionResult with all phase results
        """
        result = DockerExecutionResult(
            status=ExecutionStatus.PENDING,
            started_at=datetime.utcnow()
        )
        
        # Determine image
        image = config.docker_image or self._get_image_for_language(config.language)
        
        # Ensure image exists
        if not await self._ensure_image(image):
            result.status = ExecutionStatus.FAILED
            result.error = f"Failed to pull Docker image: {image}"
            result.completed_at = datetime.utcnow()
            return result
        
        # Check if project path exists
        if not os.path.exists(project_path):
            result.status = ExecutionStatus.FAILED
            result.error = f"Project path does not exist: {project_path}"
            result.completed_at = datetime.utcnow()
            return result
        
        container = None
        try:
            result.status = ExecutionStatus.RUNNING
            
            # Phase 1: Validation
            if stream_callback:
                await stream_callback("validation", "Validating project structure...")
            validation_result = await self._validate_project(project_path, config.language)
            if validation_result.get("errors"):
                result.status = ExecutionStatus.FAILED
                result.error = "Validation failed: " + "; ".join(validation_result["errors"])
                result.completed_at = datetime.utcnow()
                return result
            
            # Phase 2: Build (install dependencies)
            if stream_callback:
                await stream_callback("build", "Installing dependencies...")
            build_result = await self._run_build_phase(
                project_path, image, config, stream_callback
            )
            result.build_output = build_result.get("output", "")
            result.build_error = build_result.get("error", "")
            
            if build_result.get("status") != "success":
                result.status = ExecutionStatus.FAILED
                result.error = "Build failed"
                result.completed_at = datetime.utcnow()
                return result
            
            # Phase 3: Lint (code quality checks)
            if stream_callback:
                await stream_callback("lint", "Running code quality checks...")
            lint_result = await self._run_lint_phase(
                project_path, image, config, stream_callback
            )
            result.lint_output = lint_result.get("output", "")
            result.lint_issues = lint_result.get("issues", {})
            
            # Phase 4: Test
            if stream_callback:
                await stream_callback("test", "Running tests...")
            test_result = await self._run_test_phase(
                project_path, image, config, stream_callback
            )
            result.test_output = test_result.get("output", "")
            result.tests_passed = test_result.get("passed", 0)
            result.tests_failed = test_result.get("failed", 0)
            result.test_coverage = test_result.get("coverage", 0.0)
            
            # Phase 5: Execute
            if stream_callback:
                await stream_callback("execution", "Starting application...")
            exec_result = await self._run_execution_phase(
                project_path, image, config, stream_callback
            )
            result.output = exec_result.get("output", "")
            result.error = exec_result.get("error", "")
            result.exit_code = exec_result.get("exit_code", 0)
            result.container_id = exec_result.get("container_id")
            
            if exec_result.get("status") == "success":
                result.status = ExecutionStatus.SUCCESS
            elif exec_result.get("status") == "timeout":
                result.status = ExecutionStatus.TIMEOUT
            else:
                result.status = ExecutionStatus.FAILED
            
        except asyncio.TimeoutError:
            result.status = ExecutionStatus.TIMEOUT
            result.error = f"Execution timed out after {config.timeout_seconds}s"
            logger.warning(f"Execution timed out")
            
        except Exception as e:
            result.status = ExecutionStatus.FAILED
            result.error = str(e)
            logger.error(f"Execution failed: {e}", exc_info=True)
            
        finally:
            # Phase 6: Cleanup
            if container and not config.keep_container:
                try:
                    if stream_callback:
                        await stream_callback("cleanup", "Cleaning up container...")
                    await self._cleanup_container(container)
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
            
            result.completed_at = datetime.utcnow()
            if result.started_at:
                duration = result.completed_at - result.started_at
                result.duration_ms = int(duration.total_seconds() * 1000)
        
        return result
    
    async def _validate_project(
        self, 
        project_path: str, 
        language: str
    ) -> Dict[str, Any]:
        """Validate project structure and syntax"""
        errors = []
        
        if language in ["python"]:
            # Check for Python files
            py_files = [f for f in os.listdir(project_path) if f.endswith('.py')]
            if not py_files:
                errors.append("No Python files found in project")
            
            # Check for requirements.txt or main.py
            has_requirements = os.path.exists(os.path.join(project_path, "requirements.txt"))
            has_main = os.path.exists(os.path.join(project_path, "main.py"))
            
            if not (has_requirements or has_main):
                logger.warning("No requirements.txt or main.py found")
        
        elif language in ["javascript", "node", "typescript"]:
            # Check for package.json
            package_json = os.path.join(project_path, "package.json")
            if not os.path.exists(package_json):
                errors.append("No package.json found in project")
        
        return {"errors": errors, "warnings": []}
    
    async def _run_build_phase(
        self,
        project_path: str,
        image: str,
        config: DockerExecutionConfig,
        stream_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Run the build phase (install dependencies)"""
        if config.language in ["python"]:
            cmd = "pip install -r requirements.txt 2>&1 || echo 'No requirements.txt'"
        elif config.language in ["javascript", "node", "typescript"]:
            cmd = "npm install 2>&1"
        else:
            return {"status": "skipped", "output": "No build phase for this language"}
        
        return await self._run_in_container(
            project_path, image, cmd, config, timeout=120
        )
    
    async def _run_lint_phase(
        self,
        project_path: str,
        image: str,
        config: DockerExecutionConfig,
        stream_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Run the lint phase (code quality checks)"""
        if config.language in ["python"]:
            # Try flake8 or pylint if available
            cmd = "python -m flake8 . 2>&1 || echo 'No linter configured'"
        elif config.language in ["javascript", "node", "typescript"]:
            cmd = "npm run lint 2>&1 || echo 'No lint script configured'"
        else:
            return {"status": "skipped", "output": "No lint phase for this language"}
        
        result = await self._run_in_container(
            project_path, image, cmd, config, timeout=60
        )
        
        # Parse lint issues
        issues = {}
        if result.get("exit_code") != 0:
            issues["warnings"] = result.get("output", "").split("\n")[:MAX_LINT_WARNINGS]
        
        result["issues"] = issues
        return result
    
    async def _run_test_phase(
        self,
        project_path: str,
        image: str,
        config: DockerExecutionConfig,
        stream_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Run the test phase"""
        if config.language in ["python"]:
            cmd = "python -m pytest -v --tb=short 2>&1 || echo 'No tests found'"
        elif config.language in ["javascript", "node", "typescript"]:
            cmd = "npm test 2>&1 || echo 'No test script configured'"
        else:
            return {"status": "skipped", "passed": 0, "failed": 0}
        
        result = await self._run_in_container(
            project_path, image, cmd, config, timeout=180
        )
        
        # Parse test results
        output = result.get("output", "")
        passed = output.count(" PASSED") if "PASSED" in output else 0
        failed = output.count(" FAILED") if "FAILED" in output else 0
        
        result["passed"] = passed
        result["failed"] = failed
        # TODO: Parse coverage from output (pytest --cov or istanbul)
        # For now, return default coverage
        result["coverage"] = DEFAULT_TEST_COVERAGE
        
        return result
    
    async def _run_execution_phase(
        self,
        project_path: str,
        image: str,
        config: DockerExecutionConfig,
        stream_callback: Optional[callable] = None,
    ) -> Dict[str, Any]:
        """Run the execution phase (start application)"""
        if config.language in ["python"]:
            cmd = "python main.py 2>&1"
        elif config.language in ["javascript", "node"]:
            cmd = "npm start 2>&1 || node index.js 2>&1"
        else:
            cmd = "echo 'No execution command for this language'"
        
        return await self._run_in_container(
            project_path, image, cmd, config, timeout=config.timeout_seconds
        )
    
    async def _run_in_container(
        self,
        project_path: str,
        image: str,
        command: str,
        config: DockerExecutionConfig,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """Run a command in a Docker container"""
        container = None
        try:
            # Create container
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                None,
                lambda: self.client.containers.run(
                    image,
                    command=f"sh -c '{command}'",
                    detach=True,
                    volumes={project_path: {"bind": config.working_dir, "mode": "rw"}},
                    working_dir=config.working_dir,
                    mem_limit=config.memory_limit,
                    nano_cpus=config.nano_cpus,
                    network_disabled=config.network_disabled,
                    environment=config.env_vars,
                    remove=False,
                )
            )
            
            # Store container reference
            async with self._lock:
                self.active_containers[container.id] = container
            
            # Wait for container with timeout
            try:
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, container.wait),
                    timeout=timeout + 5  # Extra buffer
                )
                
                # Get logs
                logs = await loop.run_in_executor(None, container.logs)
                output = logs.decode('utf-8', errors='replace')
                
                return {
                    "status": "success" if result.get("StatusCode") == 0 else "failed",
                    "output": output,
                    "error": "",
                    "exit_code": result.get("StatusCode", -1),
                    "container_id": container.id,
                }
                
            except asyncio.TimeoutError:
                # Kill container on timeout
                await loop.run_in_executor(None, container.kill)
                return {
                    "status": "timeout",
                    "output": "",
                    "error": f"Command timed out after {timeout}s",
                    "exit_code": -1,
                    "container_id": container.id,
                }
            
        except Exception as e:
            logger.error(f"Container execution error: {e}")
            return {
                "status": "failed",
                "output": "",
                "error": str(e),
                "exit_code": -1,
            }
        
        finally:
            if container and not config.keep_container:
                try:
                    await self._cleanup_container(container)
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
    
    async def _cleanup_container(self, container: Container):
        """Clean up a Docker container"""
        try:
            loop = asyncio.get_event_loop()
            
            # Remove from active containers
            async with self._lock:
                if container.id in self.active_containers:
                    del self.active_containers[container.id]
            
            # Stop and remove container
            try:
                await loop.run_in_executor(None, container.stop)
            except Exception:
                pass
            
            await loop.run_in_executor(None, container.remove)
            logger.debug(f"Container {container.id[:12]} cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up container {container.id[:12]}: {e}")
    
    async def stop_execution(self, container_id: str) -> bool:
        """Stop a running execution by container ID"""
        async with self._lock:
            container = self.active_containers.get(container_id)
            if not container:
                logger.warning(f"Container {container_id} not found in active containers")
                return False
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, container.kill)
            await self._cleanup_container(container)
            return True
        except Exception as e:
            logger.error(f"Failed to stop container {container_id}: {e}")
            return False
    
    async def get_container_stats(self, container_id: str) -> Optional[Dict[str, Any]]:
        """Get resource usage stats for a container"""
        async with self._lock:
            container = self.active_containers.get(container_id)
            if not container:
                return None
        
        try:
            loop = asyncio.get_event_loop()
            stats = await loop.run_in_executor(
                None, lambda: container.stats(stream=False)
            )
            
            # Calculate CPU and memory usage
            memory_usage = stats.get("memory_stats", {}).get("usage", 0)
            memory_limit = stats.get("memory_stats", {}).get("limit", 1)
            memory_mb = memory_usage // (1024 * 1024)
            
            return {
                "memory_used_mb": memory_mb,
                "memory_percent": (memory_usage / memory_limit * 100) if memory_limit > 0 else 0,
            }
        except Exception as e:
            logger.error(f"Failed to get container stats: {e}")
            return None


# Global Docker executor instance
docker_executor = DockerExecutor() if DOCKER_AVAILABLE else None
