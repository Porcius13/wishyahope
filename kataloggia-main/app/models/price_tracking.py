"""
Price Tracking Model
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
from models import PriceTracking as BasePriceTracking

# Mevcut PriceTracking modelini kullan
PriceTracking = BasePriceTracking

# get_all_active method ekle (Repository pattern ile)
@classmethod
def get_all_active(cls):
    """Tüm aktif fiyat takiplerini getir (backend bağımsız, repository üzerinden)"""
    from app.repositories import get_repository

    repo = get_repository()
    trackings_data = repo.get_all_active_price_trackings()

    results = []
    for data in trackings_data:
        # Repo implementation'ı ne dönerse dönsün, beklenen alanları normalize et
        tracking_id = data.get('id')
        product_id = data.get('product_id')
        user_id = data.get('user_id')
        current_price = data.get('current_price')
        original_price = data.get('original_price')
        price_change = data.get('price_change', '0')
        is_active = data.get('is_active', True)
        alert_price = data.get('alert_price')
        created_at = data.get('created_at')
        last_checked = data.get('last_checked', created_at)

        results.append(
            cls(
                tracking_id,
                product_id,
                user_id,
                current_price,
                original_price,
                price_change,
                is_active,
                alert_price,
                created_at,
                last_checked,
            )
        )

    return results

BasePriceTracking.get_all_active = get_all_active
PriceTracking = BasePriceTracking

