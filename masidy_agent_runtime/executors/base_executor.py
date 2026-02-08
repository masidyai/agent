"""
Masidy Autonomous Agent Runtime - Base Executor
Abstract base class for all flow executors
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional


@dataclass
class StepResult:
    """Result of a single step execution"""
    step_id: str
    description: str
    tool_name: str
    status: str  # "success", "failure", "skipped"
    output: Any = None
    error: Optional[str] = None
    retries: int = 0
    duration_ms: float = 0
    verified: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ExecutionResult:
    """Final result of a complete plan execution"""
    status: str  # "success", "failure", "partial"
    steps_completed: int
    steps_total: int
    errors: list = field(default_factory=list)
    output_path: Optional[str] = None
    step_results: list = field(default_factory=list)
    duration_ms: float = 0
    started_at: str = ""
    completed_at: str = ""
    
    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "steps_completed": self.steps_completed,
            "steps_total": self.steps_total,
            "errors": self.errors,
            "output_path": self.output_path,
            "step_results": [
                {
                    "step_id": sr.step_id,
                    "description": sr.description,
                    "status": sr.status,
                    "retries": sr.retries,
                    "error": sr.error
                }
                for sr in self.step_results
            ],
            "duration_ms": self.duration_ms,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


class BaseExecutor(ABC):
    """
    Abstract base class for flow executors.
    Handles structured plan execution with retries and result tracking.
    """
    
    def __init__(
        self,
        tools: dict[str, Callable],
        state_manager,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        verbose: bool = False
    ):
        """
        Initialize the executor.
        
        Args:
            tools: Dict of available tools
            state_manager: State manager for persistence
            max_retries: Maximum retries per step
            retry_delay: Delay between retries in seconds
            verbose: Whether to print detailed output
        """
        self.tools = tools
        self.state_manager = state_manager
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.verbose = verbose
    
    @property
    @abstractmethod
    def flow_name(self) -> str:
        """Return the flow name (saas, api, refactor)"""
        pass
    
    def run(
        self,
        task_description: str,
        plan: list[dict],
        config: dict
    ) -> ExecutionResult:
        """
        Execute a structured plan.
        
        Args:
            task_description: Description of the task
            plan: List of plan steps
            config: Configuration dict
        
        Returns:
            ExecutionResult with final status
        """
        started_at = datetime.now()
        step_results = []
        errors = []
        
        total_steps = len(plan)
        completed_steps = 0
        output_path = config.get("output_folder") or config.get("project_name")
        
        # Record start in state
        self.state_manager.start_task(task_description, plan)
        
        if self.verbose:
            print(f"\n{'=' * 60}")
            print(f"  Executing {self.flow_name.upper()} Plan ({total_steps} steps)")
            print(f"{'=' * 60}")
        
        for i, step in enumerate(plan):
            step_id = step.get("id", f"step_{i+1}")
            description = step.get("description", f"Step {i+1}")
            tool_name = step.get("tool_name")
            tool_args = step.get("tool_args", {})
            verify_instruction = step.get("verify_instruction")
            
            if self.verbose:
                print(f"\n[{i+1}/{total_steps}] {description}")
            
            # Execute step with retries
            step_result = self._execute_step(
                step_id=step_id,
                description=description,
                tool_name=tool_name,
                tool_args=tool_args,
                verify_instruction=verify_instruction
            )
            
            step_results.append(step_result)
            
            # Record in state
            self.state_manager.record_step_result(i, {
                "step_id": step_result.step_id,
                "status": step_result.status,
                "output": str(step_result.output)[:200] if step_result.output else None,
                "error": step_result.error,
                "retries": step_result.retries
            })
            
            if step_result.status == "success":
                completed_steps += 1
                if self.verbose:
                    print(f"    ✓ Success")
            else:
                errors.append({
                    "step_id": step_id,
                    "description": description,
                    "error": step_result.error
                })
                if self.verbose:
                    print(f"    ✗ Failed: {step_result.error}")
        
        completed_at = datetime.now()
        duration_ms = (completed_at - started_at).total_seconds() * 1000
        
        # Determine final status
        if completed_steps == total_steps:
            status = "success"
        elif completed_steps > 0:
            status = "partial"
        else:
            status = "failure"
        
        # Record completion
        self.state_manager.complete_task(status)
        
        return ExecutionResult(
            status=status,
            steps_completed=completed_steps,
            steps_total=total_steps,
            errors=errors,
            output_path=output_path,
            step_results=step_results,
            duration_ms=duration_ms,
            started_at=started_at.isoformat(),
            completed_at=completed_at.isoformat()
        )
    
    def _execute_step(
        self,
        step_id: str,
        description: str,
        tool_name: str,
        tool_args: dict,
        verify_instruction: Optional[str] = None
    ) -> StepResult:
        """
        Execute a single step with retry logic.
        """
        start_time = time.time()
        retries = 0
        last_error = None
        
        # Check if tool exists
        if tool_name not in self.tools:
            return StepResult(
                step_id=step_id,
                description=description,
                tool_name=tool_name,
                status="failure",
                error=f"Unknown tool: {tool_name}",
                duration_ms=(time.time() - start_time) * 1000
            )
        
        tool = self.tools[tool_name]
        
        while retries <= self.max_retries:
            try:
                # Execute the tool
                result = tool(**tool_args)
                
                # Check if tool returned success
                if isinstance(result, dict) and result.get("success") is False:
                    raise Exception(result.get("error", "Tool returned failure"))
                
                # Verify if instruction provided
                verified = True
                if verify_instruction:
                    verified = self._verify_step(verify_instruction, result)
                
                duration_ms = (time.time() - start_time) * 1000
                
                return StepResult(
                    step_id=step_id,
                    description=description,
                    tool_name=tool_name,
                    status="success",
                    output=result,
                    retries=retries,
                    verified=verified,
                    duration_ms=duration_ms
                )
                
            except Exception as e:
                last_error = str(e)
                retries += 1
                if retries <= self.max_retries:
                    if self.verbose:
                        print(f"    ↻ Retry {retries}/{self.max_retries}: {last_error}")
                    time.sleep(self.retry_delay)
        
        duration_ms = (time.time() - start_time) * 1000
        
        return StepResult(
            step_id=step_id,
            description=description,
            tool_name=tool_name,
            status="failure",
            error=last_error,
            retries=retries - 1,
            duration_ms=duration_ms
        )
    
    def _verify_step(self, instruction: str, result: Any) -> bool:
        """
        Verify a step result based on instruction.
        Override in subclasses for custom verification.
        """
        # Basic verification - check if result indicates success
        if isinstance(result, dict):
            return result.get("success", True)
        return True
    
    @abstractmethod
    def build_plan(self, task_description: str, config: dict) -> list[dict]:
        """
        Build a structured plan for the task.
        Must be implemented by subclasses.
        
        Returns:
            List of plan steps, each with:
            - id: str
            - description: str
            - tool_name: str
            - tool_args: dict
            - verify_instruction: Optional[str]
        """
        pass
