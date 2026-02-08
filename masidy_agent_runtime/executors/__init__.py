"""
Masidy Autonomous Agent Runtime - Executors Module
Handles structured plan execution with retries and result tracking
"""

from .base_executor import BaseExecutor, ExecutionResult, StepResult
from .saas_executor import SaaSExecutor
from .api_executor import APIExecutor
from .refactor_executor import RefactorExecutor

# Executor registry
EXECUTORS = {
    "saas": SaaSExecutor,
    "api": APIExecutor,
    "refactor": RefactorExecutor,
}


def get_executor(flow: str, **kwargs):
    """Get an executor instance for a flow"""
    executor_class = EXECUTORS.get(flow)
    if executor_class:
        return executor_class(**kwargs)
    return None


__all__ = [
    "BaseExecutor",
    "ExecutionResult",
    "StepResult",
    "SaaSExecutor",
    "APIExecutor",
    "RefactorExecutor",
    "EXECUTORS",
    "get_executor",
]
