from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import User
from app.schemas.kb import (
    KBDocumentOut, KBDocumentDetailResponse, KBSearchRequest, KBSearchResponse, KBChunkOut
)
from app.services.kb_service import kb_service
from app.api.deps import require_roles

router = APIRouter()

@router.get("/documents", response_model=List[KBDocumentOut])
async def list_kb_documents(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["admin", "agent"]))
):
    docs = await kb_service.list_documents(db)
    return [KBDocumentOut.model_validate(d) for d in docs]

@router.post("/documents", response_model=KBDocumentOut, status_code=202)
async def upload_kb_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("tech"),
    source: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["admin"]))
):
    content = await file.read()
    doc = await kb_service.upload_document(
        session=db,
        title=title,
        category=category,
        filename=file.filename or "document.txt",
        content=content,
        source=source
    )
    return KBDocumentOut.model_validate(doc)

@router.get("/documents/{doc_id}", response_model=KBDocumentDetailResponse)
async def get_kb_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["admin", "agent"]))
):
    doc = await kb_service.get_document(db, doc_id)
    chunks = await kb_service.get_document_chunks(db, doc_id)
    chunks_out = [KBChunkOut.model_validate(c) for c in chunks]
    doc_out = KBDocumentOut.model_validate(doc)
    return KBDocumentDetailResponse(**doc_out.model_dump(), chunks=chunks_out)

@router.delete("/documents/{doc_id}")
async def delete_kb_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["admin"]))
):
    await kb_service.delete_document(db, doc_id)
    return {"status": "ok", "message": f"Document {doc_id} deleted successfully."}

@router.post("/search", response_model=KBSearchResponse)
async def search_kb(
    req: KBSearchRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["admin", "agent"]))
):
    results = await kb_service.search(
        query=req.query,
        category=req.category,
        top_k=req.top_k,
        mode=req.mode
    )
    return KBSearchResponse(results=results)

@router.post("/reconcile")
async def reconcile_kb_stores(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_roles(["admin"]))
):
    return await kb_service.reconcile(db)
