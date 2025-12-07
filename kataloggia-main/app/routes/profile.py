"""
Profile routes
"""
from flask import Blueprint, render_template, request, session, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os

# DİKKAT: url_prefix BURAYA YAZMIYORUZ!
bp = Blueprint('profile', __name__)

@bp.route('/')
@login_required
def index():
    """Profil ana sayfa"""
    return render_template('profile.html', user=current_user)

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Profil ayarları (kullanıcı adı, e-posta, şifre)"""
    from models import User

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()

        # Kullanıcı adı güncelle
        if username and username != current_user.username:
            existing_user = User.get_by_username(username)
            if existing_user and existing_user.id != current_user.id:
                flash("Bu kullanıcı adı zaten kullanılıyor", "error")
            else:
                current_user.username = username
                current_user.save()
                flash("Kullanıcı adı güncellendi", "success")

        # E-posta güncelle
        if email and email != current_user.email:
            existing_email_user = User.get_by_email(email)
            if existing_email_user and existing_email_user.id != current_user.id:
                flash("Bu e-posta adresi zaten kullanılıyor", "error")
            else:
                current_user.email = email
                current_user.save()
                flash("E-posta adresi güncellendi", "success")

        # Şifre güncelle
        if current_password or new_password:
            if not current_password or not new_password:
                flash("Şifre değiştirmek için mevcut ve yeni şifreyi birlikte girin", "error")
            else:
                if current_user.check_password(current_password):
                    current_user.set_password(new_password)
                    current_user.save()
                    flash("Şifre güncellendi", "success")
                else:
                    flash("Mevcut şifre yanlış", "error")

        return redirect(url_for('profile.settings'))

    return render_template('profile_settings.html', user=current_user)

@bp.route('/collections')
@login_required
def collections():
    """Kullanıcı koleksiyonları"""
    collections = current_user.get_collections()
    return render_template('profile_collections.html', user=current_user, collections=collections)

@bp.route('/favorites')
@login_required
def favorites():
    """Favoriler sayfası"""
    from models import Favorite
    products = Favorite.get_user_favorites(current_user.id)
    return render_template('profile_favorites.html', user=current_user, products=products)

@bp.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    """Kullanıcı tercihleri sayfası"""
    if request.method == 'POST':
        theme = request.form.get('theme', 'light')
        language = request.form.get('language', 'tr')
        notifications = request.form.get('notifications', 'off') == 'on'

        # Tercihleri session'da sakla (ileride DB'ye taşınabilir)
        session['user_theme'] = theme
        session['user_language'] = language
        session['user_notifications'] = notifications

        flash('Tercihleriniz güncellendi', 'success')
        return redirect(url_for('profile.preferences'))

    return render_template('profile_preferences.html', user=current_user)

@bp.route('/tracking')
@login_required
def tracking():
    """Fiyat takip özeti sayfası"""
    return render_template('profile_tracking.html', user=current_user)

@bp.route('/import-issues')
@login_required
def import_issues():
    """Ürün ekleme sorunları sayfası - gelişmiş filtreleme ve istatistiklerle"""
    from models import ProductImportIssue
    from flask import request
    from app.repositories import get_repository
    
    # Filtreleme parametreleri
    status_filter = request.args.get('status', 'all')  # all, failed, partial, resolved
    domain_filter = request.args.get('domain', '')
    error_category_filter = request.args.get('error_category', '')
    limit = int(request.args.get('limit', 100))
    
    # Tüm issue'ları al
    all_issues = ProductImportIssue.get_by_user_id(current_user.id, limit=1000)
    
    # Filtreleme
    filtered_issues = all_issues
    if status_filter != 'all':
        filtered_issues = [i for i in filtered_issues if i.status == status_filter]
    if domain_filter:
        domain_lower = domain_filter.lower()
        filtered_issues = [i for i in filtered_issues if hasattr(i, 'domain') and i.domain and domain_lower in i.domain.lower()]
    if error_category_filter:
        filtered_issues = [i for i in filtered_issues if hasattr(i, 'error_category') and i.error_category == error_category_filter]
    
    # Limit uygula
    filtered_issues = filtered_issues[:limit]
    
    # İstatistikler hesapla
    stats = {
        'total': len(all_issues),
        'failed': len([i for i in all_issues if i.status == 'failed']),
        'partial': len([i for i in all_issues if i.status == 'partial']),
        'resolved': len([i for i in all_issues if hasattr(i, 'resolved') and getattr(i, 'resolved', False)]),
        'by_domain': {},
        'by_error_category': {}
    }
    
    for issue in all_issues:
        # Domain istatistikleri
        if hasattr(issue, 'domain') and issue.domain:
            stats['by_domain'][issue.domain] = stats['by_domain'].get(issue.domain, 0) + 1
        
        # Error category istatistikleri
        if hasattr(issue, 'error_category') and issue.error_category:
            stats['by_error_category'][issue.error_category] = stats['by_error_category'].get(issue.error_category, 0) + 1
    
    return render_template('profile_import_issues.html', 
                         user=current_user, 
                         issues=filtered_issues,
                         stats=stats,
                         status_filter=status_filter,
                         domain_filter=domain_filter,
                         error_category_filter=error_category_filter)


@bp.route('/import-issues/<issue_id>/delete', methods=['POST'])
@login_required
def delete_import_issue(issue_id):
    """Delete an import issue"""
    from app.repositories import get_repository
    
    repo = get_repository()
    success = repo.delete_import_issue(issue_id, current_user.id)
    
    if request.is_json:
        if success:
            return jsonify({'success': True, 'message': 'Hata kaydı silindi'}), 200
        else:
            return jsonify({'success': False, 'error': 'Hata kaydı silinemedi veya bulunamadı'}), 404
    
    if success:
        flash('Hata kaydı başarıyla silindi', 'success')
    else:
        flash('Hata kaydı silinirken bir sorun oluştu', 'error')
    
    return redirect(url_for('profile.import_issues'))


@bp.route('/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Profil resmi yükleme/güncelleme"""
    from models import User

    file = request.files.get('avatar')
    if not file or file.filename == '':
        flash('Lütfen bir resim dosyası seçin', 'error')
        return redirect(url_for('profile.index'))

    # Basit mime/type kontrolü
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in allowed_extensions:
        flash('Sadece PNG, JPG, JPEG, GIF veya WEBP formatları destekleniyor', 'error')
        return redirect(url_for('profile.index'))

    # Kayıt yolu: static/avatars/<user_id>.<ext>
    # Flask'ın static_folder'ını kullan (app/__init__.py'de tanımlı)
    static_folder = current_app.static_folder
    avatars_dir = os.path.join(static_folder, 'avatars')
    os.makedirs(avatars_dir, exist_ok=True)
    print(f"[DEBUG] Static folder: {static_folder}")
    print(f"[DEBUG] Avatars directory: {avatars_dir}")

    avatar_filename = f"{current_user.id}.{ext}"
    avatar_path = os.path.join(avatars_dir, avatar_filename)

    # Önceki avatarı (farklı uzantıda olabilir) temizle
    for old_ext in allowed_extensions:
        old_path = os.path.join(avatars_dir, f"{current_user.id}.{old_ext}")
        if os.path.exists(old_path) and old_path != avatar_path:
            try:
                os.remove(old_path)
            except OSError:
                pass

    try:
        file.save(avatar_path)
        print(f"[DEBUG] Avatar dosyası kaydedildi: {avatar_path}")
    except Exception as e:
        print(f"[ERROR] Avatar dosyası kaydedilemedi: {e}")
        flash('Dosya kaydedilemedi. Lütfen tekrar deneyin.', 'error')
        return redirect(url_for('profile.index'))

    # DB'de avatar_url'i güncelle (static içindeki göreli yol)
    avatar_rel_url = f"avatars/{avatar_filename}"
    user = User.get_by_id(current_user.id)
    if user:
        user.avatar_url = avatar_rel_url
        try:
            user.save()
            print(f"[DEBUG] Avatar URL veritabanında güncellendi: {avatar_rel_url}")
        except Exception as e:
            print(f"[ERROR] Avatar URL veritabanında güncellenemedi: {e}")
            flash('Profil fotoğrafı kaydedildi ancak veritabanında güncellenemedi.', 'error')
            return redirect(url_for('profile.index'))
        # current_user objesini de güncelle
        current_user.avatar_url = avatar_rel_url
    else:
        print(f"[ERROR] Kullanıcı bulunamadı: {current_user.id}")
        flash('Kullanıcı bilgisi bulunamadı.', 'error')
        return redirect(url_for('profile.index'))

    flash('Profil fotoğrafınız güncellendi', 'success')
    return redirect(url_for('profile.index'))
