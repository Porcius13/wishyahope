import asyncio
from scraper import fetch_data

async def analyze_prices():
    urls = [
        "https://www.defacto.com.tr/regular-fit-dik-yaka-polar-hirka-3285794"
    ]

    for url in urls:
        print(f"\nAnalyzing: {url}")
        try:
            data = await fetch_data(url)
            print(f"Title: {data.get('title')}")
            print(f"Price: {data.get('price')}")
            print(f"Brand: {data.get('brand')}")
            print(f"Image: {data.get('image')}")
            print("-" * 50)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_prices())
