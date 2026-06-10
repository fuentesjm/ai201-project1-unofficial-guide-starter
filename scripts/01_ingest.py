import os
import json
import time
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Create output directory
OUTPUT_DIR = "raw_documents"
Path(OUTPUT_DIR).mkdir(exist_ok=True)

print("=" * 80)
print("YELP SCRAPER WITH SELENIUM")
print("=" * 80)

def scrape_yelp_selenium(url, restaurant_name, max_reviews=10):
    """
    Scrape Yelp using Selenium with browser automation.
    
    Args:
        url: Yelp restaurant URL
        restaurant_name: Name of restaurant
        max_reviews: Maximum reviews to collect per restaurant
    """
    
    # Chrome options for stable scraping
    options = webdriver.ChromeOptions()
    # Uncomment to run headless (no window):
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = None
    reviews = []
    
    try:
        print(f"\n[1/4] Opening browser for {restaurant_name}...")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        driver.get(url)
        
        print(f"[2/4] Waiting for reviews to load...")
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='review']")))
        time.sleep(2)
        
        print(f"[3/4] Scrolling to load more reviews (this takes ~10 seconds)...")
        # Scroll down multiple times to trigger lazy loading
        for scroll_count in range(6):
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(1.5)
            print(f"       → Scroll {scroll_count + 1}/6")
        
        print(f"[4/4] Extracting review text...")
        review_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='review']")
        print(f"       → Found {len(review_elements)} total reviews on page")
        
        for idx, review in enumerate(review_elements[:max_reviews]):
            try:
                # Extract rating
                try:
                    rating_elem = review.find_element(By.CSS_SELECTOR, "[role='img']")
                    rating_text = rating_elem.get_attribute("aria-label")
                    rating = rating_text.split()[0] if rating_text else "N/A"
                except NoSuchElementException:
                    rating = "N/A"
                
                # Extract review text - try multiple selectors
                text = "No text found"
                try:
                    text_elem = review.find_element(By.CSS_SELECTOR, "p[lang]")
                    text = text_elem.text.strip()
                except NoSuchElementException:
                    try:
                        text_elem = review.find_element(By.CSS_SELECTOR, "p")
                        text = text_elem.text.strip()
                    except:
                        pass
                
                # Extract author
                try:
                    # Look for review header which contains author info
                    header = review.find_element(By.CSS_SELECTOR, "[role='heading']")
                    author_text = header.text
                    author = author_text.split()[0] if author_text else "Anonymous"
                except NoSuchElementException:
                    author = "Anonymous"
                
                # Store review
                reviews.append({
                    "rating": rating,
                    "author": author,
                    "text": text[:300]  # Limit text length
                })
                
                print(f"       ✓ Review {idx + 1}: {rating} stars from {author}")
                
            except Exception as e:
                print(f"       ⚠ Error extracting review {idx + 1}: {str(e)[:50]}")
                continue
        
        print(f"\n✓ Successfully scraped {len(reviews)} reviews from {restaurant_name}")
        
        return {
            "source": "yelp",
            "restaurant": restaurant_name,
            "url": url,
            "scraped_at": datetime.now().isoformat(),
            "reviews_found": len(reviews),
            "reviews": reviews
        }
    
    except TimeoutException:
        print(f"✗ Timeout: Reviews didn't load for {restaurant_name}")
        print(f"   → Try checking if the URL is correct: {url}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error scraping {restaurant_name}: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def save_document(doc_data, doc_id):
    """Save document to JSON file."""
    if not doc_data:
        return None
    
    filename = f"{OUTPUT_DIR}/doc_{doc_id:02d}_yelp_{doc_data['restaurant'].replace(' ', '_').replace('&', 'and')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(doc_data, f, indent=2, ensure_ascii=False)
    print(f"   Saved to: {filename}\n")
    return filename

# === MAIN EXECUTION ===
if __name__ == "__main__":
    
    # Define restaurants to scrape
    restaurants = {
        "The Outpost Grill": "https://www.yelp.com/biz/the-outpost-grill-long-beach",
        "Marris Pizza": "https://www.yelp.com/biz/marris-pizza-and-italian-restaurant-long-beach",
        "Blue Burro": "https://www.yelp.com/biz/blue-burro-long-beach-3",
        "Fantastic Cafe": "https://www.yelp.com/biz/fantastic-caf%C3%A9-long-beach-3",
        "Sapporo Sushi": "https://www.yelp.com/biz/sapporo-sushi-long-beach"
    }
    
    doc_id = 4  # Start after existing documents (doc_01, doc_02, doc_03)
    saved_count = 0
    
    print(f"\nTarget: Scrape {len(restaurants)} Yelp restaurants\n")
    
    for restaurant_name, url in restaurants.items():
        print(f"{'='*80}")
        print(f"Scraping: {restaurant_name}")
        print(f"URL: {url}")
        print(f"{'='*80}")
        
        # Scrape
        doc = scrape_yelp_selenium(url, restaurant_name, max_reviews=10)
        
        # Save
        if doc:
            save_document(doc, doc_id)
            doc_id += 1
            saved_count += 1
        else:
            print(f"Skipped {restaurant_name}\n")
        
        # Add delay between requests (be respectful to Yelp)
        if restaurant_name != list(restaurants.keys())[-1]:
            print("Waiting 5 seconds before next restaurant...\n")
            time.sleep(5)
    
    print(f"\n{'='*80}")
    print(f"COMPLETE: Successfully saved {saved_count}/{len(restaurants)} restaurants")
    print(f"Output directory: {OUTPUT_DIR}/")
    print(f"{'='*80}")