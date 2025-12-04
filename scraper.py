import asyncio
import logging
import re
import json
from urllib.parse import urlparse
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.DEBUG)

# Site bazlı selector havuzu
SITE_SELECTORS = {
    "zara.com": {
        "title": [
            "h1[data-qa-action='product-name']",
            "h1.product-name",
            "h1",
            "[data-testid='product-name']",
            ".product-name"
        ],
        "price": [
            "span[data-qa-action='price-current']",
            ".price-current",
            "[data-testid='price']",
            ".product-price"
        ],
        "image": [
            "img[data-qa-action='product-image']",
            "img.product-image",
            "img[loading='lazy']"
        ],
        "brand": ["ZARA"]
    },
    "mango.com": {
        "title": ["h1.product-name", "h1", "[data-testid='product-name']"],
        "price": [
            "span[class*='SinglePrice_finalPrice']", 
            "span[class*='SinglePrice_center']",
            "span[class*='price-sale']",
            ".product-price", 
            "[data-testid='price']", 
            ".price"
        ],
        "original_price": [
            "span[class*='SinglePrice_crossed']",
            "span[class*='price-original']"
        ],
        "image": [
            "img[class*='ImageGridItem_image']",
            "img[src*='imwidth=2048']", 
            "img[src*='_D2.jpg']",
            "meta[property='og:image']", 
            "img.product-image", 
            "img[loading='lazy']"
        ],
        "brand": ["MANGO"]
    },
    "hm.com": {
        "title": ["h1.product-name", "h1", "[data-testid='product-name']"],
        "price": [".product-price", "[data-testid='price']", ".price"],
        "image": ["img.product-image", "img[loading='lazy']"],
        "brand": ["H&M"]
    },
    "nike.com": {
        "title": ["h1[id='pdp_product_title']", "h1", "[data-testid='product-title']"],
        "price": ["[data-testid='currentPrice-container']", ".product-price", "[data-testid='price']"],
        "image": ["img[data-testid='hero-image']", "img[src*='static.nike.com']", "img"],
        "brand": ["NIKE"]
    },
    "bershka.com": {
        "title": ["h1.product-title", "h1"],
        "price": [".current-price-elem", ".price-elem"],
        "image": ["img.image-item", "img"],
        "brand": ["BERSHKA"]
    },
    "amazon": {
        "title": ["#productTitle", "#title", "span#productTitle"],
        "price": [
            ".a-price .a-offscreen", 
            "#priceblock_ourprice", 
            "#priceblock_dealprice", 
            "#corePrice_feature_div .a-offscreen",
            "#corePriceDisplay_desktop_feature_div .a-offscreen",
            ".a-price"
        ],
        "image": ["#landingImage", "#imgTagWrapperId img", "#main-image", "img[data-a-image-name]"],
        "brand": ["#bylineInfo", "#brand", "a#bylineInfo"]
    },
    "teknosa.com": {
        "title": ["h1.pdp-title", "h1.product-title", "h1"],
        "price": [
            ".pdp-price .price", 
            ".price-tag", 
            ".current-price", 
            ".product-price",
            "div[class*='price']"
        ],
        "image": ["#pdp-main-image", ".pdp-image img", "img.pdp-image"],
        "brand": ["b.pdp-brand", ".pdp-brand a", ".brand-name"]
    },
    "adidas.com.tr": {
        "title": ["h1[data-auto-id='product-title']", "h1.gl-heading", "h1"],
        "price": [".gl-price-item", ".gl-price", ".product-price"],
        "image": ["img[data-auto-id='image']", "img.product-image", "div.image-carousel img"],
        "brand": ["ADIDAS"]
    },
    "pullandbear.com": {
        "title": ["h1", "meta[property='og:title']", "title"],
        "price": [
            # JSON-LD is primary, but these are fallbacks
            "meta[property='product:price:amount']",
            "meta[name='price']"
        ],
        "original_price": [], # Explicitly empty to prevent risky fallbacks
        "image": [
            "meta[property='og:image']",
            "img[class*='image']"
        ],
        "brand": ["PULL&BEAR"]
    },
    "massimodutti.com": {
        "title": ["h1.md-product-heading-title-txt", "h1", "meta[property='og:title']", "title"],
        "price": [
            "meta[property='product:price:amount']",
            "meta[name='price']",
            "div.formatted-price-detail-handler",
            "div[class*='formatted-price']",
            "span[class*='price']",
            "div[class*='price']"
        ],
        "original_price": [
            "span[class*='old-price']",
            "div[class*='old-price']",
            "span[class*='original-price']",
            "div[class*='original-price']"
        ],
        "image": [
            "meta[property='og:image']",
            "img[class*='product-image']",
            "img[src*='massimodutti']",
            ".product-image img",
            ".product-gallery img"
        ],
        "brand": ["MASSIMO DUTTI"]
    },
    "victoriassecret.com.tr": {
        "title": [
            "h1",
            "h1.product-title",
            "h1[class*='product-title']",
            "h1[class*='product-name']",
            "h1[class*='title']",
            "[data-testid*='product-name']",
            "[data-testid*='title']",
            "[class*='product-name']",
            "[class*='product-title']",
            "meta[property='og:title']",
            "title"
        ],
        "price": [
            "span#indirimliFiyat span.spanFiyat",
            "div.IndirimliFiyatContent span.spanFiyat",
            "div#divIndirimliFiyat span.spanFiyat:last-of-type",
            "span.spanFiyat",
            "div.indirimliFiyat",
            "div.product-price-discounted",
            "div.product-price-not-discounted",
            "div[class*='product-price']",
            "span[class*='price']",
            "div[class*='price']",
            "meta[property='product:price:amount']",
            "div.recommended-item-discounted-price",
            "[data-testid*='price']",
            "span.price",
            "div.price"
        ],
        "original_price": [
            "span#fiyat span.spanFiyat",
            "div.PiyasafiyatiContent span.spanFiyat",
            "div.product-price-old",
            "div.recommended-item-old-price",
            "span[class*='old-price']",
            "div[class*='old-price']",
            "span[class*='original-price']",
            "div[class*='original-price']",
            "s[class*='price']",
            "del[class*='price']"
        ],
        "image": [
            "meta[property='og:image']",
            "img#imgurunresmi",
            "img[alt*='Kalpli']",
            "img[class*='product-image']",
            "img[class*='product__image']",
            "img[data-testid='product-image']",
            "img[alt*='product']",
            "img[src*='victoriassecret']",
            "img[src*='cdn']",
            ".product-image img",
            ".product__image img"
        ],
        "brand": ["VICTORIA'S SECRET"]
    },
    "boyner.com.tr": {
        "title": ["h1.product-name", "h1"],
        "price": [".product-price", ".price"],
        "image": ["img.product-image", "img"],
        "brand": ["BOYNER"]
    },
    "lesbenjamins.com": {
        "title": ["h1", "meta[property='og:title']", "title"],
        "price": [
            "meta[property='product:price:amount']",
            "span.price-item--sale",
            "span.price-item--regular"
        ],
        "image": [
            "meta[property='og:image']",
            "a.lightbox-image img",
            "img[src*='products']"
        ],
        "brand": ["LES BENJAMINS"]
    },
    "columbia.com.tr": {
        "title": ["h1", "meta[property='og:title']", "title"],
        "price": [
            "span.product-sale-price",
            "span.price-sales",
            "meta[property='product:price:amount']",
            "span[class*='price']"
        ],
        "original_price": [
            "span.seg-older-price",
            "span.product-list-price",
            "span.price-standard"
        ],
        "image": [
            "meta[property='og:image']",
            "img.iiz__img",
            "img.product-image"
        ],
        "brand": ["COLUMBIA"]
    },
    "lego.tr": {
        "title": ["h1", "meta[property='og:title']", "title"],
        "price": [
            "span.product-price",
            "meta[property='product:price:amount']",
            "span[class*='price']",
            "div[class*='price']"
        ],
        "original_price": [
            "span[class*='old-price']",
            "div[class*='old-price']",
            "span[class*='original-price']",
            "div[class*='original-price']"
        ],
        "image": [
            "meta[property='og:image']",
            "img.product-image",
            "img[class*='product-image']",
            "img[src*='lego']"
        ],
        "brand": ["LEGO"]
    },
    "reflectstudio.com": {
        "title": ["div.product__info-container h1", "h1.product__title"],
        "price": [
            "meta[property='product:price:amount']",
            "div.product__info-container span.price-item--sale",
            "div.product__info-container span.price-item--regular",
            "span.price-item--sale"
        ],
        "original_price": [
            "div.product__info-container span.price-item--regular",
            "span.price-item--regular"
        ],
        "image": [
            "meta[property='og:image']",
            "img.product__media-image"
        ],
        "brand": ["Reflect Studio"]
    },
    "gratis.com": {
        "title": [
            "h1",
            "h1[class*='product-title']",
            "h1[class*='product-name']",
            "h1[class*='title']",
            "[data-testid*='product-name']",
            "[data-testid*='title']",
            "[class*='product-name']",
            "[class*='product-title']",
            "meta[property='og:title']",
            "title"
        ],
        "price": [
            "span.text-primary-900.font-bold",
            "span[class*='discounted']",
            "span[class*='sale']",
            "div[class*='discounted-price']",
            "span[class*='gratis-kart']",
            "[data-testid*='discounted-price']",
            "span[class*='price']",
            "div[class*='price']",
            "meta[property='product:price:amount']",
            "[data-testid*='price']",
            "span.price",
            "div.price"
        ],
        "original_price": [
            "span[class*='old-price']",
            "div[class*='old-price']",
            "span[class*='original-price']",
            "div[class*='original-price']",
            "s[class*='price']",
            "del[class*='price']",
            "span[class*='text-gray']",
            "div[class*='text-gray']"
        ],
        "image": [
            "meta[property='og:image']",
            "img[class*='product-image']",
            "img[class*='product__image']",
            "img[data-testid='product-image']",
            "img[alt*='product']",
            "img[src*='gratis']",
            "img[src*='cdn']",
            "img.product-image",
            ".product-image img",
            ".product__image img"
        ],
        "brand": ["GRATIS"]
    },
    "dr.com.tr": {
        "title": ["h1", "meta[property='og:title']", "title"],
        "price": [
            "span.current-price",
            "div.product-price",
            "meta[property='product:price:amount']"
        ],
        "original_price": [
            "span.old-price",
            "div.old-price"
        ],
        "image": [
            "meta[property='og:image']",
            "img.product-image",
            "img[class*='product-image']"
        ],
        "brand": ["D&R"]
    },
    "vakkorama.com.tr": {
        "title": ["h1", "meta[property='og:title']", "title"],
        "price": [
            "meta[property='product:price:amount']",
            "div.product-price-container div.price",
            "div.price",
            "span[class*='price']",
            "div[class*='price']",
            "span.current-price",
            "div.current-price"
        ],
        "original_price": [
            "div.product-price-container div.old-price",
            "div.old-price",
            "span[class*='old-price']",
            "div[class*='old-price']",
            "span[class*='original-price']",
            "div[class*='original-price']"
        ],
        "image": [
            "meta[property='og:image']",
            "img.product-image",
            "img[class*='product-image']",
            "img[src*='vakkorama']",
            ".product-image img",
            ".product-slider img"
        ],
        "brand": ["Vakkorama"]
    },
    "mavi.com": {
        "title": ["h1.product-name", "h1", "meta[property='og:title']", "title"],
        "price": [
            "span[class*='price']",
            "div[class*='price']",
            "span.current-price",
            "div.current-price",
            "meta[property='product:price:amount']"
        ],
        "original_price": [
            "span[class*='old-price']",
            "div[class*='old-price']",
            "span[class*='original-price']",
            "div[class*='original-price']"
        ],
        "image": [
            "meta[property='og:image']",
            "img[class*='product-image']",
            "img[class*='product__image']",
            "img[src*='mavi.com']"
        ],
        "brand": ["MAVI"]
    },
    "jerf.com.tr": {
        "title": ["h1.product-title", "h1", "meta[property='og:title']", "title"],
        "price": [
            "span[class*='price']",
            "div[class*='price']",
            "span.current-price",
            "div.current-price",
            "span.sale-price",
            "div.sale-price",
            "meta[property='product:price:amount']",
            ".product-price",
            ".product__price"
        ],
        "original_price": [
            "span[class*='old-price']",
            "div[class*='old-price']",
            "span[class*='original-price']",
            "div[class*='original-price']",
            "span[class*='compare-price']",
            "div[class*='compare-price']"
        ],
        "image": [
            "meta[property='og:image']",
            "img[class*='product-image']",
            "img[class*='product__image']",
            "img[src*='jerf']",
            ".product-image img",
            ".product__image img"
        ],
        "brand": ["JERF"]
    }
}

async def extract_jsonld(page):
    """JSON-LD verisini çeker"""
    try:
        return await page.evaluate('''() => {
            const scripts = document.querySelectorAll('script[type="application/ld+json"]');
            for (const script of scripts) {
                try {
                    const json = JSON.parse(script.innerText);
                    
                    // Direkt Product objesi
                    if (json['@type'] === 'Product') return json;
                    
                    // Array içinde Product
                    if (Array.isArray(json)) {
                        const product = json.find(i => i['@type'] === 'Product');
                        if (product) return product;
                    }
                    
                    // Graph içinde Product
                    if (json['@graph']) {
                        const product = json['@graph'].find(i => i['@type'] === 'Product');
                        if (product) return product;
                    }
                } catch (e) {}
            }
            return null;
        }''')
    except Exception as e:
        logging.debug(f"JSON-LD extraction failed: {e}")
        return None

async def extract_meta_tags(page):
    """Meta tag ve OG tag verilerini çeker"""
    return await page.evaluate('''() => {
        const data = {};
        
        // Title
        const ogTitle = document.querySelector('meta[property="og:title"]');
        if (ogTitle) data.title = ogTitle.content;
        
        // Image
        const ogImage = document.querySelector('meta[property="og:image"]');
        if (ogImage) data.image = ogImage.content;
        
        // Price
        const priceAmount = document.querySelector('meta[property="product:price:amount"]');
        if (priceAmount) data.price = priceAmount.content;
        
        const price = document.querySelector('meta[name="price"]');
        if (price && !data.price) data.price = price.content;
        
        return data;
    }''')

async def extract_decathlon_data(page):
    """Decathlon özel veri çekme (window.__DKT)"""
    return await page.evaluate('''() => {
        try {
            if (window.__DKT && window.__DKT._ctx && window.__DKT._ctx.data) {
                const supermodel = window.__DKT._ctx.data.find(item => item.type === 'Supermodel');
                if (supermodel && supermodel.data) {
                    const modelData = supermodel.data.models ? supermodel.data.models[0] : null;
                    if (modelData) {
                        let price = null;
                        if (modelData.skus && modelData.skus.length > 0) {
                            price = modelData.skus[0].price;
                        }
                        return {
                            title: modelData.webLabel,
                            image: modelData.image ? modelData.image.url : null,
                            price: price,
                            brand: supermodel.data.brand ? supermodel.data.brand.label : "DECATHLON"
                        };
                    }
                }
            }
        } catch (e) { return null; }
        return null;
    }''')

