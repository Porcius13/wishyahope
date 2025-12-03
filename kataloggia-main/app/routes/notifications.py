"""
Notifications routes
"""
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from models import Notification

bp = Blueprint('notifications', __name__)


@bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Get current user's notifications from the persistent table."""
    try:
        notifications = []
        unread_count = 0

        items = Notification.get_for_user(current_user.id, limit=50)

        for n in items:
            ts_str = str(n.created_at)
            is_read = n.read_at is not None
            if not is_read:
                unread_count += 1

            notifications.append({
                'id': n.id,
                'type': n.type.lower(),
                'message': n.message,
                'product_id': n.product_id,
                'timestamp': ts_str,
                'is_read': is_read,
            })

        return jsonify({
            'success': True,
            'notifications': notifications,
            'unread_count': unread_count,
        }), 200

    except Exception as e:
        print(f"[ERROR] Get notifications error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'notifications': [],
            'unread_count': 0,
        }), 500


@bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """Mark all current user's notifications as read."""
    try:
        # Update notifications table
        Notification.mark_all_read(current_user.id)

        # Backwards compatibility: also update users.last_read_notifications_at via repository-backed model
        now = datetime.now()
        current_user.last_read_notifications_at = now
        current_user.save()

        return jsonify({
            'success': True,
            'message': 'Tüm bildirimler okundu olarak işaretlendi.',
        }), 200

    except Exception as e:
        print(f"[ERROR] Mark all read error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
        }), 500

