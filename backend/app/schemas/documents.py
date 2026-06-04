from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    uploaded = "uploaded"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class DocumentRecord(BaseModel):
    id: str
    subject: str
    filename: str
    stored_path: str
    description: str = ""
    content_type: str = "application/octet-stream"
    sha256: str
    status: DocumentStatus = DocumentStatus.uploaded
    chunk_count: int = 0
    summary_cache_key: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def stored_file(self) -> Path:
        return Path(self.stored_path)


class DocumentUploadResponse(BaseModel):
    document: DocumentRecord
    message: str


class DocumentIngestRequest(BaseModel):
    document_id: str
    model_id: str | None = None
    force_summary_refresh: bool = False

