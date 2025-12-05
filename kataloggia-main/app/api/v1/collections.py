"""
Collections API endpoints
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.collection_service import CollectionService

bp = Blueprint('collections', __name__)
collection_service = CollectionService()

@bp.route('', methods=['GET'])
@login_required
def get_collections():
    """Tüm koleksiyonları getir"""
    try:
        collections = collection_service.get_user_collections(current_user.id)
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in collections],
            'count': len(collections)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('', methods=['POST'])
@login_required
def create_collection():
    """Yeni koleksiyon oluştur"""
    try:
        data = request.get_json()
        
        collection = collection_service.create_collection(
            user_id=current_user.id,
            name=data.get('name'),
            description=data.get('description'),
            type=data.get('type', 'custom'),
            is_public=data.get('is_public', True)
        )
        
        return jsonify({
            'success': True,
            'data': collection.to_dict(),
            'message': 'Koleksiyon başarıyla oluşturuldu'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<collection_id>', methods=['GET'])
@login_required
def get_collection(collection_id):
    """Tek bir koleksiyonu getir"""
    try:
        collection = collection_service.get_collection(collection_id, current_user.id)
        if not collection:
            return jsonify({
                'success': False,
                'error': 'Koleksiyon bulunamadı'
            }), 404
        
        return jsonify({
            'success': True,
            'data': collection.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<collection_id>/products/<product_id>', methods=['POST'])
@login_required
def add_product_to_collection(collection_id, product_id):
    """Koleksiyona ürün ekle"""
    try:
        success = collection_service.add_product(
            collection_id=collection_id,
            product_id=product_id,
            user_id=current_user.id
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'İşlem başarısız'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Ürün koleksiyona eklendi'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<collection_id>/like', methods=['POST'])
@login_required
def like_collection(collection_id):
    """Koleksiyonu beğen"""
    try:
        from app.repositories import get_repository
        
        repo = get_repository()
        success = repo.like_collection(current_user.id, collection_id)
        
        if success:
            likes_count = repo.get_collection_likes_count(collection_id)
            return jsonify({
                'success': True,
                'message': 'Koleksiyon beğenildi',
                'likes_count': likes_count
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Zaten beğenilmiş veya işlem başarısız'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<collection_id>/unlike', methods=['POST'])
@login_required
def unlike_collection(collection_id):
    """Koleksiyon beğenisini kaldır"""
    try:
        from app.repositories import get_repository
        
        repo = get_repository()
        success = repo.unlike_collection(current_user.id, collection_id)
        
        if success:
            likes_count = repo.get_collection_likes_count(collection_id)
            return jsonify({
                'success': True,
                'message': 'Beğeni kaldırıldı',
                'likes_count': likes_count
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Zaten beğenilmemiş'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<collection_id>/like-status', methods=['GET'])
@login_required
def get_like_status(collection_id):
    """Koleksiyon beğeni durumunu kontrol et"""
    try:
        from app.repositories import get_repository
        
        repo = get_repository()
        is_liked = repo.is_collection_liked(current_user.id, collection_id)
        likes_count = repo.get_collection_likes_count(collection_id)
        
        return jsonify({
            'success': True,
            'is_liked': is_liked,
            'likes_count': likes_count
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<collection_id>/save-to-profile', methods=['POST'])
@login_required
def save_collection_to_profile(collection_id):
    """Koleksiyonu kendi profiline kaydet (kopyala)"""
    try:
        from app.repositories import get_repository
        from models import Collection
        from datetime import datetime
        import uuid
        
        # Get original collection
        original_collection = Collection.get_by_id(collection_id)
        if not original_collection:
            return jsonify({
                'success': False,
                'message': 'Koleksiyon bulunamadı'
            }), 404
        
        # Check if user already has this collection
        repo = get_repository()
        user_collections = repo.get_collections_by_user_id(current_user.id)
        for col in user_collections:
            if col.get('name') == original_collection.name and col.get('type') == original_collection.type:
                return jsonify({
                    'success': False,
                    'message': 'Bu koleksiyon zaten profilinizde mevcut'
                }), 400
        
        # Create new collection for current user (mark as copied)
        new_share_url = f"collection_{uuid.uuid4().hex[:8]}"
        
        # Mark as copied in description (prevent editing)
        # Use a more visible marker that's harder to remove
        copied_description = original_collection.description or ""
        if "[KOPYALANMIŞ]" not in copied_description:
            copied_description = f"[KOPYALANMIŞ-ORIGINAL-ID:{collection_id}] {copied_description}".strip()
        
        new_collection_id = repo.create_collection(
            user_id=current_user.id,
            name=original_collection.name,
            description=copied_description,
            collection_type=original_collection.type,
            is_public=True,
            share_url=new_share_url,
            created_at=datetime.now(),
            cover_image=original_collection.cover_image if hasattr(original_collection, 'cover_image') else None
        )
        
        if not new_collection_id:
            return jsonify({
                'success': False,
                'message': 'Koleksiyon oluşturulamadı'
            }), 500
        
        # Copy products from original collection
        original_products = original_collection.get_products()
        for product in original_products:
            repo.add_product_to_collection(new_collection_id, product.id)
        
        return jsonify({
            'success': True,
            'message': 'Koleksiyon profilinize kaydedildi',
            'collection_id': new_collection_id
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

