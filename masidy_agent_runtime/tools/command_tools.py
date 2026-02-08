"""
Masidy Autonomous Agent Runtime - Command Tools
Tools for executing shell commands and system operations
"""

import os
import subprocess
import shlex
from typing import Optional
from pathlib import Path


def run_command(
    command: str,
    cwd: Optional[str] = None,
    timeout: int = 60,
    shell: bool = True,
    capture_output: bool = True
) -> dict:
    """
    Execute a shell command.
    
    Args:
        command: Command to execute
        cwd: Working directory for the command
        timeout: Timeout in seconds (default: 60)
        shell: Run through shell (default: True)
        capture_output: Capture stdout/stderr (default: True)
    
    Returns:
        dict with status, output, and return code
    """
    try:
        result = subprocess.run(
            command,
            shell=shell,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        
        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout.strip() if result.stdout else "",
            "stderr": result.stderr.strip() if result.stderr else "",
            "command": command,
            "cwd": cwd or os.getcwd()
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds",
            "command": command
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Command not found: {command.split()[0] if command else 'empty'}",
            "command": command
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": command
        }


def run_python_script(
    script_path: str,
    args: Optional[list[str]] = None,
    cwd: Optional[str] = None,
    timeout: int = 120
) -> dict:
    """
    Execute a Python script.
    
    Args:
        script_path: Path to the Python script
        args: Command line arguments for the script
        cwd: Working directory
        timeout: Timeout in seconds (default: 120)
    
    Returns:
        dict with status and output
    """
    if not Path(script_path).exists():
        return {
            "success": False,
            "error": f"Script not found: {script_path}"
        }
    
    cmd_parts = ["python", script_path]
    if args:
        cmd_parts.extend(args)
    
    command = " ".join(shlex.quote(p) for p in cmd_parts)
    return run_command(command, cwd=cwd, timeout=timeout)


def run_pip_install(
    packages: list[str],
    upgrade: bool = False,
    quiet: bool = True
) -> dict:
    """
    Install Python packages using pip.
    
    Args:
        packages: List of package names to install
        upgrade: Upgrade packages if already installed
        quiet: Suppress output (default: True)
    
    Returns:
        dict with status and output
    """
    cmd_parts = ["pip", "install"]
    
    if upgrade:
        cmd_parts.append("--upgrade")
    if quiet:
        cmd_parts.append("-q")
    
    cmd_parts.extend(packages)
    command = " ".join(cmd_parts)
    
    return run_command(command, timeout=300)


def get_environment_variable(name: str) -> dict:
    """
    Get an environment variable value.
    
    Args:
        name: Name of the environment variable
    
    Returns:
        dict with value or error
    """
    value = os.environ.get(name)
    
    if value is not None:
        return {
            "success": True,
            "name": name,
            "value": value
        }
    else:
        return {
            "success": False,
            "error": f"Environment variable not found: {name}",
            "name": name
        }


def set_environment_variable(name: str, value: str) -> dict:
    """
    Set an environment variable.
    
    Args:
        name: Name of the environment variable
        value: Value to set
    
    Returns:
        dict with status
    """
    try:
        os.environ[name] = value
        return {
            "success": True,
            "message": f"Environment variable set: {name}",
            "name": name
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_current_directory() -> dict:
    """
    Get the current working directory.
    
    Returns:
        dict with current directory path
    """
    return {
        "success": True,
        "path": os.getcwd()
    }


def change_directory(path: str) -> dict:
    """
    Change the current working directory.
    
    Args:
        path: Directory to change to
    
    Returns:
        dict with status and new path
    """
    try:
        os.chdir(path)
        return {
            "success": True,
            "message": f"Changed directory to: {path}",
            "path": os.getcwd()
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Directory not found: {path}"
        }
    except NotADirectoryError:
        return {
            "success": False,
            "error": f"Not a directory: {path}"
        }
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: {path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def which_command(command_name: str) -> dict:
    """
    Find the path of a command (similar to 'which' in Unix).
    
    Args:
        command_name: Name of the command to find
    
    Returns:
        dict with path or error
    """
    import shutil
    
    path = shutil.which(command_name)
    
    if path:
        return {
            "success": True,
            "command": command_name,
            "path": path
        }
    else:
        return {
            "success": False,
            "error": f"Command not found: {command_name}",
            "command": command_name
        }


def get_system_info() -> dict:
    """
    Get basic system information.
    
    Returns:
        dict with system information
    """
    import platform
    
    return {
        "success": True,
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "processor": platform.processor()
    }


def run_background_command(
    command: str,
    cwd: Optional[str] = None,
    log_file: Optional[str] = None
) -> dict:
    """
    Start a command in the background.
    
    Args:
        command: Command to execute
        cwd: Working directory
        log_file: File to redirect output to
    
    Returns:
        dict with process ID
    """
    try:
        if log_file:
            full_command = f"{command} > {log_file} 2>&1 &"
        else:
            full_command = f"{command} &"
        
        result = subprocess.Popen(
            full_command,
            shell=True,
            cwd=cwd,
            start_new_session=True
        )
        
        return {
            "success": True,
            "pid": result.pid,
            "command": command,
            "message": "Command started in background"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Tool registry for easy access
COMMAND_TOOLS = {
    "run_command": run_command,
    "run_python_script": run_python_script,
    "run_pip_install": run_pip_install,
    "get_environment_variable": get_environment_variable,
    "set_environment_variable": set_environment_variable,
    "get_current_directory": get_current_directory,
    "change_directory": change_directory,
    "which_command": which_command,
    "get_system_info": get_system_info,
    "run_background_command": run_background_command,
}