async def extract_teknosa_data(page):
    """Teknosa özel veri çekme (window.insider_object)"""
    return await page.evaluate('''() => {
        try {
            if (window.insider_object && window.insider_object.product) {
                const p = window.insider_object.product;
                return {
                    title: p.name,
                    price: p.unit_price || p.unit_sale_price,
                    image: p.product_image_url,
                    brand: null // Markayı generic extractor'a bırak
                };
            }
        } catch (e) { return null; }
    }''')


async def extract_boyner_data(page):
    """Boyner özel veri çekme (JSON-LD öncelikli)"""
    return await page.evaluate('''() => {
        try {
            const scripts = document.querySelectorAll('script[type="application/ld+json"]');
            for (const script of scripts) {
                try {
                    const json = JSON.parse(script.innerText);
                    // Array içinde Product arama
                    let product = null;
                    if (Array.isArray(json)) {
                        product = json.find(i => i['@type'] === 'Product');
                    } else if (json['@type'] === 'Product') {
                        product = json;
                    }

                    if (product) {
                        let image = null;
                        if (Array.isArray(product.image)) {
                            // En yüksek çözünürlüklü olanı bul (örn: 900/1254)
                            const highRes = product.image.find(img => img.includes('900/1254'));
                            image = highRes || product.image[0];
                        } else {
                            image = product.image;
                        }

                        let price = null;
                        if (product.offers) {
                             if (Array.isArray(product.offers)) {
                                price = product.offers[0].price;
                             } else {
                                price = product.offers.price;
                             }
                        }

                        return {
                            title: product.name,
                            image: image,
                            price: price,
                            brand: product.brand ? (product.brand.name || product.brand) : "BOYNER"
                        };
                    }
                } catch (e) {}
            }
        } catch (e) { return null; }
        return null;
    }''')

def get_site_selectors(url):
    domain = urlparse(url).netloc.lower()
    for site, selectors in SITE_SELECTORS.items():
        if site in domain:
            return selectors
    return None

try:
    from playwright_stealth import Stealth
except ImportError:
    Stealth = None

async def extract_defacto_data(page):
    """DeFacto özel veri çekme"""
    return await page.evaluate('''() => {
        try {
            const priceEl = document.querySelector('.campaing-base-price');
            const originalPriceEl = document.querySelector('.lined-base-price');
            const nameEl = document.querySelector('h1.product-card__name');
            
            // Resim için çoklu deneme
            let image = null;
            
            // 1. Meta tag (En temiz)
            const ogImage = document.querySelector('meta[property="og:image"]');
            if (ogImage) image = ogImage.content;
            
            // 2. Slider içindeki ilk resim
            if (!image || image.includes('recocombinbos')) {
                const sliderImg = document.querySelector('.product-image-gallery__item img');
                if (sliderImg) image = sliderImg.src;
            }
            
            // 3. Mevcut selector
            if (!image || image.includes('recocombinbos')) {
                const cardImg = document.querySelector('.product-card__image img');
                if (cardImg) image = cardImg.src;
            }

            // Protokol düzeltme
            if (image && image.startsWith('//')) {
                image = 'https:' + image;
            }

            let price = priceEl ? priceEl.innerText.replace('Sepette', '').trim() : null;
            let originalPrice = originalPriceEl ? originalPriceEl.innerText.trim() : price;

            return {
                price: price,
                original_price: originalPrice,
                title: nameEl ? nameEl.innerText.trim() : null,
                image: image,
                brand: "DeFacto"
            };
        } catch (e) { return null; }
    }''')

async def extract_lcw_data(page):
    """LC Waikiki özel veri çekme"""
    return await page.evaluate('''() => {
        try {
            let model = window.productDetailModel?.AllModel || window.cartOperationViewModel;
            
            // Fallback: Script taginden parse et (Window objesi boşsa veya Badge yoksa)
            if (!model || !model.OptionBadges) {
                const scripts = document.querySelectorAll('script');
                for (const script of scripts) {
                    if (script.textContent.includes('var optimizedDetailModel')) {
                        try {
                            const match = script.textContent.match(/var optimizedDetailModel\\s*=\\s*({.+?});/);
                            if (match) {
                                model = JSON.parse(match[1]);
                                break;
                            }
                        } catch(e) {}
                    }
                    if (script.textContent.includes('var cartOperationViewModel')) {
                        try {
                            const match = script.textContent.match(/var cartOperationViewModel\\s*=\\s*({.+?});/);
                            if (match) {
                                model = JSON.parse(match[1]);
                                break;
                            }
                        } catch(e) {}
                    }
                }
            }

            if (!model) return null;

            let price = 0;
            let originalPrice = 0;

            if (model.OptionBadges && model.OptionBadges.length > 0) {
                const badge = model.OptionBadges.find(b => b.DiscountedPrice > 0);
                if (badge) price = badge.DiscountedPrice;
            }

            if (price === 0 && model.ProductPricesList && model.ProductPricesList.length > 0) {
                const priceInfo = model.ProductPricesList.find(p => p.IsDefault) || model.ProductPricesList[0];
                price = priceInfo.CartPriceValue || priceInfo.PriceValue;
                originalPrice = priceInfo.PriceValue;
            }

            if (price === 0 && model.PriceInfo) {
                price = model.PriceInfo.DiscountedPrice > 0 ? model.PriceInfo.DiscountedPrice : model.PriceInfo.Price;
                originalPrice = model.PriceInfo.Price;
            }

            if (originalPrice === 0) originalPrice = price;
            if (price > originalPrice) originalPrice = price;

            return {
                price: price,
                original_price: originalPrice,
                title: model.ModelInfo?.ModelTitle || document.title,
                image: model.Pictures?.[0]?.LargeImage || document.querySelector('meta[property="og:image"]')?.content,
                brand: "LC Waikiki"
            };
        } catch (e) { return null; }
    }''')

async def extract_mango_data(page):
    """Mango özel veri çekme - JSON-LD, meta tag ve DOM selector'ları kullanır"""
    return await page.evaluate('''() => {
        try {
            const result = {
                title: null,
                price: null,
                original_price: null,
                image: null,
                brand: "MANGO"
            };

            // 1. JSON-LD'den fiyat çek (en güvenilir)
            try {
                const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
                for (const script of jsonLdScripts) {
                    try {
                        const data = JSON.parse(script.textContent);
                        if (data['@type'] === 'Product' || (Array.isArray(data) && data.find(item => item['@type'] === 'Product'))) {
                            const product = Array.isArray(data) ? data.find(item => item['@type'] === 'Product') : data;
                            
                            if (product.name && !result.title) {
                                result.title = product.name;
                            }
                            
                            if (product.offers) {
                                const offers = Array.isArray(product.offers) ? product.offers[0] : product.offers;
                                if (offers && offers.price) {
                                    const priceValue = typeof offers.price === 'string' ? parseFloat(offers.price) : offers.price;
                                    if (priceValue > 0) {
                                        result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                    }
                                }
                            }
                            
                            if (product.image) {
                                const img = Array.isArray(product.image) ? product.image[0] : product.image;
                                result.image = typeof img === 'string' ? img : (img.url || img);
                            }
                            
                            if (product.brand) {
                                result.brand = typeof product.brand === 'string' ? product.brand : (product.brand.name || 'MANGO');
                            }
                        }
                    } catch (e) {}
                }
            } catch (e) {}

            // 2. Meta tag'lerden çek
            if (!result.price) {
                const metaPrice = document.querySelector('meta[property="product:price:amount"]');
                if (metaPrice && metaPrice.content) {
                    const priceValue = parseFloat(metaPrice.content);
                    if (priceValue > 0) {
                        result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                    }
                }
            }

            if (!result.title) {
                const ogTitle = document.querySelector('meta[property="og:title"]');
                if (ogTitle && ogTitle.content) {
                    result.title = ogTitle.content;
                }
            }

            if (!result.image) {
                const ogImage = document.querySelector('meta[property="og:image"]');
                if (ogImage && ogImage.content) {
                    result.image = ogImage.content;
                }
            }

            // 3. DOM selector'larından çek (fallback)
            if (!result.title) {
                const titleSelectors = [
                    'h1[class*="product"]',
                    'h1[class*="title"]',
                    'h1[class*="name"]',
                    'h1',
                    '[data-testid*="product-name"]',
                    '[data-testid*="title"]',
                    '[class*="product-name"]',
                    '[class*="product-title"]'
                ];
                
                for (const selector of titleSelectors) {
                    try {
                        const el = document.querySelector(selector);
                        if (el && el.textContent && el.textContent.trim() && !el.textContent.includes('ACCESS DENIED')) {
                            result.title = el.textContent.trim();
                            break;
                        }
                    } catch (e) {}
                }
            }

            if (!result.price) {
                const priceSelectors = [
                    'span[class*="SinglePrice_finalPrice"]',
                    'span[class*="finalPrice"]',
                    'span[class*="SinglePrice_center"]',
                    'span[class*="price-sale"]',
                    '[data-testid*="price"]',
                    '[class*="price"]',
                    'span.price'
                ];
                
                for (const selector of priceSelectors) {
                    try {
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {
                            const text = el.textContent.trim();
                            // Fiyat formatı: 1.299,99 TL veya 1299,99 TL
                            const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*,[0-9]{2}|[0-9]+[.,][0-9]{2})/);
                            if (priceMatch) {
                                let priceStr = priceMatch[1];
                                // Format: 1.299,99 -> 1299.99
                                if (priceStr.includes(',')) {
                                    priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                }
                                const priceNum = parseFloat(priceStr);
                                if (priceNum >= 10 && priceNum <= 100000) {
                                    if (priceNum >= 1000) {
                                        result.price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                    } else {
                                        result.price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                    }
                                    break;
                                }
                            }
                        }
                        if (result.price) break;
                    } catch (e) {}
                }
            }

            // Eski fiyat
            const oldPriceSelectors = [
                'span[class*="SinglePrice_crossed"]',
                'span[class*="crossed"]',
                'span[class*="old"]',
                'del.price',
                's[class*="price"]'
            ];
            
            for (const selector of oldPriceSelectors) {
                try {
                    const elements = document.querySelectorAll(selector);
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*,[0-9]{2}|[0-9]+[.,][0-9]{2})/);
                        if (priceMatch) {
                            let priceStr = priceMatch[1];
                            if (priceStr.includes(',')) {
                                priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                            }
                            const priceNum = parseFloat(priceStr);
                            if (priceNum >= 10 && priceNum <= 100000) {
                                if (priceNum >= 1000) {
                                    result.original_price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                } else {
                                    result.original_price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                }
                                break;
                            }
                        }
                    }
                    if (result.original_price) break;
                } catch (e) {}
            }

            // Görsel
            if (!result.image) {
                const imageSelectors = [
                    'img[src*="shop.mango.com/assets"]',
                    'img[srcset*="shop.mango.com/assets"]',
                    'img[class*="ImageGridItem"]',
                    'img[class*="image"]',
                    'img[data-testid="product-image"]',
                    'img[class*="product"]',
                    'img[src*="mango"]'
                ];
                
                for (const selector of imageSelectors) {
                    try {
                        const img = document.querySelector(selector);
                        if (img) {
                            let src = img.getAttribute('src') || img.getAttribute('data-src');
                            const srcset = img.getAttribute('srcset');
                            
                            // srcset'ten en yüksek çözünürlüklü görseli al
                            if (srcset) {
                                const parts = srcset.split(',');
                                let highestRes = null;
                                let maxWidth = 0;
                                
                                for (const part of parts) {
                                    const trimmed = part.trim();
                                    if (trimmed.includes(' ')) {
                                        const lastSpaceIndex = trimmed.lastIndexOf(' ');
                                        const urlPart = trimmed.substring(0, lastSpaceIndex).trim();
                                        const sizePart = trimmed.substring(lastSpaceIndex + 1).trim();
                                        if (sizePart.includes('w')) {
                                            const width = parseInt(sizePart.replace('w', ''));
                                            if (width > maxWidth) {
                                                maxWidth = width;
                                                highestRes = urlPart;
                                            }
                                        }
                                    }
                                }
                                
                                if (highestRes) {
                                    src = highestRes;
                                }
                            }
                            
                            if (src && (src.includes('.jpg') || src.includes('.jpeg') || src.includes('.webp') || src.includes('.png'))) {
                                // Relative URL'yi absolute yap
                                if (src.startsWith('//')) {
                                    src = 'https:' + src;
                                } else if (src.startsWith('/')) {
                                    src = 'https://shop.mango.com' + src;
                                }
                                
                                // URL'deki boyut parametrelerini optimize et
                                if (src.includes('w=') && src.includes('h=')) {
                                    src = src.replace(/w=\\d+/, 'w=800').replace(/h=\\d+/, 'h=1200');
                                }
                                
                                result.image = src;
                                break;
                            }
                        }
                    } catch (e) {}
                }
            }

            return (result.title && result.price && result.image) ? result : null;
        } catch (e) {
            return null;
        }
    }''')

