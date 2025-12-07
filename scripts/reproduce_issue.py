
import asyncio
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import fetch_data

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_urls():
    urls = [
        "https://reflectstudio.com/collections/best-seller/products/sincap-sherpa-sweatshirt-kahverengi",
        "https://lego.tr/product/72043-lego-super-mario-mario-kart-interaktif-lego-mario-ve-standard-kart",
        "https://www.mediamarkt.com.tr/tr/product/_xiaomi-redmi-note-14-pro-8256-gb-akilli-telefon-siyah-1243823.html", 
        "https://www.massimodutti.com/tr/tr/yilan-desenli-triko-hirka-l05792923", 
        "https://www.beymen.com/tr/p_lasttouch-geisha-serisi-no6-tablo_1174709"
    ]
    
    for url in urls:
        print(f"\nTesting URL: {url}")
        try:
            # fetch_data is the async function
            result = await fetch_data(url)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_urls())
