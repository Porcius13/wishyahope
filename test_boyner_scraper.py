import logging
from scraper import scrape_product

logging.basicConfig(level=logging.INFO)

def test_boyner():
    url = "https://www.boyner.com.tr/erkek-lacivert-basic-sweatshirt-p-15623165?magaza=u-s-polo-assn"
    print(f"Testing scraper for: {url}")
    
    result = scrape_product(url)
    
    if result:
        print("\n--- Scraper Result ---")
        print(f"Title: {result.get('title')}")
        print(f"Price: {result.get('price')}")
        print(f"Image: {result.get('image')}")
        print(f"Brand: {result.get('brand')}")
        
        # Verification
        if result.get('price') == '1399.95':
            print("\n[PASS] Price is correct.")
        else:
            print(f"\n[FAIL] Price is incorrect. Expected 1399.95, got {result.get('price')}")
            
        if '900/1254' in result.get('image', '') or 'mnresize/900' in result.get('image', ''):
            print("[PASS] Image is high resolution.")
        else:
            print(f"[FAIL] Image might be low resolution: {result.get('image')}")
            
    else:
        print("\n[FAIL] Scraper returned None.")

if __name__ == "__main__":
    test_boyner()
