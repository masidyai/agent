"""
Masidy Autonomous Agent Runtime - Default Configuration
Base configuration shared by all flows
"""

from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class DockerConfig:
    """Docker configuration"""
    enabled: bool = True
    base_image: str = "python:3.11-slim"
    expose_port: int = 8000
    compose_version: str = "3.8"


@dataclass
class CIConfig:
    """CI/CD configuration"""
    enabled: bool = True
    provider: str = "github"  # github, gitlab, bitbucket
    python_version: str = "3.11"
    node_version: str = "20"
    run_tests: bool = True
    run_lint: bool = True
    build_docker: bool = True


@dataclass
class DatabaseConfig:
    """Database configuration"""
    type: str = "sqlite"  # sqlite, postgresql, mysql
    name: str = "app.db"
    host: str = "localhost"
    port: int = 5432
    user: str = "user"
    password: str = "password"


@dataclass
class DefaultConfig:
    """Default configuration for all flows"""
    project_name: str = "project"
    output_folder: str = "project"
    description: str = ""
    version: str = "0.1.0"
    author: str = "Masidy Agent"
    license: str = "MIT"
    
    # Feature flags
    include_docker: bool = True
    include_ci: bool = True
    include_tests: bool = True
    include_docs: bool = True
    
    # Sub-configs
    docker: DockerConfig = field(default_factory=DockerConfig)
    ci: CIConfig = field(default_factory=CIConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)


# Default configuration as dict
DEFAULT_CONFIG = {
    "project_name": "project",
    "output_folder": "project",
    "description": "",
    "version": "0.1.0",
    "author": "Masidy Agent",
    "license": "MIT",
    
    # Feature flags
    "include_docker": True,
    "include_ci": True,
    "include_tests": True,
    "include_docs": True,
    
    # Docker settings
    "docker": {
        "enabled": True,
        "base_image": "python:3.11-slim",
        "expose_port": 8000,
        "compose_version": "3.8",
    },
    
    # CI settings
    "ci": {
        "enabled": True,
        "provider": "github",
        "python_version": "3.11",
        "node_version": "20",
        "run_tests": True,
        "run_lint": True,
        "build_docker": True,
    },
    
    # Database settings
    "database": {
        "type": "sqlite",
        "name": "app.db",
        "host": "localhost",
        "port": 5432,
        "user": "user",
        "password": "password",
    },
}


def get_default_config(overrides: Optional[dict] = None) -> dict:
    """
    Get default configuration with optional overrides.
    
    Args:
        overrides: Dict of values to override
    
    Returns:
        Configuration dict
    """
    config = DEFAULT_CONFIG.copy()
    
    if overrides:
        # Deep merge for nested configs
        for key, value in overrides.items():
            if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                config[key] = {**config[key], **value}
            else:
                config[key] = value
    
    return config


def create_config_from_dataclass(
    project_name: str = "project",
    output_folder: Optional[str] = None,
    **kwargs
) -> DefaultConfig:
    """
    Create a configuration object from parameters.
    
    Args:
        project_name: Name of the project
        output_folder: Output folder (defaults to project_name)
        **kwargs: Additional configuration options
    
    Returns:
        DefaultConfig instance
    """
    return DefaultConfig(
        project_name=project_name,
        output_folder=output_folder or project_name,
        **kwargs
    )