async def extract_reflectstudio_data(page):
    """Reflect Studio özel veri çekme - Shopify mağazası için optimize edilmiş"""
    return await page.evaluate('''() => {
        try {
            const result = {
                title: null,
                price: null,
                original_price: null,
                image: null,
                brand: "Reflect Studio"
            };

            // 1. JSON-LD'den veri çek (en güvenilir)
            try {
                const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
                for (const script of jsonLdScripts) {
                    try {
                        const data = JSON.parse(script.textContent);
                        let product = null;
                        
                        if (data['@type'] === 'Product') {
                            product = data;
                        } else if (Array.isArray(data)) {
                            product = data.find(item => item['@type'] === 'Product');
                        } else if (data['@graph']) {
                            product = data['@graph'].find(item => item['@type'] === 'Product');
                        }
                        
                        if (product) {
                            if (product.name && !result.title) {
                                result.title = product.name;
                            }
                            
                            if (product.offers) {
                                const offers = Array.isArray(product.offers) ? product.offers[0] : product.offers;
                                if (offers && offers.price) {
                                    const priceValue = typeof offers.price === 'string' ? parseFloat(offers.price) : offers.price;
                                    if (priceValue > 0) {
                                        // Shopify formatı: 2499.00 -> 2,499.00 TL
                                        if (priceValue >= 1000) {
                                            result.price = priceValue.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}).replace(',', 'X').replace('.', ',').replace('X', '.') + ' TL';
                                        } else {
                                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                    }
                                }
                            }
                            
                            if (product.image) {
                                const img = Array.isArray(product.image) ? product.image[0] : product.image;
                                result.image = typeof img === 'string' ? img : (img.url || img);
                            }
                            
                            if (product.brand) {
                                result.brand = typeof product.brand === 'string' ? product.brand : (product.brand.name || 'Reflect Studio');
                            }
                        }
                    } catch (e) {}
                }
            } catch (e) {}

            // 2. ShopifyAnalytics'ten fiyat çek (Shopify mağazaları için)
            if (!result.price) {
                try {
                    if (window.ShopifyAnalytics && window.ShopifyAnalytics.meta && window.ShopifyAnalytics.meta.product && window.ShopifyAnalytics.meta.product.variants) {
                        const variant = window.ShopifyAnalytics.meta.product.variants[0];
                        if (variant && variant.price) {
                            // Shopify fiyatı kuruş cinsinden gelir (249900 -> 2499.00)
                            const priceValue = variant.price / 100;
                            if (priceValue >= 1000) {
                                result.price = priceValue.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}).replace(',', 'X').replace('.', ',').replace('X', '.') + ' TL';
                            } else {
                                result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                            }
                        }
                    }
                } catch (e) {}
            }

            // 3. Meta tag'lerden çek
            if (!result.price) {
                const metaPrice = document.querySelector('meta[property="product:price:amount"]');
                if (metaPrice && metaPrice.content) {
                    const priceValue = parseFloat(metaPrice.content);
                    if (priceValue > 0) {
                        if (priceValue >= 1000) {
                            result.price = priceValue.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}).replace(',', 'X').replace('.', ',').replace('X', '.') + ' TL';
                        } else {
                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                        }
                    }
                }
            }

            if (!result.title) {
                const ogTitle = document.querySelector('meta[property="og:title"]');
                if (ogTitle && ogTitle.content) {
                    result.title = ogTitle.content;
                }
            }

            if (!result.image) {
                const ogImage = document.querySelector('meta[property="og:image"]');
                if (ogImage && ogImage.content) {
                    result.image = ogImage.content;
                }
            }

            // 4. DOM selector'larından çek (fallback)
            if (!result.title) {
                const titleSelectors = [
                    'div.product__info-container h1',
                    'h1.product__title',
                    'h1[class*="product"]',
                    'h1[class*="title"]',
                    'h1',
                    '[data-testid*="product-name"]',
                    '[data-testid*="title"]',
                    '[class*="product-name"]',
                    '[class*="product-title"]'
                ];
                
                for (const selector of titleSelectors) {
                    try {
                        const el = document.querySelector(selector);
                        if (el && el.textContent && el.textContent.trim()) {
                            result.title = el.textContent.trim();
                            break;
                        }
                    } catch (e) {}
                }
            }

            if (!result.price) {
                const priceSelectors = [
                    'div.product__info-container span.price-item--sale',
                    'span.price-item--sale',
                    'div.product__info-container span.price-item--regular',
                    'span.price-item--regular',
                    '[class*="price-item--sale"]',
                    '[class*="price-item--regular"]',
                    'meta[property="product:price:amount"]',
                    '[class*="price"]',
                    'span.price'
                ];
                
                for (const selector of priceSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                const priceValue = parseFloat(meta.content);
                                if (priceValue > 0) {
                                    if (priceValue >= 1000) {
                                        result.price = priceValue.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}).replace(',', 'X').replace('.', ',').replace('X', '.') + ' TL';
                                    } else {
                                        result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                    }
                                    break;
                                }
                            }
                        } else {
                            const elements = document.querySelectorAll(selector);
                            for (const el of elements) {
                                const text = el.textContent.trim();
                                // Shopify fiyat formatı: "2,499.00₺" veya "2,499.00 TL"
                                const priceMatch = text.match(/([0-9]{1,3}(?:,[0-9]{3})*\\.[0-9]{2}|[0-9]+[.,][0-9]{2})/);
                                if (priceMatch) {
                                    let priceStr = priceMatch[1];
                                    // Format: 2,499.00 -> 2499.00 (Shopify formatı)
                                    if (priceStr.includes(',')) {
                                        priceStr = priceStr.replace(/,/g, '');
                                    }
                                    const priceNum = parseFloat(priceStr);
                                    if (priceNum >= 10 && priceNum <= 100000) {
                                        // Türk Lirası formatına çevir: 2.499,00 TL
                                        if (priceNum >= 1000) {
                                            result.price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                        break;
                                    }
                                }
                            }
                            if (result.price) break;
                        }
                    } catch (e) {}
                }
            }

            // Eski fiyat (original_price)
            const oldPriceSelectors = [
                'div.product__info-container span.price-item--regular',
                'span.price-item--regular',
                '[class*="price-item--regular"]',
                's[class*="price"]',
                'del[class*="price"]'
            ];
            
            for (const selector of oldPriceSelectors) {
                try {
                    const elements = document.querySelectorAll(selector);
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        const priceMatch = text.match(/([0-9]{1,3}(?:,[0-9]{3})*\\.[0-9]{2}|[0-9]+[.,][0-9]{2})/);
                        if (priceMatch) {
                            let priceStr = priceMatch[1];
                            if (priceStr.includes(',')) {
                                priceStr = priceStr.replace(/,/g, '');
                            }
                            const priceNum = parseFloat(priceStr);
                            if (priceNum >= 10 && priceNum <= 100000) {
                                if (priceNum >= 1000) {
                                    result.original_price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                } else {
                                    result.original_price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                }
                                break;
                            }
                        }
                    }
                    if (result.original_price) break;
                } catch (e) {}
            }

            // Görsel
            if (!result.image) {
                const imageSelectors = [
                    'meta[property="og:image"]',
                    'img.product__media-image',
                    'img[class*="product__media"]',
                    'img[class*="product-image"]',
                    'img[data-testid="product-image"]',
                    'img[alt*="product"]',
                    'img[src*="cdn.shop"]'
                ];
                
                for (const selector of imageSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                result.image = meta.content;
                                break;
                            }
                        } else {
                            const img = document.querySelector(selector);
                            if (img) {
                                let src = img.getAttribute('src') || img.getAttribute('data-src');
                                if (src) {
                                    // Relative URL'yi absolute yap
                                    if (src.startsWith('//')) {
                                        src = 'https:' + src;
                                    } else if (src.startsWith('/')) {
                                        src = 'https://reflectstudio.com' + src;
                                    }
                                    result.image = src;
                                    break;
                                }
                            }
                        }
                    } catch (e) {}
                }
            }

            return (result.title && result.price && result.image) ? result : null;
        } catch (e) {
            return null;
        }
    }''')

async def extract_dr_data(page):
    """D&R özel veri çekme - Kitap ve ürün bilgileri için optimize edilmiş"""
    return await page.evaluate('''() => {
        try {
            const result = {
                title: null,
                price: null,
                original_price: null,
                image: null,
                brand: "D&R"
            };

            // 1. JSON-LD'den veri çek (en güvenilir)
            try {
                const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
                for (const script of jsonLdScripts) {
                    try {
                        const data = JSON.parse(script.textContent);
                        let product = null;
                        
                        if (data['@type'] === 'Product') {
                            product = data;
                        } else if (Array.isArray(data)) {
                            product = data.find(item => item['@type'] === 'Product' || item['@type'] === 'Book');
                        } else if (data['@graph']) {
                            product = data['@graph'].find(item => item['@type'] === 'Product' || item['@type'] === 'Book');
                        }
                        
                        if (product) {
                            if (product.name && !result.title) {
                                result.title = product.name;
                            }
                            
                            if (product.offers) {
                                const offers = Array.isArray(product.offers) ? product.offers[0] : product.offers;
                                if (offers && offers.price) {
                                    const priceValue = typeof offers.price === 'string' ? parseFloat(offers.price) : offers.price;
                                    if (priceValue > 0) {
                                        // Türk Lirası formatı: 2499.00 -> 2.499,00 TL
                                        if (priceValue >= 1000) {
                                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                    }
                                }
                            }
                            
                            if (product.image) {
                                const img = Array.isArray(product.image) ? product.image[0] : product.image;
                                result.image = typeof img === 'string' ? img : (img.url || img);
                            }
                            
                            if (product.brand) {
                                result.brand = typeof product.brand === 'string' ? product.brand : (product.brand.name || 'D&R');
                            }
                        }
                    } catch (e) {}
                }
            } catch (e) {}

            // 2. Meta tag'lerden çek
            if (!result.price) {
                const metaPrice = document.querySelector('meta[property="product:price:amount"]');
                if (metaPrice && metaPrice.content) {
                    const priceValue = parseFloat(metaPrice.content);
                    if (priceValue > 0) {
                        if (priceValue >= 1000) {
                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                        } else {
                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                        }
                    }
                }
            }

            if (!result.title) {
                const ogTitle = document.querySelector('meta[property="og:title"]');
                if (ogTitle && ogTitle.content) {
                    result.title = ogTitle.content;
                }
            }

            if (!result.image) {
                const ogImage = document.querySelector('meta[property="og:image"]');
                if (ogImage && ogImage.content) {
                    result.image = ogImage.content;
                }
            }

            // 3. DOM selector'larından çek (fallback)
            if (!result.title) {
                const titleSelectors = [
                    'h1',
                    'h1.product-title',
                    'h1[class*="product"]',
                    'h1[class*="title"]',
                    '[data-testid*="product-name"]',
                    '[data-testid*="title"]',
                    '[class*="product-name"]',
                    '[class*="product-title"]',
                    'title'
                ];
                
                for (const selector of titleSelectors) {
                    try {
                        const el = document.querySelector(selector);
                        if (el && el.textContent && el.textContent.trim()) {
                            result.title = el.textContent.trim();
                            break;
                        }
                    } catch (e) {}
                }
            }

            if (!result.price) {
                const priceSelectors = [
                    'span.current-price',
                    'div.product-price',
                    'span[class*="current-price"]',
                    'div[class*="product-price"]',
                    'span[class*="price"]',
                    'div[class*="price"]',
                    'meta[property="product:price:amount"]',
                    '[data-testid*="price"]',
                    'span.price',
                    'div.price'
                ];
                
                for (const selector of priceSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                const priceValue = parseFloat(meta.content);
                                if (priceValue > 0) {
                                    if (priceValue >= 1000) {
                                        result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                    } else {
                                        result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                    }
                                    break;
                                }
                            }
                        } else {
                            const elements = document.querySelectorAll(selector);
                            for (const el of elements) {
                                const text = el.textContent.trim();
                                // D&R fiyat formatı: "24,99 TL" veya "24.99 TL" veya "2499 TL"
                                const priceMatch = text.match(/([0-9]{1,3}(?:[.,][0-9]{3})*[.,][0-9]{2}|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                                if (priceMatch) {
                                    let priceStr = priceMatch[1];
                                    // Format: 24,99 veya 24.99 veya 2499 -> 24.99
                                    if (priceStr.includes(',')) {
                                        // Türkçe format: 24,99 veya 1.234,99
                                        if (priceStr.includes('.')) {
                                            // 1.234,99 formatı
                                            priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                        } else {
                                            // 24,99 formatı
                                            priceStr = priceStr.replace(',', '.');
                                        }
                                    } else if (priceStr.includes('.')) {
                                        // 24.99 veya 1.234.99 formatı
                                        const parts = priceStr.split('.');
                                        if (parts.length > 2) {
                                            // 1.234.99 -> 1234.99 (binlik ayırıcı)
                                            priceStr = priceStr.replace(/\\./g, '');
                                        }
                                        // 24.99 -> 24.99 (ondalık)
                                    }
                                    
                                    const priceNum = parseFloat(priceStr);
                                    if (priceNum >= 1 && priceNum <= 100000) {
                                        // Türk Lirası formatına çevir: 24,99 TL
                                        if (priceNum >= 1000) {
                                            result.price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                        break;
                                    }
                                }
                            }
                            if (result.price) break;
                        }
                    } catch (e) {}
                }
            }

            // Eski fiyat (original_price)
            const oldPriceSelectors = [
                'span.old-price',
                'div.old-price',
                'span[class*="old-price"]',
                'div[class*="old-price"]',
                's[class*="price"]',
                'del[class*="price"]',
                'span[class*="original"]',
                'div[class*="original"]'
            ];
            
            for (const selector of oldPriceSelectors) {
                try {
                    const elements = document.querySelectorAll(selector);
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        const priceMatch = text.match(/([0-9]{1,3}(?:[.,][0-9]{3})*[.,][0-9]{2}|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                        if (priceMatch) {
                            let priceStr = priceMatch[1];
                            if (priceStr.includes(',')) {
                                if (priceStr.includes('.')) {
                                    priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                } else {
                                    priceStr = priceStr.replace(',', '.');
                                }
                            } else if (priceStr.includes('.')) {
                                const parts = priceStr.split('.');
                                if (parts.length > 2) {
                                    priceStr = priceStr.replace(/\\./g, '');
                                }
                            }
                            const priceNum = parseFloat(priceStr);
                            if (priceNum >= 1 && priceNum <= 100000) {
                                if (priceNum >= 1000) {
                                    result.original_price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                } else {
                                    result.original_price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                }
                                break;
                            }
                        }
                    }
                    if (result.original_price) break;
                } catch (e) {}
            }

            // Görsel
            if (!result.image) {
                const imageSelectors = [
                    'meta[property="og:image"]',
                    'img.product-image',
                    'img[class*="product-image"]',
                    'img[class*="product"]',
                    'img[data-testid="product-image"]',
                    'img[alt*="product"]',
                    'img[alt*="kitap"]',
                    'img[src*="dr.com.tr"]'
                ];
                
                for (const selector of imageSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                result.image = meta.content;
                                break;
                            }
                        } else {
                            const img = document.querySelector(selector);
                            if (img) {
                                let src = img.getAttribute('src') || img.getAttribute('data-src');
                                if (src) {
                                    // Relative URL'yi absolute yap
                                    if (src.startsWith('//')) {
                                        src = 'https:' + src;
                                    } else if (src.startsWith('/')) {
                                        src = 'https://www.dr.com.tr' + src;
                                    }
                                    result.image = src;
                                    break;
                                }
                            }
                        }
                    } catch (e) {}
                }
            }

            return (result.title && result.price && result.image) ? result : null;
        } catch (e) {
            return null;
        }
    }''')

