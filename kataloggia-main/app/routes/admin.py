"""
Admin Routes
"""
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.utils.db_path import get_db_connection

bp = Blueprint('admin', __name__)


@bp.route('/')
@login_required
def index():
    """Basit admin ana sayfası – kullanıcı listesine yönlendirir."""
    # TODO: Gerçek admin kontrolü (örn. current_user.is_admin) eklenebilir
    from flask import redirect, url_for
    return redirect(url_for('admin.users'))


@bp.route('/brands')
@login_required
def brands():
    """Admin Brands Page"""
    # TODO: Gerçek admin kontrolü eklenecek (ör. is_admin alanı)
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get unique brands and their product counts
    cursor.execute(
        '''
        SELECT brand, COUNT(*) as count
        FROM products
        GROUP BY brand
        ORDER BY brand ASC
        '''
    )
    brands_data = cursor.fetchall()
    conn.close()

    brands = [{'name': row[0], 'count': row[1]} for row in brands_data]

    return render_template('admin_brands.html', brands=brands, user=current_user)


@bp.route('/users')
@login_required
def users():
    """Basit kullanıcı listesi (admin görünümü)."""
    # TODO: Gerçek admin kontrolü (örn. current_user.is_admin) eklenebilir
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT id, username, email, created_at, profile_url
        FROM users
        ORDER BY datetime(created_at) DESC
        '''
    )
    rows = cursor.fetchall()
    conn.close()

    users = [
        {
            'id': row[0],
            'username': row[1],
            'email': row[2],
            'created_at': row[3],
            'profile_url': row[4],
        }
        for row in rows
    ]

    return render_template('admin_users.html', users=users, user=current_user)


@bp.route('/products')
@login_required
def products():
    """Basit ürün listesi (admin görünümü) ve hafif filtreler."""
    # TODO: Gerçek admin kontrolü eklenebilir
    conn = get_db_connection()
    cursor = conn.cursor()

    # Basit filtreler: q (isimde arama), brand, user_id
    q = request.args.get('q', '').strip()
    brand = request.args.get('brand', '').strip()
    user_id = request.args.get('user_id', '').strip()

    where_clauses = []
    params = []

    if q:
        where_clauses.append('p.name LIKE ?')
        params.append(f'%{q}%')
    if brand:
        where_clauses.append('p.brand = ?')
        params.append(brand)
    if user_id:
        where_clauses.append('p.user_id = ?')
        params.append(user_id)

    where_sql = ''
    if where_clauses:
        where_sql = 'WHERE ' + ' AND '.join(where_clauses)

    query = f'''
        SELECT p.id, p.name, p.brand, p.price, p.user_id, p.created_at, u.username
        FROM products p
        LEFT JOIN users u ON p.user_id = u.id
        {where_sql}
        ORDER BY datetime(p.created_at) DESC
        LIMIT 200
    '''
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Ayrı bir sorgu ile mevcut markaları al (filtre için)
    cursor.execute('SELECT DISTINCT brand FROM products ORDER BY brand ASC')
    brand_rows = cursor.fetchall()

    conn.close()

    products = [
        {
            'id': row[0],
            'name': row[1],
            'brand': row[2],
            'price': row[3],
            'user_id': row[4],
            'created_at': row[5],
            'username': row[6],
        }
        for row in rows
    ]

    brands = [b[0] for b in brand_rows]

    return render_template(
        'admin_products.html',
        products=products,
        brands=brands,
        filters={'q': q, 'brand': brand, 'user_id': user_id},
        user=current_user,
    )


@bp.route('/import-issues')
@login_required
def import_issues():
    """Tüm kullanıcılar için ürün import sorunlarını listeleyen basit admin görünümü."""
    # TODO: Gerçek admin kontrolü eklenebilir
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        '''
        SELECT pii.id,
               pii.user_id,
               u.username,
               pii.url,
               pii.status,
               pii.reason,
               pii.raw_data,
               pii.created_at
        FROM product_import_issues pii
        LEFT JOIN users u ON pii.user_id = u.id
        ORDER BY datetime(pii.created_at) DESC
        LIMIT 200
        '''
    )
    rows = cursor.fetchall()
    conn.close()

    issues = []
    for row in rows:
        issue_id, user_id, username, url, status, reason, raw_data, created_at = row

        # İnsan okunabilir açıklama üret
        reason_code = (reason or '').upper()
        if status == 'failed':
            if reason_code == 'SCRAPING_FAILED':
                reason_text = 'Scraper ürün sayfasını okuyamadı (SCRAPING_FAILED).'
            elif reason_code == 'PRODUCT_NAME_NOT_FOUND':
                reason_text = 'Ürün ismi bulunamadı; başlık/parça adı çekilemedi (PRODUCT_NAME_NOT_FOUND).'
            elif reason_code == 'URL_REQUIRED':
                reason_text = 'URL alanı boş bırakıldı (URL_REQUIRED).'
            elif reason_code == 'UNKNOWN_ERROR':
                reason_text = 'Bilinmeyen bir hata nedeniyle ürün eklenemedi (UNKNOWN_ERROR).'
            else:
                reason_text = reason or 'Bilinmeyen hata.'
        elif status == 'partial':
            # Gelecekte eksik alanları raw_data içine yazarsak burada detaylandırabiliriz
            reason_text = reason or 'Ürün eksik bilgiyle kaydedildi (PARTIAL).'
        else:
            reason_text = reason or 'Bilinmeyen durum.'

        issues.append(
            {
                'id': issue_id,
                'user_id': user_id,
                'username': username,
                'url': url,
                'status': status,
                'reason': reason,
                'reason_text': reason_text,
                'raw_data': raw_data,
                'created_at': created_at,
            }
        )

    return render_template(
        'admin_import_issues.html',
        issues=issues,
        user=current_user,
    )
