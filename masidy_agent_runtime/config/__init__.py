"""
Masidy Autonomous Agent Runtime - Config Module
Configuration management for flows and blueprints
"""

from .defaults import DEFAULT_CONFIG, get_default_config
from .saas_config import SAAS_CONFIG, get_saas_config
from .api_config import API_CONFIG, get_api_config
from .refactor_config import REFACTOR_CONFIG, get_refactor_config

# Config registry
FLOW_CONFIGS = {
    "saas": SAAS_CONFIG,
    "api": API_CONFIG,
    "refactor": REFACTOR_CONFIG,
}


def get_config(flow: str, overrides: dict = None) -> dict:
    """
    Get configuration for a specific flow.
    
    Args:
        flow: Flow name ('saas', 'api', 'refactor')
        overrides: Optional config overrides
    
    Returns:
        Merged configuration dict
    """
    # Start with defaults
    config = DEFAULT_CONFIG.copy()
    
    # Add flow-specific config
    flow_config = FLOW_CONFIGS.get(flow, {})
    config.update(flow_config)
    
    # Apply overrides
    if overrides:
        config.update(overrides)
    
    return config


def list_configs() -> dict:
    """List all available configurations"""
    return {
        "default": DEFAULT_CONFIG,
        "flows": {
            name: cfg for name, cfg in FLOW_CONFIGS.items()
        }
    }


__all__ = [
    "DEFAULT_CONFIG",
    "SAAS_CONFIG",
    "API_CONFIG", 
    "REFACTOR_CONFIG",
    "FLOW_CONFIGS",
    "get_config",
    "get_default_config",
    "get_saas_config",
    "get_api_config",
    "get_refactor_config",
    "list_configs",
]
