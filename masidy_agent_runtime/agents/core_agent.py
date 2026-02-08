"""
Masidy Autonomous Agent Runtime - Core Agent
Uses OpenAI Swarm for agent orchestration
"""

import json
import os
import time
from typing import Any, Callable, Optional
from dataclasses import dataclass, field

# Conditional import - Swarm requires OpenAI API key
try:
    from swarm import Swarm, Agent
    SWARM_AVAILABLE = True
except ImportError:
    SWARM_AVAILABLE = False
    Swarm = None
    Agent = None


@dataclass
class ExecutionResult:
    """Result of a tool execution"""
    success: bool
    output: Any
    error: Optional[str] = None
    retries: int = 0


@dataclass 
class TaskContext:
    """Context for the current task execution"""
    task: str
    plan: list[dict] = field(default_factory=list)
    current_step: int = 0
    results: list[ExecutionResult] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed


class CoreAgent:
    """
    Core agent that orchestrates task execution using OpenAI Swarm.
    Handles task acceptance, tool execution, and failure retries.
    """
    
    def __init__(
        self,
        tools: dict[str, Callable],
        max_retries: int = 3,
        retry_delay: float = 1.0,
        model: str = "gpt-4o-mini"
    ):
        self.tools = tools
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.model = model
        self.context: Optional[TaskContext] = None
        
        # Initialize Swarm client only if available and API key is set
        self.swarm_enabled = False
        self.client = None
        self.executor_agent = None
        
        if SWARM_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
            try:
                self.client = Swarm()
                self.executor_agent = Agent(
                    name="Executor",
                    model=self.model,
                    instructions=self._get_executor_instructions(),
                    functions=list(tools.values())
                )
                self.swarm_enabled = True
            except Exception as e:
                print(f"  Note: Swarm initialization skipped ({e})")
    
    def _get_executor_instructions(self) -> str:
        return """You are an autonomous task executor. Your job is to:
1. Execute the current step from the plan using the available tools
2. Report success or failure clearly
3. Provide detailed output of what was accomplished

Available tools will be provided to you. Use them to complete each step.
Always be precise and report exactly what happened."""
    
    def accept_task(self, task: str) -> TaskContext:
        """Accept a new task and create context"""
        self.context = TaskContext(task=task, status="pending")
        return self.context
    
    def set_plan(self, plan: list[dict]) -> None:
        """Set the execution plan for the current task"""
        if not self.context:
            raise ValueError("No task context. Call accept_task first.")
        self.context.plan = plan
        self.context.status = "in_progress"
    
    def execute_step(self, step: dict) -> ExecutionResult:
        """Execute a single step from the plan with retry logic"""
        tool_name = step.get("tool")
        args = step.get("args", {})
        description = step.get("description", "")
        
        if tool_name not in self.tools:
            return ExecutionResult(
                success=False,
                output=None,
                error=f"Unknown tool: {tool_name}"
            )
        
        tool = self.tools[tool_name]
        retries = 0
        last_error = None
        
        while retries <= self.max_retries:
            try:
                # Execute the tool
                result = tool(**args)
                return ExecutionResult(
                    success=True,
                    output=result,
                    retries=retries
                )
            except Exception as e:
                last_error = str(e)
                retries += 1
                if retries <= self.max_retries:
                    print(f"  Retry {retries}/{self.max_retries} after error: {last_error}")
                    time.sleep(self.retry_delay)
        
        return ExecutionResult(
            success=False,
            output=None,
            error=last_error,
            retries=retries
        )
    
    def execute_plan(self) -> list[ExecutionResult]:
        """Execute all steps in the plan"""
        if not self.context or not self.context.plan:
            raise ValueError("No plan to execute. Set plan first.")
        
        results = []
        
        for i, step in enumerate(self.context.plan):
            self.context.current_step = i
            print(f"\n[Step {i+1}/{len(self.context.plan)}] {step.get('description', 'Executing...')}")
            
            result = self.execute_step(step)
            results.append(result)
            self.context.results.append(result)
            
            if result.success:
                print(f"  ✓ Success: {result.output}")
            else:
                print(f"  ✗ Failed: {result.error}")
                # Don't stop on failure, continue with remaining steps
        
        # Determine overall status
        all_success = all(r.success for r in results)
        self.context.status = "completed" if all_success else "failed"
        
        return results
    
    def run_with_swarm(self, user_message: str) -> dict:
        """Run task using Swarm for conversational orchestration"""
        if not self.swarm_enabled:
            return {
                "error": "Swarm not available. Set OPENAI_API_KEY to enable.",
                "agent": None,
                "messages": [],
                "context_variables": {}
            }
        
        messages = [{"role": "user", "content": user_message}]
        
        response = self.client.run(
            agent=self.executor_agent,
            messages=messages
        )
        
        return {
            "agent": response.agent.name,
            "messages": response.messages,
            "context_variables": response.context_variables
        }
    
    def get_status(self) -> dict:
        """Get current execution status"""
        if not self.context:
            return {"status": "no_task"}
        
        return {
            "task": self.context.task,
            "status": self.context.status,
            "current_step": self.context.current_step,
            "total_steps": len(self.context.plan),
            "completed_steps": len(self.context.results),
            "success_count": sum(1 for r in self.context.results if r.success),
            "failure_count": sum(1 for r in self.context.results if not r.success)
        }
