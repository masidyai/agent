#!/usr/bin/env python3
"""
Masidy Autonomous Agent Runtime - Premium Edition
==================================================
An ALL-IN-ONE autonomous agent system for creating complete projects.

Flows:
- SaaS: Full-stack application (FastAPI + React + DB + Auth + Docker + CI)
- API: Backend service (FastAPI + DB + Tests + Docker + CI)
- Refactor: Modernize existing repositories

This runtime can:
- Accept tasks
- Route to appropriate flow
- Execute blueprints with configurable settings
- Update memory
- Retry failures
- Complete tasks end-to-end
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents.core_agent import CoreAgent, TaskContext
from agents.planner import (
    TaskPlanner, 
    create_simple_plan,
    infer_blueprint
)
from tools.file_tools import FILE_TOOLS
from tools.command_tools import COMMAND_TOOLS
from tools.github_tools import GITHUB_TOOLS
from memory.state_manager import get_state_manager, StateManager
from blueprints import BLUEPRINTS, list_blueprints
from flows import FlowRouter
from config import get_config, list_configs, FLOW_CONFIGS


class MasidyAgentRuntime:
    """
    Main runtime class that orchestrates the autonomous agent.
    Combines planning, execution, and memory management.
    Supports multiple high-level flows via blueprints.
    Uses FlowRouter for intelligent flow selection and routing.
    """
    
    def __init__(
        self,
        use_llm_planner: bool = False,
        model: str = "gpt-4o-mini",
        max_retries: int = 3,
        quiet: bool = False
    ):
        """
        Initialize the Masidy Agent Runtime.
        
        Args:
            use_llm_planner: Use LLM-based planning (requires OpenAI API key)
            model: Model to use for LLM operations
            max_retries: Maximum retries for failed steps
            quiet: Suppress initialization banner
        """
        # Combine all available tools
        self.tools = {}
        self.tools.update(FILE_TOOLS)
        self.tools.update(COMMAND_TOOLS)
        self.tools.update(GITHUB_TOOLS)
        
        # Initialize components
        self.core_agent = CoreAgent(
            tools=self.tools,
            max_retries=max_retries,
            model=model
        )
        
        self.use_llm_planner = use_llm_planner
        self.model = model
        
        if use_llm_planner and os.environ.get("OPENAI_API_KEY"):
            self.planner = TaskPlanner(
                available_tools=list(self.tools.keys()),
                model=model
            )
        else:
            self.planner = None
        
        # Initialize state manager
        self.state = get_state_manager()
        
        # Initialize flow router
        self.flow_router = FlowRouter(
            core_agent=self.core_agent,
            planner=self.planner,
            state_manager=self.state
        )
        
        # Available blueprints
        self.blueprints = BLUEPRINTS
        
        if not quiet:
            self._print_banner()
    
    def _print_banner(self):
        """Print initialization banner"""
        print("=" * 60)
        print("  🚀 Masidy Autonomous Agent Runtime - Premium Edition")
        print("=" * 60)
        print(f"  Available tools: {len(self.tools)}")
        print(f"  Available flows: {', '.join(self.blueprints.keys())}")
        print(f"  Config system: Enabled")
        print(f"  LLM Planner: {'Enabled' if self.planner else 'Disabled'}")
        print(f"  Swarm: {'Enabled' if self.core_agent.swarm_enabled else 'Disabled'}")
        print("=" * 60)
    
    def run_flow(
        self,
        flow: Optional[str],
        task: str,
        config: Optional[dict] = None,
        verbose: bool = False
    ) -> dict:
        """
        Run a high-level flow (blueprint) end-to-end using the FlowRouter.
        
        Args:
            flow: Flow name ('saas', 'api', 'refactor') or None for auto-detect
            task: Natural language description of what to build
            config: Optional configuration overrides
            verbose: Whether to print detailed step output
        
        Returns:
            dict with execution results including:
            - status: "success" | "failure" | "partial"
            - steps_completed: int
            - steps_total: int
            - errors: list
            - output_path: str | None
        """
        # Merge with flow-specific config if flow is specified
        merged_config = None
        if config:
            merged_config = config
        elif flow:
            # Get default config for this flow
            merged_config = get_config(flow)
        
        # Route to the appropriate blueprint
        return self.flow_router.route(
            task=task,
            flow=flow,
            config=merged_config,
            verbose=verbose
        )
    
    def run_task(self, task: str) -> dict:
        """
        Run a simple task end-to-end (non-blueprint mode).
        
        Args:
            task: Natural language description of the task
        
        Returns:
            dict with execution results
        """
        print(f"\n📋 Task: {task}")
        print("-" * 60)
        
        # Step 1: Accept the task
        print("\n[1/5] Accepting task...")
        context = self.core_agent.accept_task(task)
        
        # Step 2: Create plan
        print("\n[2/5] Creating execution plan...")
        if self.planner:
            plan = self.planner.create_plan(task)
        else:
            plan = create_simple_plan(task, list(self.tools.keys()))
        
        if not plan:
            print("  ⚠ Warning: Could not create plan. Using fallback.")
            plan = self._create_fallback_plan(task)
        
        print(f"  Plan created with {len(plan)} step(s):")
        for step in plan:
            print(f"    {step.get('step', '?')}. {step.get('description', 'No description')}")
        
        # Step 3: Record task start in memory
        print("\n[3/5] Updating memory...")
        task_id = self.state.start_task(task, plan)
        print(f"  Task ID: {task_id}")
        
        # Step 4: Execute plan
        print("\n[4/5] Executing plan...")
        self.core_agent.set_plan(plan)
        results = self.core_agent.execute_plan()
        
        # Record results in memory
        for i, result in enumerate(results):
            self.state.record_step_result(i, {
                "success": result.success,
                "output": str(result.output),
                "error": result.error,
                "retries": result.retries
            })
        
        # Step 5: Complete task and update memory
        print("\n[5/5] Completing task...")
        status = self.core_agent.get_status()
        task_record = self.state.complete_task(status["status"])
        
        # Print summary
        print("\n" + "=" * 60)
        print("  EXECUTION SUMMARY")
        print("=" * 60)
        print(f"  Task: {task}")
        print(f"  Status: {status['status'].upper()}")
        print(f"  Steps: {status['completed_steps']}/{status['total_steps']}")
        print(f"  Successes: {status['success_count']}")
        print(f"  Failures: {status['failure_count']}")
        print("=" * 60)
        
        return {
            "task": task,
            "task_id": task_id,
            "status": status["status"],
            "plan": plan,
            "results": [
                {
                    "success": r.success,
                    "output": r.output,
                    "error": r.error,
                    "retries": r.retries
                }
                for r in results
            ],
            "stats": self.state.get_stats()
        }
    
    def _create_fallback_plan(self, task: str) -> list[dict]:
        """Create a basic fallback plan when no planner is available"""
        return [{
            "step": 1,
            "tool": "run_command",
            "args": {"command": f"echo 'Task received: {task}'"},
            "description": "Acknowledge task",
            "depends_on": []
        }]
    
    def get_available_tools(self) -> list[str]:
        """Get list of available tool names"""
        return list(self.tools.keys())
    
    def get_available_flows(self) -> list[dict]:
        """Get list of available flows/blueprints"""
        return list_blueprints()
    
    def get_flow_config(self, flow: str) -> dict:
        """Get default configuration for a flow"""
        return get_config(flow)
    
    def get_all_configs(self) -> dict:
        """Get all available configurations"""
        return list_configs()
    
    def get_stats(self) -> dict:
        """Get runtime statistics"""
        return self.state.get_stats()
    
    def get_history(self, limit: int = 10) -> list[dict]:
        """Get task execution history"""
        return self.state.get_task_history(limit)


def run_example_task():
    """Run the example task: Create a new folder and write a hello world file"""
    
    # Initialize runtime (without LLM planner for demo)
    runtime = MasidyAgentRuntime(use_llm_planner=False)
    
    # Define the example task
    task = "Create a new folder called 'hello_demo' and write a hello world file inside it"
    
    # Run the task
    result = runtime.run_task(task)
    
    # Verify the results
    print("\n🔍 Verification:")
    print("-" * 40)
    
    from tools.file_tools import file_exists, read_file
    
    folder_check = file_exists("hello_demo")
    if folder_check.get("exists") and folder_check.get("is_directory"):
        print("  ✓ Folder 'hello_demo' exists")
    else:
        print("  ✗ Folder 'hello_demo' not found")
    
    file_check = file_exists("hello_demo/hello.txt")
    if file_check.get("exists") and file_check.get("is_file"):
        print("  ✓ File 'hello_demo/hello.txt' exists")
        content = read_file("hello_demo/hello.txt")
        if content.get("success"):
            print(f"  ✓ File content: {content['content']}")
    else:
        print("  ✗ File 'hello_demo/hello.txt' not found")
    
    return result


def interactive_mode():
    """Run in interactive mode with flow selection and config"""
    
    print("\n" + "=" * 60)
    print("  🚀 Masidy Agent - Interactive Mode")
    print("=" * 60)
    print("  Commands:")
    print("    flows     - List available flows")
    print("    config    - Show flow configurations")
    print("    tools     - List available tools")
    print("    stats     - Show statistics")
    print("    history   - Show task history")
    print("    quit      - Exit")
    print("=" * 60)
    
    runtime = MasidyAgentRuntime(use_llm_planner=False, quiet=True)
    
    while True:
        try:
            # Ask for flow selection
            print("\n📦 Available flows: saas, api, refactor (or 'auto' to infer)")
            flow_input = input("Select flow (or press Enter for auto): ").strip().lower()
            
            if flow_input == "quit":
                print("Goodbye!")
                break
            
            if flow_input == "flows":
                flows = runtime.get_available_flows()
                print("\n📦 Available Flows:")
                for f in flows:
                    print(f"  • {f['name']}: {f['description']}")
                    if f.get('components'):
                        print(f"    Components: {', '.join(f['components'])}")
                continue
            
            if flow_input == "config":
                print("\n⚙️  Flow Configurations:")
                for flow_name in ["saas", "api", "refactor"]:
                    cfg = runtime.get_flow_config(flow_name)
                    print(f"\n  [{flow_name.upper()}]")
                    print(f"    project_name: {cfg.get('project_name', 'N/A')}")
                    print(f"    database: {cfg.get('database', {}).get('type', 'N/A')}")
                    print(f"    docker: {cfg.get('docker', {}).get('enabled', 'N/A')}")
                    print(f"    ci: {cfg.get('ci', {}).get('enabled', 'N/A')}")
                continue
            
            if flow_input == "tools":
                tools = runtime.get_available_tools()
                print(f"\n🔧 Available Tools ({len(tools)}):")
                for i, tool in enumerate(tools, 1):
                    print(f"  {i:2}. {tool}")
                continue
            
            if flow_input == "stats":
                stats = runtime.get_stats()
                print("\n📊 Statistics:")
                for key, value in stats.items():
                    print(f"  {key}: {value}")
                continue
            
            if flow_input == "history":
                history = runtime.get_history()
                print("\n📜 Recent Tasks:")
                if history:
                    for record in history:
                        print(f"  - {record['task'][:50]}... ({record['status']})")
                else:
                    print("  No task history yet.")
                continue
            
            # Get task description
            task = input("\n📝 Describe what you want to build: ").strip()
            
            if not task:
                print("Task description required.")
                continue
            
            if task.lower() == "quit":
                print("Goodbye!")
                break
            
            # Determine flow
            flow = None if flow_input in ["auto", ""] else flow_input
            
            # Get config for the flow
            config = runtime.get_flow_config(flow) if flow else None
            
            # Run the flow
            runtime.run_flow(flow, task, config)
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


def print_premium_summary(result: dict, task: str):
    """Print a premium formatted summary of the execution"""
    status = result.get("status", "unknown")
    steps_completed = result.get("steps_completed", 0)
    steps_total = result.get("steps_total", 0)
    output_path = result.get("output_path")
    errors = result.get("errors", [])
    flow = result.get("routed_flow", "unknown")
    duration_ms = result.get("duration_ms", 0)
    
    # Status symbols
    if status == "success":
        status_icon = "✅"
        status_text = "SUCCESS"
    elif status == "partial":
        status_icon = "⚠️"
        status_text = "PARTIAL"
    else:
        status_icon = "❌"
        status_text = "FAILURE"
    
    print("\n" + "═" * 60)
    print("  🚀 MASIDY AGENT RUNTIME - EXECUTION SUMMARY")
    print("═" * 60)
    print(f"  Flow:           {flow.upper()}")
    print(f"  Task:           {task[:45]}{'...' if len(task) > 45 else ''}")
    print(f"  Status:         {status_icon} {status_text}")
    print(f"  Steps:          {steps_completed} / {steps_total} completed")
    if duration_ms > 0:
        print(f"  Duration:       {duration_ms:.0f}ms ({duration_ms/1000:.2f}s)")
    if output_path:
        print(f"  Output:         ./{output_path}/")
    if errors:
        print(f"  Errors:         {len(errors)}")
        for err in errors[:3]:  # Show first 3 errors
            err_msg = err.get("error", str(err))[:50]
            print(f"                  - {err_msg}")
        if len(errors) > 3:
            print(f"                  ... and {len(errors) - 3} more")
    print("═" * 60)


def main():
    """Main entry point"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(
        description="Masidy Autonomous Agent Runtime - Premium Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run SaaS flow
  python main.py --flow saas --task "Build a task management SaaS"
  
  # Run API flow
  python main.py --flow api --task "Create an API for notes with CRUD"
  
  # Run API flow with verbose output
  python main.py --flow api --task "Create an API" --verbose
  
  # Run refactor flow
  python main.py --flow refactor --task "Modernize this repo and add CI"
  
  # Auto-detect flow
  python main.py --task "Build a REST API for user management"
  
  # Interactive mode
  python main.py --interactive
  
  # Show flow config
  python main.py --show-config api
