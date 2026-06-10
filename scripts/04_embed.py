"""Embedding + Vector Store step of the CSULB dining RAG pipeline.

Architecture (planning.md):
    Chunking → [Embedding + Vector Store] → Retrieval → Generation
    sentence-transformers all-MiniLM-L6-v2 → embeddings, stored in ChromaDB.

Loads chunks produced by 03_chunk.py, embeds them with all-MiniLM-L6-v2, and
stores them in a persistent ChromaDB collection with source metadata so
retrieval can surface attribution (which restaurant / thread / author).
"""

import json
from pathlib import Path

import chromadb

from retrieve import (
    COLLECTION_NAME,
    EMBED_MODEL,
    PERSIST_DIR,
    embed_texts,
)

CHUNKS_FILE = "chunks/chunks.json"
BATCH_SIZE = 64

print("=" * 80)
print(f"EMBEDDING + VECTOR STORE: {EMBED_MODEL} → ChromaDB")
print("=" * 80)


def sanitize_metadata(meta):
    """ChromaDB metadata values must be non-None scalars (str/int/float/bool).

    Drop None values and coerce anything else to a string so add() never fails.
    """
    clean = {}
    for key, value in meta.items():
        if value is None:
            continue
        if isinstance(value, (str, int, float, bool)):
            clean[key] = value
        else:
            clean[key] = str(value)
    return clean


# --- Load chunks from the ingestion/chunking pipeline ---
chunks_path = Path(CHUNKS_FILE)
if not chunks_path.exists():
    raise SystemExit(f"✗ {CHUNKS_FILE} not found — run 03_chunk.py first.")

data = json.loads(chunks_path.read_text(encoding="utf-8"))
chunks = data["chunks"]
print(f"\nLoaded {len(chunks)} chunks from {CHUNKS_FILE}")

# --- (Re)create a clean collection so re-running gives a fresh index ---
client = chromadb.PersistentClient(path=PERSIST_DIR)
try:
    client.delete_collection(COLLECTION_NAME)
    print(f"Removed existing collection '{COLLECTION_NAME}'")
except Exception:
    pass

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},  # cosine matches normalized MiniLM vectors
)

# --- Embed and store in batches ---
print(f"\nEmbedding and indexing in batches of {BATCH_SIZE} ...")
for start in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[start:start + BATCH_SIZE]

    ids = [c["id"] for c in batch]
    documents = [c["text"] for c in batch]
    embeddings = embed_texts(documents)

    # Keep the original chunk id inside metadata too (handy on the way back out)
    metadatas = []
    for c in batch:
        meta = dict(c["metadata"])
        meta["chunk_id"] = c["id"]
        meta["tokens"] = c.get("tokens")
        metadatas.append(sanitize_metadata(meta))

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )
    print(f"   indexed {min(start + BATCH_SIZE, len(chunks))}/{len(chunks)}")

# === SUMMARY ===
count = collection.count()
by_source = {}
for c in chunks:
    s = c["metadata"]["source"]
    by_source[s] = by_source.get(s, 0) + 1

print(f"\n{'=' * 80}")
print(f"COMPLETE: {count} chunks embedded and stored in '{COLLECTION_NAME}'")
print(f"Persisted to: {PERSIST_DIR}/")
print(f"{'=' * 80}")
print("Chunks per source:")
for src, n in sorted(by_source.items()):
    print(f"   {src:8s}: {n}")
print("\nNext: run `python scripts/retrieve.py` to test retrieval.")
