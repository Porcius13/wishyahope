"""
Notifications routes
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
from app.models.price_tracking import PriceTracking
from app.models.product import Product

bp = Blueprint('notifications', __name__)

@bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Kullanıcının bildirimlerini getir"""
    try:
        # Şimdilik basit bir bildirim listesi döndür
        # Gelecekte veritabanından çekilebilir
        notifications = []
        unread_count = 0
        
        # Kullanıcının son okuma zamanını al
        last_read_at = current_user.last_read_notifications_at
        if isinstance(last_read_at, str):
            try:
                last_read_at = datetime.strptime(last_read_at, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    last_read_at = datetime.strptime(last_read_at, '%Y-%m-%d %H:%M:%S')
                except:
                    last_read_at = None
        
        # Fiyat değişikliği bildirimleri
        trackings = PriceTracking.get_user_tracking(current_user.id)
        for tracking in trackings:
            # tracking is a tuple: (id, product_id, user_id, current_price, price_change, 
            #                      original_price, is_active, alert_price, created_at, last_checked,
            #                      product_name, product_brand, product_image)
            if len(tracking) >= 7 and tracking[6]:  # is_active check
                product_name = tracking[10] if len(tracking) > 10 else 'Ürün'
                price_change = tracking[4] or '0'
                try:
                    price_change_num = float(str(price_change).replace('₺', '').replace('TL', '').replace(',', '').strip())
                except:
                    price_change_num = 0
                
                # Timestamp parsing
                timestamp_str = str(tracking[9]) if len(tracking) > 9 else str(datetime.now())
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    try:
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    except:
                        timestamp = datetime.now()

                # is_read calculation
                is_read = False
                if last_read_at and timestamp <= last_read_at:
                    is_read = True
                
                notifications.append({
                    'id': tracking[0],
                    'type': 'price_drop' if price_change_num < 0 else 'price_increase',
                    'message': f'{product_name} fiyatı değişti',
                    'timestamp': timestamp_str,
                    'is_read': is_read
                })
                
                if not is_read:
                    unread_count += 1
        
        return jsonify({
            'success': True,
            'notifications': notifications[:20],  # Son 20 bildirim
            'unread_count': unread_count
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get notifications error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'notifications': [],
            'unread_count': 0
        }), 500

@bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """Tüm bildirimleri okundu işaretle"""
    try:
        import sqlite3
        conn = sqlite3.connect('favit.db')
        cursor = conn.cursor()
        
        now = datetime.now()
        cursor.execute('UPDATE users SET last_read_notifications_at = ? WHERE id = ?', (now, current_user.id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Tüm bildirimler okundu işaretlendi'
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Mark all read error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

