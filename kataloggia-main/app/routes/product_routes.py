"""
Product Routes
"""
from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.utils.db_path import get_db_connection

bp = Blueprint('product_routes', __name__)

@bp.route('/<product_id>/tracking-status')
@login_required
def get_tracking_status(product_id):
    """Get price tracking status for a product (Repository pattern)"""
    try:
        from app.repositories import get_repository
        
        repo = get_repository()
        tracking_data = repo.get_price_tracking_by_product_and_user(product_id, current_user.id)
        
        if tracking_data:
            return jsonify({
                'is_tracking': tracking_data.get('is_active', True),
                'last_checked': tracking_data.get('last_checked'),
                'current_price': tracking_data.get('current_price'),
                'original_price': tracking_data.get('original_price'),
                'price_change': tracking_data.get('price_change', '0')
            })
        else:
            return jsonify({
                'is_tracking': False,
                'last_checked': None,
                'current_price': None,
                'original_price': None,
                'price_change': 0
            })
            
    except Exception as e:
        print(f"[ERROR] Get tracking status error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/<product_id>/add-to-tracking', methods=['POST'])
@login_required
def add_to_tracking(product_id):
    """Add product to price tracking (Repository pattern)"""
    try:
        from app.models.product import Product
        from models import PriceTracking

        # Check if product exists
        product = Product.get_by_id(product_id)
        if not product:
            return jsonify({'success': False, 'message': 'Ürün bulunamadı'}), 404

        # Check if already tracking
        existing = PriceTracking.get_by_product_and_user(product_id, current_user.id)
        if existing:
            # Idempotent davran: zaten takipteyse 200 dön ve mesaj ver
            return jsonify({'success': True, 'message': 'Bu ürün zaten takip ediliyor'}), 200

        # Create tracking
        print(f"[DEBUG add_to_tracking] Creating tracking for product: {product_id}, user: {current_user.id}")
        tracking_id = PriceTracking.create(
            user_id=current_user.id,
            product_id=product_id,
            current_price=product.price,
            original_price=product.price
        )
        print(f"[DEBUG add_to_tracking] Tracking created: {tracking_id}")

        return jsonify({'success': True, 'message': 'Fiyat takibi başlatıldı'})

    except Exception as e:
        print(f"[ERROR] Add to tracking error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<product_id>/remove-from-tracking', methods=['POST'])
@login_required
def remove_from_tracking(product_id):
    """Remove product from price tracking (Repository pattern)"""
    try:
        from models import PriceTracking

        # Check if tracking exists
        existing = PriceTracking.get_by_product_and_user(product_id, current_user.id)
        if not existing:
            return jsonify({'success': False, 'message': 'Takip kaydı bulunamadı'}), 404

        # Remove tracking (existing is a tuple, id is at index 0)
        tracking_id = existing[0]
        print(f"[DEBUG remove_from_tracking] Removing tracking: {tracking_id}")
        result = PriceTracking.remove_tracking(tracking_id)
        print(f"[DEBUG remove_from_tracking] Result: {result}")

        if result:
            return jsonify({'success': True, 'message': 'Fiyat takibi durduruldu'})
        else:
            return jsonify({'success': False, 'message': 'Takip durdurulamadı'}), 500

    except Exception as e:
        print(f"[ERROR] Remove from tracking error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<product_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(product_id):
    """Toggle favorite status for a product"""
    try:
        from models import Favorite
        
        # Check current status
        is_favorite = Favorite.check_favorite(current_user.id, product_id)
        
        if is_favorite:
            # Remove from favorites
            success = Favorite.delete(current_user.id, product_id)
            message = 'Favorilerden çıkarıldı'
            action = 'removed'
        else:
            # Add to favorites
            success = Favorite.create(current_user.id, product_id)
            message = 'Favorilere eklendi'
            action = 'added'
            
        if success:
            return jsonify({
                'success': True, 
                'message': message,
                'action': action,
                'is_favorite': not is_favorite
            })
        else:
            return jsonify({'success': False, 'message': 'İşlem başarısız'}), 500
            
    except Exception as e:
        print(f"[ERROR] Toggle favorite error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
