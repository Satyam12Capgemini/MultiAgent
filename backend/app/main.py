import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.errors import AppError, app_error_handler
from app.db.session import engine, Base, AsyncSessionLocal
from app.rag.ingest import ingestion_service
import app.db.models  # ensure models are registered

# API Routers
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.tickets import router as tickets_router
from app.api.v1.escalations import router as escalations_router
from app.api.v1.orders import router as orders_router
from app.api.v1.kb import router as kb_router
from app.api.v1.rag import router as rag_router
from app.api.v1.eval import router as eval_router
from app.api.v1.analytics import router as analytics_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Initializing Support Copilot Application...")

    # Create tables if not existing
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified.")

    # Initialize BM25 search index
    async with AsyncSessionLocal() as session:
        try:
            await ingestion_service.refresh_bm25_index(session)
        except Exception as e:
            logger.warning(f"Could not initialize BM25 index on startup: {e}")

    yield

    logger.info("Shutting down Support Copilot Application...")
    await engine.dispose()

app = FastAPI(
    title="Support Copilot API",
    description="Multi-agent customer support platform with LangGraph, RAG, Critic Fact-Checking loop, and Guardrails.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID Middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Custom Error Handlers
app.add_exception_handler(AppError, app_error_handler)

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred.",
                "details": str(exc) if settings.APP_ENV == "dev" else {},
                "request_id": request_id
            }
        }
    )

# Include Routers
api_v1_prefix = "/api/v1"
app.include_router(health_router, prefix=api_v1_prefix, tags=["System"])
app.include_router(auth_router, prefix=f"{api_v1_prefix}/auth", tags=["Auth"])
app.include_router(tickets_router, prefix=f"{api_v1_prefix}/tickets", tags=["Tickets"])
app.include_router(escalations_router, prefix=f"{api_v1_prefix}/escalations", tags=["Escalations"])
app.include_router(orders_router, prefix=f"{api_v1_prefix}/orders", tags=["Orders"])
app.include_router(kb_router, prefix=f"{api_v1_prefix}/kb", tags=["Knowledge Base"])
app.include_router(rag_router, prefix=f"{api_v1_prefix}/rag", tags=["RAG"])
app.include_router(eval_router, prefix=f"{api_v1_prefix}/eval", tags=["Evaluation"])
app.include_router(analytics_router, prefix=f"{api_v1_prefix}/analytics", tags=["Analytics"])
