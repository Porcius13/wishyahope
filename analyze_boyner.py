import asyncio
from playwright.async_api import async_playwright
import json

async def analyze_boyner():
    url = "https://www.boyner.com.tr/erkek-lacivert-basic-sweatshirt-p-15623165?magaza=u-s-polo-assn"
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-infobars',
                '--window-position=0,0',
                '--ignore-certificate-errors',
                '--ignore-certificate-errors-spki-list',
                '--disable-accelerated-2d-canvas',
                '--no-zygote',
                '--no-first-run',
                '--disable-gpu',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="tr-TR",
            timezone_id="Europe/Istanbul"
        )
        
        page = await context.new_page()
        
        try:
            from playwright_stealth import Stealth
            await Stealth().apply_stealth_async(page)
        except ImportError:
            print("Stealth import failed")
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)
            
            # Scroll down to trigger lazy loading
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
            content = await page.content()
            with open("boyner_dump.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("Dump created: boyner_dump.html")
            
            # Extract JSON-LD
            json_lds = await page.evaluate("""() => {
                const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                return Array.from(scripts).map(s => s.innerText);
            }""")
            
            print(f"Found {len(json_lds)} JSON-LD scripts")
            for i, ld in enumerate(json_lds):
                try:
                    data = json.loads(ld)
                    print(f"\n--- JSON-LD #{i+1} ---")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                except:
                    print(f"Failed to parse JSON-LD #{i+1}")

            await page.screenshot(path="boyner_screenshot.png")
            print("Screenshot created: boyner_screenshot.png")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze_boyner())
