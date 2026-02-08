"""
Masidy Autonomous Agent Runtime - Flow Router
Routes tasks to the correct blueprint based on flow type or inference
"""

from typing import Optional, Any
from datetime import datetime

from blueprints import BLUEPRINTS, get_blueprint, infer_blueprint


# Flow inference keywords
FLOW_KEYWORDS = {
    "saas": [
        "saas", "software as a service", "subscription", "billing",
        "frontend and backend", "full stack", "fullstack", "full-stack",
        "react", "next.js", "nextjs", "web app", "webapp", "dashboard",
        "user management", "multi-tenant", "landing page", "signup",
        "login page", "authentication ui", "portal"
    ],
    "api": [
        "api", "rest", "restful", "endpoint", "crud", "backend only",
        "microservice", "service", "json api", "data service",
        "fastapi", "flask", "no frontend", "backend", "server",
        "graphql", "webhook"
    ],
    "refactor": [
        "refactor", "modernize", "clean", "improve", "fix",
        "upgrade", "update", "existing", "legacy", "migrate",
        "document", "add ci", "add tests", "restructure", "organize",
        "cleanup", "optimize"
    ],
}


class FlowRouter:
    """
    Routes tasks to the appropriate blueprint.
    Handles flow selection, inference, and execution.
    """
    
    def __init__(self, core_agent, planner, state_manager):
        """
        Initialize the flow router.
        
        Args:
            core_agent: The core agent instance
            planner: The planner instance
            state_manager: The state manager instance
        """
        self.core_agent = core_agent
        self.planner = planner
        self.state_manager = state_manager
        self.blueprints = BLUEPRINTS
    
    def infer_flow(self, task_description: str) -> str:
        """
        Infer the best flow from the task description.
        
        Args:
            task_description: Natural language task description
        
        Returns:
            Flow name ('saas', 'api', or 'refactor')
        """
        task_lower = task_description.lower()
        
        # Score each flow
        scores = {}
        for flow, keywords in FLOW_KEYWORDS.items():
            scores[flow] = sum(1 for kw in keywords if kw in task_lower)
        
        # Return highest scoring, default to 'api' for generic tasks
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "api"
    
    def select_flow(self, flow: Optional[str], task_description: str) -> str:
        """
        Select a flow based on explicit parameter or inference.
        
        Args:
            flow: Explicit flow name or None
            task_description: Task description for inference
        
        Returns:
            Selected flow name
        """
        if flow and flow.lower() in self.blueprints:
            return flow.lower()
        
        return self.infer_flow(task_description)
    
    def get_flow_info(self, flow: str) -> dict:
        """Get information about a flow"""
        blueprint = self.blueprints.get(flow)
        if blueprint:
            return blueprint.get("info", {})
        return {}
    
    def list_flows(self) -> list[dict]:
        """List all available flows with their info"""
        return [
            {"name": name, **bp["info"]}
            for name, bp in self.blueprints.items()
        ]
    
    def route(
        self,
        task: str,
        flow: Optional[str] = None,
        config: Optional[dict] = None,
        verbose: bool = False
    ) -> dict:
        """
        Route a task to the appropriate blueprint and execute it.
        
        Args:
            task: Natural language task description
            flow: Explicit flow name ('saas', 'api', 'refactor') or None for auto-detect
            config: Configuration options for the blueprint
            verbose: Whether to print detailed step output
        
        Returns:
            dict with execution results including:
            - status: "success" | "failure" | "partial"
            - steps_completed: int
            - steps_total: int
            - errors: list
            - output_path: str | None
        """
        # Select the flow
        selected_flow = self.select_flow(flow, task)
        blueprint = self.blueprints.get(selected_flow)
        
        if not blueprint:
            return {
                "status": "failure",
                "steps_completed": 0,
                "steps_total": 0,
                "errors": [{"error": f"Unknown flow: {selected_flow}"}],
                "output_path": None,
                "available_flows": list(self.blueprints.keys())
            }
        
        # Get flow info
        flow_info = blueprint.get("info", {})
        
        # Merge default config with provided config
        final_config = self._build_config(task, selected_flow, config)
        
        # Execute the blueprint
        try:
            result = blueprint["run"](
                task_description=task,
                config=final_config,
                core_agent=self.core_agent,
                planner=self.planner,
                state_manager=self.state_manager,
                verbose=verbose
            )
            
            # Ensure result has standard format
            if "status" not in result:
                # Convert legacy format
                result["status"] = "success" if result.get("success", True) else "failure"
            
            # Add routing metadata
            result["routed_flow"] = selected_flow
            result["flow_info"] = flow_info
            result["config_used"] = final_config
            result["task"] = task
            
            return result
            
        except Exception as e:
            return {
                "status": "failure",
                "steps_completed": 0,
                "steps_total": 0,
                "errors": [{"error": str(e)}],
                "output_path": None,
                "flow": selected_flow,
                "task": task
            }
    
    def _build_config(
        self,
        task: str,
        flow: str,
        user_config: Optional[dict]
    ) -> dict:
        """Build the final configuration by merging defaults with user config"""
        # Extract project name from task
        project_name = self._extract_project_name(task, flow)
        
        # Base config
        config = {
            "project_name": project_name,
            "output_folder": project_name,
            "task_description": task,
        }
        
        # Flow-specific defaults
        if flow == "saas":
            config.update({
                "db_type": "sqlite",
                "include_frontend": True,
                "include_auth": True,
                "include_docker": True,
                "include_ci": True,
            })
        elif flow == "api":
            config.update({
                "db_type": "sqlite",
                "include_docker": True,
                "include_ci": True,
                "include_tests": True,
            })
        elif flow == "refactor":
            config.update({
                "target_path": ".",
                "run_tests": True,
                "improve_docs": True,
                "add_docker": True,
                "add_ci": True,
            })
        
        # Override with user config
        if user_config:
            config.update(user_config)
        
        return config
    
    def _extract_project_name(self, task: str, flow: str) -> str:
        """Extract project name from task description"""
        task_lower = task.lower()
        
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
                    if name and len(name) > 2 and name.isalnum():
                        return name
        
        # Default names based on flow
        defaults = {
            "saas": "saas_app",
            "api": "api_service",
            "refactor": "refactored_project"
        }
        return defaults.get(flow, "project")


# Convenience function for direct routing
def route(
    task: str,
    flow: Optional[str],
    config: Optional[dict],
    core_agent,
    planner,
    state_manager
) -> dict:
    """
    Convenience function to route a task without creating a FlowRouter instance.
    
    Args:
        task: Task description
        flow: Flow name or None for auto-detect
        config: Configuration options
        core_agent: Core agent instance
        planner: Planner instance
        state_manager: State manager instance
    
    Returns:
        Execution results
    """
    router = FlowRouter(core_agent, planner, state_manager)
    return router.route(task, flow, config)
