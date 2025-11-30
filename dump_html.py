import asyncio
from playwright.async_api import async_playwright

async def dump_html():
    urls = {
        "defacto": "https://www.defacto.com.tr/regular-fit-kapusonlu-sweatshirt-3285821",
        "lcw": "https://www.lcw.com/yuksek-bel-kadin-tayt-siyah-o-5143405"
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        for name, url in urls.items():
            print(f"Fetching {name}...")
            page = await browser.new_page()
            await page.goto(url, timeout=60000)
            content = await page.content()
            with open(f"{name}.html", "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Saved {name}.html")
            await page.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(dump_html())
