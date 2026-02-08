"""
Masidy Autonomous Agent Runtime - API Configuration
Configuration specific to the API blueprint
"""

from typing import Optional
from .defaults import DEFAULT_CONFIG


# API-specific configuration
API_CONFIG = {
    # Project settings
    "project_name": "api_service",
    "output_folder": "api_service",
    "description": "RESTful API service",
    
    # API-specific features
    "include_frontend": False,
    "include_backend": True,
    "include_docker": True,
    "include_ci": True,
    "include_tests": True,
    
    # Backend settings
    "backend": {
        "framework": "fastapi",
        "port": 8000,
        "cors_enabled": True,
        "docs_enabled": True,
        "redoc_enabled": True,
        "versioning": True,  # /api/v1/
    },
    
    # Database settings
    "database": {
        "type": "sqlite",  # sqlite, postgresql, mysql
        "name": "app.db",
        "orm": "sqlalchemy",
        "migrations": False,  # Use alembic
    },
    
    # API settings
    "api": {
        "prefix": "/api/v1",
        "include_health": True,
        "include_openapi": True,
        "rate_limiting": False,
        "pagination": True,
        "default_page_size": 20,
    },
    
    # Docker settings
    "docker": {
        "enabled": True,
        "base_image": "python:3.11-slim",
        "expose_port": 8000,
        "compose_version": "3.8",
        "health_check": True,
    },
    
    # CI settings
    "ci": {
        "enabled": True,
        "provider": "github",
        "python_version": "3.11",
        "run_tests": True,
        "run_lint": True,
        "build_docker": True,
        "test_coverage": False,
    },
    
    # Testing settings
    "testing": {
        "framework": "pytest",
        "async_tests": True,
        "test_client": "httpx",
        "fixtures": True,
    },
}


def get_api_config(overrides: Optional[dict] = None) -> dict:
    """
    Get API configuration with optional overrides.
    
    Args:
        overrides: Dict of values to override
    
    Returns:
        Configuration dict
    """
    # Start with defaults
    config = {**DEFAULT_CONFIG}
    
    # Apply API-specific config
    for key, value in API_CONFIG.items():
        if key in config and isinstance(config[key], dict) and isinstance(value, dict):
            config[key] = {**config[key], **value}
        else:
            config[key] = value
    
    # Apply user overrides
    if overrides:
        for key, value in overrides.items():
            if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                config[key] = {**config[key], **value}
            else:
                config[key] = value
    
    return config


def create_api_config(
    project_name: str,
    db_type: str = "sqlite",
    include_tests: bool = True,
    **kwargs
) -> dict:
    """
    Create a customized API configuration.
    
    Args:
        project_name: Name of the project
        db_type: Database type (sqlite, postgresql, mysql)
        include_tests: Whether to include tests
        **kwargs: Additional overrides
    
    Returns:
        Configuration dict
    """
    overrides = {
        "project_name": project_name,
        "output_folder": project_name,
        "include_tests": include_tests,
        "database": {"type": db_type},
        **kwargs
    }
    
    return get_api_config(overrides)


# Preset configurations
API_PRESETS = {
    "minimal": {
        "database": {"type": "sqlite"},
        "docker": {"health_check": False},
        "ci": {"build_docker": False, "run_lint": False},
        "api": {"rate_limiting": False},
    },
    "standard": {
        "database": {"type": "sqlite"},
        "docker": {"health_check": True},
        "ci": {"build_docker": True, "run_lint": True},
        "api": {"rate_limiting": False},
    },
    "production": {
        "database": {"type": "postgresql", "migrations": True},
        "docker": {"health_check": True},
        "ci": {"build_docker": True, "test_coverage": True},
        "api": {"rate_limiting": True},
    },
}


def get_api_preset(preset: str, project_name: str) -> dict:
    """Get an API preset configuration"""
    preset_config = API_PRESETS.get(preset, API_PRESETS["standard"])
    return get_api_config({
        "project_name": project_name,
        "output_folder": project_name,
        **preset_config
    })
