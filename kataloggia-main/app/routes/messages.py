"""
Messages routes
Mesaj görüntüleme ve yönetimi
"""
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user

from models import Notification
from app.repositories import get_repository

bp = Blueprint('messages', __name__)


@bp.route('/messages', methods=['GET'])
@login_required
def messages_page():
    """Mesajlar sayfası"""
    return render_template('messages.html')


@bp.route('/api/v1/messages/debug', methods=['GET'])
@login_required
def debug_messages():
    """Debug endpoint - tüm notification'ları göster"""
    try:
        notifications = Notification.get_for_user(current_user.id, limit=200)
        
        debug_info = {
            'user_id': current_user.id,
            'total_notifications': len(notifications),
            'notifications': []
        }
        
        for notif in notifications:
            payload_data = {}
            try:
                if notif.payload:
                    payload_data = json.loads(notif.payload)
            except:
                payload_data = {'raw': notif.payload}
            
            debug_info['notifications'].append({
                'id': notif.id,
                'type': notif.type,
                'type_lower': notif.type.lower() if notif.type else '',
                'message': notif.message[:100] if notif.message else None,
                'payload': payload_data,
                'created_at': str(notif.created_at),
                'read_at': str(notif.read_at) if notif.read_at else None
            })
        
        return jsonify(debug_info), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/api/v1/messages', methods=['GET'])
