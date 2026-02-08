"""
FastAPI application entry point (Phase III Update).
Configures the application, middleware, routes, and Phase III integration.

T001-T006: Project setup
T013: CORS middleware configuration
T019: MCP server startup integration
T051-T052: Chat endpoint routing
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import close_db, async_engine
from app.models.user import User
from app.models.task import Task
from app.chat.models.conversation import Conversation
from app.chat.models.message import Message
from app.routers import auth_router, tasks_router
from app.chat.routers import chat_router
from app.middleware.security import SecurityHeadersMiddleware
from app.chat.mcp_server import init_mcp_server, shutdown_mcp_server


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events (startup/shutdown).

    T001-T006: Phase III project setup hooks
    T013: Initialize during startup
    T017-T019: MCP server lifecycle
    """
    # Startup
    print(f"[START] Starting {settings.app_name}")
    print(f"[INFO] Environment: {settings.environment}")

    # Create all tables (Phase II + Phase III)
    # T007-T008: Create Conversation and Message tables for chat persistence
    async with async_engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: (
            # Phase II tables
            User.__table__.create(sync_conn, checkfirst=True),
            Task.__table__.create(sync_conn, checkfirst=True),
            # T007-T008: Phase III tables
            Conversation.__table__.create(sync_conn, checkfirst=True),
            Message.__table__.create(sync_conn, checkfirst=True),
        ))
    print("[OK] Database tables ready (Phase II + Phase III)")

    # Store settings in app state for middleware access
    app.state.settings = settings

    # T019: MCP Server Startup Integration
    # Initialize MCP server on startup
    try:
        await init_mcp_server()
        print("[OK] MCP Server initialized with all tools")
    except Exception as e:
        print(f"[ERROR] Failed to initialize MCP Server: {e}")
        raise

    yield
    # Shutdown

    # T019: MCP Server Shutdown
    try:
        await shutdown_mcp_server()
        print("[OK] MCP Server shutdown")
    except Exception as e:
        print(f"[ERROR] Failed to shutdown MCP Server: {e}")

    await close_db()
    print("[SHUTDOWN] Shutting down")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version="0.3.0",
    description="Phase III Backend - Multi-user Todo App with AI Chatbot",
    lifespan=lifespan,
)


# Configure middleware (order matters - first added is outermost)
# Security headers
app.add_middleware(SecurityHeadersMiddleware)

# T013: CORS Middleware - Allow frontend communication
# Configured to support:
# - Development: localhost:3000
# - Production: Custom domain via PRODUCTION_DOMAIN env var
cors_origins = [
    "http://localhost:3000",  # Development
    "http://127.0.0.1:3000",  # Development (alternate)
]

# Add production domain if configured
if hasattr(settings, 'production_domain') and settings.production_domain:
    cors_origins.append(settings.production_domain)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": "0.3.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment,
    }


# Include Phase II routers
app.include_router(auth_router)
app.include_router(tasks_router)

# T051-T052: Include Phase III chat router
# Endpoints:
# - POST /api/{user_id}/chat
# - GET /api/{user_id}/conversations
app.include_router(chat_router)
