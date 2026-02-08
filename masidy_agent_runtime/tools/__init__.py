"""
Masidy Autonomous Agent Runtime - Tools Module
"""

from .file_tools import FILE_TOOLS
from .command_tools import COMMAND_TOOLS
from .github_tools import GITHUB_TOOLS

# Combined tool registry
ALL_TOOLS = {}
ALL_TOOLS.update(FILE_TOOLS)
ALL_TOOLS.update(COMMAND_TOOLS)
ALL_TOOLS.update(GITHUB_TOOLS)

__all__ = [
    "FILE_TOOLS",
    "COMMAND_TOOLS",
    "GITHUB_TOOLS",
    "ALL_TOOLS",
]
