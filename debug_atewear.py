from playwright.sync_api import sync_playwright

def dump_html():
    url = "https://www.atewear.com.tr/products/kislik-ayarlanabilir-paca-baggy-esofman-alti"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        content = page.content()
        with open("atewear_dump.html", "w", encoding="utf-8") as f:
            f.write(content)
        browser.close()

if __name__ == "__main__":
    dump_html()
