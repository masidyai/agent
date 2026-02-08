"""
Masidy Autonomous Agent Runtime - Planner
Uses LangGraph for planning loops and state management
Supports blueprint selection and inference
"""

import json
import os
import operator
from dataclasses import dataclass
from typing import Annotated, TypedDict, Sequence, Any, Optional

# Conditional imports for LangGraph
try:
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
    from langchain_openai import ChatOpenAI
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    BaseMessage = None
    HumanMessage = None
    AIMessage = None
    ChatOpenAI = None
    StateGraph = None
    END = None


class PlannerState(TypedDict):
    """State for the planning graph"""
    task: str
    messages: Annotated[Sequence[BaseMessage], operator.add]
    plan: list[dict]
    current_step: int
    execution_results: list[dict]
    needs_replan: bool
    completed: bool
    iteration: int
    max_iterations: int


class TaskPlanner:
    """
    Task planner using LangGraph for multi-step planning loops.
    Creates execution plans and handles re-planning when needed.
    """
    
    def __init__(
        self,
        available_tools: list[str],
        model: str = "gpt-4o-mini",
        max_iterations: int = 10
    ):
        self.available_tools = available_tools
        self.model = model
        self.max_iterations = max_iterations
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph planning workflow"""
        workflow = StateGraph(PlannerState)
        
        # Add nodes
        workflow.add_node("analyze", self._analyze_task)
        workflow.add_node("create_plan", self._create_plan)
        workflow.add_node("validate_plan", self._validate_plan)
        workflow.add_node("check_completion", self._check_completion)
        workflow.add_node("replan", self._replan)
        
        # Set entry point
        workflow.set_entry_point("analyze")
        
        # Add edges
        workflow.add_edge("analyze", "create_plan")
        workflow.add_edge("create_plan", "validate_plan")
        workflow.add_conditional_edges(
            "validate_plan",
            self._should_continue,
            {
                "execute": END,
                "replan": "replan"
            }
        )
        workflow.add_edge("replan", "create_plan")
        
        return workflow.compile()
    
    def _analyze_task(self, state: PlannerState) -> dict:
        """Analyze the task and identify requirements"""
        task = state["task"]
        
        prompt = f"""Analyze this task and identify:
1. What needs to be accomplished
2. What tools will be needed
3. Any dependencies between steps

Task: {task}

Available tools: {', '.join(self.available_tools)}

Provide a brief analysis."""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        return {
            "messages": [HumanMessage(content=prompt), response],
            "iteration": state.get("iteration", 0) + 1
        }
    
    def _create_plan(self, state: PlannerState) -> dict:
        """Create an execution plan for the task"""
        task = state["task"]
        previous_results = state.get("execution_results", [])
        
        context = ""
        if previous_results:
            context = f"\n\nPrevious execution results:\n{json.dumps(previous_results, indent=2)}"
        
        prompt = f"""Create a step-by-step execution plan for this task.

Task: {task}
{context}

Available tools: {', '.join(self.available_tools)}

Each step should be a JSON object with:
- "step": step number
- "tool": tool name to use
- "args": arguments for the tool (as a dictionary)
- "description": what this step accomplishes
- "depends_on": list of step numbers this depends on (empty if none)

