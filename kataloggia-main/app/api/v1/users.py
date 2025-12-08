"""
Users API endpoints
"""
import json
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import User

bp = Blueprint('users', __name__)

@bp.route('/me', methods=['GET'])
@login_required
def get_profile():
    """Kullanıcı profil bilgileri"""
    return jsonify({
        'success': True,
        'data': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'created_at': current_user.created_at.isoformat() if hasattr(current_user.created_at, 'isoformat') else str(current_user.created_at)
        }
    }), 200

@bp.route('/me', methods=['PUT'])
@login_required
def update_profile():
    """Profil güncelle"""
    try:
        data = request.get_json()
        # Update logic here
        return jsonify({
            'success': True,
            'message': 'Profil güncellendi'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<user_id>/follow', methods=['POST'])
@login_required
def follow_user(user_id):
    """Kullanıcıyı takip et"""
    try:
        from app.repositories import get_repository
        from models import Notification
        from datetime import datetime
        
        if user_id == current_user.id:
            return jsonify({
                'success': False,
                'message': 'Kendinizi takip edemezsiniz'
            }), 400
        
        # Check if user exists
        target_user = User.get_by_id(user_id)
        if not target_user:
            return jsonify({
                'success': False,
                'message': 'Kullanıcı bulunamadı'
            }), 404
        
        repo = get_repository()
        success = repo.follow_user(current_user.id, user_id)
        
        if success:
            # Takip edilen kullanıcıya bildirim gönder
            try:
                notification_message = f"{current_user.username} sizi takip etmeye başladı"
                Notification.create(
                    user_id=user_id,
                    product_id=None,
                    type='follow',
                    message=notification_message,
                    payload=json.dumps({
                        'follower_id': current_user.id,
                        'follower_username': current_user.username
                    })
                )
            except Exception as notif_error:
                # Bildirim gönderme hatası işlemi durdurmamalı
                print(f"[WARNING] Failed to send follow notification: {notif_error}")
            
            return jsonify({
                'success': True,
                'message': 'Kullanıcı takip edildi'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Zaten takip ediliyor veya işlem başarısız'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<user_id>/unfollow', methods=['POST'])
@login_required
def unfollow_user(user_id):
    """Kullanıcıyı takipten çıkar"""
    try:
        from app.repositories import get_repository
        
        repo = get_repository()
        success = repo.unfollow_user(current_user.id, user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Takip bırakıldı'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Zaten takip edilmiyor'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<user_id>/follow-status', methods=['GET'])
@login_required
def get_follow_status(user_id):
    """Kullanıcıyı takip edip etmediğini kontrol et"""
    try:
        from app.repositories import get_repository
        
        repo = get_repository()
        is_following = repo.is_following(current_user.id, user_id)
        
        return jsonify({
            'success': True,
            'is_following': is_following
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/<user_id>/message', methods=['POST'])
@login_required
def send_message(user_id):
    """Kullanıcıya mesaj gönder (notification olarak)"""
    try:
        from app.repositories import get_repository
        from datetime import datetime
        from flask import current_app
        
        data = request.get_json()
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return jsonify({
                'success': False,
                'message': 'Mesaj boş olamaz'
            }), 400
        
        if user_id == current_user.id:
            return jsonify({
                'success': False,
                'message': 'Kendinize mesaj gönderemezsiniz'
            }), 400
        
        # Check if user exists
        target_user = User.get_by_id(user_id)
        if not target_user:
            return jsonify({
                'success': False,
                'message': 'Kullanıcı bulunamadı'
            }), 404
        
        repo = get_repository()
        notification_message = f"{current_user.username} size mesaj gönderdi: {message_text}"
        
        print(f"[DEBUG send_message] Sending message from {current_user.id} to {user_id}")
        print(f"[DEBUG send_message] Message text: {message_text[:50]}")
        
        # Alıcıya bildirim oluştur
        notification_id = repo.create_notification(
            user_id=user_id,
            product_id=None,
            notification_type='message',
            message=notification_message,
            payload=json.dumps({
                'from_user_id': current_user.id,
                'from_username': current_user.username,
                'to_user_id': user_id,
                'to_username': target_user.username,
                'message': message_text,
                'sent': False  # Bu alınan bir mesajdır
            }),
            created_at=datetime.now()
        )
        print(f"[DEBUG send_message] Created notification for receiver: {notification_id}")
        
        # Gönderene de kayıt oluştur (gönderdiği mesajları görebilmesi için)
        sender_notification_message = f"{target_user.username} kullanıcısına mesaj gönderdiniz: {message_text}"
        sender_notification_id = repo.create_notification(
            user_id=current_user.id,
            product_id=None,
            notification_type='message',
            message=sender_notification_message,
            payload=json.dumps({
                'from_user_id': current_user.id,
                'from_username': current_user.username,
                'to_user_id': user_id,
                'to_username': target_user.username,
                'message': message_text,
                'sent': True  # Bu mesajın gönderildiğini belirt
            }),
            created_at=datetime.now()
        )
        print(f"[DEBUG send_message] Created notification for sender: {sender_notification_id}")
        
        if notification_id and sender_notification_id:
            # SocketIO ile real-time bildirim gönder
            socketio = current_app.socketio if hasattr(current_app, 'socketio') else None
            if socketio:
                from app.services.notification_service import NotificationService
                notification_service = NotificationService(socketio)
                notification_service.send_notification(
                    user_id=user_id,
                    notification_type='message',
                    message=notification_message,
                    data={
                        'from_user_id': current_user.id,
                        'from_username': current_user.username,
                        'message': message_text,
                        'notification_id': notification_id
                    }
                )
            
            return jsonify({
                'success': True,
                'message': 'Mesaj gönderildi',
                'notification_id': notification_id,
                'sender_notification_id': sender_notification_id
            }), 200
        else:
            print(f"[ERROR send_message] Failed to create notifications. receiver_id={notification_id}, sender_id={sender_notification_id}")
            return jsonify({
                'success': False,
                'message': 'Mesaj gönderilemedi'
            }), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

