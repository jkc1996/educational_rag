from pathlib import Path

import docx2txt
from langchain_core.documents import Document
from pypdf import PdfReader


class DocumentLoader:
    def load(self, path: Path) -> list[Document]:
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return self._load_pdf(path)
        if suffix in {".doc", ".docx"}:
            return self._load_docx(path)
        raise ValueError(f"Unsupported document type: {suffix}")

    def _load_pdf(self, path: Path) -> list[Document]:
        reader = PdfReader(str(path))
        docs: list[Document] = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                docs.append(
                    Document(
                        page_content=text,
                        metadata={"source_file": path.name, "page": index},
                    )
                )
        return docs

    def _load_docx(self, path: Path) -> list[Document]:
        text = docx2txt.process(str(path)) or ""
        if not text.strip():
            return []
        return [Document(page_content=text, metadata={"source_file": path.name, "page": 1})]