Return ONLY a JSON array of steps. Example:
[
    {{"step": 1, "tool": "create_directory", "args": {{"path": "example"}}, "description": "Create the example directory", "depends_on": []}},
    {{"step": 2, "tool": "write_file", "args": {{"path": "example/file.txt", "content": "Hello"}}, "description": "Write content to file", "depends_on": [1]}}
]"""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        # Parse the plan from response
        try:
            plan_text = response.content
            # Extract JSON from response
            if "```json" in plan_text:
                plan_text = plan_text.split("```json")[1].split("```")[0]
            elif "```" in plan_text:
                plan_text = plan_text.split("```")[1].split("```")[0]
            plan = json.loads(plan_text.strip())
        except (json.JSONDecodeError, IndexError):
            # Fallback to empty plan if parsing fails
            plan = []
        
        return {
            "plan": plan,
            "messages": [HumanMessage(content=prompt), response]
        }
    
    def _validate_plan(self, state: PlannerState) -> dict:
        """Validate the created plan"""
        plan = state.get("plan", [])
        
        # Check if plan is valid
        is_valid = True
        issues = []
        
        if not plan:
            is_valid = False
            issues.append("Plan is empty")
        
        for step in plan:
            tool = step.get("tool")
            if tool not in self.available_tools:
                is_valid = False
                issues.append(f"Unknown tool: {tool}")
        
        if not is_valid:
            return {
                "needs_replan": True,
                "messages": [AIMessage(content=f"Plan validation failed: {issues}")]
            }
        
        return {
            "needs_replan": False,
            "messages": [AIMessage(content="Plan validated successfully")]
        }
    
    def _should_continue(self, state: PlannerState) -> str:
        """Determine if we should continue planning or execute"""
        if state.get("needs_replan", False):
            if state.get("iteration", 0) >= state.get("max_iterations", self.max_iterations):
                return "execute"  # Give up and try to execute what we have
            return "replan"
        return "execute"
    
    def _check_completion(self, state: PlannerState) -> dict:
        """Check if the task is completed"""
        results = state.get("execution_results", [])
        plan = state.get("plan", [])
        
        if not results:
            return {"completed": False}
        
        # Check if all steps succeeded
        all_success = all(r.get("success", False) for r in results)
        
        return {
            "completed": all_success,
            "needs_replan": not all_success
        }
    
    def _replan(self, state: PlannerState) -> dict:
        """Re-plan based on execution results"""
        return {
            "messages": [AIMessage(content="Re-planning based on previous results...")]
        }
    
    def create_plan(self, task: str) -> list[dict]:
        """Create an execution plan for a task"""
        initial_state: PlannerState = {
            "task": task,
            "messages": [],
            "plan": [],
            "current_step": 0,
            "execution_results": [],
            "needs_replan": False,
            "completed": False,
            "iteration": 0,
            "max_iterations": self.max_iterations
        }
        
        result = self.graph.invoke(initial_state)
        return result.get("plan", [])
    
    def replan_after_failure(
        self,
        task: str,
        original_plan: list[dict],
        execution_results: list[dict]
    ) -> list[dict]:
        """Create a new plan after execution failures"""
        initial_state: PlannerState = {
            "task": task,
            "messages": [],
            "plan": original_plan,
            "current_step": 0,
            "execution_results": execution_results,
            "needs_replan": True,
            "completed": False,
            "iteration": 0,
            "max_iterations": self.max_iterations
        }
        
        result = self.graph.invoke(initial_state)
        return result.get("plan", [])


def create_simple_plan(task: str, available_tools: list[str]) -> list[dict]:
    """
    Create a simple plan without LLM (for testing/offline use).
    Maps common task patterns to tool sequences.
    
    Returns structured plan with:
    - id: str
    - description: str  
    - tool_name: str
    - tool_args: dict
    - verify_instruction: Optional[str]
    """
    task_lower = task.lower()
    
    # Pattern matching for common tasks
    if "create" in task_lower and "folder" in task_lower:
        # Extract folder name if mentioned
        folder_name = "new_folder"
        if "called" in task_lower:
            parts = task_lower.split("called")
            if len(parts) > 1:
                folder_name = parts[1].strip().split()[0].strip('"\'')
        
        plan = [
            {
                "id": "create_folder",
                "description": f"Create directory: {folder_name}",
                "tool_name": "create_directory",
                "tool_args": {"path": folder_name},
                "verify_instruction": "Directory should exist"
            }
        ]
        
        # Check if we need to write a file too
        if "write" in task_lower or "hello world" in task_lower:
            file_content = "Hello, World!"
            file_name = "hello.txt"
            
            plan.append({
                "id": "write_file",
                "description": f"Write hello world to {file_name}",
                "tool_name": "write_file",
                "tool_args": {
                    "path": f"{folder_name}/{file_name}",
                    "content": file_content
                },
                "verify_instruction": "File should contain 'Hello, World!'"
            })
        
        return plan
    
    # Default empty plan for unknown tasks
    return []


@dataclass
class PlanStep:
    """Structured plan step"""
    id: str
    description: str
    tool_name: str
    tool_args: dict
    verify_instruction: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "description": self.description,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "verify_instruction": self.verify_instruction
        }


@dataclass  
class StructuredPlan:
    """A complete structured plan"""
    task: str
    flow: str
    steps: list[PlanStep]
    
    def to_list(self) -> list[dict]:
        return [step.to_dict() for step in self.steps]
    
    def __len__(self) -> int:
        return len(self.steps)


class StructuredPlanner:
    """
    Creates structured plans for tasks.
    Ready for LLM-based planning but implements rule-based fallback.
    """
    
    def __init__(self, available_tools: list[str], use_llm: bool = False):
        self.available_tools = available_tools
        self.use_llm = use_llm
    
    def create_plan(self, task: str, flow: str, config: dict) -> StructuredPlan:
        """
        Create a structured plan for a task.
        
        Args:
            task: Task description
            flow: Flow type (saas, api, refactor)
            config: Configuration dict
        
        Returns:
            StructuredPlan with steps
        """
        if self.use_llm:
            return self._create_llm_plan(task, flow, config)
        else:
            return self._create_rule_based_plan(task, flow, config)
    
    def _create_llm_plan(self, task: str, flow: str, config: dict) -> StructuredPlan:
        """Create plan using LLM (placeholder for future implementation)"""
        # For now, fall back to rule-based
        return self._create_rule_based_plan(task, flow, config)
    
    def _create_rule_based_plan(self, task: str, flow: str, config: dict) -> StructuredPlan:
        """Create plan using rule-based logic"""
        # Delegate to flow-specific executors
        # This is a simple fallback - actual planning is in executors
        steps = []
        
        project_name = config.get("project_name", "project")
        
        if flow == "api":
            steps = [
                PlanStep(
                    id="setup",
                    description="Initialize API project structure",
                    tool_name="create_directory",
                    tool_args={"path": project_name}
                ),
            ]
        elif flow == "saas":
            steps = [
                PlanStep(
                    id="setup",
                    description="Initialize SaaS project structure",
                    tool_name="create_directory",
                    tool_args={"path": project_name}
                ),
            ]
        elif flow == "refactor":
            steps = [
                PlanStep(
                    id="analyze",
                    description="Analyze repository structure",
                    tool_name="list_directory",
                    tool_args={"path": config.get("target_path", ".")}
                ),
            ]
        
        return StructuredPlan(task=task, flow=flow, steps=steps)


# Blueprint Selection and Inference

BLUEPRINT_KEYWORDS = {
    "saas": [
        "saas", "software as a service", "subscription", "billing",
        "frontend and backend", "full stack", "fullstack", "full-stack",
        "react", "next.js", "nextjs", "web app", "webapp", "dashboard",
        "user management", "multi-tenant", "landing page", "signup",
        "login page", "authentication ui"
    ],
    "api": [
        "api", "rest", "restful", "endpoint", "crud", "backend only",
        "microservice", "service", "json api", "data service",
        "fastapi", "flask", "no frontend", "backend", "server"
    ],
    "refactor": [
        "refactor", "modernize", "clean", "improve", "fix",
        "upgrade", "update", "existing", "legacy", "migrate",
        "document", "add ci", "add tests", "restructure", "organize"
    ],
}


def infer_blueprint(task_description: str) -> str:
    """
    Infer the best blueprint based on task description.
    Returns: 'saas', 'api', or 'refactor'
    """
    task_lower = task_description.lower()
    
    # Score each blueprint
    scores = {}
    for blueprint, keywords in BLUEPRINT_KEYWORDS.items():
        scores[blueprint] = sum(1 for kw in keywords if kw in task_lower)
    
    # Return highest scoring, default to saas for new projects
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "saas"


def select_blueprint(flow: Optional[str], task_description: str) -> str:
    """
    Select a blueprint based on explicit flow or inference.
    
    Args:
        flow: Explicit flow name ('saas', 'api', 'refactor') or None
        task_description: Task description for inference
    
    Returns:
        Selected blueprint name
    """
    if flow and flow.lower() in BLUEPRINT_KEYWORDS:
        return flow.lower()
    
    return infer_blueprint(task_description)


def extract_project_name(task_description: str, default: str = "project") -> str:
    """
    Extract project name from task description.
    """
    task_lower = task_description.lower()
    
    # Look for common patterns
    patterns = [
        "called ", "named ", "for ", "create a ", "build a ", "make a "
    ]
    
    for pattern in patterns:
        if pattern in task_lower:
            parts = task_lower.split(pattern)
            if len(parts) > 1:
                # Get first word after pattern
                name_part = parts[1].strip().split()[0] if parts[1].strip() else ""
                # Clean up
                name = name_part.strip('"\'".,!?').replace(" ", "_").replace("-", "_")
                if name and len(name) > 2:
                    return name
    
    return default


def get_blueprint_config(task_description: str, blueprint: str) -> dict:
    """
    Generate configuration for a blueprint based on task description.
    """
    config = {
        "project_name": extract_project_name(task_description, f"{blueprint}_app"),
        "task_description": task_description,
    }
    
    task_lower = task_description.lower()
    
    if blueprint == "saas":
        config["db_type"] = "postgresql" if "postgres" in task_lower else "sqlite"
        config["include_frontend"] = "no frontend" not in task_lower
    
    elif blueprint == "api":
        config["db_type"] = "sqlite"
    
    elif blueprint == "refactor":
        config["target_path"] = "."  # Default to current directory
    
    return config
