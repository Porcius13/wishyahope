from playwright.sync_api import sync_playwright

def dump_sites():
    urls = [
        ("mediamarkt", "https://www.mediamarkt.com.tr/tr/product/_xiaomi-redmi-note-14-pro-8256-gb-akilli-telefon-siyah-1243823.html"),
        ("beymen", "https://www.beymen.com/tr/p_lasttouch-geisha-serisi-no6-tablo_1174709")
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for name, url in urls:
            print(f"Dumping {name}...")
            try:
                page.goto(url)
                content = page.content()
                with open(f"{name}_dump.html", "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Saved {name}_dump.html")
            except Exception as e:
                print(f"Error dumping {name}: {e}")
                
        browser.close()

if __name__ == "__main__":
    dump_sites()
