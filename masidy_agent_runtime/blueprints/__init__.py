"""
Masidy Autonomous Agent Runtime - Blueprints Module
High-level end-to-end flows for creating complete projects
"""

from .saas_blueprint import run_blueprint as run_saas_blueprint, SAAS_BLUEPRINT_INFO
from .api_blueprint import run_blueprint as run_api_blueprint, API_BLUEPRINT_INFO
from .refactor_blueprint import run_blueprint as run_refactor_blueprint, REFACTOR_BLUEPRINT_INFO

# Blueprint registry
BLUEPRINTS = {
    "saas": {
        "run": run_saas_blueprint,
        "info": SAAS_BLUEPRINT_INFO,
    },
    "api": {
        "run": run_api_blueprint,
        "info": API_BLUEPRINT_INFO,
    },
    "refactor": {
        "run": run_refactor_blueprint,
        "info": REFACTOR_BLUEPRINT_INFO,
    },
}


def get_blueprint(name: str):
    """Get a blueprint by name"""
    return BLUEPRINTS.get(name.lower())


def list_blueprints() -> list[dict]:
    """List all available blueprints with their info"""
    return [
        {"name": name, **bp["info"]}
        for name, bp in BLUEPRINTS.items()
    ]


def infer_blueprint(task_description: str) -> str:
    """Infer the best blueprint based on task description"""
    task_lower = task_description.lower()
    
    # SaaS indicators
    saas_keywords = [
        "saas", "software as a service", "subscription", "billing",
        "frontend and backend", "full stack", "fullstack", "full-stack",
        "react", "next.js", "nextjs", "web app", "webapp", "dashboard",
        "user management", "multi-tenant", "landing page"
    ]
    
    # API indicators
    api_keywords = [
        "api", "rest", "restful", "endpoint", "crud", "backend only",
        "microservice", "service", "json api", "data service",
        "fastapi", "flask", "no frontend", "backend"
    ]
    
    # Refactor indicators
    refactor_keywords = [
        "refactor", "modernize", "clean", "improve", "fix",
        "upgrade", "update", "existing", "legacy", "migrate",
        "document", "add ci", "add tests", "restructure"
    ]
    
    # Score each blueprint
    scores = {
        "saas": sum(1 for kw in saas_keywords if kw in task_lower),
        "api": sum(1 for kw in api_keywords if kw in task_lower),
        "refactor": sum(1 for kw in refactor_keywords if kw in task_lower),
    }
    
    # Return highest scoring, default to saas
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "saas"


__all__ = [
    "BLUEPRINTS",
    "get_blueprint",
    "list_blueprints",
    "infer_blueprint",
    "run_saas_blueprint",
    "run_api_blueprint", 
    "run_refactor_blueprint",
]
