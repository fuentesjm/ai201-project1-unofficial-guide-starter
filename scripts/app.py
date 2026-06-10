"""Gradio interface for the CSULB dining RAG assistant (Milestone 5).

Wires the full pipeline together for an end user:
    query → retrieve (ChromaDB) → grounded generation (Groq) → answer + sources

Run:  python scripts/app.py     then open the printed local URL.
"""

import importlib

import gradio as gr

# 05_generate.py starts with a digit, so import it via importlib.
gen = importlib.import_module("05_generate")
from retrieve import DEFAULT_K

EXAMPLES = [
    "What do reviews say about wait times and crowds at The Outpost Grill?",
    "What do students say on Reddit about dining options directly on the CSULB campus?",
    "Is Sapporo Sushi well-reviewed, and what are students saying about it?",
]


def respond(question, k):
    """Answer a question and return (markdown answer+sources, retrieved chunks)."""
    if not question or not question.strip():
        return "Please enter a question about CSULB dining.", ""

    result = gen.answer_question(question.strip(), k=int(k))
    answer_md = gen.format_response(result)

    # Show the raw retrieved chunks so grounding is transparent/auditable.
    retrieved = []
    for i, hit in enumerate(result["hits"], 1):
        retrieved.append(
            f"[{i}] dist={hit['distance']:.3f}  {gen.source_label(hit)}\n{hit['text']}"
        )
    return answer_md, "\n\n".join(retrieved)


with gr.Blocks(title="CSULB Dining Guide") as demo:
    gr.Markdown(
        "# 🍔 The Unofficial CSULB Dining Guide\n"
        "Ask about on- and off-campus food. Answers come **only** from retrieved "
        "Reddit, Yelp, and CSULB documents, with sources listed."
    )

    with gr.Row():
        question = gr.Textbox(
            label="Your question",
            placeholder="e.g. Which sandwich spots near campus are good?",
            scale=4,
        )
        k = gr.Slider(
            minimum=3, maximum=8, value=DEFAULT_K, step=1,
            label="Chunks to retrieve (top-k)", scale=1,
        )

    ask = gr.Button("Ask", variant="primary")
    answer = gr.Markdown(label="Answer")
    with gr.Accordion("Retrieved context (what the answer is grounded in)", open=False):
        retrieved = gr.Textbox(label="", lines=12)

    gr.Examples(examples=EXAMPLES, inputs=question)

    ask.click(respond, inputs=[question, k], outputs=[answer, retrieved])
    question.submit(respond, inputs=[question, k], outputs=[answer, retrieved])


if __name__ == "__main__":
    demo.launch()
