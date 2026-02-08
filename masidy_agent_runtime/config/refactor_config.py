"""
Masidy Autonomous Agent Runtime - Refactor Configuration
Configuration specific to the Refactor blueprint
"""

from typing import Optional
from .defaults import DEFAULT_CONFIG


# Refactor-specific configuration
REFACTOR_CONFIG = {
    # Project settings
    "project_name": "refactored_project",
    "output_folder": ".",  # Refactor in place
    "description": "Modernized and improved project",
    
    # Target settings
    "target_path": ".",
    
    # Analysis settings
    "analysis": {
        "detect_framework": True,
        "detect_languages": True,
        "count_files": True,
        "check_tests": True,
        "check_docker": True,
        "check_ci": True,
    },
    
    # Testing settings
    "testing": {
        "run_existing_tests": True,
        "timeout_seconds": 120,
        "fail_on_error": False,
    },
    
    # Cleanup settings
    "cleanup": {
        "enabled": True,
        "remove_cache": False,  # __pycache__, node_modules (careful!)
        "remove_logs": False,
        "identify_unused": True,
        "safe_mode": True,  # Only suggest, don't delete
    },
    
    # Documentation settings
    "documentation": {
        "improve_readme": True,
        "add_sections": True,
        "create_if_missing": True,
        "add_badges": False,
    },
    
    # Docker settings
    "docker": {
        "enabled": True,
        "add_if_missing": True,
        "update_existing": False,
        "add_dockerignore": True,
    },
    
    # CI settings
    "ci": {
        "enabled": True,
        "provider": "github",
        "add_if_missing": True,
        "update_existing": False,
    },
    
    # Git settings
    "git": {
        "check_gitignore": True,
        "improve_gitignore": True,
    },
}


def get_refactor_config(overrides: Optional[dict] = None) -> dict:
    """
    Get refactor configuration with optional overrides.
    
    Args:
        overrides: Dict of values to override
    
    Returns:
        Configuration dict
    """
    # Start with defaults
    config = {**DEFAULT_CONFIG}
    
    # Apply refactor-specific config
    for key, value in REFACTOR_CONFIG.items():
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


def create_refactor_config(
    target_path: str = ".",
    run_tests: bool = True,
    add_docker: bool = True,
    add_ci: bool = True,
    **kwargs
) -> dict:
    """
    Create a customized refactor configuration.
    
    Args:
        target_path: Path to the project to refactor
        run_tests: Whether to run existing tests
        add_docker: Whether to add Docker if missing
        add_ci: Whether to add CI if missing
        **kwargs: Additional overrides
    
    Returns:
        Configuration dict
    """
    overrides = {
        "target_path": target_path,
        "testing": {"run_existing_tests": run_tests},
        "docker": {"add_if_missing": add_docker},
        "ci": {"add_if_missing": add_ci},
        **kwargs
    }
    
    return get_refactor_config(overrides)


# Preset configurations
REFACTOR_PRESETS = {
    "light": {
        "cleanup": {"enabled": False},
        "documentation": {"improve_readme": True, "add_sections": False},
        "docker": {"add_if_missing": False},
        "ci": {"add_if_missing": False},
    },
    "standard": {
        "cleanup": {"enabled": True, "safe_mode": True},
        "documentation": {"improve_readme": True, "add_sections": True},
        "docker": {"add_if_missing": True},
        "ci": {"add_if_missing": True},
    },
    "aggressive": {
        "cleanup": {"enabled": True, "safe_mode": False, "remove_cache": True},
        "documentation": {"improve_readme": True, "add_sections": True, "add_badges": True},
        "docker": {"add_if_missing": True, "update_existing": True},
        "ci": {"add_if_missing": True, "update_existing": True},
    },
}


def get_refactor_preset(preset: str, target_path: str = ".") -> dict:
    """Get a refactor preset configuration"""
    preset_config = REFACTOR_PRESETS.get(preset, REFACTOR_PRESETS["standard"])
    return get_refactor_config({
        "target_path": target_path,
        **preset_config
    })
