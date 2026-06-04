from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import Settings
from app.schemas.documents import DocumentRecord, DocumentStatus
from app.schemas.summaries import DocumentSummary


class DocumentRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.ensure_storage()

    def list(self, subject: str | None = None) -> list[DocumentRecord]:
        records = [DocumentRecord.model_validate(row) for row in self._read()]
        if subject:
            records = [record for record in records if record.subject == subject]
        return sorted(records, key=lambda item: item.created_at, reverse=True)

    def subjects(self) -> list[str]:
        return sorted({record.subject for record in self.list()})

    def get(self, document_id: str) -> DocumentRecord:
        for record in self.list():
            if record.id == document_id:
                return record
        raise KeyError(f"Document not found: {document_id}")

    def add(
        self,
        *,
        subject: str,
        filename: str,
        stored_path: Path,
        description: str,
        content_type: str,
        sha256: str,
    ) -> DocumentRecord:
        record = DocumentRecord(
            id=str(uuid.uuid4()),
            subject=subject,
            filename=filename,
            stored_path=str(stored_path),
            description=description,
            content_type=content_type,
            sha256=sha256,
        )
        rows = self._read()
        rows.append(record.model_dump(mode="json"))
        self._write(rows)
        return record

    def update(self, record: DocumentRecord) -> DocumentRecord:
        record.updated_at = datetime.now(timezone.utc)
        rows = self._read()
        updated = False
        for index, row in enumerate(rows):
            if row.get("id") == record.id:
                rows[index] = record.model_dump(mode="json")
                updated = True
                break
        if not updated:
            rows.append(record.model_dump(mode="json"))
        self._write(rows)
        return record

    def mark_status(
        self,
        document_id: str,
        status: DocumentStatus,
        *,
        error: str | None = None,
        chunk_count: int | None = None,
        summary_cache_key: str | None = None,
    ) -> DocumentRecord:
        record = self.get(document_id)
        record.status = status
        record.error = error
        if chunk_count is not None:
            record.chunk_count = chunk_count
        if summary_cache_key is not None:
            record.summary_cache_key = summary_cache_key
        return self.update(record)

    def _read(self) -> list[dict[str, Any]]:
        if not self.settings.documents_index_path.exists():
            return []
        return json.loads(self.settings.documents_index_path.read_text(encoding="utf-8") or "[]")

    def _write(self, rows: list[dict[str, Any]]) -> None:
        self.settings.documents_index_path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


class SummaryRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.ensure_storage()

    def path_for(self, cache_key: str) -> Path:
        return self.settings.summaries_dir / f"{cache_key}.json"

    def exists(self, cache_key: str) -> bool:
        return self.path_for(cache_key).exists()

    def load(self, cache_key: str) -> DocumentSummary:
        path = self.path_for(cache_key)
        return DocumentSummary.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, cache_key: str, summary: DocumentSummary) -> None:
        self.path_for(cache_key).write_text(summary.model_dump_json(indent=2), encoding="utf-8")


class FeedbackRepository:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.settings.ensure_storage()

    def append(self, payload: dict[str, Any]) -> None:
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()
        with self.settings.feedback_log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
