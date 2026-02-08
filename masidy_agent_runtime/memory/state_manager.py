"""
Masidy Autonomous Agent Runtime - State Manager
Handles persistent memory and state management
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, asdict
import threading


@dataclass
class TaskRecord:
    """Record of a completed task"""
    task: str
    status: str  # completed, failed
    plan: list[dict]
    results: list[dict]
    started_at: str
    completed_at: str
    steps_executed: int
    steps_succeeded: int


class StateManager:
    """
    Manages persistent state for the agent runtime.
    Thread-safe with automatic saving.
    """
    
    def __init__(self, state_file: Optional[str] = None):
        if state_file is None:
            # Default to state.json in the same directory
            state_file = Path(__file__).parent / "state.json"
        
        self.state_file = Path(state_file)
        self._lock = threading.Lock()
        self._state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load state from file or create default"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Return default state
        return {
            "version": "1.0.0",
            "agent_name": "Masidy Autonomous Agent",
            "current_task": None,
            "task_history": [],
            "execution_stats": {
                "total_tasks": 0,
                "completed_tasks": 0,
                "failed_tasks": 0,
                "total_steps_executed": 0
            },
            "last_updated": None,
            "context": {}
        }
    
    def _save_state(self) -> None:
        """Save state to file"""
        self._state["last_updated"] = datetime.now().isoformat()
        
        # Ensure directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.state_file, "w") as f:
            json.dump(self._state, f, indent=4, default=str)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from state"""
        with self._lock:
            return self._state.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True) -> None:
        """Set a value in state"""
        with self._lock:
            self._state[key] = value
            if save:
                self._save_state()
    
    def update_context(self, key: str, value: Any) -> None:
        """Update the context dictionary"""
        with self._lock:
            if "context" not in self._state:
                self._state["context"] = {}
            self._state["context"][key] = value
            self._save_state()
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a value from context"""
        with self._lock:
            return self._state.get("context", {}).get(key, default)
    
    def start_task(self, task: str, plan: list[dict]) -> str:
        """Record the start of a new task"""
        with self._lock:
            task_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            self._state["current_task"] = {
                "id": task_id,
                "task": task,
                "plan": plan,
                "status": "in_progress",
                "started_at": datetime.now().isoformat(),
                "results": []
            }
            
            self._state["execution_stats"]["total_tasks"] += 1
            self._save_state()
            
            return task_id
    
    def record_step_result(self, step_index: int, result: dict) -> None:
        """Record the result of a step execution"""
        with self._lock:
            if self._state.get("current_task"):
                self._state["current_task"]["results"].append({
                    "step": step_index,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                })
                self._state["execution_stats"]["total_steps_executed"] += 1
                self._save_state()
    
    def complete_task(self, status: str = "completed") -> Optional[TaskRecord]:
        """Mark the current task as completed"""
        with self._lock:
            current = self._state.get("current_task")
            if not current:
                return None
            
            # Create task record
            results = current.get("results", [])
            steps_succeeded = sum(
                1 for r in results 
                if r.get("result", {}).get("success", False)
            )
            
            record = TaskRecord(
                task=current["task"],
                status=status,
                plan=current.get("plan", []),
                results=results,
                started_at=current.get("started_at", ""),
                completed_at=datetime.now().isoformat(),
                steps_executed=len(results),
                steps_succeeded=steps_succeeded
            )
            
            # Add to history
            self._state["task_history"].append(asdict(record))
            
            # Update stats
            if status == "completed":
                self._state["execution_stats"]["completed_tasks"] += 1
            else:
                self._state["execution_stats"]["failed_tasks"] += 1
            
            # Clear current task
            self._state["current_task"] = None
            self._save_state()
            
            return record
    
    def get_task_history(self, limit: int = 10) -> list[dict]:
        """Get recent task history"""
        with self._lock:
            history = self._state.get("task_history", [])
            return history[-limit:]
    
    def get_stats(self) -> dict:
        """Get execution statistics"""
        with self._lock:
            return self._state.get("execution_stats", {}).copy()
    
    def clear_history(self) -> None:
        """Clear task history"""
        with self._lock:
            self._state["task_history"] = []
            self._save_state()
    
    def reset_stats(self) -> None:
        """Reset execution statistics"""
        with self._lock:
            self._state["execution_stats"] = {
                "total_tasks": 0,
                "completed_tasks": 0,
                "failed_tasks": 0,
                "total_steps_executed": 0
            }
            self._save_state()
    
    def export_state(self) -> dict:
        """Export full state as dictionary"""
        with self._lock:
            return self._state.copy()
    
    def import_state(self, state: dict) -> None:
        """Import state from dictionary"""
        with self._lock:
            self._state = state
            self._save_state()


# Global state manager instance
_global_state: Optional[StateManager] = None


def get_state_manager(state_file: Optional[str] = None) -> StateManager:
    """Get or create the global state manager"""
    global _global_state
    
    if _global_state is None:
        _global_state = StateManager(state_file)
    
    return _global_state
