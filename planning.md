# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
Domain of choosing was on-campus and off-campus dining options. I believe this knowledge is valuable because it is hard to know where it the best place to eat at in and around campus. CSULB has very limited on-campus dining options and alot of off-campus dining options. There is some great resturants off-campus which may not be well known and hard to find on CSULB website.
---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Reddit | Different opinions of places to eat aorund CSULB Campus | https://www.reddit.com/r/CSULB/comments/1e5w502/good_food_place_around_csulb_and_in_long_beach/|
| 2 | Grubhub | Reviews | |
| 3 | CSULB | List of Places to Eat on Campus | https://www.csulb.edu/beach-shops/eat-and-shop?utm_source=Drupal&utm_medium=Web%20Rotator&utm_campaign=Rotator#eateries |
| 4 | Yelp | List of resturants near campus and on in order of best reviews | https://www.yelp.com/search?find_desc=Food&find_loc=90815&l=g%3A-118.11471984191658%2C33.78240576943979%2C-118.12422850106053%2C33.77138750241378 |
| 5 | Google Places  | List of resturants near campus | https://www.google.com/search?sca_esv=b0e7c006bdd513b1&sxsrf=ANbL-n6XK0j3QvNX5gJ1muqjFsYaSAN7hA:1781039070811&q=top+rated+restaurants+near+california+state+university+long+beach&uds=ALYpb_ncDc7jTlmw6Mmq7NjuX5c-FcIr1Fzv1FPScOtQ3QSiLeHGE33Ku6PfayYRWmciqP4yKPr0MofYsYpYQ-4L_XcFqiKp2flnQcOF5TTJVdJGytOUdyuZaUlgwDuQsuzJaHaFvYtJWfdtDi6b78aK6ht1NUaKdipNQfwGd71kfo5XiZthUEvhn5zIt17cdFadatlkb-zeYmFu_EhG6ub1nVEcHilSKMH_k-a-OIKxDWOr0Tp9Uv4KyN_uBTbL0FsFsjj-LfVg&udm=1&sa=X&ved=2ahUKEwj1h5bJh_uUAxXrIUQIHf-3F90QxKsJKAF6BAghEAE&ictx=0&biw=1440&bih=789&dpr=2 |
| 6 | Yelp  | Yelp Reviews of Outpost Grill | https://www.yelp.com/biz/the-outpost-grill-long-beach#reviews |
| 7 | Yelp | Yelp Reviews of Marris Pizza and Italian restaurant | https://www.yelp.com/biz/marris-pizza-and-italian-restaurant-long-beach?osq=Sandwiches#reviews|
| 8 | Yelp | Yelp Reviews of Blue Burro | https://www.yelp.com/biz/blue-burro-long-beach-3?osq=Sandwiches#reviews |
| 9 | Yelp | Yelp Reviews of Fantastic Cafe | https://www.yelp.com/biz/fantastic-caf%C3%A9-long-beach-3?osq=Sandwiches |
| 10 | Yelp |  Yelp Reviews of Sapporo sushi | https://www.yelp.com/biz/sapporo-sushi-long-beach?osq=Sandwiches#reviews|

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
200-300 tokens

**Overlap:**
30-50 tokens

**Reasoning:**
Large chunk token size over 300 tokens might create more noise such as irrelevant gibberish being retrieved. Majority of reviews and lists in my URLs have information that consist of decent size sentences which will make small chunks have no surrounding context.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
all-MiniLM-L6-v2 via sentence-transformer
(why? model is good at semantic similarity for conversational, opinion-based text not keyword matching)

**Top-k:**
5-7
(why? gives multiple restuaarant recommendations or varied opions on the same resturant)

