"""
Masidy Autonomous Agent Runtime - SaaS Configuration
Configuration specific to the SaaS blueprint
"""

from typing import Optional
from .defaults import DEFAULT_CONFIG


# SaaS-specific configuration
SAAS_CONFIG = {
    # Project settings
    "project_name": "saas_app",
    "output_folder": "saas_app",
    "description": "Full-stack SaaS application",
    
    # SaaS-specific features
    "include_frontend": True,
    "include_backend": True,
    "include_auth": True,
    "include_docker": True,
    "include_ci": True,
    "include_tests": True,
    
    # Frontend settings
    "frontend": {
        "framework": "react",  # react, nextjs, vue
        "bundler": "vite",
        "port": 3000,
        "typescript": False,
    },
    
    # Backend settings
    "backend": {
        "framework": "fastapi",
        "port": 8000,
        "cors_enabled": True,
        "docs_enabled": True,
    },
    
    # Auth settings
    "auth": {
        "type": "jwt",  # jwt, session, oauth
        "token_expire_minutes": 30,
        "algorithm": "HS256",
        "include_registration": True,
        "include_password_reset": False,
    },
    
    # Database settings
    "database": {
        "type": "sqlite",  # sqlite, postgresql
        "name": "app.db",
        "orm": "sqlalchemy",
    },
    
    # Docker settings
    "docker": {
        "enabled": True,
        "backend_image": "python:3.11-slim",
        "frontend_image": "node:20-alpine",
        "compose_version": "3.8",
        "include_nginx": True,
    },
    
    # CI settings
    "ci": {
        "enabled": True,
        "provider": "github",
        "test_backend": True,
        "test_frontend": False,
        "build_docker": True,
        "deploy": False,
    },
}


def get_saas_config(overrides: Optional[dict] = None) -> dict:
    """
    Get SaaS configuration with optional overrides.
    
    Args:
        overrides: Dict of values to override
    
    Returns:
        Configuration dict
    """
    # Start with defaults
    config = {**DEFAULT_CONFIG}
    
    # Apply SaaS-specific config
    for key, value in SAAS_CONFIG.items():
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


def create_saas_config(
    project_name: str,
    db_type: str = "sqlite",
    include_frontend: bool = True,
    frontend_framework: str = "react",
    **kwargs
) -> dict:
    """
    Create a customized SaaS configuration.
    
    Args:
        project_name: Name of the project
        db_type: Database type (sqlite, postgresql)
        include_frontend: Whether to include frontend
        frontend_framework: Frontend framework to use
        **kwargs: Additional overrides
    
    Returns:
        Configuration dict
    """
    overrides = {
        "project_name": project_name,
        "output_folder": project_name,
        "include_frontend": include_frontend,
        "frontend": {"framework": frontend_framework},
        "database": {"type": db_type},
        **kwargs
    }
    
    return get_saas_config(overrides)


# Preset configurations
SAAS_PRESETS = {
    "minimal": {
        "include_frontend": True,
        "include_auth": True,
        "database": {"type": "sqlite"},
        "docker": {"include_nginx": False},
        "ci": {"build_docker": False},
    },
    "standard": {
        "include_frontend": True,
        "include_auth": True,
        "database": {"type": "sqlite"},
        "docker": {"include_nginx": True},
        "ci": {"build_docker": True},
    },
    "production": {
        "include_frontend": True,
        "include_auth": True,
        "database": {"type": "postgresql"},
        "docker": {"include_nginx": True},
        "ci": {"build_docker": True, "deploy": True},
        "auth": {"include_password_reset": True},
    },
}


def get_saas_preset(preset: str, project_name: str) -> dict:
    """Get a SaaS preset configuration"""
    preset_config = SAAS_PRESETS.get(preset, SAAS_PRESETS["standard"])
    return get_saas_config({
        "project_name": project_name,
        "output_folder": project_name,
        **preset_config
    })
