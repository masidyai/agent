"""
Visual Builder API endpoints
Drag-and-drop component editor
"""
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/visual-builder", tags=["visual-builder"])


# Component definitions
class ComponentProperty(BaseModel):
    """Property definition for a component"""
    name: str
    type: str  # string, number, boolean, color, select, etc.
    default: Any = None
    options: Optional[List[str]] = None  # For select type
    description: Optional[str] = None


class ComponentDefinition(BaseModel):
    """Definition of a UI component"""
    id: str
    name: str
    category: str  # layout, input, display, navigation, etc.
    icon: str
    properties: List[ComponentProperty]
    children_allowed: bool = False
    default_styles: Dict[str, Any] = {}


class ComponentInstance(BaseModel):
    """Instance of a component in a layout"""
    id: str
    component_id: str
    properties: Dict[str, Any] = {}
    styles: Dict[str, Any] = {}
    children: List["ComponentInstance"] = []


ComponentInstance.model_rebuild()


class LayoutPage(BaseModel):
    """A page in the visual builder"""
    id: str
    name: str
    path: str
    components: List[ComponentInstance] = []
    meta: Dict[str, Any] = {}


class VisualProject(BaseModel):
    """Visual builder project structure"""
    id: str
    project_id: UUID
    pages: List[LayoutPage] = []
    theme: Dict[str, Any] = {}
    global_styles: Dict[str, Any] = {}