async def extract_mavi_data(page):
    """Mavi özel veri çekme - Giyim ürünleri için optimize edilmiş"""
    return await page.evaluate('''() => {
        try {
            const result = {
                title: null,
                price: null,
                original_price: null,
                image: null,
                brand: "MAVI"
            };

            // 1. JSON-LD'den veri çek (en güvenilir)
            try {
                const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
                for (const script of jsonLdScripts) {
                    try {
                        const data = JSON.parse(script.textContent);
                        let product = null;
                        
                        if (data['@type'] === 'Product') {
                            product = data;
                        } else if (Array.isArray(data)) {
                            product = data.find(item => item['@type'] === 'Product');
                        } else if (data['@graph']) {
                            product = data['@graph'].find(item => item['@type'] === 'Product');
                        }
                        
                        if (product) {
                            if (product.name && !result.title) {
                                result.title = product.name;
                            }
                            
                            if (product.offers) {
                                const offers = Array.isArray(product.offers) ? product.offers[0] : product.offers;
                                if (offers && offers.price) {
                                    const priceValue = typeof offers.price === 'string' ? parseFloat(offers.price) : offers.price;
                                    if (priceValue > 0) {
                                        // Türk Lirası formatı: 2499.00 -> 2.499,00 TL
                                        if (priceValue >= 1000) {
                                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                    }
                                }
                            }
                            
                            if (product.image) {
                                const img = Array.isArray(product.image) ? product.image[0] : product.image;
                                result.image = typeof img === 'string' ? img : (img.url || img);
                            }
                            
                            if (product.brand) {
                                result.brand = typeof product.brand === 'string' ? product.brand : (product.brand.name || 'MAVI');
                            }
                        }
                    } catch (e) {}
                }
            } catch (e) {}

            // 2. Meta tag'lerden çek
            if (!result.price) {
                const metaPrice = document.querySelector('meta[property="product:price:amount"]');
                if (metaPrice && metaPrice.content) {
                    const priceValue = parseFloat(metaPrice.content);
                    if (priceValue > 0) {
                        if (priceValue >= 1000) {
                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                        } else {
                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                        }
                    }
                }
            }

            if (!result.title) {
                const ogTitle = document.querySelector('meta[property="og:title"]');
                if (ogTitle && ogTitle.content) {
                    result.title = ogTitle.content;
                }
            }

            if (!result.image) {
                const ogImage = document.querySelector('meta[property="og:image"]');
                if (ogImage && ogImage.content) {
                    result.image = ogImage.content;
                }
            }

            // 3. DOM selector'larından çek (fallback)
            if (!result.title) {
                const titleSelectors = [
                    'h1.product-name',
                    'h1[class*="product-name"]',
                    'h1[class*="product-title"]',
                    'h1[class*="title"]',
                    'h1',
                    '[data-testid*="product-name"]',
                    '[data-testid*="title"]',
                    '[class*="product-name"]',
                    '[class*="product-title"]',
                    'title'
                ];
                
                for (const selector of titleSelectors) {
                    try {
                        const el = document.querySelector(selector);
                        if (el && el.textContent && el.textContent.trim()) {
                            result.title = el.textContent.trim();
                            break;
                        }
                    } catch (e) {}
                }
            }

            if (!result.price) {
                const priceSelectors = [
                    'span[class*="price"]',
                    'div[class*="price"]',
                    'span[class*="Price"]',
                    'div[class*="Price"]',
                    'span.current-price',
                    'div.current-price',
                    'span.sale-price',
                    'div.sale-price',
                    'span[data-price]',
                    'div[data-price]',
                    'meta[property="product:price:amount"]',
                    '[data-testid*="price"]',
                    'span.price',
                    'div.price'
                ];
                
                for (const selector of priceSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                const priceValue = parseFloat(meta.content);
                                if (priceValue > 0) {
                                    if (priceValue >= 1000) {
                                        result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                    } else {
                                        result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                    }
                                    break;
                                }
                            }
                        } else {
                            const elements = document.querySelectorAll(selector);
                            for (const el of elements) {
                                const text = el.textContent.trim();
                                // Mavi fiyat formatı: "1.299,00 TL" veya "1.299 TL" veya "1299 TL"
                                const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*[.,][0-9]{2}|[0-9]{1,3}(?:\\.[0-9]{3})*|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                                if (priceMatch) {
                                    let priceStr = priceMatch[1];
                                    // Format: 1.299,00 veya 1.299 veya 1299,00 veya 1299 -> 1299.00
                                    if (priceStr.includes(',')) {
                                        // Türkçe format: 1.299,00 veya 1299,00
                                        if (priceStr.includes('.')) {
                                            // 1.299,00 formatı
                                            priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                        } else {
                                            // 1299,00 formatı
                                            priceStr = priceStr.replace(',', '.');
                                        }
                                    } else if (priceStr.includes('.')) {
                                        // 1.299 formatı (binlik ayırıcı)
                                        priceStr = priceStr.replace(/\\./g, '');
                                    }
                                    
                                    const priceNum = parseFloat(priceStr);
                                    if (priceNum >= 1 && priceNum <= 100000) {
                                        // Türk Lirası formatına çevir: 1.299,00 TL
                                        if (priceNum >= 1000) {
                                            result.price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                        break;
                                    }
                                }
                            }
                            if (result.price) break;
                        }
                    } catch (e) {}
                }
            }

            // Eski fiyat (original_price)
            const oldPriceSelectors = [
                'span[class*="old-price"]',
                'div[class*="old-price"]',
                'span[class*="original-price"]',
                'div[class*="original-price"]',
                'span[class*="regular-price"]',
                'div[class*="regular-price"]',
                's[class*="price"]',
                'del[class*="price"]',
                'span[class*="previous"]',
                'div[class*="previous"]'
            ];
            
            for (const selector of oldPriceSelectors) {
                try {
                    const elements = document.querySelectorAll(selector);
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*[.,][0-9]{2}|[0-9]{1,3}(?:\\.[0-9]{3})*|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                        if (priceMatch) {
                            let priceStr = priceMatch[1];
                            if (priceStr.includes(',')) {
                                if (priceStr.includes('.')) {
                                    priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                } else {
                                    priceStr = priceStr.replace(',', '.');
                                }
                            } else if (priceStr.includes('.')) {
                                priceStr = priceStr.replace(/\\./g, '');
                            }
                            const priceNum = parseFloat(priceStr);
                            if (priceNum >= 1 && priceNum <= 100000) {
                                if (priceNum >= 1000) {
                                    result.original_price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                } else {
                                    result.original_price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                }
                                break;
                            }
                        }
                    }
                    if (result.original_price) break;
                } catch (e) {}
            }

            // Görsel
            if (!result.image) {
                const imageSelectors = [
                    'meta[property="og:image"]',
                    'img[class*="product-image"]',
                    'img[class*="product__image"]',
                    'img[class*="productImage"]',
                    'img[data-testid="product-image"]',
                    'img[alt*="product"]',
                    'img[src*="mavi.com"]',
                    'img[src*="cdn"]',
                    'img[class*="main-image"]',
                    'img[class*="hero-image"]'
                ];
                
                for (const selector of imageSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                result.image = meta.content;
                                break;
                            }
                        } else {
                            const img = document.querySelector(selector);
                            if (img) {
                                let src = img.getAttribute('src') || img.getAttribute('data-src') || img.getAttribute('data-lazy-src');
                                if (src) {
                                    // Relative URL'yi absolute yap
                                    if (src.startsWith('//')) {
                                        src = 'https:' + src;
                                    } else if (src.startsWith('/')) {
                                        src = 'https://www.mavi.com' + src;
                                    }
                                    result.image = src;
                                    break;
                                }
                            }
                        }
                    } catch (e) {}
                }
            }

            return (result.title && result.price && result.image) ? result : null;
        } catch (e) {
            return null;
        }
    }''')

async def extract_lego_data(page):
    """LEGO.tr özel veri çekme - Oyuncak ve set ürünleri için optimize edilmiş"""
    return await page.evaluate('''() => {
        try {
            const result = {
                title: null,
                price: null,
                original_price: null,
                image: null,
                brand: "LEGO"
            };

            // 1. JSON-LD'den veri çek (en güvenilir)
            try {
                const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
                for (const script of jsonLdScripts) {
                    try {
                        const data = JSON.parse(script.textContent);
                        let product = null;
                        
                        if (data['@type'] === 'Product') {
                            product = data;
                        } else if (Array.isArray(data)) {
                            product = data.find(item => item['@type'] === 'Product');
                        } else if (data['@graph']) {
                            product = data['@graph'].find(item => item['@type'] === 'Product');
                        }
                        
                        if (product) {
                            if (product.name && !result.title) {
                                result.title = product.name;
                            }
                            
                            if (product.offers) {
                                const offers = Array.isArray(product.offers) ? product.offers[0] : product.offers;
                                if (offers && offers.price) {
                                    const priceValue = typeof offers.price === 'string' ? parseFloat(offers.price) : offers.price;
                                    if (priceValue > 0) {
                                        // Türk Lirası formatı: 2499.00 -> 2.499,00 TL
                                        if (priceValue >= 1000) {
                                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                    }
                                }
                            }
                            
                            if (product.image) {
                                const img = Array.isArray(product.image) ? product.image[0] : product.image;
                                result.image = typeof img === 'string' ? img : (img.url || img);
                            }
                            
                            if (product.brand) {
                                result.brand = typeof product.brand === 'string' ? product.brand : (product.brand.name || 'LEGO');
                            }
                        }
                    } catch (e) {}
                }
            } catch (e) {}

            // 2. Meta tag'lerden çek
            if (!result.price) {
                const metaPrice = document.querySelector('meta[property="product:price:amount"]');
                if (metaPrice && metaPrice.content) {
                    const priceValue = parseFloat(metaPrice.content);
                    if (priceValue > 0) {
                        if (priceValue >= 1000) {
                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                        } else {
                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                        }
                    }
                }
            }

            if (!result.title) {
                const ogTitle = document.querySelector('meta[property="og:title"]');
                if (ogTitle && ogTitle.content) {
                    result.title = ogTitle.content;
                }
            }

            if (!result.image) {
                const ogImage = document.querySelector('meta[property="og:image"]');
                if (ogImage && ogImage.content) {
                    result.image = ogImage.content;
                }
            }

            // 3. DOM selector'larından çek (fallback)
            if (!result.title) {
                const titleSelectors = [
                    'h1',
                    'h1.product-title',
                    'h1[class*="product"]',
                    'h1[class*="title"]',
                    '[data-testid*="product-name"]',
                    '[data-testid*="title"]',
                    '[class*="product-name"]',
                    '[class*="product-title"]',
                    'title'
                ];
                
                for (const selector of titleSelectors) {
                    try {
                        const el = document.querySelector(selector);
                        if (el && el.textContent && el.textContent.trim()) {
                            result.title = el.textContent.trim();
                            break;
                        }
                    } catch (e) {}
                }
            }

            if (!result.price) {
                const priceSelectors = [
                    'span.product-price',
                    'div.product-price',
                    'span[class*="product-price"]',
                    'div[class*="product-price"]',
                    'span[class*="price"]',
                    'div[class*="price"]',
                    'span[class*="Price"]',
                    'div[class*="Price"]',
                    'meta[property="product:price:amount"]',
                    '[data-testid*="price"]',
                    'span.price',
                    'div.price'
                ];
                
                for (const selector of priceSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                const priceValue = parseFloat(meta.content);
                                if (priceValue > 0) {
                                    if (priceValue >= 1000) {
                                        result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                    } else {
                                        result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                    }
                                    break;
                                }
                            }
                        } else {
                            const elements = document.querySelectorAll(selector);
                            for (const el of elements) {
                                const text = el.textContent.trim();
                                // LEGO fiyat formatı: "1.299,00 TL" veya "1.299 TL" veya "1299 TL"
                                const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*[.,][0-9]{2}|[0-9]{1,3}(?:\\.[0-9]{3})*|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                                if (priceMatch) {
                                    let priceStr = priceMatch[1];
                                    // Format: 1.299,00 veya 1.299 veya 1299,00 veya 1299 -> 1299.00
                                    if (priceStr.includes(',')) {
                                        // Türkçe format: 1.299,00 veya 1299,00
                                        if (priceStr.includes('.')) {
                                            // 1.299,00 formatı
                                            priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                        } else {
                                            // 1299,00 formatı
                                            priceStr = priceStr.replace(',', '.');
                                        }
                                    } else if (priceStr.includes('.')) {
                                        // 1.299 formatı (binlik ayırıcı)
                                        priceStr = priceStr.replace(/\\./g, '');
                                    }
                                    
                                    const priceNum = parseFloat(priceStr);
                                    if (priceNum >= 1 && priceNum <= 100000) {
                                        // Türk Lirası formatına çevir: 1.299,00 TL
                                        if (priceNum >= 1000) {
                                            result.price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                        break;
                                    }
                                }
                            }
                            if (result.price) break;
                        }
                    } catch (e) {}
                }
            }

            // Eski fiyat (original_price)
            const oldPriceSelectors = [
                'span[class*="old-price"]',
                'div[class*="old-price"]',
                'span[class*="original-price"]',
                'div[class*="original-price"]',
                'span[class*="regular-price"]',
                'div[class*="regular-price"]',
                's[class*="price"]',
                'del[class*="price"]',
                'span[class*="previous"]',
                'div[class*="previous"]'
            ];
            
            for (const selector of oldPriceSelectors) {
                try {
                    const elements = document.querySelectorAll(selector);
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*[.,][0-9]{2}|[0-9]{1,3}(?:\\.[0-9]{3})*|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                        if (priceMatch) {
                            let priceStr = priceMatch[1];
                            if (priceStr.includes(',')) {
                                if (priceStr.includes('.')) {
                                    priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                } else {
                                    priceStr = priceStr.replace(',', '.');
                                }
                            } else if (priceStr.includes('.')) {
                                priceStr = priceStr.replace(/\\./g, '');
                            }
                            const priceNum = parseFloat(priceStr);
                            if (priceNum >= 1 && priceNum <= 100000) {
                                if (priceNum >= 1000) {
                                    result.original_price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                } else {
                                    result.original_price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                }
                                break;
                            }
                        }
                    }
                    if (result.original_price) break;
                } catch (e) {}
            }

            // Görsel
            if (!result.image) {
                const imageSelectors = [
                    'meta[property="og:image"]',
                    'img.product-image',
                    'img[class*="product-image"]',
                    'img[class*="product"]',
                    'img[data-testid="product-image"]',
                    'img[alt*="product"]',
                    'img[alt*="LEGO"]',
                    'img[src*="lego"]',
                    'img[src*="cdn"]'
                ];
                
                for (const selector of imageSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                result.image = meta.content;
                                break;
                            }
                        } else {
                            const img = document.querySelector(selector);
                            if (img) {
                                let src = img.getAttribute('src') || img.getAttribute('data-src') || img.getAttribute('data-lazy-src');
                                if (src) {
                                    // Relative URL'yi absolute yap
                                    if (src.startsWith('//')) {
                                        src = 'https:' + src;
                                    } else if (src.startsWith('/')) {
                                        src = 'https://lego.tr' + src;
                                    }
                                    result.image = src;
                                    break;
                                }
                            }
                        }
                    } catch (e) {}
                }
            }

            return (result.title && result.price && result.image) ? result : null;
        } catch (e) {
            return null;
        }
    }''')

