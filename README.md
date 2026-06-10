# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
My domain is on-campus and off-campus dining options for CSULB students. This knowledge is valuable because it is genuinely hard to know where the best places to eat are in and around campus. CSULB has very limited on-campus dining options and a large number of off-campus options. Some of the best off-campus restaurants are not well known and are hard to find through the official CSULB website, which only lists campus eateries and their hours — not opinions, prices, wait times, or whether a place is actually good. 

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

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

**Documents actually ingested into the corpus** (`raw_documents/` → `cleaned_documents/`):

| File | Source | Content |
|------|--------|---------|
| `doc_01_csulb.json` | CSULB official page | Campus eateries + summer hours (one long page) |
| `doc_04_yelp_sample_data.json` | Yelp | 5 restaurants (Outpost Grill, Marris Pizza, Blue Burro, Fantastic Cafe, Sapporo Sushi), 25 reviews total |
| `reddit_good_food_place_around_csulb_and_in_long_beach.json` | Reddit r/CSULB | Thread asking for food recommendations around campus |
| `reddit_another_subreddit.json` | Reddit r/CSULB | "Food on campus" thread (complaints about limited options, dining hall, meal plans) |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 250 tokens because our raw documents are not huge responses, some are short but others are moderate in size.

**Overlap:** 40 tokens. When a chunk is closed, trailing sentences worth ~40 tokens are carried into the next chunk so information that sits on a boundary isn't cut in half.

**Why these choices fit my documents:** My planning spec called for 200–300 tokens / 30–50 overlap. I locked in **250 / 40** for a concrete reason: `all-MiniLM-L6-v2` truncates input at **256 tokens**, so a 300-token chunk would be silently cut off at embed time. 250 sits at the top of my range while staying under that hard cap — verified that **0 of 79 chunks exceed 256 tokens** (max = 250). My documents are mostly short, self-contained reviews and comments, so most chunks are a single review/comment (avg 73 tokens); the only document that actually needs splitting is the run-on CSULB hours page, which has no sentence boundaries and is split with a sliding token window.

**Preprocessing before chunking** (`scripts/02_clean.py`):
- Stripped HTML tags and entities; removed cookie banners, nav menus, "read more"/share UI elements, and copyright/footer boilerplate.
- Parsed the raw Reddit API JSON (a post-listing + nested comment tree), keeping the post text and recursively extracting substantive comments (>5 words), dropping `[deleted]`/`[removed]`.
- **Reply-threading:** each reply stores its parent comment's text, so a comment like *"I tried it once and it was great"* keeps its referent ("it") instead of becoming meaningless once chunked.
- Cleaned the CSULB page's leftover `Image` alt-text noise and inserted spaces at run-on field boundaries.
- During chunking, source context (restaurant name + rating, or Reddit thread title) is folded into each chunk's text so every chunk is self-describing, and each chunk records its **source document name + position in that document** as metadata for attribution.

**Final chunk count:** **79 chunks** total — 25 Yelp, 49 Reddit, 5 CSULB.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, loaded with `SentenceTransformer("all-MiniLM-L6-v2")`. I chose it because it runs locally with no API key and no rate limits, and it is strong at *semantic* similarity for conversational, opinion-based text (reviews and Reddit comments) rather than pure keyword matching. Embeddings are L2-normalized and stored in ChromaDB with a cosine distance space.

**Production tradeoff reflection:** If I were deploying this for real students and cost weren't a constraint, I would weigh:
- **Accuracy on domain-specific text** — `all-MiniLM-L6-v2` is small (384-dim) and, as my Q3 failure shows, it doesn't strongly separate a specific category like "sandwich" from generic "food near campus" recommendations. `OpenAI text-embedding-3-large` (3072-dim) would likely rank the genuinely relevant reviews higher.
- **Context length** — MiniLM's 256-token cap forced my chunk-size ceiling. A model with a larger window would let me keep whole multi-paragraph reviews together without splitting.
- **Latency vs. local control** — MiniLM is instant and private (nothing leaves the machine). An API-hosted model adds per-query network latency and sends user questions to a third party, which is a privacy tradeoff for a student tool.
- **Multilingual support** — not a big factor for this English-only CSULB corpus, but a multilingual model would matter if I added non-English reviews.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**LLM:** Groq `llama-3.3-70b-versatile` (free-tier, OpenAI-compatible), initialized with `from groq import Groq` and `GROQ_API_KEY` from `.env`. Run at `temperature=0` for deterministic, context-faithful output (`scripts/05_generate.py`).

