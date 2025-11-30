"""
Scraping Service
Web scraping business logic with caching
"""
import asyncio
import hashlib
import sys
import os
from urllib.parse import urlparse

from app.services.cache_service import cache_service, cached


class ScrapingService:
    """Scraping business logic with caching"""

    def __init__(self):
        # Import scraper from project root
        parent_dir = os.path.join(os.path.dirname(__file__), '../../..')
        parent_dir = os.path.abspath(parent_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

    @cached(expiration=3600, key_prefix='scrape')
    def scrape_product(self, url):
        """Tek bir ürünü çek (cached) - güvenli ve filtreli"""
        try:
            # clear_scraping_cache ile uyumlu manual cache key
            cache_key = f"scrape:{hashlib.md5(url.encode()).hexdigest()}"
            cached_result = cache_service.get(cache_key)
            if cached_result:
                print(f"[DEBUG] Using cached result for: {url}")
                return cached_result

            print(f"[DEBUG] Scraping URL: {url}")

            # 1) Domain kontrolü - Artık tüm siteleri destekliyoruz
            parsed = urlparse(url)
            domain = (parsed.netloc or "").lower().replace("www.", "")
            
            # 2) scraper.py içindeki scrape_product fonksiyonunu çağır
            try:
                from scraper import scrape_product as base_scrape
            except ImportError as e:
                print(f"[ERROR] Could not import scraper: {e}")
                return None

            result = base_scrape(url)
            print(f"[DEBUG] Raw scraping result: {result}")

            if not result:
                print(f"[ERROR] Scraping returned no result for: {url}")
                return None

            # 3) Title kontrolü
            raw_title = (result.get("title") or "").strip()
            if not raw_title:
                print(f"[ERROR] Product title not found in result: {result}")
                return None

            upper_title = raw_title.upper()
            if ("ACCESS DENIED" in upper_title or
                "FORBIDDEN" in upper_title or
                "BOT DETECTED" in upper_title):
                print(f"[ERROR] Access denied / bot page detected for: {url}")
                return None

            # 4) Fiyat
            raw_price = result.get("price")
            if not raw_price or not str(raw_price).strip():
                print(f"[ERROR] Price not found in result: {result}")
                return None

            price = self._clean_price(raw_price)
            if not price:
                print(f"[ERROR] Price cleaning failed for: {raw_price}")
                return None

            # 5) Görsel zorunlu
            image = result.get("image")
            if not image or not str(image).strip():
                print(f"[ERROR] Image not found in result: {result}")
                return None

            # 6) Marka yoksa domain'den üret
            brand = result.get("brand")
            if not brand or not str(brand).strip():
                brand = domain.split('.')[0].upper() if domain else "UNKNOWN"
            
            # Clean old_price if exists
            old_price = result.get("original_price")
            if old_price:
                old_price = self._clean_price(old_price)

            formatted_result = {
                "name": raw_title,
                "price": price,
                "image": image,
                "brand": brand,
                "url": url,
                "images": [image],
                "old_price": old_price,
                "discount_message": result.get("discount_message")
            }

            # Manual cache + decorator cache beraber çalışacak, sorun değil
            cache_service.set(cache_key, formatted_result, expiration=3600)
            print(
                f"[DEBUG] Scraping successful - Name: {formatted_result.get('name')}, "
                f"Price: {formatted_result.get('price')}, Brand: {formatted_result.get('brand')}"
            )
            return formatted_result

        except Exception as e:
            print(f"[ERROR] Scraping error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def scrape_multiple(self, urls):
        """Toplu ürün çekme"""
        results = []
        for url in urls:
            result = self.scrape_product(url)
            if result:
                results.append(result)
        return results

    def clear_scraping_cache(self, url=None):
        """Scraping cache'ini temizle"""
        if url:
            cache_key = f"scrape:{hashlib.md5(url.encode()).hexdigest()}"
            cache_service.delete(cache_key)
        else:
            cache_service.clear("scrape:*")

    def _clean_price(self, raw_price):
        """Helper method to clean and format price strings"""
        if not raw_price:
            return None
            
        price_clean = str(raw_price).strip()
        
        try:
            import re
            # Sadece sayı ve virgül/nokta kalsın
            # Para birimi sembollerini temizle
            price_str = re.sub(r"[^\d,\.]", "", price_clean)

            if not price_str:
                print(f"[DEBUG] Price string empty after cleaning: {price_clean}")
                return None

            # Basit mantık:
            # Eğer hem nokta hem virgül varsa: sondaki ondalıktır, ortadaki binliktir
            # Eğer sadece virgül varsa: genelde ondalıktır (TR), ama bazen binliktir (US)
            # Eğer sadece nokta varsa: genelde binliktir (TR), ama bazen ondalıktır (US)
            
            price_num = 0.0
            if "," in price_str and "." in price_str:
                if price_str.rfind(",") > price_str.rfind("."):
                    # 1.299,99 formatı (TR/EU) -> Noktaları sil, virgülü nokta yap
                    price_num = float(price_str.replace(".", "").replace(",", "."))
                else:
                    # 1,299.99 formatı (US) -> Virgülleri sil
                    price_num = float(price_str.replace(",", ""))
            elif "," in price_str:
                # Sadece virgül var: 129,90 veya 1,299
                parts = price_str.split(",")
                if len(parts[-1]) == 2:
                    # 129,90 -> 129.90
                    price_num = float(price_str.replace(",", "."))
                else:
                    # 1,299 -> 1299
                    price_num = float(price_str.replace(",", "."))
            elif "." in price_str:
                # Sadece nokta var: 1.299 veya 12.99
                parts = price_str.split(".")
                if len(parts[-1]) == 3:
                     price_num = float(price_str.replace(".", ""))
                else:
                     price_num = float(price_str)
            else:
                price_num = float(price_str)

            # Türk Lirası formatla
            if price_num >= 1000:
                return f"{price_num:,.2f} TL".replace(",", "X").replace(".", ",").replace("X", ".")
            else:
                return f"{price_num:.2f} TL".replace(".", ",")
        except Exception as e:
            print(f"[DEBUG] Price formatting error: {e}, using raw: {price_clean}")
            # Fallback: just return raw but stripped
            return f"{price_clean} TL"
