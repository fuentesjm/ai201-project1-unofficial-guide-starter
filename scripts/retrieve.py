"""Retrieval module for the CSULB dining RAG pipeline.

Pipeline (from planning.md architecture diagram):
    Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
                                                       ^^^^^^^^^ this file

Shared config + the retrieve() function used by both the embedding step
(04_embed.py) and the generation step (Milestone 5).
"""

import chromadb
from sentence_transformers import SentenceTransformer

# === RETRIEVAL CONFIG (from planning.md → Retrieval Approach) ===
EMBED_MODEL = "all-MiniLM-L6-v2"   # good at semantic similarity for opinion text
DEFAULT_K = 5                       # start at 5 (low end of spec 5-7); tune up after seeing results
PERSIST_DIR = "chroma_db"
COLLECTION_NAME = "csulb_dining"

# Lazy singletons so importing this module is cheap; the model (~90MB) and the
# Chroma client load only on first actual use.
_model = None
_collection = None


def get_model():
    """Load the embedding model once and reuse it."""
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def get_collection():
    """Open the persisted Chroma collection (cosine space)."""
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=PERSIST_DIR)
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def embed_texts(texts):
    """Encode texts into normalized vectors (cosine similarity ready)."""
    model = get_model()
    return model.encode(
        texts,
        normalize_embeddings=True,   # unit vectors → cosine distance is meaningful
        show_progress_bar=False,
    ).tolist()


def retrieve(query, k=DEFAULT_K):
    """Return the top-k most relevant chunks for a query.

    Each result: {id, text, source, metadata, similarity}. Similarity is
    1 - cosine_distance, so higher = closer (1.0 is identical).
    """
    collection = get_collection()
    query_embedding = embed_texts([query])

    res = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for doc, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        hits.append({
            "id": meta.get("chunk_id"),
            "text": doc,
            "source": meta.get("source"),
            "metadata": meta,
            "distance": round(dist, 4),            # cosine distance (lower = closer)
            "similarity": round(1.0 - dist, 4),    # 1 - distance (higher = closer)
        })
    return hits


# === CLI DEMO: run the 5 evaluation questions from planning.md ===
if __name__ == "__main__":
    EVAL_QUESTIONS = [
        "What do reviews say about wait times and crowds at The Outpost Grill?",
        "What do students say on Reddit about dining options directly on the CSULB campus?",
        "Which sandwich restaurants near CSULB campus are recommended on Yelp?",
        "What quick lunch options do students recommend for between classes at CSULB?",
        "Is Sapporo Sushi well-reviewed, and what are students saying about it?",
    ]

    print("=" * 80)
    print(f"RETRIEVAL DEMO — top-{DEFAULT_K} chunks per question")
    print("=" * 80)

    for i, q in enumerate(EVAL_QUESTIONS, 1):
        print(f"\n[Q{i}] {q}")
        print("-" * 80)
        for rank, hit in enumerate(retrieve(q), 1):
            preview = hit["text"][:120].replace("\n", " ")
            src = f"{hit['metadata'].get('doc_name')}#{hit['metadata'].get('chunk_index')}"
            print(f"  {rank}. dist={hit['distance']:.3f} sim={hit['similarity']:.3f} "
                  f"[{src}] {preview}")
