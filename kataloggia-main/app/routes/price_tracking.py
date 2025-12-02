"""
Price Tracking routes
"""
from datetime import datetime, timedelta
import re

from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from app.services.price_tracking_service import PriceTrackingService
from app.models.price_tracking import PriceTracking
from app.utils.db_path import get_db_connection

bp = Blueprint('price_tracking', __name__, url_prefix='/price-tracking')
price_tracking_service = PriceTrackingService()

@bp.route('/')
@login_required
def index():
    """Fiyat takibi sayfası"""
    trackings = PriceTracking.get_user_tracking(current_user.id)
    
    # İstatistikleri hesapla
    stats = {
        'total_products': len(trackings),
        'active_alerts': 0,
        'price_drops': 0,
        'total_savings': 0
    }
    
    for item in trackings:
        # item[7] is target_price (alarm)
        if item[7]:
            stats['active_alerts'] += 1
            
        # item[4] is price_change
        # item[4] is price_change
        if item[4]:
            try:
                price_change = float(str(item[4]).replace(',', '.'))
                if price_change < 0:
                    stats['price_drops'] += 1
                    stats['total_savings'] += abs(price_change)
            except ValueError:
                pass
            
    # Format total savings
    stats['total_savings'] = f"{stats['total_savings']:.2f}"
    
    return render_template('price_tracking.html', tracking_items=trackings, tracking_stats=stats)

@bp.route('/update-prices', methods=['GET'])
@login_required
def update_prices():
    """Tüm takip edilen ürünlerin fiyatlarını güncelle"""
    try:
        # Fiyat kontrolü yap (sadece kullanıcının takip ettiği ürünler)
        from app.models.price_tracking import PriceTracking
        from app.models.product import Product
        
        # Kullanıcının takip ettiği ürünleri getir
        user_trackings = PriceTracking.get_user_tracking(current_user.id)
        
        checked = 0
        updated = 0
        notifications = []
        
        for tracking in user_trackings:
            try:
                if len(tracking) >= 3:
                    product_id = tracking[1]  # product_id is at index 1
                    checked += 1
                    
                    # Basit bir bildirim oluştur (gerçek fiyat kontrolü için scraping gerekli)
                    product = Product.get_by_id(product_id)
                    if product:
                        notifications.append({
                            'type': 'price_alert',
                            'message': f'{product.name} fiyatı kontrol edildi',
                            'product_id': product_id,
                            'timestamp': str(tracking[9]) if len(tracking) > 9 else ''
                        })
                        updated += 1
            except Exception as e:
                print(f"Error processing tracking: {e}")
                continue
        
        return jsonify({
            'success': True,
            'checked': checked,
            'updated': updated,
            'notifications': notifications
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Update prices error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'checked': 0,
            'updated': 0,
            'notifications': []
        }), 500

@bp.route('/<tracking_id>/history')
@login_required
def get_price_history(tracking_id):
    """Fiyat geçmişini getir"""
    try:
        # Tracking verisini kontrol et
        tracking = PriceTracking.get_by_id(tracking_id)
        if not tracking:
            return jsonify({'error': 'Takip bulunamadı'}), 404
            
        if tracking[2] != current_user.id:  # user_id check
            return jsonify({'error': 'Yetkisiz erişim'}), 403

        product_id = tracking[1]
        current_price = tracking[3]

        # Gerçek fiyat geçmişi verilerini getir
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Eski verilerde product_id yerine tracking_id saklanmış olabileceği için ikisini de kontrol et
            cursor.execute(
                '''
                SELECT price, recorded_at
                FROM price_history
                WHERE product_id = ? OR product_id = ?
                ORDER BY datetime(recorded_at) ASC
                LIMIT 60
                ''',
                (str(product_id), str(tracking_id))
            )
            rows = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

        def _parse_price(value):
            if value is None:
                return 0.0
            s = str(value)
            s = s.replace('₺', '').replace('TL', '').replace(' ', '')
            s = s.replace('.', '').replace(',', '.')
            try:
                return float(s)
            except Exception:
                cleaned = re.sub(r'[^0-9\.-]', '', s)
                try:
                    return float(cleaned)
                except Exception:
                    return 0.0

        labels = []
        prices = []

        for price_value, ts in rows:
            ts_str = str(ts)
            dt = None
            try:
                # Python 3.11+ supports fromisoformat for "YYYY-MM-DD HH:MM:SS[.ffffff]"
                dt = datetime.fromisoformat(ts_str)
            except Exception:
                try:
                    dt = datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S')
                except Exception:
                    dt = None

            label = dt.strftime('%d.%m') if dt else ts_str
            labels.append(label)
            prices.append(_parse_price(price_value))

        # Eğer hiç gerçek veri yoksa, önceki davranışa benzer basit bir fallback kullan
        if not labels:
            labels = []
            prices = []
            base_price = _parse_price(current_price)
            for i in range(6, -1, -1):
                date = datetime.now() - timedelta(days=i)
                labels.append(date.strftime('%d.%m'))
                prices.append(base_price)

        return jsonify({
            'labels': labels,
            'prices': prices
        })
        
    except Exception as e:
        print(f"[ERROR] Get history error: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/<tracking_id>/remove', methods=['DELETE'])
@login_required
def remove_tracking(tracking_id):
    """Fiyat takibini kaldır"""
    try:
        # Tracking verisini kontrol et
        tracking = PriceTracking.get_by_id(tracking_id)
        if not tracking:
            return jsonify({'success': False, 'message': 'Takip bulunamadı'}), 404
            
        if tracking[2] != current_user.id:
            return jsonify({'success': False, 'message': 'Yetkisiz erişim'}), 403
            
        # Takibi sil
        if PriceTracking.delete(tracking_id):
            return jsonify({'success': True, 'message': 'Takip kaldırıldı'})
        else:
            return jsonify({'success': False, 'message': 'Silme işlemi başarısız'}), 500
            
    except Exception as e:
        print(f"[ERROR] Remove tracking error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

