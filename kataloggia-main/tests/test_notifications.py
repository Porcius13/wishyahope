"""
Tests for notifications and price history endpoints.
"""
import json

from models import Notification, init_db
from models import User


def _create_user(username: str, email: str, password: str):
    """Helper to create a user in the test database."""
    try:
        return User.create(username, email, password)
    except Exception:
        # If user already exists, fetch it
        return User.get_by_email(email)


def test_notification_create_get_mark_all_read(app):
    """Notification.create / get_for_user / mark_all_read basic flow."""
    with app.app_context():
        init_db()

        user = _create_user('notif_user', 'notif@test.com', 'password123')
        assert user is not None

        # Create notification
        notif_id = Notification.create(
            user_id=user.id,
            product_id=None,
            type='PRICE_DROP',
            message='Test drop',
            payload={'foo': 'bar'},
        )
        assert notif_id is not None

        # Fetch notifications
        items = Notification.get_for_user(user.id, limit=10)
        assert len(items) == 1
        n = items[0]
        assert n.type == 'PRICE_DROP'
        assert n.message == 'Test drop'
        assert n.read_at is None

        # Payload is stored as text; ensure it contains the key
        if n.payload:
            assert 'foo' in n.payload

        # Mark all as read
        Notification.mark_all_read(user.id)
        items_after = Notification.get_for_user(user.id, limit=10)
        assert len(items_after) == 1
        assert items_after[0].read_at is not None


def test_notifications_endpoints_flow(app, client):
    """Test /notifications and /notifications/mark-all-read endpoints."""
    with app.app_context():
        init_db()

        # Create user and log in via /auth/register
        username = 'notif_api_user'
        email = 'notif_api@test.com'
        password = 'password123'

        resp = client.post(
            '/auth/register',
            json={'username': username, 'email': email, 'password': password},
        )
        assert resp.status_code in (200, 201)

        # Login to establish session for browser-style endpoints
        login_resp = client.post(
            '/login',
            data={'username': username, 'password': password},
            follow_redirects=True,
        )
        assert login_resp.status_code == 200

        user = User.get_by_email(email)
        assert user is not None

        # Create a couple of notifications directly
        Notification.create(
            user_id=user.id,
            product_id=None,
            type='PRICE_DROP',
            message='Drop 1',
            payload={'seq': 1},
        )
        Notification.create(
            user_id=user.id,
            product_id=None,
            type='PRICE_DROP',
            message='Drop 2',
            payload={'seq': 2},
        )

    # Fetch notifications via API
    api_resp = client.get('/notifications')
    assert api_resp.status_code == 200
    data = api_resp.get_json()
    assert data['success'] is True
    assert 'notifications' in data
    assert 'unread_count' in data
    assert data['unread_count'] >= 2

    for item in data['notifications']:
        assert 'id' in item
        assert 'type' in item
        assert 'message' in item
        assert 'timestamp' in item
        assert 'product_id' in item
        assert 'is_read' in item

    # Mark all as read
    mark_resp = client.post('/notifications/mark-all-read')
    assert mark_resp.status_code == 200
    mark_data = mark_resp.get_json()
    assert mark_data['success'] is True

    # Fetch again - all should be read
    api_resp2 = client.get('/notifications')
    assert api_resp2.status_code == 200
    data2 = api_resp2.get_json()
    assert data2['success'] is True
    assert data2['unread_count'] == 0
    assert all(n['is_read'] for n in data2['notifications'])