**Production tradeoff reflection:**
OpenAI's text-embedding-3-large
much higher accuracy for dining opinions if cost weren't a constraint

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What do reviews say about wait times and crowds at The Outpost Grill? | reviews of Outpost Grill that mention wait time, crowd size, or service speed from their reviews section. |
| 2 | What do students say on Reddit about dining options directly on the CSULB campus? | discussion mentioning limited on-campus options and specific student opinions (e.g., complaints about limited choices or specific dining hall names). |
| 3 | Which sandwich restaurants near CSULB campus are recommended on Yelp? | Yelp reviews/mentions of Blue Burro, Marris Pizza, or Fantastic Cafe, showing they are the sandwich-focused options |
| 4 | What quick lunch options do students recommend for between classes at CSULB? | discussion or review mentions of fast-casual restaurants suitable for quick dining near campus. |
| 5 | Is Sapporo Sushi well-reviewed, and what are students saying about it? | Sapporo Sushi Yelp reviews with rating/sentiment and specific feedback about the restaurant. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. off-topic retrieval. output information which does not make sense with the prompt

2. missing source attribution

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->


    ┌─────────────────────┐
    │ Document Ingestion  │
    │  (BeautifulSoup,    │
    │   requests, Yelp    │
    │   & Reddit APIs)    │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │    Chunking         │
    │  (LangChain's       │
    │   RecursiveCharacter│
    │   TextSplitter or   │
    │   custom splitter)  │
    │  200-300 tokens,    │
    │  30-50 overlap      │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────────────────────┐
    │ Embedding + Vector Store            │
    │  (sentence-transformers:            │
    │   all-MiniLM-L6-v2 → embeddings)    │
    │  (FAISS or ChromaDB for storage)    │
    └──────────┬──────────────────────────┘
               │
               ▼
    ┌─────────────────────┐
    │    Retrieval        │
    │  (FAISS/ChromaDB    │
    │   similarity search)│
    │  top-k = 5-7        │
    │  chunks retrieved   │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │    Generation       │
    │  (Claude or GPT-4   │
    │   with retrieved    │
    │   context)          │
    │  → Student-friendly │
    │     answer          │
    └─────────────────────┘
---


## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

Milestone 3 — Ingestion and chunking:

- Tool: Claude (Claude Code).
- Input: My Documents table (the Reddit/Yelp/CSULB URLs) and my Chunking Strategy section (250-token chunks, 40 overlap, MiniLM's 256-token cap). I'll ask it to write the ingest, clean, and chunk scripts.
- Expected output: Ingestion into raw_documents/, cleaning that strips HTML/nav/footer noise and parses the Reddit comment tree, and a token-aware chunker that packs whole sentences up to 250 tokens with overlap and records source metadata.
- Verification: Read ~5 sample chunks and assert no chunk exceeds 256 tokens. I'll override chunk size from 300 to 250 and add parent-comment threading if a reply loses its referent.

Milestone 4 — Embedding and retrieval:

- Tool: Claude (Claude Code).
- Input: My Retrieval Approach section (all-MiniLM-L6-v2, top-k 5–7) and the architecture diagram. I'll ask it to implement embedding and a retrieval function with source metadata.
- Expected output: A script that stores normalized embeddings in a persistent ChromaDB collection (cosine space), and a retrieve(query, k) function returning top-k chunks with distance scores and metadata.
- Verification: Run my 5 eval questions through retrieve() and inspect the returned chunks and distances. I expect to override the metadata to store doc_name + chunk_index for attribution and lower top-k to 5 to cut off-target results.

Milestone 5 — Generation and interface:

- Tool: Claude (Claude Code).
- Input: The Generation stage of my diagram plus my Anticipated Challenges (off-topic retrieval, missing attribution), with the rule that the model answers only from retrieved context, refuses when context is thin, and cites sources. I'll ask it to write the generation script and a simple app interface.
- Expected output: A generation function at temperature 0 with a system prompt that forbids outside knowledge and forces a fixed refusal string, plus a source list built programmatically from chunk metadata so attribution can't be hallucinated.
- Verification: Ask an out-of-corpus question (capital of France) and confirm it returns only the refusal string with no sources, then run all 5 eval questions and check each claim traces to a retrieved chunk. I diverged from the diagram's Claude/GPT-4 to Groq's free llama-3.3-70b-versatile, noted here per the spec.
