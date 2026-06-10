import json
import re
from pathlib import Path

from transformers import AutoTokenizer

# === CHUNKING CONFIG (from planning.md → Chunking Strategy) ===
# Spec: 200-300 tokens per chunk, 30-50 token overlap.
# all-MiniLM-L6-v2 truncates input at 256 tokens, so CHUNK_SIZE is set to the
# top of the spec range while staying under that cap — no chunk is silently
# truncated at embed time. Overlap is the midpoint of the 30-50 range.
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 250      # tokens, measured with the embedding model's own tokenizer
CHUNK_OVERLAP = 40    # tokens carried from the end of one chunk into the next

# Anchor to project root so the script works regardless of launch directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR = str(PROJECT_ROOT / "cleaned_documents")
OUTPUT_DIR = str(PROJECT_ROOT / "chunks")
OUTPUT_FILE = f"{OUTPUT_DIR}/chunks.json"

Path(OUTPUT_DIR).mkdir(exist_ok=True)

print("=" * 80)
print(f"CHUNKING: {CHUNK_SIZE}-token chunks, {CHUNK_OVERLAP}-token overlap")
print("=" * 80)

# Load the embedding model's tokenizer so chunk token counts match exactly what
# the model will encode in the next milestone (no surprises at embed time).
print(f"\nLoading tokenizer for {EMBED_MODEL} ...")
tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL)


def count_tokens(text):
    """Token count using the embedding model's tokenizer (excludes [CLS]/[SEP])."""
    return len(tokenizer.encode(text, add_special_tokens=False))


def split_into_sentences(text):
    """Split text into sentence-ish units on sentence punctuation and newlines."""
    parts = re.split(r'(?<=[.!?])\s+|\n+', text)
    return [p.strip() for p in parts if p.strip()]


def hard_split_long_segment(segment):
    """Token-window split for a single segment longer than CHUNK_SIZE.

    Used for run-on text with no sentence boundaries (e.g. the scraped CSULB
    page). Slides a CHUNK_SIZE window with CHUNK_OVERLAP stride over the tokens.
    """
    # Use offset mapping to slice the ORIGINAL text at token boundaries — this
    # preserves casing/spacing instead of round-tripping through decode().
    encoding = tokenizer(segment, add_special_tokens=False, return_offsets_mapping=True)
    offsets = encoding["offset_mapping"]
    stride = CHUNK_SIZE - CHUNK_OVERLAP
    windows = []
    for start in range(0, len(offsets), stride):
        window = offsets[start:start + CHUNK_SIZE]
        char_start = window[0][0]
        char_end = window[-1][1]
        windows.append(segment[char_start:char_end].strip())
        if start + CHUNK_SIZE >= len(offsets):
            break
    return windows


def chunk_text(text):
    """Pack sentences into <=CHUNK_SIZE token chunks with CHUNK_OVERLAP carryover."""
    sentences = split_into_sentences(text)
    chunks = []
    current = []           # list of (sentence, token_count) in the in-progress chunk
    current_tokens = 0

    def flush():
        nonlocal current, current_tokens
        if current:
            chunks.append(" ".join(s for s, _ in current))

    for sent in sentences:
        n = count_tokens(sent)

        # A single sentence/segment bigger than a whole chunk: flush, then
        # hard-split it on token windows.
        if n > CHUNK_SIZE:
            flush()
            current, current_tokens = [], 0
            chunks.extend(hard_split_long_segment(sent))
            continue

        # Adding this sentence would overflow the chunk → close the current one
        # and seed the next with trailing sentences worth ~CHUNK_OVERLAP tokens.
        if current_tokens + n > CHUNK_SIZE and current:
            flush()
            overlap_sents, overlap_tokens = [], 0
            for s, c in reversed(current):
                if overlap_tokens + c > CHUNK_OVERLAP:
                    break
                overlap_sents.insert(0, (s, c))
                overlap_tokens += c
            current, current_tokens = overlap_sents, overlap_tokens

        current.append((sent, n))
        current_tokens += n

    flush()
    return chunks


