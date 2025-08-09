# src/retriever.py

import logging
from typing import List, Callable, Optional
from langchain.schema import Document
from langchain_core.retrievers import BaseRetriever  # <-- key change

def get_retriever(vectorstore, k: int = 5):
    """
    Returns a retriever object from a vectorstore, for RAG-style context retrieval.
    """
    logging.info({
        "event": "retriever_create_start",
        "top_k": k,
        "vectorstore_type": str(type(vectorstore))
    })
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    logging.info({
        "event": "retriever_created",
        "top_k": k,
        "retriever_type": str(type(retriever))
    })
    return retriever


class FeedbackAwareRetriever(BaseRetriever):
    """
    Runnable-compatible retriever that wraps an existing retriever and reorders
    the same top-k documents with a small penalty for chunks that have more
    downvotes than upvotes.

    - Inherits BaseRetriever -> provides .invoke/.batch etc., so it can be piped (|).
    - If no feedback exists for a chunk, original order is preserved.
    """

    def __init__(
        self,
        base_retriever,
        rep_lookup: Callable[[str], Optional[dict]],
        beta: float = 0.2,
    ):
        super().__init__()
        self.base = base_retriever
        self.rep_lookup = rep_lookup
        self.beta = beta

    # BaseRetriever requires implementing this method
    def _get_relevant_documents(self, query, *, run_manager=None, **kwargs) -> List[Document]:
        docs: List[Document] = self.base.get_relevant_documents(query)
        rescored = []
        for i, d in enumerate(docs):
            md = getattr(d, "metadata", {}) or {}
            uid = md.get("chunk_uid")
            up = down = 0
            if uid:
                rep = self.rep_lookup(uid) or {"up": 0, "down": 0}
                up = int(rep.get("up", 0))
                down = int(rep.get("down", 0))
            penalty = max(0, down - up) * self.beta
            rescored.append((penalty, i, d))

        rescored.sort(key=lambda x: (x[0], x[1]))  # lower penalty first, stable by original rank
        return [d for _, _, d in rescored]
