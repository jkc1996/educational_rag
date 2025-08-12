# inspect_chroma_db_final.py

import sqlite3
import os

# --- Your database path ---
CHROMA_DIR = "outputs/chroma_machine_learning"
DB_PATH = os.path.join(CHROMA_DIR, "chroma.sqlite3")

def show_chunks(cur, n=5):
    """
    Fetches and displays the actual text chunks from the database.
    """
    print(f"Showing the first {n} text chunks:\n")
    
    # ▼▼▼ UPDATE THESE TWO COLUMN NAMES ▼▼▼
    # Replace 'id' and 'string_value' with the names you found in DBeaver.
    id_column = "id"
    text_column = "string_value" 
    
    # The query now uses the column names you provide.
    query = f"""
        SELECT {id_column}, {text_column} 
        FROM embedding_metadata 
        WHERE key = 'chroma:document' AND {text_column} IS NOT NULL
        LIMIT ?;
    """
    
    try:
        for row in cur.execute(query, (n,)):
            chunk_id = row[0]
            chunk_text = row[1]
            
            print(f"✅ Chunk (Linked to Embedding ID: {chunk_id})")
            print("-" * 35)
            print(f"{chunk_text}\n")
            
    except sqlite3.OperationalError as e:
        print(f"❌ An error occurred: {e}")
        print("Please double-check the column names you entered from DBeaver.")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Chroma DB not found at {DB_PATH}. Please check your path.")
        exit(1)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    show_chunks(cur, n=5)

    conn.close()
    print("\nDone.")