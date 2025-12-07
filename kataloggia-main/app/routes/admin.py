"""
Admin Routes
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
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
    """Admin Brands Page (Repository pattern)"""
    # TODO: Gerçek admin kontrolü eklenecek (ör. is_admin alanı)
    try:
        from app.repositories import get_repository
        
        repo = get_repository()
        
        # For now, return empty list - admin features can be enhanced later
        # To get all brands, we would need to iterate through all products
        # which is expensive. This can be optimized with a separate brands collection
        brands = []
        
        return render_template('admin_brands.html', brands=brands, user=current_user)
    except Exception as e:
        print(f"[ERROR] Admin brands error: {e}")
        return render_template('admin_brands.html', brands=[], user=current_user)


@bp.route('/users')
@login_required
def users():
    """Basit kullanıcı listesi (admin görünümü) - Repository pattern"""
    # TODO: Gerçek admin kontrolü (örn. current_user.is_admin) eklenebilir
    # TODO: Implement get_all_users in repository for admin features
    # For now, return empty list - admin features can be enhanced later
    users = []
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
    """Tüm kullanıcılar için ürün import sorunlarını listeleyen basit admin görünümü - Repository pattern"""
    # TODO: Gerçek admin kontrolü eklenebilir
    try:
        from app.repositories import get_repository
        
        repo = get_repository()
        issues_data = repo.get_all_import_issues(limit=200)
        
        issues = []
        for issue_data in issues_data:
            issue_id = issue_data.get('id')
            user_id = issue_data.get('user_id')
            username = issue_data.get('username', 'Unknown')
            url = issue_data.get('url')
            status = issue_data.get('status')
            reason = issue_data.get('reason')
            raw_data = issue_data.get('raw_data')
            created_at = issue_data.get('created_at')

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
                    'error_code': issue_data.get('error_code'),
                    'error_category': issue_data.get('error_category'),
                    'domain': issue_data.get('domain'),
                    'retry_count': issue_data.get('retry_count', 0),
                    'resolved': issue_data.get('resolved', False),
                    'last_retry_at': issue_data.get('last_retry_at'),
                }
            )
        
        return render_template(
            'admin_import_issues.html',
            issues=issues,
            user=current_user,
        )
    except Exception as e:
        print(f"[ERROR] Admin import issues error: {e}")
        return render_template('admin_import_issues.html', issues=[], user=current_user)


@bp.route('/import-issues/<issue_id>/delete', methods=['POST'])
@login_required
def delete_import_issue(issue_id):
    """Delete an import issue (admin can delete any issue)"""
    from app.repositories import get_repository
    from flask import jsonify
    
    repo = get_repository()
    # Admin can delete any issue, so we don't check user_id
    try:
        # Get the issue first to check if it exists
        all_issues = repo.get_all_import_issues(limit=10000)
        issue_exists = any(issue.get('id') == issue_id for issue in all_issues)
        
        if not issue_exists:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Hata kaydı bulunamadı'}), 404
            flash('Hata kaydı bulunamadı', 'error')
            return redirect(url_for('admin.import_issues'))
        
        # For admin, we need to get the user_id from the issue
        issue_data = next((issue for issue in all_issues if issue.get('id') == issue_id), None)
        if not issue_data:
            if request.is_json:
                return jsonify({'success': False, 'error': 'Hata kaydı bulunamadı'}), 404
            flash('Hata kaydı bulunamadı', 'error')
            return redirect(url_for('admin.import_issues'))
        
        user_id = issue_data.get('user_id')
        success = repo.delete_import_issue(issue_id, user_id)
        
        if request.is_json:
            if success:
                return jsonify({'success': True, 'message': 'Hata kaydı silindi'}), 200
            else:
                return jsonify({'success': False, 'error': 'Hata kaydı silinemedi'}), 500
        
        if success:
            flash('Hata kaydı başarıyla silindi', 'success')
        else:
            flash('Hata kaydı silinirken bir sorun oluştu', 'error')
        
        return redirect(url_for('admin.import_issues'))
    except Exception as e:
        print(f"[ERROR] Admin delete import issue error: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f'Hata kaydı silinirken bir sorun oluştu: {str(e)}', 'error')
        return redirect(url_for('admin.import_issues'))
