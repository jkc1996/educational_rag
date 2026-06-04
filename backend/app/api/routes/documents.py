from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.dependencies import get_document_service, get_ingestion_service, get_summary_repository
from app.schemas.documents import DocumentIngestRequest, DocumentRecord, DocumentUploadResponse
from app.services.document_service import DocumentService
from app.services.ingestion_service import IngestionService

router = APIRouter()


@router.get("/subjects", response_model=list[str])
def list_subjects(service: DocumentService = Depends(get_document_service)) -> list[str]:
    return service.list_subjects()


@router.get("/documents", response_model=list[DocumentRecord])
def list_documents(subject: str | None = None, service: DocumentService = Depends(get_document_service)) -> list[DocumentRecord]:
    return service.list_documents(subject)


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    subject: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service),
) -> DocumentUploadResponse:
    document = await service.upload(subject=subject, description=description, file=file)
    return DocumentUploadResponse(document=document, message="Document uploaded. Start ingestion to index it.")


@router.post("/documents/ingest", response_model=DocumentRecord)
def ingest_document(
    request: DocumentIngestRequest,
    service: IngestionService = Depends(get_ingestion_service),
) -> DocumentRecord:
    return service.ingest(
        document_id=request.document_id,
        model_id=request.model_id,
        force_summary_refresh=request.force_summary_refresh,
    )


@router.get("/documents/{document_id}/summary")
def get_document_summary(
    document_id: str,
    doc_service: DocumentService = Depends(get_document_service),
    summaries=Depends(get_summary_repository),
):
    document = next((item for item in doc_service.list_documents() if item.id == document_id), None)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    if not document.summary_cache_key:
        raise HTTPException(status_code=404, detail="Document summary has not been generated yet.")
    return summaries.load(document.summary_cache_key)

