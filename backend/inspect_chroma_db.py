# inspect_chroma_db.py

import sqlite3
import os

# Change this if your persist_directory is different
CHROMA_DIR = "outputs/chroma_semantic_allpdfs_v2"
DB_PATH = os.path.join(CHROMA_DIR, "chroma.sqlite3")

def show_tables(cur):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    print("Tables in Chroma DB:")
    for t in tables:
        print(" -", t[0])

def peek_embeddings(cur, n=5):
    print(f"\nFirst {n} entries in 'embeddings' table:")
    for row in cur.execute("SELECT * FROM embeddings LIMIT ?;", (n,)):
        # Likely columns: id, collection_id, embedding, etc.
        print(f"ID: {row[0]}")
        print(f"Collection ID: {row[1]}")
        print(f"Embedding (truncated): {str(row[2])[:60]} ...")
        print(f"Seq ID: {row[3]}\n")

def peek_embedding_metadata(cur, n=5):
    print(f"\nFirst {n} entries in 'embedding_metadata' table:")
    for row in cur.execute("SELECT * FROM embedding_metadata LIMIT ?;", (n,)):
        # Columns: id, key, value (value is typically JSON-encoded string)
        print(f"Embedding ID: {row[0]}")
        print(f"Key: {row[1]}")
        val = row[2]
        try:
            val_json = json.loads(val)
            print(f"Value (as JSON): {val_json}\n")
        except Exception:
            print(f"Value: {val}\n")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Chroma DB not found at {DB_PATH}. Please check your path.")
        exit(1)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    show_tables(cur)
    peek_embeddings(cur, n=5)
    peek_embedding_metadata(cur, n=5)

    conn.close()
    print("\nDone.")
