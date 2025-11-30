import json
from bs4 import BeautifulSoup

def extract_json_ld():
    with open("boyner_dump.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    scripts = soup.find_all('script', type='application/ld+json')
    
    print(f"Found {len(scripts)} JSON-LD scripts")
    
    all_data = []
    for i, script in enumerate(scripts):
        try:
            data = json.loads(script.string)
            all_data.append(data)
        except Exception as e:
            print(f"Error parsing script #{i+1}: {e}")
            
    with open("boyner.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    print("Saved to boyner.json")

if __name__ == "__main__":
    extract_json_ld()
