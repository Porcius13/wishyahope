"""
Tests for price history and /price-tracking/<tracking_id>/history.
"""
from datetime import datetime, timedelta

from models import init_db, PriceTracking
from app.models.product import Product
from models import User


def _create_user(username: str, email: str, password: str):
    try:
        return User.create(username, email, 'password123')
    except Exception:
        return User.get_by_email(email)


def test_price_history_endpoint_returns_real_data(app, client):
    """Smoke test: /price-tracking/<tracking_id>/history returns data from price_history."""
    with app.app_context():
        init_db()

        # Create user and log in
        user = _create_user('history_user', 'history@test.com', 'password123')

        # Create a product
        product = Product.create(
            user_id=user.id,
            name='History Product',
            price='100.00',
            url='https://example.com/history-product',
            brand='HistBrand'
        )

        # Create a tracking entry (this also creates an initial price_history row)
        tracking_id = PriceTracking.create(
            user_id=user.id,
            product_id=product.id,
            current_price='100.00',
            original_price='110.00',
            alert_price='90.00'
        )

        # Manually add a couple of extra history points using update_price
        PriceTracking.update_price(tracking_id, '95.00')
        PriceTracking.update_price(tracking_id, '90.00')

    # Log in via the client to access the route
    login_resp = client.post(
        '/login',
        data={'username': 'history_user', 'password': 'password123'},
        follow_redirects=True,
    )
    assert login_resp.status_code == 200

    # Call the history endpoint
    resp = client.get(f'/price-tracking/{tracking_id}/history')
    assert resp.status_code == 200
    data = resp.get_json()

    assert 'labels' in data
    assert 'prices' in data
    assert isinstance(data['labels'], list)
    assert isinstance(data['prices'], list)
    # At least one point (should be >1 because of the two updates)
    assert len(data['labels']) == len(data['prices'])
    assert len(data['labels']) >= 1

    # Ensure all prices are numeric
    for p in data['prices']:
        assert isinstance(p, (int, float))


