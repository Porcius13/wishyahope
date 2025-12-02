"""
Profile routes
"""
from flask import Blueprint, render_template, request, session, flash, redirect, url_for, current_app
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
    """Ürün ekleme sorunları sayfası"""
    from models import ProductImportIssue
    issues = ProductImportIssue.get_by_user_id(current_user.id, limit=100)
    return render_template('profile_import_issues.html', user=current_user, issues=issues)


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
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # kataloggia-main/kataloggia-main
    project_root = os.path.dirname(app_root)  # üst dizin, static burada
    avatars_dir = os.path.join(project_root, 'static', 'avatars')
    os.makedirs(avatars_dir, exist_ok=True)

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

    file.save(avatar_path)

    # DB'de avatar_url'i güncelle (static içindeki göreli yol)
    avatar_rel_url = f"avatars/{avatar_filename}"
    user = User.get_by_id(current_user.id)
    if user:
        user.avatar_url = avatar_rel_url
        user.save()
        # current_user objesini de güncelle
        current_user.avatar_url = avatar_rel_url

    flash('Profil fotoğrafınız güncellendi', 'success')
    return redirect(url_for('profile.index'))
