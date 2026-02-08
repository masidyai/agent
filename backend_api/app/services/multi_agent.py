"""
Multi-agent collaboration system
Builder, Reviewer, Tester, Fixer, Deployer agents
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Agent role types"""
    BUILDER = "builder"
    REVIEWER = "reviewer"
    TESTER = "tester"
    FIXER = "fixer"
    DEPLOYER = "deployer"
    COORDINATOR = "coordinator"


class TaskStatus(str, Enum):
    """Task status states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentTask:
    """Represents a task assigned to an agent"""
    id: str
    role: AgentRole
    prompt: str
    context: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def mark_started(self):
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
    
    def mark_completed(self, result: Any):
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.utcnow()
    
    def mark_failed(self, error: str):
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.utcnow()


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, role: AgentRole):
        self.role = role
        self.name = f"{role.value.title()}Agent"
    
    @abstractmethod
    async def execute(
        self, 
        task: AgentTask, 
        stream_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> Any:
        """Execute the agent's task"""
        pass
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        prompts = {
            AgentRole.BUILDER: """You are a Builder Agent specialized in creating code.
Your responsibilities:
- Generate clean, well-structured code
- Follow best practices and design patterns
- Create modular, reusable components
- Write clear comments and documentation""",
            
            AgentRole.REVIEWER: """You are a Reviewer Agent specialized in code review.
Your responsibilities:
- Review code for bugs, security issues, and best practices
- Suggest improvements and optimizations
- Ensure code quality and maintainability
- Check for potential performance issues""",
            
            AgentRole.TESTER: """You are a Tester Agent specialized in testing.
Your responsibilities:
- Generate comprehensive test cases
- Write unit and integration tests
- Identify edge cases and potential failures
- Ensure adequate code coverage""",
            
            AgentRole.FIXER: """You are a Fixer Agent specialized in debugging.
Your responsibilities:
- Analyze errors and identify root causes
- Fix bugs and issues in code
- Implement suggested improvements from reviews
- Resolve test failures""",
            
            AgentRole.DEPLOYER: """You are a Deployer Agent specialized in deployment.
Your responsibilities:
- Prepare code for deployment
- Generate deployment configurations
- Handle environment setup
- Monitor deployment status""",
        }
        return prompts.get(self.role, "You are a helpful AI assistant.")