async def extract_jerf_data(page):
    """Jerf.com.tr özel veri çekme - Giyim ürünleri için optimize edilmiş"""
    return await page.evaluate('''() => {
        try {
            const result = {
                title: null,
                price: null,
                original_price: null,
                image: null,
                brand: "JERF"
            };

            // 1. JSON-LD'den veri çek (en güvenilir)
            try {
                const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
                for (const script of jsonLdScripts) {
                    try {
                        const data = JSON.parse(script.textContent);
                        let product = null;
                        
                        if (data['@type'] === 'Product') {
                            product = data;
                        } else if (Array.isArray(data)) {
                            product = data.find(item => item['@type'] === 'Product');
                        } else if (data['@graph']) {
                            product = data['@graph'].find(item => item['@type'] === 'Product');
                        }
                        
                        if (product) {
                            if (product.name && !result.title) {
                                result.title = product.name;
                            }
                            
                            if (product.offers) {
                                const offers = Array.isArray(product.offers) ? product.offers[0] : product.offers;
                                if (offers && offers.price) {
                                    const priceValue = typeof offers.price === 'string' ? parseFloat(offers.price) : offers.price;
                                    if (priceValue > 0) {
                                        // Türk Lirası formatı: 2499.00 -> 2.499,00 TL
                                        if (priceValue >= 1000) {
                                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                    }
                                }
                            }
                            
                            if (product.image) {
                                const img = Array.isArray(product.image) ? product.image[0] : product.image;
                                result.image = typeof img === 'string' ? img : (img.url || img);
                            }
                            
                            if (product.brand) {
                                result.brand = typeof product.brand === 'string' ? product.brand : (product.brand.name || 'JERF');
                            }
                        }
                    } catch (e) {}
                }
            } catch (e) {}

            // 2. ShopifyAnalytics'ten fiyat çek (Shopify mağazaları için)
            if (!result.price) {
                try {
                    if (window.ShopifyAnalytics && window.ShopifyAnalytics.meta && window.ShopifyAnalytics.meta.product && window.ShopifyAnalytics.meta.product.variants) {
                        const variant = window.ShopifyAnalytics.meta.product.variants[0];
                        if (variant && variant.price) {
                            // Shopify fiyatı kuruş cinsinden gelir (249900 -> 2499.00)
                            const priceValue = variant.price / 100;
                            if (priceValue >= 1000) {
                                result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                            } else {
                                result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                            }
                        }
                    }
                } catch (e) {}
            }

            // 3. Meta tag'lerden çek
            if (!result.price) {
                const metaPrice = document.querySelector('meta[property="product:price:amount"]');
                if (metaPrice && metaPrice.content) {
                    const priceValue = parseFloat(metaPrice.content);
                    if (priceValue > 0) {
                        if (priceValue >= 1000) {
                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                        } else {
                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                        }
                    }
                }
            }

            if (!result.title) {
                const ogTitle = document.querySelector('meta[property="og:title"]');
                if (ogTitle && ogTitle.content) {
                    result.title = ogTitle.content;
                }
            }

            if (!result.image) {
                const ogImage = document.querySelector('meta[property="og:image"]');
                if (ogImage && ogImage.content) {
                    result.image = ogImage.content;
                }
            }

            // 4. DOM selector'larından çek (fallback)
            if (!result.title) {
                const titleSelectors = [
                    'h1.product-title',
                    'h1[class*="product-title"]',
                    'h1[class*="product-name"]',
                    'h1[class*="title"]',
                    'h1',
                    '[data-testid*="product-name"]',
                    '[data-testid*="title"]',
                    '[class*="product-name"]',
                    '[class*="product-title"]',
                    'title'
                ];
                
                for (const selector of titleSelectors) {
                    try {
                        const el = document.querySelector(selector);
                        if (el && el.textContent && el.textContent.trim()) {
                            result.title = el.textContent.trim();
                            break;
                        }
                    } catch (e) {}
                }
            }

            if (!result.price) {
                const priceSelectors = [
                    'span[class*="price"]',
                    'div[class*="price"]',
                    'span[class*="Price"]',
                    'div[class*="Price"]',
                    'span.current-price',
                    'div.current-price',
                    'span.sale-price',
                    'div.sale-price',
                    'span[data-price]',
                    'div[data-price]',
                    'meta[property="product:price:amount"]',
                    '[data-testid*="price"]',
                    'span.price',
                    'div.price',
                    '.product-price',
                    '.product__price'
                ];
                
                for (const selector of priceSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                const priceValue = parseFloat(meta.content);
                                if (priceValue > 0) {
                                    if (priceValue >= 1000) {
                                        result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                    } else {
                                        result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                    }
                                    break;
                                }
                            }
                        } else {
                            const elements = document.querySelectorAll(selector);
                            for (const el of elements) {
                                const text = el.textContent.trim();
                                // Jerf fiyat formatı: "1.299,00 TL" veya "1.299 TL" veya "1299 TL"
                                const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*[.,][0-9]{2}|[0-9]{1,3}(?:\\.[0-9]{3})*|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                                if (priceMatch) {
                                    let priceStr = priceMatch[1];
                                    // Format: 1.299,00 veya 1.299 veya 1299,00 veya 1299 -> 1299.00
                                    if (priceStr.includes(',')) {
                                        // Türkçe format: 1.299,00 veya 1299,00
                                        if (priceStr.includes('.')) {
                                            // 1.299,00 formatı
                                            priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                        } else {
                                            // 1299,00 formatı
                                            priceStr = priceStr.replace(',', '.');
                                        }
                                    } else if (priceStr.includes('.')) {
                                        // 1.299 formatı (binlik ayırıcı)
                                        priceStr = priceStr.replace(/\\./g, '');
                                    }
                                    
                                    const priceNum = parseFloat(priceStr);
                                    if (priceNum >= 1 && priceNum <= 100000) {
                                        // Türk Lirası formatına çevir: 1.299,00 TL
                                        if (priceNum >= 1000) {
                                            result.price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                        break;
                                    }
                                }
                            }
                            if (result.price) break;
                        }
                    } catch (e) {}
                }
            }

            // Eski fiyat (original_price)
            const oldPriceSelectors = [
                'span[class*="old-price"]',
                'div[class*="old-price"]',
                'span[class*="original-price"]',
                'div[class*="original-price"]',
                'span[class*="regular-price"]',
                'div[class*="regular-price"]',
                'span[class*="compare-price"]',
                'div[class*="compare-price"]',
                's[class*="price"]',
                'del[class*="price"]',
                'span[class*="previous"]',
                'div[class*="previous"]'
            ];
            
            for (const selector of oldPriceSelectors) {
                try {
                    const elements = document.querySelectorAll(selector);
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*[.,][0-9]{2}|[0-9]{1,3}(?:\\.[0-9]{3})*|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                        if (priceMatch) {
                            let priceStr = priceMatch[1];
                            if (priceStr.includes(',')) {
                                if (priceStr.includes('.')) {
                                    priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                } else {
                                    priceStr = priceStr.replace(',', '.');
                                }
                            } else if (priceStr.includes('.')) {
                                priceStr = priceStr.replace(/\\./g, '');
                            }
                            const priceNum = parseFloat(priceStr);
                            if (priceNum >= 1 && priceNum <= 100000) {
                                if (priceNum >= 1000) {
                                    result.original_price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                } else {
                                    result.original_price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                }
                                break;
                            }
                        }
                    }
                    if (result.original_price) break;
                } catch (e) {}
            }

            // Görsel
            if (!result.image) {
                const imageSelectors = [
                    'meta[property="og:image"]',
                    'img[class*="product-image"]',
                    'img[class*="product__image"]',
                    'img[class*="productImage"]',
                    'img[data-testid="product-image"]',
                    'img[alt*="product"]',
                    'img[src*="jerf"]',
                    'img[src*="cdn"]',
                    'img[class*="main-image"]',
                    'img[class*="hero-image"]',
                    '.product-image img',
                    '.product__image img'
                ];
                
                for (const selector of imageSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                result.image = meta.content;
                                break;
                            }
                        } else {
                            const img = document.querySelector(selector);
                            if (img) {
                                let src = img.getAttribute('src') || img.getAttribute('data-src') || img.getAttribute('data-lazy-src') || img.getAttribute('data-original');
                                if (src) {
                                    // Relative URL'yi absolute yap
                                    if (src.startsWith('//')) {
                                        src = 'https:' + src;
                                    } else if (src.startsWith('/')) {
                                        src = 'https://www.jerf.com.tr' + src;
                                    }
                                    result.image = src;
                                    break;
                                }
                            }
                        }
                    } catch (e) {}
                }
            }

            return (result.title && result.price && result.image) ? result : null;
        } catch (e) {
            return null;
        }
    }''')

async def extract_vakkorama_data(page):
    """Vakkorama özel veri çekme - Giyim ürünleri için optimize edilmiş"""
    return await page.evaluate('''() => {
        try {
            const result = {
                title: null,
                price: null,
                original_price: null,
                image: null,
                brand: "Vakkorama"
            };

            // 1. JSON-LD'den veri çek (en güvenilir)
            try {
                const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
                for (const script of jsonLdScripts) {
                    try {
                        const data = JSON.parse(script.textContent);
                        let product = null;
                        
                        if (data['@type'] === 'Product') {
                            product = data;
                        } else if (Array.isArray(data)) {
                            product = data.find(item => item['@type'] === 'Product');
                        } else if (data['@graph']) {
                            product = data['@graph'].find(item => item['@type'] === 'Product');
                        }
                        
                        if (product) {
                            if (product.name && !result.title) {
                                result.title = product.name;
                            }
                            
                            if (product.offers) {
                                const offers = Array.isArray(product.offers) ? product.offers[0] : product.offers;
                                if (offers && offers.price) {
                                    const priceValue = typeof offers.price === 'string' ? parseFloat(offers.price) : offers.price;
                                    if (priceValue > 0) {
                                        // Türk Lirası formatı: 2667.00 -> 2.667,00 TL
                                        if (priceValue >= 1000) {
                                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                    }
                                }
                            }
                            
                            if (product.image) {
                                const img = Array.isArray(product.image) ? product.image[0] : product.image;
                                result.image = typeof img === 'string' ? img : (img.url || img);
                            }
                            
                            if (product.brand) {
                                result.brand = typeof product.brand === 'string' ? product.brand : (product.brand.name || 'Vakkorama');
                            }
                        }
                    } catch (e) {}
                }
            } catch (e) {}

            // 2. Meta tag'lerden çek
            if (!result.price) {
                const metaPrice = document.querySelector('meta[property="product:price:amount"]');
                if (metaPrice && metaPrice.content) {
                    const priceValue = parseFloat(metaPrice.content);
                    if (priceValue > 0) {
                        if (priceValue >= 1000) {
                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                        } else {
                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                        }
                    }
                }
            }

            if (!result.title) {
                const ogTitle = document.querySelector('meta[property="og:title"]');
                if (ogTitle && ogTitle.content) {
                    result.title = ogTitle.content;
                }
            }

            if (!result.image) {
                const ogImage = document.querySelector('meta[property="og:image"]');
                if (ogImage && ogImage.content) {
                    result.image = ogImage.content;
                }
            }

            // 3. DOM selector'larından çek (fallback)
            if (!result.title) {
                const titleSelectors = [
                    'h1',
                    'h1.product-title',
                    'h1[class*="product-title"]',
                    'h1[class*="product-name"]',
                    'h1[class*="title"]',
                    '[data-testid*="product-name"]',
                    '[data-testid*="title"]',
                    '[class*="product-name"]',
                    '[class*="product-title"]',
                    'title'
                ];
                
                for (const selector of titleSelectors) {
                    try {
                        const el = document.querySelector(selector);
                        if (el && el.textContent && el.textContent.trim()) {
                            result.title = el.textContent.trim();
                            break;
                        }
                    } catch (e) {}
                }
            }

            if (!result.price) {
                const priceSelectors = [
                    'div.product-price-container div.price',
                    'div.price',
                    'span[class*="price"]',
                    'div[class*="price"]',
                    'span.current-price',
                    'div.current-price',
                    'span.sale-price',
                    'div.sale-price',
                    'meta[property="product:price:amount"]',
                    '[data-testid*="price"]',
                    'span.price',
                    'div.price'
                ];
                
                for (const selector of priceSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                const priceValue = parseFloat(meta.content);
                                if (priceValue > 0) {
                                    if (priceValue >= 1000) {
                                        result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                    } else {
                                        result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                    }
                                    break;
                                }
                            }
                        } else {
                            const elements = document.querySelectorAll(selector);
                            for (const el of elements) {
                                const text = el.textContent.trim();
                                // Vakkorama fiyat formatı: "2.667,00" veya "2.667" veya "2667"
                                const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*[.,][0-9]{2}|[0-9]{1,3}(?:\\.[0-9]{3})*|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                                if (priceMatch) {
                                    let priceStr = priceMatch[1];
                                    // Format: 2.667,00 veya 2.667 veya 2667,00 veya 2667 -> 2667.00
                                    if (priceStr.includes(',')) {
                                        // Türkçe format: 2.667,00 veya 2667,00
                                        if (priceStr.includes('.')) {
                                            // 2.667,00 formatı
                                            priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                        } else {
                                            // 2667,00 formatı
                                            priceStr = priceStr.replace(',', '.');
                                        }
                                    } else if (priceStr.includes('.')) {
                                        // 2.667 formatı (binlik ayırıcı)
                                        priceStr = priceStr.replace(/\\./g, '');
                                    }
                                    
                                    const priceNum = parseFloat(priceStr);
                                    if (priceNum >= 1 && priceNum <= 100000) {
                                        // Türk Lirası formatına çevir: 2.667,00 TL
                                        if (priceNum >= 1000) {
                                            result.price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                        break;
                                    }
                                }
                            }
                            if (result.price) break;
                        }
                    } catch (e) {}
                }
            }

            // Eski fiyat (original_price) - Vakkorama'da genelde üstte eski fiyat, altta yeni fiyat gösterilir
            const oldPriceSelectors = [
                'div.product-price-container div.old-price',
                'div.old-price',
                'span[class*="old-price"]',
                'div[class*="old-price"]',
                'span[class*="original-price"]',
                'div[class*="original-price"]',
                'span[class*="regular-price"]',
                'div[class*="regular-price"]',
                's[class*="price"]',
                'del[class*="price"]',
                'span[class*="previous"]',
                'div[class*="previous"]'
            ];
            
            for (const selector of oldPriceSelectors) {
                try {
                    const elements = document.querySelectorAll(selector);
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*[.,][0-9]{2}|[0-9]{1,3}(?:\\.[0-9]{3})*|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                        if (priceMatch) {
                            let priceStr = priceMatch[1];
                            if (priceStr.includes(',')) {
                                if (priceStr.includes('.')) {
                                    priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                } else {
                                    priceStr = priceStr.replace(',', '.');
                                }
                            } else if (priceStr.includes('.')) {
                                priceStr = priceStr.replace(/\\./g, '');
                            }
                            const priceNum = parseFloat(priceStr);
                            if (priceNum >= 1 && priceNum <= 100000) {
                                if (priceNum >= 1000) {
                                    result.original_price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                } else {
                                    result.original_price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                }
                                break;
                            }
                        }
                    }
                    if (result.original_price) break;
                } catch (e) {}
            }

            // Görsel - Vakkorama'da genelde slider içinde görseller var
            if (!result.image) {
                const imageSelectors = [
                    'meta[property="og:image"]',
                    'img.product-image',
                    'img[class*="product-image"]',
                    'img[class*="product"]',
                    'img[data-testid="product-image"]',
                    'img[alt*="product"]',
                    'img[src*="vakkorama"]',
                    'img[src*="cdn"]',
                    '.product-image img',
                    '.product__image img',
                    '.product-slider img',
                    '.product-gallery img'
                ];
                
                for (const selector of imageSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                result.image = meta.content;
                                break;
                            }
                        } else {
                            const img = document.querySelector(selector);
                            if (img) {
                                let src = img.getAttribute('src') || img.getAttribute('data-src') || img.getAttribute('data-lazy-src') || img.getAttribute('data-original');
                                if (src) {
                                    // Relative URL'yi absolute yap
                                    if (src.startsWith('//')) {
                                        src = 'https:' + src;
                                    } else if (src.startsWith('/')) {
                                        src = 'https://www.vakkorama.com.tr' + src;
                                    }
                                    result.image = src;
                                    break;
                                }
                            }
                        }
                    } catch (e) {}
                }
            }

            return (result.title && result.price && result.image) ? result : null;
        } catch (e) {
            return null;
        }
    }''')