# Predefined component library
COMPONENT_LIBRARY: List[ComponentDefinition] = [
    # Layout components
    ComponentDefinition(
        id="container",
        name="Container",
        category="layout",
        icon="square",
        properties=[
            ComponentProperty(name="maxWidth", type="select", options=["sm", "md", "lg", "xl", "full"], default="lg"),
            ComponentProperty(name="padding", type="number", default=4),
        ],
        children_allowed=True,
        default_styles={"display": "flex", "flexDirection": "column"}
    ),
    ComponentDefinition(
        id="row",
        name="Row",
        category="layout",
        icon="columns",
        properties=[
            ComponentProperty(name="gap", type="number", default=4),
            ComponentProperty(name="align", type="select", options=["start", "center", "end", "stretch"], default="start"),
        ],
        children_allowed=True,
        default_styles={"display": "flex", "flexDirection": "row"}
    ),
    ComponentDefinition(
        id="column",
        name="Column",
        category="layout",
        icon="layout",
        properties=[
            ComponentProperty(name="span", type="number", default=6),
        ],
        children_allowed=True,
        default_styles={"flex": "1"}
    ),
    ComponentDefinition(
        id="section",
        name="Section",
        category="layout",
        icon="layers",
        properties=[
            ComponentProperty(name="background", type="color", default="#ffffff"),
            ComponentProperty(name="paddingY", type="number", default=12),
        ],
        children_allowed=True,
        default_styles={"width": "100%"}
    ),
    
    # Input components
    ComponentDefinition(
        id="button",
        name="Button",
        category="input",
        icon="mouse-pointer",
        properties=[
            ComponentProperty(name="text", type="string", default="Click me"),
            ComponentProperty(name="variant", type="select", options=["primary", "secondary", "outline", "ghost"], default="primary"),
            ComponentProperty(name="size", type="select", options=["sm", "md", "lg"], default="md"),
            ComponentProperty(name="onClick", type="string", description="Action to trigger"),
        ],
        children_allowed=False,
    ),
    ComponentDefinition(
        id="input",
        name="Text Input",
        category="input",
        icon="type",
        properties=[
            ComponentProperty(name="label", type="string", default="Label"),
            ComponentProperty(name="placeholder", type="string", default="Enter text..."),
            ComponentProperty(name="type", type="select", options=["text", "email", "password", "number"], default="text"),
            ComponentProperty(name="required", type="boolean", default=False),
        ],
        children_allowed=False,
    ),
    ComponentDefinition(
        id="textarea",
        name="Text Area",
        category="input",
        icon="align-left",
        properties=[
            ComponentProperty(name="label", type="string", default="Label"),
            ComponentProperty(name="placeholder", type="string", default="Enter text..."),
            ComponentProperty(name="rows", type="number", default=4),
        ],
        children_allowed=False,
    ),
    ComponentDefinition(
        id="select",
        name="Select",
        category="input",
        icon="chevron-down",
        properties=[
            ComponentProperty(name="label", type="string", default="Select option"),
            ComponentProperty(name="options", type="string", default="Option 1, Option 2, Option 3"),
        ],
        children_allowed=False,
    ),
    ComponentDefinition(
        id="checkbox",
        name="Checkbox",
        category="input",
        icon="check-square",
        properties=[
            ComponentProperty(name="label", type="string", default="Checkbox label"),
            ComponentProperty(name="checked", type="boolean", default=False),
        ],
        children_allowed=False,
    ),
    
    # Display components
    ComponentDefinition(
        id="heading",
        name="Heading",
        category="display",
        icon="heading",
        properties=[
            ComponentProperty(name="text", type="string", default="Heading"),
            ComponentProperty(name="level", type="select", options=["h1", "h2", "h3", "h4", "h5", "h6"], default="h2"),
        ],
        children_allowed=False,
    ),
    ComponentDefinition(
        id="text",
        name="Text",
        category="display",
        icon="align-justify",
        properties=[
            ComponentProperty(name="content", type="string", default="Paragraph text goes here..."),
            ComponentProperty(name="size", type="select", options=["sm", "md", "lg"], default="md"),
        ],
        children_allowed=False,
    ),
    ComponentDefinition(
        id="image",
        name="Image",
        category="display",
        icon="image",
        properties=[
            ComponentProperty(name="src", type="string", default="/placeholder.png"),
            ComponentProperty(name="alt", type="string", default="Image description"),
            ComponentProperty(name="width", type="string", default="100%"),
            ComponentProperty(name="height", type="string", default="auto"),
        ],
        children_allowed=False,
    ),
    ComponentDefinition(
        id="card",
        name="Card",
        category="display",
        icon="credit-card",
        properties=[
            ComponentProperty(name="title", type="string", default="Card Title"),
            ComponentProperty(name="description", type="string", default="Card description"),
            ComponentProperty(name="shadow", type="select", options=["none", "sm", "md", "lg"], default="md"),
        ],
        children_allowed=True,
    ),
    ComponentDefinition(
        id="divider",
        name="Divider",
        category="display",
        icon="minus",
        properties=[
            ComponentProperty(name="color", type="color", default="#e5e7eb"),
            ComponentProperty(name="margin", type="number", default=4),
        ],
        children_allowed=False,
    ),
    
    # Navigation components
    ComponentDefinition(
        id="navbar",
        name="Navigation Bar",
        category="navigation",
        icon="menu",
        properties=[
            ComponentProperty(name="logo", type="string", default="Logo"),
            ComponentProperty(name="links", type="string", default="Home, About, Contact"),
            ComponentProperty(name="sticky", type="boolean", default=True),
        ],
        children_allowed=False,
    ),
    ComponentDefinition(
        id="link",
        name="Link",
        category="navigation",
        icon="link",
        properties=[
            ComponentProperty(name="text", type="string", default="Link text"),
            ComponentProperty(name="href", type="string", default="#"),
            ComponentProperty(name="external", type="boolean", default=False),
        ],
        children_allowed=False,
    ),
    ComponentDefinition(
        id="footer",
        name="Footer",
        category="navigation",
        icon="layout",
        properties=[
            ComponentProperty(name="copyright", type="string", default="© 2024 Company"),
            ComponentProperty(name="links", type="string", default="Privacy, Terms, Contact"),
        ],
        children_allowed=False,
    ),
]


@router.get("/components", response_model=List[ComponentDefinition])
async def get_components():
    """Get all available components for the visual builder"""
    return COMPONENT_LIBRARY


