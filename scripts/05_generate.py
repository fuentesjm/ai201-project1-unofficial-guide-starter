"""Grounded generation step of the CSULB dining RAG pipeline.

Architecture (planning.md):
    ... → Retrieval → [Generation] → Student-friendly answer
    LLM = Groq llama-3.3-70b-versatile, answering ONLY from retrieved chunks.

Grounding is enforced two ways:
  1. A strict system prompt that forbids outside knowledge and mandates a
     fixed refusal string when the context is insufficient.
  2. Source attribution is appended PROGRAMMATICALLY from the retrieved chunks'
     metadata — it does not depend on the LLM remembering to cite. The model is
     also asked to cite inline [n] markers, but the authoritative source list is
     built in code so attribution is guaranteed.
"""

import os

from dotenv import load_dotenv
from groq import Groq

from retrieve import DEFAULT_K, PROJECT_ROOT, retrieve

# Load the project's .env explicitly and let it WIN over any stale GROQ_API_KEY
# already exported in the shell (override=True). Anchoring to PROJECT_ROOT means
# it's found no matter which directory the app is launched from.
load_dotenv(PROJECT_ROOT / ".env", override=True)

GROQ_MODEL = "llama-3.3-70b-versatile"   # free-tier, OpenAI-compatible
REFUSAL = "I don't have enough information on that."

# Grounding is ENFORCED here, not suggested: outside knowledge is forbidden and
# the refusal string is mandatory when the context can't answer the question.
SYSTEM_PROMPT = f"""You are a dining assistant for California State University, Long Beach (CSULB) students.

Follow these rules without exception:
1. Answer ONLY using the numbered documents in the CONTEXT provided with each question.
2. Do NOT use any prior knowledge, training data, or outside information. If a fact
   (a restaurant name, rating, price, hours, or opinion) is not in the CONTEXT, you may
   not state it.
3. If the CONTEXT does not contain enough information to answer the question, reply with
   exactly this sentence and nothing else: "{REFUSAL}"
4. Cite the document numbers you used inline, like [1] or [2][3], next to the claims they support.
5. Do not invent restaurants, reviews, ratings, or details. Do not speculate.

Write a concise, helpful answer for a student in plain language."""

USER_TEMPLATE = """CONTEXT:
{context}

QUESTION: {question}

Answer using only the CONTEXT above. If it is insufficient, reply exactly: "{refusal}\""""

_client = None


def get_client():
    """Initialize the Groq client once, using GROQ_API_KEY from .env."""
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise SystemExit("✗ GROQ_API_KEY not found in environment / .env")
        _client = Groq(api_key=api_key)
    return _client


def source_label(hit):
    """Human-readable source label with document name + position for attribution."""
    m = hit["metadata"]
    loc = f"{m.get('doc_name')}#{m.get('chunk_index')}"
    src = m.get("source")
    if src == "yelp":
        return f"Yelp review of {m.get('restaurant')} ({loc})"
    if src == "reddit":
        return f"Reddit r/CSULB — thread \"{m.get('thread_title')}\" ({loc})"
    if src == "csulb":
        return f"CSULB official dining page ({loc})"
    return f"{m.get('doc_name')} ({loc})"


def format_context(hits):
    """Number each retrieved chunk [n] with its source label, for the prompt."""
    blocks = []
    for i, hit in enumerate(hits, 1):
        blocks.append(f"[{i}] (source: {source_label(hit)})\n{hit['text']}")
    return "\n\n".join(blocks)


def build_source_list(hits):
    """Build the authoritative source list from retrieved metadata (deduped).

    This is what GUARANTEES attribution — independent of what the LLM cites.
    """
    seen = set()
    sources = []
    for hit in hits:
        label = source_label(hit)
        if label not in seen:
            seen.add(label)
            sources.append(label)
    return sources


def answer_question(query, k=DEFAULT_K):
    """Retrieve → ground → generate. Returns answer, source list, and the hits.

    Source attribution is appended in code, not left to the model.
    """
    hits = retrieve(query, k)

    # No retrieval results at all → refuse without calling the LLM.
    if not hits:
        return {"answer": REFUSAL, "sources": [], "hits": []}

    context = format_context(hits)
    user_msg = USER_TEMPLATE.format(context=context, question=query, refusal=REFUSAL)

    completion = get_client().chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0,   # deterministic, minimizes drift from the context
    )
    answer = completion.choices[0].message.content.strip()

    # Programmatic attribution: only attach sources when the model actually answered.
    sources = [] if answer.rstrip(".") == REFUSAL.rstrip(".") else build_source_list(hits)
    return {"answer": answer, "sources": sources, "hits": hits}


def format_response(result):
    """Render answer + an explicit, code-generated Sources section."""
    out = result["answer"]
    if result["sources"]:
        out += "\n\n**Sources:**\n" + "\n".join(f"- {s}" for s in result["sources"])
    return out


# === CLI: run the 5 evaluation questions from planning.md ===
if __name__ == "__main__":
    EVAL_QUESTIONS = [
        "What do reviews say about wait times and crowds at The Outpost Grill?",
        "What do students say on Reddit about dining options directly on the CSULB campus?",
        "Which sandwich restaurants near CSULB campus are recommended on Yelp?",
        "What quick lunch options do students recommend for between classes at CSULB?",
        "Is Sapporo Sushi well-reviewed, and what are students saying about it?",
    ]

    print("=" * 80)
    print(f"GROUNDED GENERATION — {GROQ_MODEL} (top-{DEFAULT_K} retrieval)")
    print("=" * 80)
    for i, q in enumerate(EVAL_QUESTIONS, 1):
        print(f"\n[Q{i}] {q}")
        print("-" * 80)
        print(format_response(answer_question(q)))