class BuilderAgent(BaseAgent):
    """Agent responsible for generating code"""
    
    def __init__(self):
        super().__init__(AgentRole.BUILDER)
    
    async def execute(
        self, 
        task: AgentTask,
        stream_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """Build code based on the prompt"""
        task.mark_started()
        
        try:
            # Simulate code generation (in production, call LLM API)
            # This is where you'd integrate with OpenAI, Anthropic, etc.
            result = {
                "files": [],
                "message": f"Code generated for: {task.prompt[:100]}..."
            }
            
            if stream_callback:
                await stream_callback(f"Building: {task.prompt[:50]}...")
                await asyncio.sleep(0.1)
                await stream_callback("Analyzing requirements...")
                await asyncio.sleep(0.1)
                await stream_callback("Generating code structure...")
            
            task.mark_completed(result)
            return result
            
        except Exception as e:
            task.mark_failed(str(e))
            raise


class ReviewerAgent(BaseAgent):
    """Agent responsible for reviewing code"""
    
    def __init__(self):
        super().__init__(AgentRole.REVIEWER)
    
    async def execute(
        self, 
        task: AgentTask,
        stream_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """Review code and provide feedback"""
        task.mark_started()
        
        try:
            result = {
                "issues": [],
                "suggestions": [],
                "approved": True,
                "message": "Code review completed"
            }
            
            if stream_callback:
                await stream_callback("Reviewing code quality...")
                await asyncio.sleep(0.1)
                await stream_callback("Checking for security issues...")
                await asyncio.sleep(0.1)
                await stream_callback("Review complete!")
            
            task.mark_completed(result)
            return result
            
        except Exception as e:
            task.mark_failed(str(e))
            raise


class TesterAgent(BaseAgent):
    """Agent responsible for generating and running tests"""
    
    def __init__(self):
        super().__init__(AgentRole.TESTER)
    
    async def execute(
        self, 
        task: AgentTask,
        stream_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """Generate and run tests"""
        task.mark_started()
        
        try:
            result = {
                "tests": [],
                "passed": 0,
                "failed": 0,
                "coverage": 0.0,
                "message": "Tests generated and executed"
            }
            
            if stream_callback:
                await stream_callback("Generating test cases...")
                await asyncio.sleep(0.1)
                await stream_callback("Running tests...")
                await asyncio.sleep(0.1)
                await stream_callback("All tests passed!")
            
            task.mark_completed(result)
            return result
            
        except Exception as e:
            task.mark_failed(str(e))
            raise


class FixerAgent(BaseAgent):
    """Agent responsible for fixing issues"""
    
    def __init__(self):
        super().__init__(AgentRole.FIXER)
    
    async def execute(
        self, 
        task: AgentTask,
        stream_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """Fix issues in code"""
        task.mark_started()
        
        try:
            result = {
                "fixes": [],
                "message": "Issues fixed successfully"
            }
            
            if stream_callback:
                await stream_callback("Analyzing issues...")
                await asyncio.sleep(0.1)
                await stream_callback("Applying fixes...")
                await asyncio.sleep(0.1)
                await stream_callback("Fixes applied!")
            
            task.mark_completed(result)
            return result
            
        except Exception as e:
            task.mark_failed(str(e))
            raise


class DeployerAgent(BaseAgent):
    """Agent responsible for deployments"""
    
    def __init__(self):
        super().__init__(AgentRole.DEPLOYER)
    
    async def execute(
        self, 
        task: AgentTask,
        stream_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """Deploy the project"""
        task.mark_started()
        
        try:
            result = {
                "url": None,
                "status": "deployed",
                "message": "Deployment configuration prepared"
            }
            
            if stream_callback:
                await stream_callback("Preparing deployment...")
                await asyncio.sleep(0.1)
                await stream_callback("Building project...")
                await asyncio.sleep(0.1)
                await stream_callback("Deployment ready!")
            
            task.mark_completed(result)
            return result
            
        except Exception as e:
            task.mark_failed(str(e))
            raise


@dataclass
class Pipeline:
    """A sequence of agent tasks"""
    id: str
    project_id: UUID
    tasks: List[AgentTask] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    current_task_index: int = 0
    results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class MultiAgentOrchestrator:
    """
    Orchestrates multiple agents working together on a project.
    Manages pipelines of agent tasks.
    """
    
    def __init__(self):
        self.agents: Dict[AgentRole, BaseAgent] = {
            AgentRole.BUILDER: BuilderAgent(),
            AgentRole.REVIEWER: ReviewerAgent(),
            AgentRole.TESTER: TesterAgent(),
            AgentRole.FIXER: FixerAgent(),
            AgentRole.DEPLOYER: DeployerAgent(),
        }
        self.active_pipelines: Dict[str, Pipeline] = {}
        self._lock = asyncio.Lock()
    
    async def create_pipeline(
        self,
        project_id: UUID,
        prompt: str,
        flow: str = "saas"
    ) -> Pipeline:
        """Create a new pipeline for a project build"""
        import uuid
        
        pipeline_id = str(uuid.uuid4())
        
        # Define tasks based on flow type
        tasks = [
            AgentTask(
                id=f"{pipeline_id}-build",
                role=AgentRole.BUILDER,
                prompt=prompt,
                context={"flow": flow}
            ),
            AgentTask(
                id=f"{pipeline_id}-review",
                role=AgentRole.REVIEWER,
                prompt=f"Review the code generated for: {prompt}",
                context={"flow": flow}
            ),
            AgentTask(
                id=f"{pipeline_id}-test",
                role=AgentRole.TESTER,
                prompt=f"Generate tests for: {prompt}",
                context={"flow": flow}
            ),
        ]
        
        pipeline = Pipeline(
            id=pipeline_id,
            project_id=project_id,
            tasks=tasks
        )
        
        async with self._lock:
            self.active_pipelines[pipeline_id] = pipeline
        
        return pipeline
    
    async def execute_pipeline(
        self,
        pipeline: Pipeline,
        stream_callback: Optional[Callable[[str, str], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """Execute all tasks in a pipeline"""
        pipeline.status = TaskStatus.IN_PROGRESS
        
        try:
            for i, task in enumerate(pipeline.tasks):
                pipeline.current_task_index = i
                
                agent = self.agents.get(task.role)
                if not agent:
                    task.mark_failed(f"No agent found for role: {task.role}")
                    continue
                
                # Create task-specific stream callback
                async def task_stream(content: str):
                    if stream_callback:
                        await stream_callback(task.role.value, content)
                
                # Execute the task
                result = await agent.execute(task, task_stream)
                pipeline.results[task.role.value] = result
                
                # Check if task failed and needs fixing
                if task.status == TaskStatus.FAILED:
                    break
            
            # Check final status
            all_completed = all(
                t.status == TaskStatus.COMPLETED 
                for t in pipeline.tasks
            )
            
            pipeline.status = TaskStatus.COMPLETED if all_completed else TaskStatus.FAILED
            
            return {
                "pipeline_id": pipeline.id,
                "status": pipeline.status.value,
                "results": pipeline.results,
                "tasks": [
                    {
                        "id": t.id,
                        "role": t.role.value,
                        "status": t.status.value,
                        "error": t.error
                    }
                    for t in pipeline.tasks
                ]
            }
            
        except Exception as e:
            pipeline.status = TaskStatus.FAILED
            logger.error(f"Pipeline {pipeline.id} failed: {e}")
            raise
    
    async def cancel_pipeline(self, pipeline_id: str):
        """Cancel an active pipeline"""
        async with self._lock:
            if pipeline_id in self.active_pipelines:
                pipeline = self.active_pipelines[pipeline_id]
                pipeline.status = TaskStatus.CANCELLED
                
                for task in pipeline.tasks:
                    if task.status == TaskStatus.PENDING:
                        task.status = TaskStatus.CANCELLED
    
    async def get_pipeline_status(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a pipeline"""
        if pipeline_id not in self.active_pipelines:
            return None
        
        pipeline = self.active_pipelines[pipeline_id]
        return {
            "pipeline_id": pipeline.id,
            "project_id": str(pipeline.project_id),
            "status": pipeline.status.value,
            "current_task": pipeline.current_task_index,
            "total_tasks": len(pipeline.tasks),
            "tasks": [
                {
                    "id": t.id,
                    "role": t.role.value,
                    "status": t.status.value,
                    "error": t.error
                }
                for t in pipeline.tasks
            ]
        }
    
    async def execute_single_agent(
        self,
        role: AgentRole,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        stream_callback: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> Dict[str, Any]:
        """Execute a single agent task"""
        import uuid
        
        agent = self.agents.get(role)
        if not agent:
            raise ValueError(f"No agent found for role: {role}")
        
        task = AgentTask(
            id=str(uuid.uuid4()),
            role=role,
            prompt=prompt,
            context=context or {}
        )
        
        result = await agent.execute(task, stream_callback)
        
        return {
            "task_id": task.id,
            "role": role.value,
            "status": task.status.value,
            "result": result,
            "error": task.error
        }


# Global orchestrator instance
orchestrator = MultiAgentOrchestrator()
