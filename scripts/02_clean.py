import json
import re
from pathlib import Path

OUTPUT_DIR = "cleaned_documents"
Path(OUTPUT_DIR).mkdir(exist_ok=True)

print("=" * 80)
print("DOCUMENT CLEANING: Remove Boilerplate, Keep Valuable Content")
print("=" * 80)

def remove_html_tags(text):
    """Remove HTML tags while preserving text content."""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&quot;', '"', text)
    return text

def remove_boilerplate(text):
    """Remove common boilerplate elements."""
    # Remove cookie banners
    text = re.sub(r'(?i)(cookie|accept cookies|privacy policy|terms of service).*?(?=\n|$)', '', text)
    
    # Remove navigation elements (only when followed by a UI separator, not mid-sentence)
    text = re.sub(r'(?i)(navigation|menu|home|about|contact|settings|sign in|log in)(?:\s*→|\s*\|)+', '', text)

    # Remove UI buttons — only as standalone lines/segments so prose like
    # "I like the tacos" or "food about 10 mins away" is preserved.
    text = re.sub(r'(?im)^\s*(read more|show more|see more|click here|share|like|comment|helpful)\s*$', '', text)

    # Remove share buttons and counts
    text = re.sub(r'(?i)(share on|posted by|comments?:\s*\d+|likes?:\s*\d+|shares?:\s*\d+)', '', text)
    
    # Remove repeated headers/footers (common patterns)
    text = re.sub(r'(?i)(home\s*>\s*restaurants?|yelp home)', '', text)
    text = re.sub(r'(?i)©.*?\d{4}.*?(?:\n|$)', '', text)
    
    # Remove empty lines and excessive whitespace
    text = re.sub(r'\n\s*\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    
    return text.strip()

def clean_csulb_document(doc):
    """Clean CSULB official page - keep dining locations and descriptions."""
    print("\n[CLEANING] CSULB Official Page")
    
    cleaned_content = doc.get("content", "")
    cleaned_content = remove_html_tags(cleaned_content)
    cleaned_content = remove_boilerplate(cleaned_content)

    # Drop leftover "Image" tokens (alt text from stripped <img> tags)
    cleaned_content = re.sub(r'Image', ' ', cleaned_content)
    # Split run-on fields: the scrape concatenates entries with no spaces
    # ("ClosedNugget Grill", "StoreSummer Hours"). Insert a space at every
    # lowercase→uppercase boundary so eatery names and hours read cleanly.
    cleaned_content = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', cleaned_content)
    cleaned_content = re.sub(r' +', ' ', cleaned_content).strip()

    return {
        "source": "csulb",
        "url": doc.get("url"),
        "content": cleaned_content,
        "content_length": len(cleaned_content.split())
    }

def clean_reddit_comment_text(text):
    """Strip boilerplate from a single Reddit comment/post body."""
    text = remove_boilerplate(text)
    text = re.sub(r'(?i)(edit:|edit \d+|ninja edit|thanks for the gold)', '', text)
    return text.strip()


def collect_reddit_comments(children, out, parent_text=None, parent_author=None):
    """Recursively walk the Reddit comment tree, keeping substantive opinions.

    Reddit's API returns each comment under {"kind": "t1", "data": {...}},
    where nested replies live in data["replies"] as another Listing (or "").

    Each reply records its parent's text/author so a comment like "I tried it
    once and it was great" stays interpretable once chunked — the referent
    ("it") would otherwise live in a sibling chunk and be lost at retrieval.
    """
    for node in children:
        if node.get("kind") != "t1":
            continue  # skip "more" stubs and non-comment kinds

        data = node.get("data", {})
        body = data.get("body", "") or ""

        # Drop deleted/removed bodies — no usable content
        cleaned = ""
        if body.strip() not in ("", "[deleted]", "[removed]"):
            cleaned = clean_reddit_comment_text(body)
            # Keep only substantive comments (more than 5 words)
            if len(cleaned.split()) > 5:
                comment = {
                    "text": cleaned,
                    "author": data.get("author", "Anonymous"),
                    "score": data.get("score"),
                }
                # Attach parent context only for actual replies (t1 → t1)
                if parent_text:
                    comment["reply_to"] = parent_author
                    comment["parent_text"] = parent_text
                out.append(comment)

        # Recurse into nested replies, passing this comment as their parent.
        # Fall back to the existing parent if this body was deleted/empty.
        replies = data.get("replies")
        if isinstance(replies, dict):
            collect_reddit_comments(
                replies.get("data", {}).get("children", []),
                out,
                parent_text=cleaned or parent_text,
                parent_author=(data.get("author", "Anonymous") if cleaned else parent_author),
            )


def clean_reddit_document(doc):
    """Clean a raw Reddit thread (.json API dump) - keep post + opinionated comments.

    Format: a 2-element list. doc[0] is the post listing (t3),
    doc[1] is the comment tree listing (t1 nodes).
    """
    print("\n[CLEANING] Reddit Discussion")

    # Handle the raw Reddit API list format
    post_data = {}
    comment_children = []
    if isinstance(doc, list) and len(doc) >= 2:
        try:
            post_data = doc[0]["data"]["children"][0]["data"]
        except (KeyError, IndexError, TypeError):
            post_data = {}
        comment_children = doc[1].get("data", {}).get("children", [])

    # Post title + selftext provide the question/context for the thread
    thread_title = post_data.get("title", "")
    selftext = clean_reddit_comment_text(post_data.get("selftext", "") or "")

    cleaned_comments = []
    collect_reddit_comments(comment_children, cleaned_comments)

    return {
        "source": "reddit",
        "subreddit": post_data.get("subreddit_name_prefixed") or post_data.get("subreddit"),
        "url": post_data.get("url"),
        "thread_title": thread_title,
        "post_text": selftext,
        "comments_found": len(cleaned_comments),
        "comments": cleaned_comments
    }

def clean_yelp_document(doc):
    """Clean Yelp reviews - keep ratings, author, and review text."""
    print("\n[CLEANING] Yelp Reviews")
    
    restaurants = doc.get("restaurants", [])
    cleaned_restaurants = []
    
    for restaurant in restaurants:
        reviews = restaurant.get("reviews", [])
        cleaned_reviews = []
        
        for review in reviews:
            # Keep structured review data
            cleaned_review = {
                "rating": review.get("rating"),
                "author": review.get("author", "Anonymous"),
                "text": remove_boilerplate(review.get("text", ""))
            }
            
            # Only keep if review text is substantive
            if len(cleaned_review["text"].split()) > 5:
                cleaned_reviews.append(cleaned_review)
        
        if cleaned_reviews:
            cleaned_restaurants.append({
                "name": restaurant.get("name"),
                "rating": restaurant.get("rating"),
                "url": restaurant.get("url"),
                "reviews_found": len(cleaned_reviews),
                "reviews": cleaned_reviews
            })
    
    return {
        "source": "yelp",
        "restaurants_found": len(cleaned_restaurants),
        "total_reviews": sum(len(r["reviews"]) for r in cleaned_restaurants),
        "restaurants": cleaned_restaurants
    }

# === MAIN PROCESSING ===
input_files = {
    "doc_01_csulb.json": clean_csulb_document,
    "doc_04_yelp_sample_data.json": clean_yelp_document,
    "reddit_good_food_place_around_csulb_and_in_long_beach.json": clean_reddit_document,
    "reddit_another_subreddit.json": clean_reddit_document
}

success_count = 0
total_count = 0

for filename, clean_func in input_files.items():
    input_path = f"raw_documents/{filename}"
    
    if not Path(input_path).exists():
        print(f"\n⚠ Skipped: {filename} (not found)")
        continue
    
    total_count += 1
    
    try:
        # Load raw document
        with open(input_path, "r", encoding="utf-8") as f:
            raw_doc = json.load(f)
        
        # Clean it
        cleaned_doc = clean_func(raw_doc)
        
        # Save cleaned version
        output_filename = f"cleaned_{filename.replace('doc_', '').replace('reddit_', '')}"
        output_path = f"{OUTPUT_DIR}/{output_filename}"
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_doc, f, indent=2, ensure_ascii=False)
        
        print(f"   ✓ Saved: {output_path}")
        success_count += 1
        
    except Exception as e:
        print(f"   ✗ Error processing {filename}: {e}")

print(f"\n{'='*80}")
print(f"COMPLETE: {success_count}/{total_count} documents cleaned successfully")
print(f"Output directory: {OUTPUT_DIR}/")
print(f"{'='*80}\n")

# === SUMMARY ===
print("WHAT WAS REMOVED:")
print("  ✓ HTML tags and entities")
print("  ✓ Cookie banners and privacy notices")
print("  ✓ Navigation menus and UI elements")
print("  ✓ 'Read more', 'Share', 'Like' buttons")
print("  ✓ Comment counts and vote counts")
print("  ✓ Website headers and footers")
print("  ✓ Copyright notices")
print("  ✓ Reddit boilerplate (edit notes, upvote notices)")
print()
print("WHAT WAS KEPT:")
print("  ✓ Review text and opinions")
print("  ✓ Ratings and scores")
print("  ✓ Author/user names")
print("  ✓ Restaurant names and descriptions")
print("  ✓ URLs and source attribution")
print("  ✓ Substantive comments (>5-10 words)")