**System prompt grounding instruction (actual text):**
> "Answer ONLY using the numbered documents in the CONTEXT provided with each question. Do NOT use any prior knowledge, training data, or outside information. If a fact (a restaurant name, rating, price, hours, or opinion) is not in the CONTEXT, you may not state it. If the CONTEXT does not contain enough information to answer the question, reply with exactly this sentence and nothing else: *'I don't have enough information on that.'* Cite the document numbers you used inline, like [1] or [2][3]. Do not invent restaurants, reviews, ratings, or details."

This **enforces** grounding rather than suggesting it: outside knowledge is forbidden and the refusal string is mandatory when context is insufficient. I verified this works — asking *"What is the capital of France?"* (nothing in the corpus) returns exactly *"I don't have enough information on that."* with no sources, instead of answering from training data. The retrieved chunks are passed in a numbered `[1]…[k]` format, each labeled with its source, so the model can cite by number.

**How source attribution is surfaced in the response:** Attribution is **programmatically guaranteed**, not left to the LLM. After generation, `build_source_list()` constructs the `Sources:` section in code from the retrieved chunks' metadata (`doc_name#chunk_index`, deduplicated). The model's inline `[n]` citations are a bonus, but the authoritative source list is built from metadata so attribution can never be hallucinated or forgotten. Sources are suppressed when the answer is the refusal string.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do reviews say about wait times and crowds at The Outpost Grill? | Outpost reviews mentioning wait time, crowd size, or service speed | Long waits especially on weekends, crowded at lunch, slow service, parking is a "nightmare" (circled 15 min); still "worth the wait" for a quick bite. All 5 sources were Outpost reviews. | Relevant | **Accurate** |
| 2 | What do students say on Reddit about dining options directly on the CSULB campus? | Limited on-campus options + specific student opinions | Dining hall is $13 all-you-can-eat (a good deal), other options overpriced, discussion of meal plans (~few hundred/month) and whether deals are dorm-only. | Partially relevant | **Partially accurate** — grounded and real, but it surfaced the dining-hall/meal-plan sub-thread and missed the headline complaint of that thread ("they got rid of the food court and the Nugget") because those chunks fell outside the top-5. |
| 3 | Which sandwich restaurants near CSULB campus are recommended on Yelp? | Yelp mentions of Blue Burro, Marris Pizza, or Fantastic Cafe as sandwich options | Named only **Fantastic Cafe** (4.2, "great sandwiches"). | Off-target | **Partially accurate / incomplete** — see Failure Case Analysis below. |
| 4 | What quick lunch options do students recommend for between classes at CSULB? | Fast-casual / quick options near campus | Bring your own lunch + campus microwaves, dining hall with a commuter plan, walk to Blue Burro / El Pollo Loco / Subway, or use Uber Eats. | Relevant | **Accurate** |
| 5 | Is Sapporo Sushi well-reviewed, and what are students saying about it? | Sapporo Yelp reviews with rating + sentiment | Yes — 4.7 overall, "best sushi near campus," fresh ingredients, great prices, friendly staff, good for study dates; spicy tuna roll and chirashi recommended. All 5 sources were Sapporo reviews (similarity 0.78–0.82). | Relevant | **Accurate** |

**Retrieval quality:** Relevant for Q1, Q4, Q5; Partially relevant for Q2; Off-target for Q3.
**Response accuracy:** Accurate for Q1, Q4, Q5; Partially accurate for Q2 and Q3.

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** Q3 — "Which sandwich restaurants near CSULB campus are recommended on Yelp?"

