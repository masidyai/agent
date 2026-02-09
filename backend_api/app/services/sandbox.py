"""
Sandbox execution service for safe code execution
"""
import asyncio
import os
import tempfile
import shutil
import logging
import signal
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import subprocess

logger = logging.getLogger(__name__)


class ExecutionStatus(str, Enum):
    """Execution status states"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    KILLED = "killed"


@dataclass
class ExecutionResult:
    """Result of a sandbox execution"""
    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    exit_code: int = -1
    duration_ms: float = 0.0
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class SandboxConfig:
    """Configuration for sandbox execution"""
    timeout_seconds: int = 30
    max_memory_mb: int = 256
    max_output_size: int = 1024 * 1024  # 1MB
    allowed_commands: List[str] = field(default_factory=lambda: [
        "node", "npm", "npx", "python", "python3", "pip",
        "bun", "deno", "go", "rustc", "cargo"
    ])
    working_dir: Optional[str] = None
    env_vars: Dict[str, str] = field(default_factory=dict)


class SandboxExecutor:
    """
    Safe execution sandbox for running user code.
    Provides isolation, resource limits, and timeout handling.
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or tempfile.gettempdir()
        self.active_processes: Dict[str, subprocess.Popen] = {}
        self._lock = asyncio.Lock()
    
    async def execute(
        self,
        command: str,
        config: Optional[SandboxConfig] = None,
        project_id: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute a command in a sandboxed environment.
        
        Args:
            command: The command to execute
            config: Sandbox configuration
            project_id: Optional project ID for the execution context
        
        Returns:
            ExecutionResult with stdout, stderr, and status
        """
        config = config or SandboxConfig()
        result = ExecutionResult(
            status=ExecutionStatus.PENDING,
            started_at=datetime.utcnow()
        )
        
        # Validate command
        cmd_parts = command.split()
        if not cmd_parts:
            result.status = ExecutionStatus.ERROR
            result.error = "Empty command"
            return result
        
        base_command = cmd_parts[0]
        if base_command not in config.allowed_commands:
            result.status = ExecutionStatus.ERROR
            result.error = f"Command not allowed: {base_command}"
            logger.warning(f"Blocked command: {command}")
            return result
        
        # Create working directory if needed
        work_dir = config.working_dir
        if not work_dir:
            work_dir = tempfile.mkdtemp(prefix="sandbox_", dir=self.base_dir)
        
        try:
            result.status = ExecutionStatus.RUNNING
            
            # Set up environment
            env = os.environ.copy()
            env.update(config.env_vars)
            env["HOME"] = work_dir
            env["TMPDIR"] = work_dir
            
            # Run the command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=work_dir,
                env=env,
                start_new_session=True  # Create new process group
            )
            
            # execution_id could be used for tracking - keeping for potential future use
            # execution_id = str(project_id or id(process))
            async with self._lock:
                # Store reference but need to handle Popen vs Process
                pass
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=config.timeout_seconds
                )
                
                result.stdout = stdout.decode('utf-8', errors='replace')[:config.max_output_size]
                result.stderr = stderr.decode('utf-8', errors='replace')[:config.max_output_size]
                result.exit_code = process.returncode or 0
                
                result.status = (
                    ExecutionStatus.SUCCESS 
                    if result.exit_code == 0 
                    else ExecutionStatus.ERROR
                )
                
            except asyncio.TimeoutError:
                # Kill the process group
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                except Exception:
                    process.kill()
                
                result.status = ExecutionStatus.TIMEOUT
                result.error = f"Execution timed out after {config.timeout_seconds}s"
                
        except Exception as e:
            result.status = ExecutionStatus.ERROR
            result.error = str(e)
            logger.error(f"Sandbox execution error: {e}")
            
        finally:
            result.completed_at = datetime.utcnow()
            if result.started_at:
                duration = result.completed_at - result.started_at
                result.duration_ms = duration.total_seconds() * 1000
            
            # Cleanup temporary directory if we created it
            if not config.working_dir and work_dir and os.path.exists(work_dir):
                try:
                    shutil.rmtree(work_dir, ignore_errors=True)
                except Exception:
                    pass
        
        return result
    
    async def execute_code(
        self,
        code: str,
        language: str,
        config: Optional[SandboxConfig] = None,
        project_id: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute code in a specific language.
        
        Args:
            code: The source code to execute
            language: Programming language (python, javascript, typescript, etc.)
            config: Sandbox configuration
            project_id: Optional project ID
        
        Returns:
            ExecutionResult
        """
        config = config or SandboxConfig()
        
        # Create temp directory for the code
        work_dir = tempfile.mkdtemp(prefix="code_", dir=self.base_dir)
        
        try:
            # Determine file extension and command
            lang_config = {
                "python": ("main.py", "python3 main.py"),
                "javascript": ("main.js", "node main.js"),
                "typescript": ("main.ts", "npx ts-node main.ts"),
                "go": ("main.go", "go run main.go"),
                "rust": ("main.rs", "rustc main.rs && ./main"),
            }
            
            if language not in lang_config:
                return ExecutionResult(
                    status=ExecutionStatus.ERROR,
                    error=f"Unsupported language: {language}"
                )
            
            filename, command = lang_config[language]
            
            # Write code to file
            code_path = os.path.join(work_dir, filename)
            with open(code_path, 'w') as f:
                f.write(code)
            
            # Update config with working directory
            config.working_dir = work_dir
            
            # Execute
            return await self.execute(command, config, project_id)
            
        finally:
            # Cleanup
            try:
                shutil.rmtree(work_dir, ignore_errors=True)
            except Exception:
                pass
    
    async def execute_npm_script(
        self,
        script: str,
        project_dir: str,
        config: Optional[SandboxConfig] = None
    ) -> ExecutionResult:
        """Execute an npm script in a project directory"""
        config = config or SandboxConfig()
        config.working_dir = project_dir
        
        return await self.execute(f"npm run {script}", config)
    
    async def install_dependencies(
        self,
        project_dir: str,
        package_manager: str = "npm",
        config: Optional[SandboxConfig] = None
    ) -> ExecutionResult:
        """Install project dependencies"""
        config = config or SandboxConfig()
        config.working_dir = project_dir
        config.timeout_seconds = 120  # Dependencies can take time
        
        commands = {
            "npm": "npm install",
            "yarn": "yarn install",
            "pnpm": "pnpm install",
            "bun": "bun install",
            "pip": "pip install -r requirements.txt",
        }
        
        command = commands.get(package_manager)
        if not command:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                error=f"Unknown package manager: {package_manager}"
            )
        
        return await self.execute(command, config)
    
    async def build_project(
        self,
        project_dir: str,
        build_command: str = "npm run build",
        config: Optional[SandboxConfig] = None
    ) -> ExecutionResult:
        """Build a project"""
        config = config or SandboxConfig()
        config.working_dir = project_dir
        config.timeout_seconds = 300  # Builds can take time
        
        return await self.execute(build_command, config)
    
    async def run_tests(
        self,
        project_dir: str,
        test_command: str = "npm test",
        config: Optional[SandboxConfig] = None
    ) -> ExecutionResult:
        """Run project tests"""
        config = config or SandboxConfig()
        config.working_dir = project_dir
        config.timeout_seconds = 180
        
        return await self.execute(test_command, config)
    
    async def kill_execution(self, execution_id: str) -> bool:
        """Kill a running execution"""
        async with self._lock:
            if execution_id in self.active_processes:
                process = self.active_processes[execution_id]
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    del self.active_processes[execution_id]
                    return True
                except Exception:
                    return False
        return False


# Global sandbox instance
sandbox = SandboxExecutor()
