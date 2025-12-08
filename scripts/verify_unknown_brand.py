import sys
import os

# Setup paths
# We are in scripts/ so up one level is project root (wishyahope)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
kataloggia_dir = os.path.join(project_root, 'kataloggia-main')

# Add paths to sys.path
if project_root not in sys.path:
    sys.path.insert(0, project_root)
if kataloggia_dir not in sys.path:
    sys.path.insert(0, kataloggia_dir)

print(f"Project root: {project_root}")
print(f"Kataloggia dir: {kataloggia_dir}")

try:
    from app.services.scraping_service import ScrapingService
except ImportError as e:
    print(f"Import Error: {e}")
    # Try importing from kataloggia-main.app... if direct app import fails? 
    # But sticking to path insertion is safer.
    exit(1)

def verify():
    print("Initializing ScrapingService...")
    service = ScrapingService()
    
    # URL that typically fails with MISSING_NAME due to UNKNOWN brand (generic site)
    url = "https://www.flyingtiger.com.tr/products/4lu-noel-baba-temali-kupe"
    
    print(f"Testing URL: {url}")
    print("Scraping started (this may take 10-20 seconds)...")
    
    try:
        result = service.scrape_product(url)
    except Exception as e:
        print(f"Scrape raised exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
    
    if result:
        print("\n✅ Scrape successful!")
        print(f"Title: {result.get('name')}")
        print(f"Price: {result.get('price')}")
        print(f"Brand: {result.get('brand')}")
        print(f"Image: {result.get('image')[:50]}...")
        
        brand = result.get('brand')
        
        if brand == 'UNKNOWN':
             print("\n❌ FAIL: Brand is still 'UNKNOWN'. Fix didn't work.")
             exit(1)
        elif not brand:
             print("\n❌ FAIL: Brand is missing/None/Empty.")
             exit(1)
        else:
             print(f"\n✅ SUCCESS: Brand fallback worked! Got '{brand}' instead of 'UNKNOWN'.")
             # It should likely be 'FLYINGTIGER' derived from domain
             if 'FLYINGTIGER' in brand:
                 print("   (Brand correctly matches domain derivation)")
                 
        old_price = result.get('old_price')
        if old_price is None:
             print("✅ SUCCESS: old_price is None (Correctly ignored 0 value)")
        elif "0,00 TL" in str(old_price):
             print("❌ FAIL: old_price is '0,00 TL'. Formatting fix failed.")
             # Non-fatal for script but fatal for test
        else:
             print(f"ℹ️ INFO: old_price is present: {old_price}")
    else:
        print("\n❌ FAIL: Scrape returned None. Site might be blocking or selectors completely failed.")
        exit(1)

if __name__ == "__main__":
    verify()