@router.get("/components/{category}", response_model=List[ComponentDefinition])
async def get_components_by_category(category: str):
    """Get components by category"""
    return [c for c in COMPONENT_LIBRARY if c.category == category]


class CreatePageRequest(BaseModel):
    """Request to create a new page"""
    name: str
    path: str
    template: Optional[str] = None  # landing, dashboard, form, etc.


class UpdatePageRequest(BaseModel):
    """Request to update a page"""
    name: Optional[str] = None
    path: Optional[str] = None
    components: Optional[List[ComponentInstance]] = None
    meta: Optional[Dict[str, Any]] = None


class GenerateCodeRequest(BaseModel):
    """Request to generate code from visual layout"""
    project_id: UUID
    page_id: str
    framework: str = "next"  # next, react, vue


class GenerateCodeResponse(BaseModel):
    """Generated code response"""
    code: str
    filename: str
    imports: List[str]


@router.post("/pages", response_model=LayoutPage)
async def create_page(
    request: CreatePageRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new page in the visual builder"""
    import uuid
    
    # Apply template if specified
    components = []
    if request.template == "landing":
        components = [
            ComponentInstance(
                id=str(uuid.uuid4()),
                component_id="navbar",
                properties={"logo": "MyApp", "links": "Home, Features, Pricing, Contact"}
            ),
            ComponentInstance(
                id=str(uuid.uuid4()),
                component_id="section",
                properties={"paddingY": 20},
                children=[
                    ComponentInstance(
                        id=str(uuid.uuid4()),
                        component_id="container",
                        children=[
                            ComponentInstance(
                                id=str(uuid.uuid4()),
                                component_id="heading",
                                properties={"text": "Welcome to MyApp", "level": "h1"}
                            ),
                            ComponentInstance(
                                id=str(uuid.uuid4()),
                                component_id="text",
                                properties={"content": "Build amazing things with our platform."}
                            ),
                            ComponentInstance(
                                id=str(uuid.uuid4()),
                                component_id="button",
                                properties={"text": "Get Started", "variant": "primary", "size": "lg"}
                            )
                        ]
                    )
                ]
            ),
            ComponentInstance(
                id=str(uuid.uuid4()),
                component_id="footer",
                properties={"copyright": "© 2024 MyApp"}
            )
        ]
    elif request.template == "dashboard":
        components = [
            ComponentInstance(
                id=str(uuid.uuid4()),
                component_id="container",
                children=[
                    ComponentInstance(
                        id=str(uuid.uuid4()),
                        component_id="heading",
                        properties={"text": "Dashboard", "level": "h1"}
                    ),
                    ComponentInstance(
                        id=str(uuid.uuid4()),
                        component_id="row",
                        properties={"gap": 4},
                        children=[
                            ComponentInstance(id=str(uuid.uuid4()), component_id="card", properties={"title": "Stats 1"}),
                            ComponentInstance(id=str(uuid.uuid4()), component_id="card", properties={"title": "Stats 2"}),
                            ComponentInstance(id=str(uuid.uuid4()), component_id="card", properties={"title": "Stats 3"}),
                        ]
                    )
                ]
            )
        ]
    
    return LayoutPage(
        id=str(uuid.uuid4()),
        name=request.name,
        path=request.path,
        components=components
    )


@router.put("/pages/{page_id}", response_model=LayoutPage)
async def update_page(
    page_id: str,
    request: UpdatePageRequest,
    current_user: User = Depends(get_current_user)
):
    """Update a page's layout"""
    # In production, this would update the database
    return LayoutPage(
        id=page_id,
        name=request.name or "Untitled",
        path=request.path or "/",
        components=request.components or [],
        meta=request.meta or {}
    )


def generate_react_code(page: LayoutPage) -> str:
    """Generate React/Next.js code from visual layout"""
    
    def render_component(comp: ComponentInstance, indent: int = 2) -> str:
        """Recursively render component to JSX"""
        spaces = "  " * indent
        props = comp.properties
        
        component_map = {
            "container": f'<div className="container mx-auto px-{props.get("padding", 4)}">',
            "row": f'<div className="flex flex-row gap-{props.get("gap", 4)} items-{props.get("align", "start")}">',
            "column": f'<div className="flex-1" style={{{{ flex: "{props.get("span", 1)}" }}}}>',
            "section": f'<section className="py-{props.get("paddingY", 12)}" style={{{{ backgroundColor: "{props.get("background", "#fff")}" }}}}>',
            "heading": f'<{props.get("level", "h2")} className="text-3xl font-bold">{props.get("text", "Heading")}</{props.get("level", "h2")}>',
            "text": f'<p className="text-{props.get("size", "md")}">{props.get("content", "")}</p>',
            "button": f'<button className="btn btn-{props.get("variant", "primary")} btn-{props.get("size", "md")}">{props.get("text", "Button")}</button>',
            "input": f'<input type="{props.get("type", "text")}" placeholder="{props.get("placeholder", "")}" className="input" />',
            "image": f'<img src="{props.get("src", "")}" alt="{props.get("alt", "")}" className="w-full" />',
            "card": f'<div className="card shadow-{props.get("shadow", "md")}"><h3>{props.get("title", "")}</h3><p>{props.get("description", "")}</p>',
            "navbar": f'<nav className="navbar"><span className="logo">{props.get("logo", "Logo")}</span></nav>',
            "footer": f'<footer className="footer"><p>{props.get("copyright", "")}</p></footer>',
            "divider": '<hr className="divider" />',
            "link": f'<a href="{props.get("href", "#")}">{props.get("text", "Link")}</a>',
        }
        
        closing_tags = {
            "container": "</div>",
            "row": "</div>",
            "column": "</div>",
            "section": "</section>",
            "card": "</div>",
        }
        
        jsx = component_map.get(comp.component_id, f'<div>{comp.component_id}</div>')
        
        if comp.children:
            children_jsx = "\n".join(
                render_component(child, indent + 1) 
                for child in comp.children
            )
            close_tag = closing_tags.get(comp.component_id, "</div>")
            return f"{spaces}{jsx}\n{children_jsx}\n{spaces}{close_tag}"
        
        return f"{spaces}{jsx}"
    
    components_jsx = "\n".join(
        render_component(comp) 
        for comp in page.components
    )
    
    return f'''import React from 'react';

export default function {page.name.replace(" ", "")}Page() {{
  return (
    <main>
{components_jsx}
    </main>
  );
}}
'''


@router.post("/generate", response_model=GenerateCodeResponse)
async def generate_code(
    request: GenerateCodeRequest,
    page: LayoutPage,
    current_user: User = Depends(get_current_user)
):
    """Generate code from visual layout"""
    
    if request.framework == "next":
        code = generate_react_code(page)
        filename = f"app/{page.path}/page.tsx"
        imports = ["react"]
    else:
        code = generate_react_code(page)
        filename = f"src/pages/{page.path}.tsx"
        imports = ["react"]
    
    return GenerateCodeResponse(
        code=code,
        filename=filename,
        imports=imports
    )


@router.get("/templates")
async def get_templates():
    """Get available page templates"""
    return {
        "templates": [
            {
                "id": "landing",
                "name": "Landing Page",
                "description": "A hero section with navigation and footer",
                "preview": "/templates/landing.png"
            },
            {
                "id": "dashboard",
                "name": "Dashboard",
                "description": "Admin dashboard with stats cards",
                "preview": "/templates/dashboard.png"
            },
            {
                "id": "form",
                "name": "Form Page",
                "description": "Contact or signup form",
                "preview": "/templates/form.png"
            },
            {
                "id": "pricing",
                "name": "Pricing Page",
                "description": "Pricing table with plans",
                "preview": "/templates/pricing.png"
            },
            {
                "id": "blank",
                "name": "Blank Page",
                "description": "Start from scratch",
                "preview": "/templates/blank.png"
            }
        ]
    }