@login_required
def get_messages():
    """Kullanıcının mesajlarını getir (gruplandırılmış)"""
    try:
        repo = get_repository()
        
        # Tüm bildirimleri al (mesaj tipinde olanlar)
        print(f"[DEBUG get_messages] ========== START ==========")
        print(f"[DEBUG get_messages] Current user ID: {current_user.id}")
        print(f"[DEBUG get_messages] Fetching notifications...")
        
        try:
            notifications = Notification.get_for_user(current_user.id, limit=500)
            print(f"[DEBUG get_messages] Total notifications fetched: {len(notifications)}")
            
            # İlk birkaç notification'ın detaylarını göster
            for i, notif in enumerate(notifications[:5]):
                print(f"[DEBUG get_messages] Notification #{i}: ID={notif.id}, Type='{notif.type}', TypeLower='{notif.type.lower() if notif.type else None}'")
        except Exception as e:
            print(f"[ERROR get_messages] Failed to fetch notifications: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Failed to fetch notifications: {str(e)}',
                'conversations': [],
                'total_unread': 0
            }), 500
        
        # Tüm notification type'larını listele
        type_counts = {}
        for notif in notifications:
            notif_type = notif.type or 'None'
            type_counts[notif_type] = type_counts.get(notif_type, 0) + 1
        print(f"[DEBUG get_messages] Notification types: {type_counts}")
        print(f"[DEBUG get_messages] Looking for type='message' (case insensitive)")
        
        # Mesaj tipindeki notification sayısını kontrol et
        message_type_count = sum(1 for n in notifications if n.type and n.type.lower() == 'message')
        print(f"[DEBUG get_messages] Notifications with type='message': {message_type_count}")
        
        # Mesaj tipindeki bildirimleri filtrele ve grupla
        message_conversations = {}
        message_notifications_count = 0
        
        for notif in notifications:
            # Sadece mesaj tipindeki bildirimleri işle (case insensitive)
            notif_type_lower = notif.type.lower() if notif.type else ''
            
            # Type kontrolü - case insensitive
            if notif_type_lower == 'message':
                print(f"[DEBUG get_messages] Found MESSAGE notification: ID={notif.id}, Type='{notif.type}', Message preview: {notif.message[:50] if notif.message else 'None'}")
                message_notifications_count += 1
                print(f"[DEBUG get_messages] Found message notification #{message_notifications_count}")
                try:
                    payload = json.loads(notif.payload) if notif.payload else {}
                    from_user_id = payload.get('from_user_id')
                    from_username = payload.get('from_username', 'Bilinmeyen')
                    to_user_id = payload.get('to_user_id')
                    to_username = payload.get('to_username')
                    message_text = payload.get('message', '')
                    is_sent = payload.get('sent', False)  # Gönderilen mesaj mı?
                    
                    print(f"[DEBUG get_messages] Parsed payload: from={from_user_id}, to={to_user_id}, sent={is_sent}, text_len={len(message_text)}")
                    
                    # Eski mesaj formatı kontrolü: eğer sent flag'i yoksa ve to_user_id yoksa,
                    # bu alınan bir mesajdır (current_user bildirimi alan kullanıcı)
                    if 'sent' not in payload and not to_user_id:
                        is_sent = False
                    
                    # Konuşma partnerini belirle
                    # Eğer mesaj gönderildiyse (sent=True), partner alıcıdır (to_user_id)
                    # Eğer mesaj alındıysa, partner gönderendir (from_user_id)
                    partner_user_id = None
                    partner_username = None
                    
                    if is_sent:
                        # Bu mesajı gönderen kullanıcıyız, partner alıcıdır
                        partner_user_id = to_user_id
                        partner_username = to_username
                    else:
                        # Bu mesajı alan kullanıcıyız, partner gönderendir
                        partner_user_id = from_user_id
                        partner_username = from_username
                    
                    # Eğer partner bilgisi yoksa (eski mesajlar için), from_user_id'yi kullan
                    # Eski mesajlarda to_user_id yoktur, sadece from_user_id vardır
                    if not partner_user_id and from_user_id:
                        partner_user_id = from_user_id
                        partner_username = from_username
                    
                    if partner_user_id:
                        print(f"[DEBUG get_messages] Processing message: partner={partner_user_id}, sent={is_sent}, text={message_text[:30]}")
                        # Kullanıcıya göre grupla
                        if partner_user_id not in message_conversations:
                            message_conversations[partner_user_id] = {
                                'user_id': partner_user_id,
                                'username': partner_username or 'Bilinmeyen',
                                'messages': [],
                                'unread_count': 0,
                                'last_message_at': notif.created_at
                            }
                            print(f"[DEBUG get_messages] Created new conversation with {partner_user_id}")
                        
                        message_conversations[partner_user_id]['messages'].append({
                            'id': notif.id,
                            'text': message_text,
                            'from_user_id': from_user_id,
                            'from_username': from_username,
                            'to_user_id': to_user_id,
                            'to_username': to_username,
                            'sent': is_sent,  # Mesajın gönderilen mi alınan mı olduğunu ekle
                            'created_at': str(notif.created_at),
                            'is_read': notif.read_at is not None
                        })
                        print(f"[DEBUG get_messages] Added message to conversation {partner_user_id}, total messages: {len(message_conversations[partner_user_id]['messages'])}")
                        
                        # Okunmamış sayısını güncelle (sadece alınan mesajlar için)
                        if not is_sent and notif.read_at is None:
                            message_conversations[partner_user_id]['unread_count'] += 1
                        
                        # En son mesaj zamanını güncelle
                        if notif.created_at > message_conversations[partner_user_id]['last_message_at']:
                            message_conversations[partner_user_id]['last_message_at'] = notif.created_at
                    else:
                        print(f"[DEBUG get_messages] Skipping message - no partner_user_id. from_user_id={from_user_id}, to_user_id={to_user_id}, is_sent={is_sent}, current_user={current_user.id}")
                            
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"[WARNING] Error parsing message notification {notif.id}: {e}")
                    print(f"[WARNING] Payload content: {notif.payload[:200] if notif.payload else 'None'}")
                    import traceback
                    traceback.print_exc()
                    continue
        
        print(f"[DEBUG get_messages] ========== RESULTS ==========")
        print(f"[DEBUG get_messages] Total message notifications processed: {message_notifications_count}")
        print(f"[DEBUG get_messages] Total conversations found: {len(message_conversations)}")
        
        if message_notifications_count == 0:
            print(f"[WARNING get_messages] No message notifications found! Check:")
            print(f"[WARNING get_messages] 1. Are notifications being created with type='message'?")
            print(f"[WARNING get_messages] 2. Is the notification type stored correctly in DB?")
            print(f"[WARNING get_messages] 3. Are there any notifications for user {current_user.id}?")
        
        if len(message_conversations) == 0 and message_notifications_count > 0:
            print(f"[WARNING get_messages] Found {message_notifications_count} message notifications but 0 conversations!")
            print(f"[WARNING get_messages] This suggests a problem with partner_user_id detection.")
        
        # Her konuşmanın mesajlarını tarihe göre sırala (en yeni en üstte)
        for conv in message_conversations.values():
            conv['messages'].sort(key=lambda x: x['created_at'], reverse=True)
        
        # Konuşmaları en son mesaj zamanına göre sırala
        conversations_list = sorted(
            message_conversations.values(),
            key=lambda x: x['last_message_at'],
            reverse=True
        )
        
        print(f"[DEBUG get_messages] Final conversations count: {len(conversations_list)}")
        for conv in conversations_list:
            print(f"[DEBUG get_messages] Conversation: {conv['username']} ({conv['user_id']}), messages: {len(conv['messages'])}")
        
        return jsonify({
            'success': True,
            'conversations': conversations_list,
            'total_unread': sum(conv['unread_count'] for conv in conversations_list)
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get messages error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'conversations': [],
            'total_unread': 0
        }), 500