async def extract_massimodutti_data(page):
    """Massimo Dutti özel veri çekme - Lüks giyim ürünleri için optimize edilmiş"""
    return await page.evaluate('''() => {
        try {
            const result = {
                title: null,
                price: null,
                original_price: null,
                image: null,
                brand: "MASSIMO DUTTI"
            };

            // 1. JSON-LD'den veri çek (en güvenilir)
            try {
                const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
                for (const script of jsonLdScripts) {
                    try {
                        const data = JSON.parse(script.textContent);
                        let product = null;
                        
                        if (data['@type'] === 'Product') {
                            product = data;
                        } else if (Array.isArray(data)) {
                            product = data.find(item => item['@type'] === 'Product');
                        } else if (data['@graph']) {
                            product = data['@graph'].find(item => item['@type'] === 'Product');
                        }
                        
                        if (product) {
                            if (product.name && !result.title) {
                                result.title = product.name;
                            }
                            
                            if (product.offers) {
                                const offers = Array.isArray(product.offers) ? product.offers[0] : product.offers;
                                if (offers && offers.price) {
                                    const priceValue = typeof offers.price === 'string' ? parseFloat(offers.price) : offers.price;
                                    if (priceValue > 0) {
                                        // Türk Lirası formatı: 2499.00 -> 2.499,00 TL
                                        if (priceValue >= 1000) {
                                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                    }
                                }
                            }
                            
                            if (product.image) {
                                const img = Array.isArray(product.image) ? product.image[0] : product.image;
                                result.image = typeof img === 'string' ? img : (img.url || img);
                            }
                            
                            if (product.brand) {
                                result.brand = typeof product.brand === 'string' ? product.brand : (product.brand.name || 'MASSIMO DUTTI');
                            }
                        }
                    } catch (e) {}
                }
            } catch (e) {}

            // 2. Meta tag'lerden çek
            if (!result.price) {
                const metaPrice = document.querySelector('meta[property="product:price:amount"]');
                if (metaPrice && metaPrice.content) {
                    const priceValue = parseFloat(metaPrice.content);
                    if (priceValue > 0) {
                        if (priceValue >= 1000) {
                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                        } else {
                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                        }
                    }
                }
                
                // Alternatif meta tag
                if (!result.price) {
                    const metaPriceAlt = document.querySelector('meta[name="price"]');
                    if (metaPriceAlt && metaPriceAlt.content) {
                        const priceValue = parseFloat(metaPriceAlt.content);
                        if (priceValue > 0) {
                            if (priceValue >= 1000) {
                                result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                            } else {
                                result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                            }
                        }
                    }
                }
            }

            if (!result.title) {
                const ogTitle = document.querySelector('meta[property="og:title"]');
                if (ogTitle && ogTitle.content) {
                    result.title = ogTitle.content;
                }
            }

            if (!result.image) {
                const ogImage = document.querySelector('meta[property="og:image"]');
                if (ogImage && ogImage.content) {
                    result.image = ogImage.content;
                }
            }

            // 3. DOM selector'larından çek (fallback)
            if (!result.title) {
                const titleSelectors = [
                    'h1.md-product-heading-title-txt',
                    'h1[class*="product-heading"]',
                    'h1[class*="product-title"]',
                    'h1[class*="product-name"]',
                    'h1[class*="title"]',
                    'h1',
                    '[data-testid*="product-name"]',
                    '[data-testid*="title"]',
                    '[class*="product-name"]',
                    '[class*="product-title"]',
                    'title'
                ];
                
                for (const selector of titleSelectors) {
                    try {
                        const el = document.querySelector(selector);
                        if (el && el.textContent && el.textContent.trim()) {
                            result.title = el.textContent.trim();
                            break;
                        }
                    } catch (e) {}
                }
            }

            if (!result.price) {
                const priceSelectors = [
                    'div.formatted-price-detail-handler',
                    'div[class*="formatted-price"]',
                    'span[class*="price"]',
                    'div[class*="price"]',
                    'span[class*="Price"]',
                    'div[class*="Price"]',
                    'meta[property="product:price:amount"]',
                    'meta[name="price"]',
                    '[data-testid*="price"]',
                    'span.price',
                    'div.price'
                ];
                
                for (const selector of priceSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                const priceValue = parseFloat(meta.content);
                                if (priceValue > 0) {
                                    if (priceValue >= 1000) {
                                        result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                    } else {
                                        result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                    }
                                    break;
                                }
                            }
                        } else {
                            const elements = document.querySelectorAll(selector);
                            for (const el of elements) {
                                const text = el.textContent.trim();
                                // Massimo Dutti fiyat formatı: "2.499,00 TL" veya "2.499 TL" veya "2499 TL"
                                const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*[.,][0-9]{2}|[0-9]{1,3}(?:\\.[0-9]{3})*|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                                if (priceMatch) {
                                    let priceStr = priceMatch[1];
                                    // Format: 2.499,00 veya 2.499 veya 2499,00 veya 2499 -> 2499.00
                                    if (priceStr.includes(',')) {
                                        // Türkçe format: 2.499,00 veya 2499,00
                                        if (priceStr.includes('.')) {
                                            // 2.499,00 formatı
                                            priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                        } else {
                                            // 2499,00 formatı
                                            priceStr = priceStr.replace(',', '.');
                                        }
                                    } else if (priceStr.includes('.')) {
                                        // 2.499 formatı (binlik ayırıcı)
                                        priceStr = priceStr.replace(/\\./g, '');
                                    }
                                    
                                    const priceNum = parseFloat(priceStr);
                                    if (priceNum >= 1 && priceNum <= 100000) {
                                        // Türk Lirası formatına çevir: 2.499,00 TL
                                        if (priceNum >= 1000) {
                                            result.price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                        break;
                                    }
                                }
                            }
                            if (result.price) break;
                        }
                    } catch (e) {}
                }
            }

            // Eski fiyat (original_price)
            const oldPriceSelectors = [
                'span[class*="old-price"]',
                'div[class*="old-price"]',
                'span[class*="original-price"]',
                'div[class*="original-price"]',
                'span[class*="regular-price"]',
                'div[class*="regular-price"]',
                's[class*="price"]',
                'del[class*="price"]',
                'span[class*="previous"]',
                'div[class*="previous"]'
            ];
            
            for (const selector of oldPriceSelectors) {
                try {
                    const elements = document.querySelectorAll(selector);
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*[.,][0-9]{2}|[0-9]{1,3}(?:\\.[0-9]{3})*|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                        if (priceMatch) {
                            let priceStr = priceMatch[1];
                            if (priceStr.includes(',')) {
                                if (priceStr.includes('.')) {
                                    priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                } else {
                                    priceStr = priceStr.replace(',', '.');
                                }
                            } else if (priceStr.includes('.')) {
                                priceStr = priceStr.replace(/\\./g, '');
                            }
                            const priceNum = parseFloat(priceStr);
                            if (priceNum >= 1 && priceNum <= 100000) {
                                if (priceNum >= 1000) {
                                    result.original_price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                } else {
                                    result.original_price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                }
                                break;
                            }
                        }
                    }
                    if (result.original_price) break;
                } catch (e) {}
            }

            // Görsel
            if (!result.image) {
                const imageSelectors = [
                    'meta[property="og:image"]',
                    'img[class*="product-image"]',
                    'img[class*="product__image"]',
                    'img[class*="productImage"]',
                    'img[data-testid="product-image"]',
                    'img[alt*="product"]',
                    'img[src*="massimodutti"]',
                    'img[src*="cdn"]',
                    'img[class*="main-image"]',
                    'img[class*="hero-image"]',
                    '.product-image img',
                    '.product__image img',
                    '.product-gallery img'
                ];
                
                for (const selector of imageSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                result.image = meta.content;
                                break;
                            }
                        } else {
                            const img = document.querySelector(selector);
                            if (img) {
                                let src = img.getAttribute('src') || img.getAttribute('data-src') || img.getAttribute('data-lazy-src') || img.getAttribute('data-original');
                                if (src) {
                                    // Relative URL'yi absolute yap
                                    if (src.startsWith('//')) {
                                        src = 'https:' + src;
                                    } else if (src.startsWith('/')) {
                                        src = 'https://www.massimodutti.com' + src;
                                    }
                                    result.image = src;
                                    break;
                                }
                            }
                        }
                    } catch (e) {}
                }
            }

            return (result.title && result.price && result.image) ? result : null;
        } catch (e) {
            return null;
        }
    }''')

async def extract_victoriassecret_data(page):
    """Victoria's Secret özel veri çekme - İç giyim ve kozmetik ürünleri için optimize edilmiş"""
    return await page.evaluate('''() => {
        try {
            const result = {
                title: null,
                price: null,
                original_price: null,
                image: null,
                brand: "VICTORIA'S SECRET"
            };

            // 1. JSON-LD'den veri çek (en güvenilir)
            try {
                const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
                for (const script of jsonLdScripts) {
                    try {
                        const data = JSON.parse(script.textContent);
                        let product = null;
                        
                        if (data['@type'] === 'Product') {
                            product = data;
                        } else if (Array.isArray(data)) {
                            product = data.find(item => item['@type'] === 'Product');
                        } else if (data['@graph']) {
                            product = data['@graph'].find(item => item['@type'] === 'Product');
                        }
                        
                        if (product) {
                            if (product.name && !result.title) {
                                result.title = product.name;
                            }
                            
                            if (product.offers) {
                                const offers = Array.isArray(product.offers) ? product.offers[0] : product.offers;
                                if (offers && offers.price) {
                                    const priceValue = typeof offers.price === 'string' ? parseFloat(offers.price) : offers.price;
                                    if (priceValue > 0) {
                                        // Türk Lirası formatı: 2499.00 -> 2.499,00 TL
                                        if (priceValue >= 1000) {
                                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                    }
                                }
                            }
                            
                            if (product.image) {
                                const img = Array.isArray(product.image) ? product.image[0] : product.image;
                                result.image = typeof img === 'string' ? img : (img.url || img);
                            }
                            
                            if (product.brand) {
                                result.brand = typeof product.brand === 'string' ? product.brand : (product.brand.name || "VICTORIA'S SECRET");
                            }
                        }
                    } catch (e) {}
                }
            } catch (e) {}

            // 2. Meta tag'lerden çek
            if (!result.price) {
                const metaPrice = document.querySelector('meta[property="product:price:amount"]');
                if (metaPrice && metaPrice.content) {
                    const priceValue = parseFloat(metaPrice.content);
                    if (priceValue > 0) {
                        if (priceValue >= 1000) {
                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                        } else {
                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                        }
                    }
                }
            }

            if (!result.title) {
                const ogTitle = document.querySelector('meta[property="og:title"]');
                if (ogTitle && ogTitle.content) {
                    result.title = ogTitle.content;
                }
            }

            if (!result.image) {
                const ogImage = document.querySelector('meta[property="og:image"]');
                if (ogImage && ogImage.content) {
                    result.image = ogImage.content;
                }
            }

            // 3. DOM selector'larından çek (fallback) - Victoria's Secret özel yapısı
            if (!result.title) {
                const titleSelectors = [
                    'h1',
                    'h1.product-title',
                    'h1[class*="product-title"]',
                    'h1[class*="product-name"]',
                    'h1[class*="title"]',
                    '[data-testid*="product-name"]',
                    '[data-testid*="title"]',
                    '[class*="product-name"]',
                    '[class*="product-title"]',
                    'title'
                ];
                
                for (const selector of titleSelectors) {
                    try {
                        const el = document.querySelector(selector);
                        if (el && el.textContent && el.textContent.trim()) {
                            result.title = el.textContent.trim();
                            break;
                        }
                    } catch (e) {}
                }
            }

            if (!result.price) {
                // Victoria's Secret özel fiyat selector'ları
                const priceSelectors = [
                    'span#indirimliFiyat span.spanFiyat',
                    'div.IndirimliFiyatContent span.spanFiyat',
                    'div#divIndirimliFiyat span.spanFiyat:last-of-type',
                    'span.spanFiyat',
                    'div.indirimliFiyat',
                    'div.product-price-discounted',
                    'div.product-price-not-discounted',
                    'div[class*="product-price"]',
                    'span[class*="price"]',
                    'div[class*="price"]',
                    'meta[property="product:price:amount"]',
                    'div.recommended-item-discounted-price',
                    '[data-testid*="price"]',
                    'span.price',
                    'div.price'
                ];
                
                for (const selector of priceSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                const priceValue = parseFloat(meta.content);
                                if (priceValue > 0) {
                                    if (priceValue >= 1000) {
                                        result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                    } else {
                                        result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                    }
                                    break;
                                }
                            }
                        } else {
                            const elements = document.querySelectorAll(selector);
                            for (const el of elements) {
                                const text = el.textContent.trim();
                                // Victoria's Secret fiyat formatı: "1.299,00 TL" veya "1.299 TL" veya "1299 TL"
                                const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*[.,][0-9]{2}|[0-9]{1,3}(?:\\.[0-9]{3})*|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                                if (priceMatch) {
                                    let priceStr = priceMatch[1];
                                    // Format: 1.299,00 veya 1.299 veya 1299,00 veya 1299 -> 1299.00
                                    if (priceStr.includes(',')) {
                                        // Türkçe format: 1.299,00 veya 1299,00
                                        if (priceStr.includes('.')) {
                                            // 1.299,00 formatı
                                            priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                        } else {
                                            // 1299,00 formatı
                                            priceStr = priceStr.replace(',', '.');
                                        }
                                    } else if (priceStr.includes('.')) {
                                        // 1.299 formatı (binlik ayırıcı)
                                        priceStr = priceStr.replace(/\\./g, '');
                                    }
                                    
                                    const priceNum = parseFloat(priceStr);
                                    if (priceNum >= 1 && priceNum <= 100000) {
                                        // Türk Lirası formatına çevir: 1.299,00 TL
                                        if (priceNum >= 1000) {
                                            result.price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                        break;
                                    }
                                }
                            }
                            if (result.price) break;
                        }
                    } catch (e) {}
                }
            }

            // Eski fiyat (original_price) - Victoria's Secret özel yapısı
            const oldPriceSelectors = [
                'span#fiyat span.spanFiyat',
                'div.PiyasafiyatiContent span.spanFiyat',
                'div.product-price-old',
                'div.recommended-item-old-price',
                'span[class*="old-price"]',
                'div[class*="old-price"]',
                'span[class*="original-price"]',
                'div[class*="original-price"]',
                's[class*="price"]',
                'del[class*="price"]'
            ];
            
            for (const selector of oldPriceSelectors) {
                try {
                    const elements = document.querySelectorAll(selector);
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*[.,][0-9]{2}|[0-9]{1,3}(?:\\.[0-9]{3})*|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                        if (priceMatch) {
                            let priceStr = priceMatch[1];
                            if (priceStr.includes(',')) {
                                if (priceStr.includes('.')) {
                                    priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                } else {
                                    priceStr = priceStr.replace(',', '.');
                                }
                            } else if (priceStr.includes('.')) {
                                priceStr = priceStr.replace(/\\./g, '');
                            }
                            const priceNum = parseFloat(priceStr);
                            if (priceNum >= 1 && priceNum <= 100000) {
                                if (priceNum >= 1000) {
                                    result.original_price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                } else {
                                    result.original_price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                }
                                break;
                            }
                        }
                    }
                    if (result.original_price) break;
                } catch (e) {}
            }

            // Görsel - Victoria's Secret özel yapısı
            if (!result.image) {
                const imageSelectors = [
                    'meta[property="og:image"]',
                    'img#imgurunresmi',
                    'img[alt*="Kalpli"]',
                    'img[class*="product-image"]',
                    'img[class*="product__image"]',
                    'img[data-testid="product-image"]',
                    'img[alt*="product"]',
                    'img[src*="victoriassecret"]',
                    'img[src*="cdn"]',
                    '.product-image img',
                    '.product__image img'
                ];
                
                for (const selector of imageSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                result.image = meta.content;
                                break;
                            }
                        } else {
                            const img = document.querySelector(selector);
                            if (img) {
                                let src = img.getAttribute('src') || img.getAttribute('data-src') || img.getAttribute('data-lazy-src') || img.getAttribute('data-original');
                                if (src) {
                                    // Relative URL'yi absolute yap
                                    if (src.startsWith('//')) {
                                        src = 'https:' + src;
                                    } else if (src.startsWith('/')) {
                                        src = 'https://www.victoriassecret.com.tr' + src;
                                    }
                                    result.image = src;
                                    break;
                                }
                            }
                        }
                    } catch (e) {}
                }
            }

            return (result.title && result.price && result.image) ? result : null;
        } catch (e) {
            return null;
        }
    }''')

