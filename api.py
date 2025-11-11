"""
RESTful API for VibeDoc SaaS
FastAPI-based API with authentication and rate limiting
"""

from fastapi import FastAPI, HTTPException, Depends, Header, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import logging

from database import (
    get_db_session, UserService, SubscriptionService,
    ProjectService, UsageTrackingService
)
from auth import AuthService
from models import SubscriptionTier

logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="VibeDoc API",
    description="AI-powered product planning and development documentation",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# =============================================================================
# Request/Response Models
# =============================================================================

class SignupRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = ""

class LoginRequest(BaseModel):
    email_or_username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class GeneratePlanRequest(BaseModel):
    idea: str
    reference_url: Optional[str] = ""

class SaveProjectRequest(BaseModel):
    title: str
    description: str
    plan: str
    reference_urls: Optional[List[str]] = []

class UpdateProjectRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    plan: Optional[str] = None
    is_favorite: Optional[bool] = None
    tags: Optional[List[str]] = None

# =============================================================================
# Authentication Dependency
# =============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Verify JWT token and return current user"""
    token = credentials.credentials

    with get_db_session() as session:
        auth_service = AuthService(session)
        user = auth_service.get_user_by_token(token)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        return user

async def get_current_user_by_api_key(
    x_api_key: Optional[str] = Header(None)
):
    """Verify API key and return current user"""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )

    with get_db_session() as session:
        auth_service = AuthService(session)
        user = auth_service.authenticate_api_key(x_api_key)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )

        return user

# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/")
async def root():
    """API root"""
    return {
        "message": "Welcome to VibeDoc API",
        "version": "3.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Authentication Endpoints

@app.post("/auth/signup", response_model=dict)
async def signup(request: SignupRequest):
    """Register new user"""
    with get_db_session() as session:
        auth_service = AuthService(session)

        success, message, user = auth_service.register_user(
            request.email,
            request.username,
            request.password,
            request.full_name
        )

        if not success:
            raise HTTPException(status_code=400, detail=message)

        return {
            "message": message,
            "user": user.to_dict()
        }

@app.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """User login"""
    with get_db_session() as session:
        auth_service = AuthService(session)

        success, message, user = auth_service.authenticate_user(
            request.email_or_username,
            request.password
        )

        if not success:
            raise HTTPException(status_code=401, detail=message)

        access_token = auth_service.create_access_token(user)

        return TokenResponse(
            access_token=access_token,
            user=user.to_dict()
        )

@app.get("/auth/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user information"""
    return current_user.to_dict()

# Plan Generation Endpoints

@app.post("/plans/generate")
async def generate_plan(
    request: GeneratePlanRequest,
    current_user = Depends(get_current_user)
):
    """Generate development plan"""
    # Check usage limits
    can_proceed, limit_msg = SubscriptionService.check_usage_limit(current_user.id, 'plan')

    if not can_proceed:
        raise HTTPException(status_code=403, detail=limit_msg)

    # Generate plan (placeholder - integrate with actual generation logic)
    plan = f"""
# Development Plan

Generated for: {request.idea}

[Plan content here...]
"""

    # Increment usage
    SubscriptionService.increment_usage(current_user.id, 'plan')

    # Log action
    UsageTrackingService.log_action(
        user_id=current_user.id,
        action_type='plan_generated_api',
        success=True,
        details={'idea': request.idea[:100]}
    )

    return {
        "plan": plan,
        "message": "Plan generated successfully"
    }

# Project Management Endpoints

@app.get("/projects")
async def list_projects(
    skip: int = 0,
    limit: int = 50,
    current_user = Depends(get_current_user)
):
    """List user's projects"""
    projects = ProjectService.get_user_projects(current_user.id, skip, limit)

    return {
        "projects": [p.to_dict() for p in projects],
        "total": len(projects)
    }

@app.post("/projects")
async def create_project(
    request: SaveProjectRequest,
    current_user = Depends(get_current_user)
):
    """Create new project"""
    # Check limits
    can_proceed, limit_msg = SubscriptionService.check_usage_limit(current_user.id, 'project')

    if not can_proceed:
        raise HTTPException(status_code=403, detail=limit_msg)

    project = ProjectService.create_project(
        user_id=current_user.id,
        title=request.title,
        description=request.description,
        generated_plan=request.plan,
        reference_urls=request.reference_urls
    )

    if not project:
        raise HTTPException(status_code=500, detail="Failed to create project")

    return {
        "project": project.to_dict(include_plan=True),
        "message": "Project created successfully"
    }

@app.get("/projects/{project_id}")
async def get_project(
    project_id: int,
    current_user = Depends(get_current_user)
):
    """Get specific project"""
    project = ProjectService.get_project(project_id, current_user.id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project.to_dict(include_plan=True)

@app.put("/projects/{project_id}")
async def update_project(
    project_id: int,
    request: UpdateProjectRequest,
    current_user = Depends(get_current_user)
):
    """Update project"""
    update_data = request.dict(exclude_unset=True)

    project = ProjectService.update_project(project_id, current_user.id, **update_data)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "project": project.to_dict(include_plan=True),
        "message": "Project updated successfully"
    }

@app.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    current_user = Depends(get_current_user)
):
    """Delete project"""
    success = ProjectService.delete_project(project_id, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Project not found")

    return {"message": "Project deleted successfully"}

# Subscription Endpoints

@app.get("/subscription")
async def get_subscription(current_user = Depends(get_current_user)):
    """Get user's subscription information"""
    subscription = SubscriptionService.get_subscription(current_user.id)

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return subscription.to_dict()

@app.get("/subscription/usage")
async def get_usage_stats(
    days: int = 30,
    current_user = Depends(get_current_user)
):
    """Get usage statistics"""
    stats = UsageTrackingService.get_user_usage_stats(current_user.id, days)
    return stats

# Admin Endpoints

@app.get("/admin/stats")
async def admin_stats(current_user = Depends(get_current_user)):
    """Get system statistics (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    stats = UsageTrackingService.get_system_stats()
    return stats

# Error handlers

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

# =============================================================================
# Run API Server
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 Starting VibeDoc API server...")

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