@bp.route('/api/v1/messages/<user_id>', methods=['GET'])
@login_required
def get_conversation(user_id):
    """Belirli bir kullanıcı ile olan konuşmayı getir"""
    try:
        repo = get_repository()
        
        # Tüm mesaj bildirimlerini al
        notifications = Notification.get_for_user(current_user.id, limit=200)
        
        # Bu kullanıcı ile olan tüm mesajları filtrele (hem gönderilen hem alınan)
        messages = []
        for notif in notifications:
            if notif.type.lower() == 'message':
                try:
                    payload = json.loads(notif.payload) if notif.payload else {}
                    from_user_id = payload.get('from_user_id')
                    to_user_id = payload.get('to_user_id')
                    is_sent = payload.get('sent', False)
                    
                    # Eski mesaj formatı kontrolü
                    if 'sent' not in payload and not to_user_id:
                        is_sent = False
                    
                    # Bu kullanıcı (user_id = konuşma partneri) ile ilgili mesajları bul
                    # user_id parametresi konuşma partnerinin id'sidir
                    message_related = False
                    message_is_sent = False
                    
                    if is_sent:
                        # Gönderilen mesaj: sent=True ve to_user_id == user_id (partner)
                        if to_user_id == user_id:
                            message_related = True
                            message_is_sent = True
                    else:
                        # Alınan mesaj: sent=False (veya yok) ve from_user_id == user_id (partner gönderen)
                        if from_user_id == user_id:
                            message_related = True
                            message_is_sent = False
                    
                    if message_related:
                        message_text = payload.get('message', '')
                        messages.append({
                            'id': notif.id,
                            'text': message_text,
                            'from_user_id': from_user_id,
                            'from_username': payload.get('from_username', 'Bilinmeyen'),
                            'to_user_id': to_user_id,
                            'to_username': payload.get('to_username'),
                            'sent': message_is_sent,  # Mesajın gönderilen mi alınan mı olduğunu ekle
                            'created_at': str(notif.created_at),
                            'is_read': notif.read_at is not None
                        })
                except (json.JSONDecodeError, KeyError):
                    continue
        
        # Mesajları tarihe göre sırala (en eski en üstte)
        messages.sort(key=lambda x: x['created_at'])
        
        # Kullanıcı bilgisini al
        from models import User
        target_user = User.get_by_id(user_id)
        username = target_user.username if target_user else 'Bilinmeyen'
        
        return jsonify({
            'success': True,
            'messages': messages,
            'user_id': user_id,
            'username': username
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Get conversation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'messages': []
        }), 500


@bp.route('/api/v1/messages/<user_id>/mark-read', methods=['POST'])
@login_required
def mark_conversation_read(user_id):
    """Belirli bir kullanıcıdan gelen tüm mesajları okundu olarak işaretle"""
    try:
        repo = get_repository()
        
        # Tüm mesaj bildirimlerini al
        notifications = Notification.get_for_user(current_user.id, limit=200)
        
        # Bu kullanıcıdan gelen okunmamış mesajları işaretle
        marked_count = 0
        for notif in notifications:
            if notif.type.lower() == 'message' and notif.read_at is None:
                try:
                    payload = json.loads(notif.payload) if notif.payload else {}
                    from_user_id = payload.get('from_user_id')
                    
                    if from_user_id == user_id:
                        # Bildirimi okundu olarak işaretle
                        if Notification.mark_read(notif.id):
                            marked_count += 1
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return jsonify({
            'success': True,
            'message': f'{marked_count} mesaj okundu olarak işaretlendi',
            'marked_count': marked_count
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Mark conversation read error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