async def extract_gratis_data(page):
    """Gratis.com özel veri çekme - Kozmetik ve kişisel bakım ürünleri için optimize edilmiş"""
    return await page.evaluate('''() => {
        try {
            const result = {
                title: null,
                price: null,
                original_price: null,
                image: null,
                brand: null
            };

            // 1. JSON-LD'den veri çek (en güvenilir)
            try {
                const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
                for (const script of jsonLdScripts) {
                    try {
                        const data = JSON.parse(script.textContent);
                        let product = null;
                        
                        if (data['@type'] === 'Product') {
                            product = data;
                        } else if (Array.isArray(data)) {
                            product = data.find(item => item['@type'] === 'Product');
                        } else if (data['@graph']) {
                            product = data['@graph'].find(item => item['@type'] === 'Product');
                        }
                        
                        if (product) {
                            if (product.name && !result.title) {
                                result.title = product.name;
                            }
                            
                            if (product.offers) {
                                const offers = Array.isArray(product.offers) ? product.offers[0] : product.offers;
                                if (offers && offers.price) {
                                    let priceValue = typeof offers.price === 'string' ? parseFloat(offers.price) : offers.price;
                                    
                                    // Gratis fiyatları kuruş cinsinden gelebilir (örn: 13500 -> 135.00)
                                    if (priceValue > 1000 && priceValue < 1000000) {
                                        priceValue = priceValue / 100;
                                    }
                                    
                                    if (priceValue > 0 && priceValue < 100000) {
                                        // Türk Lirası formatı: 135.00 -> 135,00 TL
                                        if (priceValue >= 1000) {
                                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                    }
                                }
                            }
                            
                            if (product.image) {
                                const img = Array.isArray(product.image) ? product.image[0] : product.image;
                                result.image = typeof img === 'string' ? img : (img.url || img);
                            }
                            
                            if (product.brand) {
                                result.brand = typeof product.brand === 'string' ? product.brand : (product.brand.name || null);
                            }
                        }
                    } catch (e) {}
                }
            } catch (e) {}

            // 2. Meta tag'lerden çek
            if (!result.price) {
                const metaPrice = document.querySelector('meta[property="product:price:amount"]');
                if (metaPrice && metaPrice.content) {
                    let priceValue = parseFloat(metaPrice.content);
                    // Kuruş cinsinden gelebilir
                    if (priceValue > 1000 && priceValue < 1000000) {
                        priceValue = priceValue / 100;
                    }
                    if (priceValue > 0 && priceValue < 100000) {
                        if (priceValue >= 1000) {
                            result.price = priceValue.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                        } else {
                            result.price = priceValue.toFixed(2).replace('.', ',') + ' TL';
                        }
                    }
                }
            }

            if (!result.title) {
                const ogTitle = document.querySelector('meta[property="og:title"]');
                if (ogTitle && ogTitle.content) {
                    result.title = ogTitle.content;
                }
            }

            if (!result.image) {
                const ogImage = document.querySelector('meta[property="og:image"]');
                if (ogImage && ogImage.content) {
                    result.image = ogImage.content;
                }
            }

            // 3. DOM selector'larından çek (fallback) - Gratis özel yapısı
            if (!result.title) {
                const titleSelectors = [
                    'h1',
                    'h1[class*="product-title"]',
                    'h1[class*="product-name"]',
                    'h1[class*="title"]',
                    '[data-testid*="product-name"]',
                    '[data-testid*="title"]',
                    '[class*="product-name"]',
                    '[class*="product-title"]',
                    'title'
                ];
                
                for (const selector of titleSelectors) {
                    try {
                        const el = document.querySelector(selector);
                        if (el && el.textContent && el.textContent.trim()) {
                            result.title = el.textContent.trim();
                            break;
                        }
                    } catch (e) {}
                }
            }

            if (!result.price) {
                // Gratis özel fiyat selector'ları
                // Önce indirimli fiyatı (Gratis Kart ile) bul, sonra normal fiyatı
                const discountedPriceSelectors = [
                    'span.text-primary-900.font-bold',
                    'span[class*="discounted"]',
                    'span[class*="sale"]',
                    'div[class*="discounted-price"]',
                    'span[class*="gratis-kart"]',
                    '[data-testid*="discounted-price"]'
                ];
                
                for (const selector of discountedPriceSelectors) {
                    try {
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {
                            const text = el.textContent.trim();
                            // Gratis fiyat formatı: "75,00 TL" veya "75 TL" veya "7500" (kuruş)
                            const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*[.,][0-9]{2}|[0-9]{1,3}(?:\\.[0-9]{3})*|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                            if (priceMatch) {
                                let priceStr = priceMatch[1];
                                // Format: 75,00 veya 75 veya 7500 -> 75.00
                                if (priceStr.includes(',')) {
                                    if (priceStr.includes('.')) {
                                        priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                    } else {
                                        priceStr = priceStr.replace(',', '.');
                                    }
                                } else if (priceStr.includes('.')) {
                                    // 1.299 formatı (binlik ayırıcı)
                                    priceStr = priceStr.replace(/\\./g, '');
                                }
                                
                                let priceNum = parseFloat(priceStr);
                                // Eğer çok büyükse (kuruş cinsinden olabilir)
                                if (priceNum > 1000 && priceNum < 1000000) {
                                    priceNum = priceNum / 100;
                                }
                                
                                if (priceNum >= 1 && priceNum <= 100000) {
                                    if (priceNum >= 1000) {
                                        result.price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                    } else {
                                        result.price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                    }
                                    break;
                                }
                            }
                        }
                        if (result.price) break;
                    } catch (e) {}
                }
                
                // Eğer indirimli fiyat bulunamadıysa, normal fiyatı bul
                if (!result.price) {
                    const priceSelectors = [
                        'span[class*="price"]',
                        'div[class*="price"]',
                        'span.text-primary-900.font-bold',
                        '[data-testid*="price"]',
                        'span.price',
                        'div.price'
                    ];
                    
                    for (const selector of priceSelectors) {
                        try {
                            const elements = document.querySelectorAll(selector);
                            for (const el of elements) {
                                const text = el.textContent.trim();
                                const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*[.,][0-9]{2}|[0-9]{1,3}(?:\\.[0-9]{3})*|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                                if (priceMatch) {
                                    let priceStr = priceMatch[1];
                                    if (priceStr.includes(',')) {
                                        if (priceStr.includes('.')) {
                                            priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                        } else {
                                            priceStr = priceStr.replace(',', '.');
                                        }
                                    } else if (priceStr.includes('.')) {
                                        priceStr = priceStr.replace(/\\./g, '');
                                    }
                                    
                                    let priceNum = parseFloat(priceStr);
                                    if (priceNum > 1000 && priceNum < 1000000) {
                                        priceNum = priceNum / 100;
                                    }
                                    
                                    if (priceNum >= 1 && priceNum <= 100000) {
                                        if (priceNum >= 1000) {
                                            result.price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                        } else {
                                            result.price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                        }
                                        break;
                                    }
                                }
                            }
                            if (result.price) break;
                        } catch (e) {}
                    }
                }
            }

            // Eski fiyat (original_price) - Gratis'te normal fiyat indirimli fiyatın üstünde olabilir
            const oldPriceSelectors = [
                'span[class*="old-price"]',
                'div[class*="old-price"]',
                'span[class*="original-price"]',
                'div[class*="original-price"]',
                's[class*="price"]',
                'del[class*="price"]',
                'span[class*="text-gray"]',
                'div[class*="text-gray"]'
            ];
            
            for (const selector of oldPriceSelectors) {
                try {
                    const elements = document.querySelectorAll(selector);
                    for (const el of elements) {
                        const text = el.textContent.trim();
                        const priceMatch = text.match(/([0-9]{1,3}(?:\\.[0-9]{3})*[.,][0-9]{2}|[0-9]{1,3}(?:\\.[0-9]{3})*|[0-9]+[.,][0-9]{2}|[0-9]+)/);
                        if (priceMatch) {
                            let priceStr = priceMatch[1];
                            if (priceStr.includes(',')) {
                                if (priceStr.includes('.')) {
                                    priceStr = priceStr.replace(/\\./g, '').replace(',', '.');
                                } else {
                                    priceStr = priceStr.replace(',', '.');
                                }
                            } else if (priceStr.includes('.')) {
                                priceStr = priceStr.replace(/\\./g, '');
                            }
                            let priceNum = parseFloat(priceStr);
                            if (priceNum > 1000 && priceNum < 1000000) {
                                priceNum = priceNum / 100;
                            }
                            if (priceNum >= 1 && priceNum <= 100000) {
                                if (priceNum >= 1000) {
                                    result.original_price = priceNum.toLocaleString('tr-TR', {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' TL';
                                } else {
                                    result.original_price = priceNum.toFixed(2).replace('.', ',') + ' TL';
                                }
                                break;
                            }
                        }
                    }
                    if (result.original_price) break;
                } catch (e) {}
            }

            // Marka çıkarma - Başlıktan veya ayrı bir elementten
            if (!result.brand) {
                // Başlıktan marka çıkarma (örn: "Bee Beauty Glamorous Times...")
                if (result.title) {
                    const brandMatch = result.title.match(/^([A-Z][a-zA-Z\\s&]+?)\\s/);
                    if (brandMatch) {
                        result.brand = brandMatch[1].trim();
                    }
                }
                
                // Veya ayrı bir marka elementinden
                const brandSelectors = [
                    '[class*="brand"]',
                    '[data-testid*="brand"]',
                    'span[class*="brand-name"]',
                    'div[class*="brand-name"]'
                ];
                
                for (const selector of brandSelectors) {
                    try {
                        const el = document.querySelector(selector);
                        if (el && el.textContent && el.textContent.trim()) {
                            result.brand = el.textContent.trim();
                            break;
                        }
                    } catch (e) {}
                }
            }
            
            // Eğer marka bulunamadıysa, varsayılan olarak "GRATIS"
            if (!result.brand) {
                result.brand = "GRATIS";
            }

            // Görsel - Gratis özel yapısı
            if (!result.image) {
                const imageSelectors = [
                    'meta[property="og:image"]',
                    'img[class*="product-image"]',
                    'img[class*="product__image"]',
                    'img[data-testid="product-image"]',
                    'img[alt*="product"]',
                    'img[src*="gratis"]',
                    'img[src*="cdn"]',
                    'img.product-image',
                    '.product-image img',
                    '.product__image img',
                    'img[src*="10208701"]' // Ürün kodu içeren görsel
                ];
                
                for (const selector of imageSelectors) {
                    try {
                        if (selector.startsWith('meta')) {
                            const meta = document.querySelector(selector);
                            if (meta && meta.content) {
                                result.image = meta.content;
                                break;
                            }
                        } else {
                            const img = document.querySelector(selector);
                            if (img) {
                                let src = img.getAttribute('src') || img.getAttribute('data-src') || img.getAttribute('data-lazy-src') || img.getAttribute('data-original');
                                if (src) {
                                    // Relative URL'yi absolute yap
                                    if (src.startsWith('//')) {
                                        src = 'https:' + src;
                                    } else if (src.startsWith('/')) {
                                        src = 'https://www.gratis.com' + src;
                                    }
                                    result.image = src;
                                    break;
                                }
                            }
                        }
                    } catch (e) {}
                }
            }

            return (result.title && result.price && result.image) ? result : null;
        } catch (e) {
            return null;
        }
    }''')

