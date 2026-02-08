"""
Masidy Autonomous Agent Runtime - File Tools
Tools for file system operations
"""

import os
import shutil
from pathlib import Path
from typing import Optional


def create_directory(path: str, parents: bool = True) -> dict:
    """
    Create a directory at the specified path.
    
    Args:
        path: Path where the directory should be created
        parents: If True, create parent directories as needed
    
    Returns:
        dict with status and message
    """
    try:
        Path(path).mkdir(parents=parents, exist_ok=True)
        return {
            "success": True,
            "message": f"Directory created: {path}",
            "path": str(Path(path).absolute())
        }
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: Cannot create directory {path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def write_file(path: str, content: str, encoding: str = "utf-8") -> dict:
    """
    Write content to a file.
    
    Args:
        path: Path to the file
        content: Content to write
        encoding: File encoding (default: utf-8)
    
    Returns:
        dict with status and message
    """
    try:
        # Ensure parent directory exists
        parent = Path(path).parent
        if parent and not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        
        return {
            "success": True,
            "message": f"File written: {path}",
            "path": str(Path(path).absolute()),
            "bytes_written": len(content.encode(encoding))
        }
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: Cannot write to {path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def read_file(path: str, encoding: str = "utf-8") -> dict:
    """
    Read content from a file.
    
    Args:
        path: Path to the file
        encoding: File encoding (default: utf-8)
    
    Returns:
        dict with status, content or error
    """
    try:
        with open(path, "r", encoding=encoding) as f:
            content = f.read()
        
        return {
            "success": True,
            "content": content,
            "path": str(Path(path).absolute()),
            "size": len(content)
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"File not found: {path}"
        }
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: Cannot read {path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def append_to_file(path: str, content: str, encoding: str = "utf-8") -> dict:
    """
    Append content to a file.
    
    Args:
        path: Path to the file
        content: Content to append
        encoding: File encoding (default: utf-8)
    
    Returns:
        dict with status and message
    """
    try:
        with open(path, "a", encoding=encoding) as f:
            f.write(content)
        
        return {
            "success": True,
            "message": f"Content appended to: {path}",
            "bytes_appended": len(content.encode(encoding))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def delete_file(path: str) -> dict:
    """
    Delete a file.
    
    Args:
        path: Path to the file to delete
    
    Returns:
        dict with status and message
    """
    try:
        os.remove(path)
        return {
            "success": True,
            "message": f"File deleted: {path}"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"File not found: {path}"
        }
    except PermissionError:
        return {
            "success": False,
            "error": f"Permission denied: Cannot delete {path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def delete_directory(path: str, recursive: bool = False) -> dict:
    """
    Delete a directory.
    
    Args:
        path: Path to the directory to delete
        recursive: If True, delete contents recursively
    
    Returns:
        dict with status and message
    """
    try:
        if recursive:
            shutil.rmtree(path)
        else:
            os.rmdir(path)
        
        return {
            "success": True,
            "message": f"Directory deleted: {path}"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Directory not found: {path}"
        }
    except OSError as e:
        if "not empty" in str(e).lower():
            return {
                "success": False,
                "error": f"Directory not empty: {path}. Use recursive=True to delete"
            }
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def list_directory(path: str = ".", recursive: bool = False) -> dict:
    """
    List contents of a directory.
    
    Args:
        path: Path to the directory (default: current directory)
        recursive: If True, list contents recursively
    
    Returns:
        dict with status and list of items
    """
    try:
        items = []
        base_path = Path(path)
        
        if recursive:
            for item in base_path.rglob("*"):
                items.append({
                    "name": str(item.relative_to(base_path)),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
        else:
            for item in base_path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
        
        return {
            "success": True,
            "path": str(base_path.absolute()),
            "items": items,
            "count": len(items)
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Directory not found: {path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def copy_file(source: str, destination: str) -> dict:
    """
    Copy a file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
    
    Returns:
        dict with status and message
    """
    try:
        # Ensure destination parent exists
        dest_parent = Path(destination).parent
        if dest_parent and not dest_parent.exists():
            dest_parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(source, destination)
        
        return {
            "success": True,
            "message": f"File copied from {source} to {destination}",
            "source": str(Path(source).absolute()),
            "destination": str(Path(destination).absolute())
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Source file not found: {source}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def move_file(source: str, destination: str) -> dict:
    """
    Move a file from source to destination.
    
    Args:
        source: Source file path
        destination: Destination file path
    
    Returns:
        dict with status and message
    """
    try:
        # Ensure destination parent exists
        dest_parent = Path(destination).parent
        if dest_parent and not dest_parent.exists():
            dest_parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(source, destination)
        
        return {
            "success": True,
            "message": f"File moved from {source} to {destination}",
            "destination": str(Path(destination).absolute())
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Source not found: {source}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def file_exists(path: str) -> dict:
    """
    Check if a file or directory exists.
    
    Args:
        path: Path to check
    
    Returns:
        dict with existence status
    """
    p = Path(path)
    return {
        "success": True,
        "exists": p.exists(),
        "is_file": p.is_file() if p.exists() else None,
        "is_directory": p.is_dir() if p.exists() else None,
        "path": str(p.absolute())
    }


# Tool registry for easy access
FILE_TOOLS = {
    "create_directory": create_directory,
    "write_file": write_file,
    "read_file": read_file,
    "append_to_file": append_to_file,
    "delete_file": delete_file,
    "delete_directory": delete_directory,
    "list_directory": list_directory,
    "copy_file": copy_file,
    "move_file": move_file,
    "file_exists": file_exists,
}
