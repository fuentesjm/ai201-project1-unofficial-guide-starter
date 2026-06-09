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
Domain of choosing was on-campus and off-campus dining options. I believe this knowledge is valuable because it is hard to know where it the best place to eat at in and around campus. CSULB has very limited on-campus dining options and alot of off-campus dining options. There is some great resturants off-campus which may not be well known and hard to find on CSULB website.
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

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

**Overlap:**

**Why these choices fit your documents:**

**Final chunk count:**

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