async def fetch_data(url):
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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            locale="tr-TR",
            timezone_id="Europe/Istanbul",

            extra_http_headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-User": "?1"
            } if "mango.com" in url else None
        )
        
        # Anti-detection scripts
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        await context.add_init_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        await context.add_init_script("Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR', 'tr', 'en-US', 'en']})")
        
        page = await context.new_page()
        
        # Apply stealth if available
        if Stealth:
            await Stealth().apply_stealth_async(page)

        try:
            logging.info(f"Navigating to {url}")
            
            # Adidas ve Zara için özel timeout ve wait stratejisi
            if "adidas.com" in url or "zara.com" in url or "vakkorama.com.tr" in url:
                await page.goto(url, wait_until="domcontentloaded", timeout=90000)
                try:
                    await page.wait_for_load_state("networkidle", timeout=30000)
                except:
                    pass
            else:
                await page.goto(url, wait_until="domcontentloaded", timeout=90000)
            
            page_title = await page.title()
            logging.info(f"Page Title: {page_title}")

            # Rastgele bekleme
            import random
            await page.wait_for_timeout(random.randint(3000, 7000))

            result = {
                "title": None,
                "price": None,
                "original_price": None,
                "discount_message": None,
                "image": None,
                "brand": None,
                "url": url
            }

            # 0. DeFacto ve LCW Özel Kontrolü
            if "defacto" in url:
                defacto_data = await extract_defacto_data(page)
                if defacto_data:
                    logging.info("DeFacto data found via DOM")
                    # Fiyat temizleme işlemi gerekebilir, ama JS tarafında hallettik
                    result.update(defacto_data)
                    if result["title"] and result["price"]:
                        return result

            if "lcw" in url:
                lcw_data = await extract_lcw_data(page)
                if lcw_data:
                    logging.info("LCW data found via window object")
                    result.update(lcw_data)
                    if result["title"] and result["price"]:
                        return result

            # 0.5. Mango Özel Kontrolü
            if "mango.com" in url:
                mango_data = await extract_mango_data(page)
                if mango_data:
                    logging.info("Mango data found via extractor")
                    result.update(mango_data)
                    if result["title"] and result["price"] and result["image"]:
                        return result

            # 0.6. Reflect Studio Özel Kontrolü
            if "reflectstudio.com" in url:
                reflect_data = await extract_reflectstudio_data(page)
                if reflect_data:
                    logging.info("Reflect Studio data found via extractor")
                    result.update(reflect_data)
                    if result["title"] and result["price"] and result["image"]:
                        return result

            # 0.7. D&R Özel Kontrolü
            if "dr.com.tr" in url:
                dr_data = await extract_dr_data(page)
                if dr_data:
                    logging.info("D&R data found via extractor")
                    result.update(dr_data)
                    if result["title"] and result["price"] and result["image"]:
                        return result

            # 0.8. Mavi Özel Kontrolü
            if "mavi.com" in url:
                mavi_data = await extract_mavi_data(page)
                if mavi_data:
                    logging.info("Mavi data found via extractor")
                    result.update(mavi_data)
                    if result["title"] and result["price"] and result["image"]:
                        return result

            # 0.9. LEGO.tr Özel Kontrolü
            if "lego.tr" in url:
                lego_data = await extract_lego_data(page)
                if lego_data:
                    logging.info("LEGO.tr data found via extractor")
                    result.update(lego_data)
                    if result["title"] and result["price"] and result["image"]:
                        return result

            # 0.10. Jerf.com.tr Özel Kontrolü
            if "jerf.com.tr" in url:
                jerf_data = await extract_jerf_data(page)
                if jerf_data:
                    logging.info("Jerf.com.tr data found via extractor")
                    result.update(jerf_data)
                    if result["title"] and result["price"] and result["image"]:
                        return result

            # 0.11. Vakkorama Özel Kontrolü
            if "vakkorama.com.tr" in url:
                vakkorama_data = await extract_vakkorama_data(page)
                if vakkorama_data:
                    logging.info("Vakkorama data found via extractor")
                    result.update(vakkorama_data)
                    if result["title"] and result["price"] and result["image"]:
                        return result

            # 0.12. Massimo Dutti Özel Kontrolü
            if "massimodutti.com" in url:
                massimodutti_data = await extract_massimodutti_data(page)
                if massimodutti_data:
                    logging.info("Massimo Dutti data found via extractor")
                    result.update(massimodutti_data)
                    if result["title"] and result["price"] and result["image"]:
                        return result

            # 0.13. Victoria's Secret Özel Kontrolü
            if "victoriassecret.com.tr" in url:
                victoriassecret_data = await extract_victoriassecret_data(page)
                if victoriassecret_data:
                    logging.info("Victoria's Secret data found via extractor")
                    result.update(victoriassecret_data)
                    if result["title"] and result["price"] and result["image"]:
                        return result

            # 0.14. Gratis Özel Kontrolü
            if "gratis.com" in url:
                gratis_data = await extract_gratis_data(page)
                if gratis_data:
                    logging.info("Gratis data found via extractor")
                    result.update(gratis_data)
                    if result["title"] and result["price"] and result["image"]:
                        return result

            # 1. Decathlon Özel Kontrolü
            if "decathlon" in url:
                decathlon_data = await extract_decathlon_data(page)
                if decathlon_data:
                    logging.info("Decathlon data found via window object")
                    result.update(decathlon_data)
                    # Decathlon verisi genelde tamdır, dönülebilir
                    if result["title"] and result["price"]:
                        return result
            
            # 2. Teknosa Özel Kontrolü
            if "teknosa" in url:
                teknosa_data = await extract_teknosa_data(page)
                if teknosa_data:
                    logging.info("Teknosa data found via window object")
                    # Mevcut result ile birleştir (None olmayanları al)
                    for k, v in teknosa_data.items():
                        if v: result[k] = v

            # 3. Boyner Özel Kontrolü
            if "boyner" in url:
                boyner_data = await extract_boyner_data(page)
                if boyner_data:
                    logging.info("Boyner data found via JSON-LD")
                    result.update(boyner_data)
                    if result["title"] and result["price"]:
                        return result

            # 4. Columbia Özel Kontrolü (DOM öncelikli)
            if "columbia.com.tr" in url:
                # DOM'dan "Sepette ... TL" içeren fiyatı bulmaya çalış
                try:
                    columbia_price = await page.evaluate('''() => {
                        const elements = document.querySelectorAll('div, span, p');
                        for (let el of elements) {
                            const text = el.innerText;
                            if (text.includes('Sepette') && text.includes('TL')) {
                                // "Sepette" kelimesinden sonra gelen fiyatı bul
                                const match = text.match(/Sepette.*?([\d\.,]+)\s*TL/);
                                if (match) return match[1] + " TL";
                            }
                        }
                        return null;
                    }''')
                    
                    if columbia_price:
                        result["price"] = columbia_price
                        logging.info(f"Columbia DOM price found: {result['price']}")
                except Exception as e:
                    logging.debug(f"Columbia DOM price extraction failed: {e}")
                
                # Eğer DOM'dan fiyat bulduysak, JSON-LD'yi sadece diğer veriler için kullan
                # Fiyatı ezmesine izin verme

            # 5. Reflect Studio Özel Kontrolü (Script Data)
            if "reflectstudio.com" in url:
                try:
                    # Shopify script verisinden fiyatı çekmeye çalış
                    reflect_price = await page.evaluate('''() => {
                        // ShopifyAnalytics.meta.product.variants[0].price
                        if (window.ShopifyAnalytics && window.ShopifyAnalytics.meta && window.ShopifyAnalytics.meta.product && window.ShopifyAnalytics.meta.product.variants) {
                            const variant = window.ShopifyAnalytics.meta.product.variants[0];
                            if (variant && variant.price) {
                                return (variant.price / 100).toFixed(2).replace('.', ',') + " TL";
                            }
                        }
                        // Alternatif: meta tag
                        const metaPrice = document.querySelector("meta[property='product:price:amount']");
                        if (metaPrice) return metaPrice.content + " TL";
                        
                        return null;
                    }''')
                    
                    if reflect_price:
                        result["price"] = reflect_price
                        logging.info(f"Reflect Studio script price found: {result['price']}")
                except Exception as e:
                    logging.debug(f"Reflect Studio script price extraction failed: {e}")

            # 6. Gratis Özel Kontrolü (Fiyat Formatlama)
            if "gratis.com" in url and result["price"] and result["price"].isdigit():
                # Gratis JSON-LD fiyatı kuruş cinsinden veya noktasız gelebiliyor (örn: 29900 -> 299.00)
                try:
                    price_val = float(result["price"])
                    if price_val > 1000: # Muhtemelen kuruş cinsinden
                        result["price"] = f"{price_val/100:.2f}".replace('.', ',') + " TL"
                except: pass


            # 3. JSON-LD Kontrolü (En güvenilir kaynak)
            json_data = await extract_jsonld(page)
            if json_data:
                logging.info("JSON-LD data found")
                if not result["title"]:
                    result["title"] = json_data.get("name")
                
                if not result["image"]:
                    img = json_data.get("image")
                    if isinstance(img, list):
                        result["image"] = img[0]
                    elif isinstance(img, dict):
                        result["image"] = img.get("url")
                    else:
                        result["image"] = img
                
                # Les Benjamins specific fix for malformed JSON-LD image
                if result["image"] and isinstance(result["image"], str):
                    if result["image"].startswith("https:files/"):
                        result["image"] = result["image"].replace("https:files/", "https://lesbenjamins.com/cdn/shop/files/")
                    elif result["image"].startswith("//"):
                        result["image"] = "https:" + result["image"]
                elif isinstance(result["image"], list) and len(result["image"]) > 0:
                     # If it's a list, take the first element and apply fixes if needed
                     img = result["image"][0]
                     if isinstance(img, str):
                        if img.startswith("https:files/"):
                            result["image"] = img.replace("https:files/", "https://lesbenjamins.com/cdn/shop/files/")
                        elif img.startswith("//"):
                            result["image"] = "https:" + img
                        else:
                            result["image"] = img
                
                if not result["price"]:
                    offers = json_data.get("offers")
                    if offers:
                        if isinstance(offers, list):
                            result["price"] = offers[0].get("price")
                        elif isinstance(offers, dict):
                            result["price"] = offers.get("price")
                            if offers.get("@type") == "AggregateOffer":
                                result["original_price"] = offers.get("highPrice")
                
                if not result["brand"]:
                    brand_data = json_data.get("brand")
                    if brand_data:
                        if isinstance(brand_data, dict):
                            result["brand"] = brand_data.get("name")
                        else:
                            result["brand"] = brand_data

            # 6. Gratis Özel Kontrolü (Fiyat Formatlama - JSON-LD sonrası)
            if "gratis.com" in url and result["price"]:
                try:
                    price_val = float(result["price"])
                    if price_val > 1000: 
                        result["price"] = f"{price_val/100:.2f}".replace('.', ',') + " TL"
                    else:
                        result["price"] = f"{price_val:.2f}".replace('.', ',') + " TL"
                except: pass

            # 4. Meta Tags / OG Tags Kontrolü
            if not result["title"] or not result["price"] or not result["image"]:
                meta_data = await extract_meta_tags(page)
                if meta_data:
                    if not result["title"] and meta_data.get("title"):
                        result["title"] = meta_data["title"]
                    if not result["image"] and meta_data.get("image"):
                        result["image"] = meta_data["image"]
                    if not result["price"] and meta_data.get("price"):
                        result["price"] = meta_data["price"]

            # 5. DOM Selectors (Site bazlı veya fallback)
            selectors = get_site_selectors(url)
            if not selectors:
                selectors = {
                    "title": [
                        "h1", 
                        "[data-testid='product-name']", 
                        ".product-name", 
                        ".product-title",
                        ".pdp-title",
                        "[itemprop='name']",
                        "title"
                    ],
                    "price": [
                        "[data-testid='price']", 
                        ".price", 
                        ".product-price", 
                        ".current-price",
                        ".sale-price",
                        ".amount",
                        "span[class*='price']",
                        "div[class*='price']",
                        "[itemprop='price']",
                        "[itemprop='lowPrice']",
                        "meta[itemprop='price']"
                    ],
                    "original_price": [
                        "del", 
                        ".old-price", 
                        ".original-price",
                        ".regular-price",
                        "[data-testid='original-price']", 
                        "span[class*='old-price']",
                        "s"
                    ],
                    "image": [
                        "img[itemprop='image']",
                        "img.product-image",
                        "img.main-image",
                        "[data-testid='product-image'] img",
                        "img[loading='lazy']", 
                        "img"
                    ],
                    "brand": ["UNKNOWN"]
                }
            else:
                if "original_price" not in selectors:
                    selectors["original_price"] = ["del", ".old-price", "[data-testid='original-price']", "span[class*='old-price']"]

            # Eksik verileri DOM'dan çekmeye çalış
            if not result["title"]:
                for sel in selectors["title"]:
                    try:
                        el = await page.query_selector(sel)
                        if el:
                            text = await el.inner_text()
                            if text:
                                result["title"] = text.strip()
                                break
                    except: continue

            if not result["price"]:
                for sel in selectors["price"]:
                    try:
                        el = await page.query_selector(sel)
                        if el:
                            text = await el.inner_text()
                            if text:
                                # Clean price text
                                cleaned_price = text.replace("TL", "").replace("TRY", "").replace("₺", "").strip()
                                if cleaned_price and any(char.isdigit() for char in cleaned_price) and len(cleaned_price) < 30:
                                    result["price"] = cleaned_price + " TL" if "TL" not in cleaned_price else cleaned_price
                                    break
                    except: continue
            
            # Original Price (İndirimsiz Fiyat) Arama
            if not result["original_price"]:
                for sel in selectors["original_price"]:
                    try:
                        el = await page.query_selector(sel)
                        if el:
                            text = await el.inner_text()
                            if text:
                                result["original_price"] = text.strip()
                                break
                    except: continue

            # Kampanya / Sepette İndirim Mesajı Arama (Geniş Kapsamlı)
            try:
                # Tüm sayfa metnini çek
                page_text = await page.evaluate("document.body.innerText")
                
                # Satır satır incele
                lines = page_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    lower_line = line.lower()
                    # Anahtar kelimeler: sepette, sepete özel, sepet fiyatı
                    if "sepette" in lower_line or "sepete özel" in lower_line:
                        # Çok uzun metinleri ele
                        if len(line) < 150:
                            # Eğer içinde rakam varsa (fiyat belirtiyorsa) daha değerli
                            if any(char.isdigit() for char in line):
                                result["discount_message"] = line
                                break
                            # Henüz mesaj bulamadıysak bunu tut
                            if not result["discount_message"]:
                                result["discount_message"] = line
            except Exception as e:
                logging.debug(f"Deep campaign extraction failed: {e}")

            if not result["image"]:
                for sel in selectors["image"]:
                    try:
                        el = await page.query_selector(sel)
                        if el:
                            src = await el.get_attribute("src")
                            if src:
                                result["image"] = src
                                break
                    except: continue

            if not result["brand"]:
                for sel in selectors.get("brand", []):
                    # Eğer selector bir CSS selector değil de direkt marka adıysa (örn: "ZARA")
                    # CSS selector karakterleri: . # [ ] > + :
                    if not any(c in sel for c in [".", "#", "[", "]", ">", "+", ":"]):
                        result["brand"] = sel
                        break
                        
                    try:
                        el = await page.query_selector(sel)
                        if el:
                            text = await el.inner_text()
                            if text:
                                # "Brand: Puma" gibi textleri temizle
                                clean_text = text.replace("Marka:", "").replace("Brand:", "").strip()
                                if clean_text:
                                    result["brand"] = clean_text
                                    break
                    except: continue

            if not result["brand"]:
                # Domain'den marka çıkar
                domain = urlparse(url).netloc
                if "amazon" in domain:
                    result["brand"] = "AMAZON"
                elif "trendyol" in domain:
                    result["brand"] = "TRENDYOL"
                elif "hepsiburada" in domain:
                    result["brand"] = "HEPSIBURADA"
                else:
                    result["brand"] = domain.replace("www.", "").split(".")[0].upper()

            # 7. Regex Fallback for Price (Universal)
            if not result["price"]:
                try:
                    # Sayfa metnini tekrar al (eğer yukarıda alınmadıysa veya hata verdiyse)
                    if 'page_text' not in locals():
                        page_text = await page.evaluate("document.body.innerText")
                    
                    # Regex ile fiyat ara: 1.234,56 TL veya 1234 TL veya 1234.56 TL
                    # Öncelik: TL simgesi olanlar
                    price_patterns = [
                        r'(?:(?:\d{1,3}(?:[.,]\d{3})*)|(?:\d+))(?:[.,]\d{2})?\s*(?:TL|TRY|₺)',
                        r'(?:TL|TRY|₺)\s*(?:(?:\d{1,3}(?:[.,]\d{3})*)|(?:\d+))(?:[.,]\d{2})?'
                    ]
                    
                    for pattern in price_patterns:
                        matches = re.findall(pattern, page_text)
                        if matches:
                            # İlk eşleşmeyi al (genelde ürün fiyatı sayfanın üst kısımlarındadır)
                            # Ancak bazen kargo bedeli vs. olabilir, bu yüzden basit bir heuristic:
                            # En sık tekrar eden fiyatı veya ilk fiyatı al.
                            # Şimdilik ilk fiyatı alıyoruz.
                            result["price"] = matches[0]
                            logging.info(f"Price found via Regex Fallback: {result['price']}")
                            break
                except Exception as e:
                    logging.debug(f"Regex price fallback failed: {e}")

            # Son Temizlik ve Formatlama
            if result["title"]:
                result["title"] = result["title"].strip().upper()
            
            if result["price"]:
                result["price"] = str(result["price"]).strip()
            
            if result["original_price"]:
                result["original_price"] = str(result["original_price"]).strip()
                if result["original_price"] == result["price"]:
                    result["original_price"] = None

            logging.info(f"Scraping result: {result}")
            return result

        except Exception as e:
            logging.error(f"Error scraping {url}: {e}")
            return None
        finally:
            await browser.close()

def scrape_product(url):
    """Main entry point - 3 deneme hakkı"""
    for i in range(3):
        try:
            logging.debug(f"Attempt {i+1}/3 - {url}")
            result = asyncio.run(fetch_data(url))
            if result and result.get("title"): # En azından başlık olmalı
                return result
        except Exception as e:
            logging.debug(f"Attempt {i+1} failed: {e}")
            # Son deneme değilse bekle
            if i < 2:
                import time
                time.sleep(2)
    
    logging.error(f"All attempts failed for {url}")
    return None