**What the system returned:** Only **Fantastic Cafe**, even though the corpus contains **10 chunks** that explicitly mention "sandwich(es)," including **four** Fantastic Cafe reviews (#20, #21, #23, #24), a Blue Burro review, and a Reddit mention of Ike's sandwiches.

**Root cause (tied to a specific pipeline stage):** This is a **retrieval / embedding** failure, not a generation failure. With top-k = 5, the retrieved set was:
1. `good_food..#0` (dist 0.307) — the Reddit OP's *question* ("any good food places around campus?")
2. `good_food..#18` (0.361) — East Coast Bagels comment
3. `good_food..#5` (0.364) — an unrelated "corner Chinese restaurant" comment
4. `doc_04_yelp..#20` (0.366) — Fantastic Cafe (the only relevant Yelp chunk that made the cut)
5. `good_food..#2` (0.369) — a taco/bakery comment

Two embedding-model effects combined:
- **Question-matches-question artifact.** `all-MiniLM-L6-v2` embeds my query mostly on its "recommended food places near CSULB" framing. The Reddit OP post is almost the same sentence ("good food places around campus… any types of foods"), so it scored *highest* (0.307) despite containing **zero answer content** — it consumed the #1 slot with a non-answer.
- **Weak category sensitivity.** The genuinely relevant Yelp reviews phrase it as "Great sandwiches and coffee" / "Decent sandwiches but lines," leading with other words. The small 384-dim model weights the generic "near campus / recommended" semantics over the specific token *sandwich*, so three of the four Fantastic Cafe sandwich reviews ranked *below* the top-5 cutoff. With one slot lost to the OP question and three to off-target Reddit comments, only a single sandwich review survived — so generation could only name one restaurant. (Generation itself behaved correctly: it grounded on the one relevant chunk and did **not** hallucinate other sandwich shops.)

**What I would change to fix it:**
1. **Exclude OP "question" chunks from the index** — they match queries semantically but contain no answers, and they keep stealing the top retrieval slot (this also hurt Q2).
2. **Hybrid retrieval** — combine vector similarity with a keyword/BM25 signal so the literal token "sandwich" is weighted, pulling the corroborating Fantastic Cafe reviews into the top-k.
3. **Upgrade the embedding model** (e.g., `text-embedding-3-large`) for better category separation, as noted in my Embedding Model reflection.
4. A lighter fix: raise k or add a reranker so more of the on-topic reviews survive the cutoff.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
 Writing the Chunking Strategy and Retrieval Approach sections *before* coding forced me to commit to concrete numbers (200–300 token chunks, `all-MiniLM-L6-v2`, top-k 5–7). That specificity surfaced a conflict early: my planned 300-token chunks would exceed MiniLM's 256-token limit and get silently truncated at embed time. Because the spec named both the chunk range *and* the model, I caught this before indexing and locked the chunk size at 250 — under the cap and verified against the tokenizer. The architecture diagram also kept the pipeline honest: each stage had a defined input/output, so I built `ingest → clean → chunk → embed → retrieve → generate` as discrete, testable scripts instead of one tangled file.

**One way your implementation diverged from the spec, and why:** 
My planning diagram listed **Claude or GPT-4** for generation and **LangChain's RecursiveCharacterTextSplitter** for chunking, but I diverged on both. For generation I used **Groq `llama-3.3-70b-versatile`** because it's free-tier and rate-limit-free, which fits a no-budget student project better than a paid API. For chunking I wrote a **custom token-aware splitter** instead of LangChain because LangChain wasn't a project dependency, and a custom splitter let me measure tokens with the embedding model's exact tokenizer and add reply-threading — something the generic character splitter couldn't do. Both divergences were driven by practical constraints (cost, dependencies) discovered during implementation, which is exactly what the spec told me to update as I went.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1 — Chunking implementation**

- *What I gave the AI:* My Chunking Strategy section (200–300 tokens / 30–50 overlap) plus the fact that `all-MiniLM-L6-v2` truncates at 256 tokens, and asked it to implement the chunker.
- *What it produced:* A token-aware sentence-packing splitter (`scripts/03_chunk.py`) that counts tokens with the model's own tokenizer, packs whole sentences up to the limit, carries overlap sentences, and falls back to a sliding token window for the run-on CSULB page.
- *What I changed or overrode:* I set the chunk size to exactly **250** (not 300) so nothing exceeds the 256-token model cap, and **40** overlap. After printing and inspecting 5 sample chunks, I found a reply like *"I tried it once and it was great"* had lost its referent, so I directed it to add **parent-comment threading** so replies keep the comment they're answering.

**Instance 2 — Embedding + retrieval**

- *What I gave the AI:* My Retrieval Approach section and the architecture diagram (all-MiniLM-L6-v2 → ChromaDB, top-k 5–7), asking it to implement the embedding step and a retrieval function with source metadata.
- *What it produced:* `scripts/04_embed.py` (embeds all chunks into a persistent ChromaDB collection with cosine space) and `scripts/retrieve.py` (a `retrieve(query, k)` function returning chunks with distance scores and source metadata).
- *What I changed or overrode:* The initial metadata only stored a global chunk id, so I directed it to add **`doc_name` + `chunk_index`** (the chunk's position *within its source document*) for proper attribution. I also lowered top-k from 6 to **5** to match the "start at 4–5" guidance and to reduce the off-target dilution I saw in the Q3 results, and anchored all file paths to the project root after the app silently read an empty database when launched from the wrong directory.