def build_records():
    """Turn each cleaned document into (text, metadata) records ready to chunk.

    Context (restaurant name, rating, thread title) is folded into the chunk
    text so every chunk is self-describing for retrieval and grounding.
    """
    records = []

    # --- CSULB official dining page (one long run-on document) ---
    path = Path(INPUT_DIR) / "cleaned_01_csulb.json"
    if path.exists():
        doc = json.loads(path.read_text(encoding="utf-8"))
        records.append({
            "text": f"CSULB campus dining options and hours: {doc.get('content', '')}",
            "metadata": {
                "source": "csulb",
                "doc_name": "doc_01_csulb",
                "title": "CSULB Campus Dining",
                "url": doc.get("url"),
            },
        })

    # --- Yelp reviews (one record per review) ---
    path = Path(INPUT_DIR) / "cleaned_04_yelp_sample_data.json"
    if path.exists():
        doc = json.loads(path.read_text(encoding="utf-8"))
        for r in doc.get("restaurants", []):
            name = r.get("name")
            for rev in r.get("reviews", []):
                records.append({
                    "text": (
                        f"Yelp review of {name} "
                        f"(overall rating {r.get('rating')}, this review {rev.get('rating')} stars) "
                        f"by {rev.get('author')}: {rev.get('text')}"
                    ),
                    "metadata": {
                        "source": "yelp",
                        "doc_name": "doc_04_yelp_sample_data",
                        "restaurant": name,
                        "restaurant_rating": r.get("rating"),
                        "review_rating": rev.get("rating"),
                        "author": rev.get("author"),
                        "url": r.get("url"),
                    },
                })

    # --- Reddit threads (the post, then one record per comment) ---
    for fname in ("cleaned_good_food_place_around_csulb_and_in_long_beach.json",
                  "cleaned_another_subreddit.json"):
        path = Path(INPUT_DIR) / fname
        if not path.exists():
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        title = (doc.get("thread_title") or "").strip()
        doc_name = fname.replace("cleaned_", "").replace(".json", "")

        if doc.get("post_text"):
            records.append({
                "text": f"Reddit post in {doc.get('subreddit')} titled '{title}': {doc['post_text']}",
                "metadata": {
                    "source": "reddit",
                    "doc_name": doc_name,
                    "thread_title": title,
                    "subreddit": doc.get("subreddit"),
                    "author": "OP",
                    "url": doc.get("url"),
                },
            })

        for c in doc.get("comments", []):
            # For replies, fold the parent comment in so pronouns/references
            # ("I tried it once") resolve within this chunk alone.
            if c.get("parent_text"):
                text = (
                    f"Reddit comment in thread '{title}', "
                    f"replying to {c.get('reply_to')} who said \"{c['parent_text']}\": "
                    f"{c.get('text')}"
                )
            else:
                text = f"Reddit comment in thread '{title}': {c.get('text')}"
            records.append({
                "text": text,
                "metadata": {
                    "source": "reddit",
                    "doc_name": doc_name,
                    "thread_title": title,
                    "subreddit": doc.get("subreddit"),
                    "author": c.get("author"),
                    "reply_to": c.get("reply_to"),
                    "score": c.get("score"),
                    "url": doc.get("url"),
                },
            })

    return records


# === MAIN ===
records = build_records()
print(f"\nBuilt {len(records)} records from {INPUT_DIR}/")

all_chunks = []
doc_positions = {}  # doc_name -> next chunk position within that document
for rec in records:
    doc_name = rec["metadata"]["doc_name"]
    for piece in chunk_text(rec["text"]):
        if not piece.strip():
            continue
        # Per-document position, for source attribution later
        position = doc_positions.get(doc_name, 0)
        doc_positions[doc_name] = position + 1

        meta = dict(rec["metadata"])
        meta["chunk_index"] = position

        all_chunks.append({
            "id": f"chunk_{len(all_chunks):04d}",
            "text": piece,
            "tokens": count_tokens(piece),
            "metadata": meta,
        })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        {
            "embed_model": EMBED_MODEL,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
            "total_chunks": len(all_chunks),
            "chunks": all_chunks,
        },
        f,
        indent=2,
        ensure_ascii=False,
    )

# === SUMMARY ===
by_source = {}
for c in all_chunks:
    by_source[c["metadata"]["source"]] = by_source.get(c["metadata"]["source"], 0) + 1
token_counts = [c["tokens"] for c in all_chunks]

print(f"\n{'='*80}")
print(f"COMPLETE: {len(all_chunks)} chunks written to {OUTPUT_FILE}")
print(f"{'='*80}")
print("Chunks per source:")
for src, n in sorted(by_source.items()):
    print(f"   {src:8s}: {n}")
if token_counts:
    print(f"Token counts → min {min(token_counts)}, "
          f"max {max(token_counts)}, "
          f"avg {sum(token_counts) // len(token_counts)}")
    over = [t for t in token_counts if t > 256]
    print(f"Chunks over the model's 256-token limit: {len(over)}")
