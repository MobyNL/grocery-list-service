import os
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .database import create_tables
from .routes import items, lists

load_dotenv()

app = FastAPI(
    title="Grocery List Service",
    description="FastAPI backend for managing grocery lists and items",
    version="0.1.0",
)

# Enable CORS for Angular frontend
allowed_origins = [
    "http://localhost:4200",
    "https://localhost:4200",
]

# Add Vercel frontend URL if provided
frontend_url: str | None = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(lists.router, prefix="/api")
app.include_router(items.router, prefix="/api")


# Add JWT Bearer security to OpenAPI docs
def custom_openapi() -> Dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema: Dict[str, Any] = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    # Apply security to all endpoints except health
    for path in openapi_schema["paths"].values():
        for method in path.values():
            if "security" not in method:
                method["security"] = [{"BearerAuth": []}]

    # Exclude health endpoint from requiring authentication
    if "/" in openapi_schema["paths"]:
        for method in openapi_schema["paths"]["/"].values():
            method.pop("security", None)
    if "/health" in openapi_schema["paths"]:
        for method in openapi_schema["paths"]["/health"].values():
            method.pop("security", None)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.on_event("startup")
def on_startup() -> None:
    """Create database tables on startup"""
    create_tables()


@app.get("/")
def read_root() -> dict[str, str]:
    """Root endpoint"""
    return {"message": "Grocery List Service is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "grocery-list-service"}
