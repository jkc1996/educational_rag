import hashlib
import re
import shutil
from pathlib import Path

from fastapi import UploadFile

from app.core.config import Settings
from app.infrastructure.app_logger import app_event, log_context, new_flow_id
from app.infrastructure.repositories import DocumentRepository
from app.schemas.documents import DocumentRecord


class DocumentService:
    def __init__(self, settings: Settings, documents: DocumentRepository) -> None:
        self.settings = settings
        self.documents = documents

    def list_documents(self, subject: str | None = None) -> list[DocumentRecord]:
        return self.documents.list(subject)

    def list_subjects(self) -> list[str]:
        return self.documents.subjects()

    async def upload(self, *, subject: str, description: str, file: UploadFile) -> DocumentRecord:
        flow_id = new_flow_id("upload")
        safe_filename = self._safe_filename(file.filename or "document")
        with log_context(flow="document_upload", flow_id=flow_id):
            app_event(
                "document_upload_started",
                message=f"Document upload started: {safe_filename}",
                step="upload",
                subject=subject,
                filename=safe_filename,
                content_type=file.content_type,
            )
            subject_dir = self.settings.uploads_dir / self._slug(subject)
            subject_dir.mkdir(parents=True, exist_ok=True)
            destination = subject_dir / safe_filename

            digest = hashlib.sha256()
            byte_count = 0
            with destination.open("wb") as output:
                while chunk := await file.read(1024 * 1024):
                    digest.update(chunk)
                    output.write(chunk)
                    byte_count += len(chunk)

            record = self.documents.add(
                subject=subject,
                filename=safe_filename,
                stored_path=destination,
                description=description,
                content_type=file.content_type or "application/octet-stream",
                sha256=digest.hexdigest(),
            )
            app_event(
                "document_upload_completed",
                message=f"Document uploaded: {safe_filename}",
                step="upload",
                document_id=record.id,
                subject=record.subject,
                filename=record.filename,
                bytes=byte_count,
                sha256=record.sha256,
            )
            return record

    def _safe_filename(self, filename: str) -> str:
        name = Path(filename).name
        return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") or "document"

    def _slug(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "default"