"""
    )
    parser.add_argument(
        "--flow", "-f",
        type=str,
        choices=["saas", "api", "refactor"],
        help="Flow to run: saas (full-stack), api (backend), refactor (modernize)"
    )
    parser.add_argument(
        "--task", "-t",
        type=str,
        help="Task description"
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="JSON config overrides (e.g., '{\"project_name\": \"myapp\"}')"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed step-by-step execution output"
    )
    parser.add_argument(
        "--example",
        action="store_true",
        help="Run the simple example task (create folder + hello world)"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="Use LLM-based planner (requires OPENAI_API_KEY)"
    )
    parser.add_argument(
        "--list-flows",
        action="store_true",
        help="List available flows and exit"
    )
    parser.add_argument(
        "--show-config",
        type=str,
        choices=["saas", "api", "refactor"],
        help="Show default config for a flow and exit"
    )
    
    args = parser.parse_args()
    
    # Show config for a flow
    if args.show_config:
        print(f"\n⚙️  Configuration for [{args.show_config.upper()}] flow:")
        print("-" * 50)
        cfg = get_config(args.show_config)
        print(json.dumps(cfg, indent=2))
        return
    
    # List flows
    if args.list_flows:
        print("\n📦 Available Flows:")
        print("-" * 50)
        for bp in list_blueprints():
            print(f"\n  {bp['name']}")
            print(f"    {bp['description']}")
            print(f"    Components: {', '.join(bp.get('components', []))}")
        return
    
    # Simple example
    if args.example:
        run_example_task()
        return
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Run with flow
    if args.task:
        runtime = MasidyAgentRuntime(use_llm_planner=args.use_llm)
        
        # Parse config overrides if provided
        config_overrides = None
        if args.config:
            try:
                config_overrides = json.loads(args.config)
            except json.JSONDecodeError as e:
                print(f"❌ Invalid config JSON: {e}")
                return
        
        if args.flow:
            # Explicit flow with optional config
            base_config = get_config(args.flow)
            if config_overrides:
                base_config.update(config_overrides)
            result = runtime.run_flow(args.flow, args.task, base_config, verbose=args.verbose)
        else:
            # Auto-detect: check if it looks like a blueprint task
            inferred = infer_blueprint(args.task)
            # If inferred with confidence, use flow mode
            task_lower = args.task.lower()
            if any(kw in task_lower for kw in ["saas", "api", "refactor", "full stack", "backend", "modernize"]):
                result = runtime.run_flow(inferred, args.task, config_overrides, verbose=args.verbose)
            else:
                # Simple task mode
                result = runtime.run_task(args.task)
        
        # Print premium summary
        print_premium_summary(result, args.task)
        return
    
    # Default: show help
    print("=" * 60)
    print("  🚀 Masidy Autonomous Agent Runtime - Premium Edition")
    print("=" * 60)
    print("\n  Use --help for all options, or try:")
    print("\n  Quick start:")
    print("    python main.py --flow saas --task 'Build a task manager'")
    print("    python main.py --flow api --task 'Create a notes API'")
    print("    python main.py --interactive")
    print("\n  With verbose output:")
    print("    python main.py --flow api --task 'Create an API' --verbose")
    print("\n  Show config:")
    print("    python main.py --show-config api")
    print("\n  Simple demo:")
    print("    python main.py --example")
    print()


if __name__ == "__main__":
    main()
