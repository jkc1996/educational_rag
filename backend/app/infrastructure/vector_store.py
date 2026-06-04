import hashlib
import re

from langchain_core.documents import Document

from app.core.config import Settings
from app.infrastructure.openai_factory import OpenAIModelFactory


class ChromaVectorRepository:
    def __init__(self, settings: Settings, model_factory: OpenAIModelFactory) -> None:
        self.settings = settings
        self.model_factory = model_factory
        self.settings.ensure_storage()

    def split_documents(self, docs: list[Document], *, document_id: str, subject: str) -> list[Document]:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        chunks = splitter.split_documents(docs)
        for index, chunk in enumerate(chunks):
            chunk.page_content = self._clean_text(chunk.page_content)
            source_file = chunk.metadata.get("source_file") or chunk.metadata.get("source") or "unknown"
            page = chunk.metadata.get("page")
            digest = hashlib.sha256(chunk.page_content.encode("utf-8")).hexdigest()[:12]
            chunk.metadata.update(
                {
                    "document_id": document_id,
                    "subject": subject,
                    "source_file": source_file,
                    "page": page,
                    "chunk_uid": f"{document_id}_{index}_{digest}",
                    "chunk_index": index,
                }
            )
        return chunks

    def add_documents(self, subject: str, chunks: list[Document]) -> None:
        if not chunks:
            return
        store = self._store(subject)
        ids = [chunk.metadata["chunk_uid"] for chunk in chunks]
        store.add_documents(chunks, ids=ids)

    def retriever(self, subject: str, *, top_k: int):
        return self._store(subject).as_retriever(search_kwargs={"k": top_k})

    def _store(self, subject: str):
        from langchain_chroma import Chroma

        return Chroma(
            collection_name=self._collection_name(subject),
            persist_directory=str(self.settings.chroma_dir),
            embedding_function=self.model_factory.embeddings(),
        )

    def _collection_name(self, subject: str) -> str:
        slug = re.sub(r"[^a-z0-9_]+", "_", subject.lower()).strip("_")
        return slug or "default_subject"

    def _clean_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()
