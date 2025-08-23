# view_vectors.py

import chromadb
import numpy as np

PERSIST_DIR = "outputs/chroma_natural_language_processing"
chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)

collection = chroma_client.get_collection("langchain")

results = collection.get(include=["embeddings", "documents", "metadatas"], limit=5)

for i, emb in enumerate(results["embeddings"]):
    print(f"\n--- Chunk {i+1} ---")
    print("Text preview:", results["documents"][i][:120], "...")
    print("Metadata:", results["metadatas"][i])
    vector = np.array(emb, dtype=np.float32)
    print("Embedding length:", len(vector))
    print("First 10 dims:", vector[:10])
