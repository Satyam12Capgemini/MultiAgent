from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.rag.chroma_store import chroma_store

router = APIRouter()

@router.get("/health", summary="Liveness check")
async def health_check():
    return {"status": "ok", "service": "support-copilot-backend"}

@router.get("/health/ready", summary="Readiness check")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    # Check Database connection
    try:
        await db.execute(text("SELECT 1"))
        db_ready = True
    except Exception:
        db_ready = False

    # Check ChromaDB
    try:
        chroma_count = chroma_store.count()
        chroma_ready = True
    except Exception:
        chroma_ready = False

    all_ready = db_ready and chroma_ready
    return {
        "status": "ready" if all_ready else "not_ready",
        "database": "ok" if db_ready else "error",
        "vector_store": "ok" if chroma_ready else "error"
    }
