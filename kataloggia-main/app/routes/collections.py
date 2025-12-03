"""
Collection Routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.collection import Collection
from app.repositories import get_repository
import uuid

bp = Blueprint('collections_ui', __name__)

@bp.route('/')
@login_required
def index():
    """Koleksiyonları listele"""
    collections = Collection.get_user_collections(current_user.id)
    return render_template('collections/index.html', collections=collections)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Yeni koleksiyon oluştur"""
    if request.method == 'POST':
        from werkzeug.utils import secure_filename
        import os
        from flask import current_app
        
        name = request.form.get('name')
        description = request.form.get('description')

        # Yeni tasarımdaki form alanlarını oku
        # type: kombinler / favoriler ... (zorunlu)
        # privacy: public / private
        collection_type = request.form.get('type') or 'custom'
        privacy = request.form.get('privacy', 'public')
        is_public = (privacy == 'public')
        
        if not name:
            flash('Koleksiyon adı gerekli', 'error')
            return redirect(url_for('collections_ui.create'))
        
        # Kapak fotoğrafı yükleme
        cover_image_url = None
        cover_file = request.files.get('cover_image')
        if cover_file and cover_file.filename:
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            filename = secure_filename(cover_file.filename)
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
            
            if ext in allowed_extensions:
                static_folder = current_app.static_folder
                covers_dir = os.path.join(static_folder, 'collection_covers')
                os.makedirs(covers_dir, exist_ok=True)
                
                collection_id = str(uuid.uuid4())
                cover_filename = f"{collection_id}.{ext}"
                cover_path = os.path.join(covers_dir, cover_filename)
                
                cover_file.save(cover_path)
                cover_image_url = f"collection_covers/{cover_filename}"
            else:
                flash('Sadece PNG, JPG, JPEG, GIF veya WEBP formatları destekleniyor', 'error')
                return redirect(url_for('collections_ui.create'))
            
        try:
            Collection.create(
                user_id=current_user.id,
                name=name,
                description=description,
                type=collection_type,
                is_public=is_public,
                cover_image=cover_image_url
            )
            flash('Koleksiyon başarıyla oluşturuldu', 'success')
            return redirect(url_for('profile.collections'))
        except Exception as e:
            flash(f'Hata: {str(e)}', 'error')
            return redirect(url_for('collections_ui.create'))
            
    return render_template('collections/create.html')

@bp.route('/<collection_id>')
@login_required
def view(collection_id):
    """Koleksiyon detayını görüntüle"""
    collection = Collection.get_by_id(collection_id)
    if not collection or collection.user_id != current_user.id:
        flash('Koleksiyon bulunamadı', 'error')
        return redirect(url_for('profile.collections'))
        
    products = collection.get_products()
    return render_template('collections/view.html', collection=collection, products=products)

@bp.route('/<collection_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(collection_id):
    """Koleksiyonu düzenle"""
    collection = Collection.get_by_id(collection_id)
    if not collection or collection.user_id != current_user.id:
        flash('Koleksiyon bulunamadı', 'error')
        return redirect(url_for('profile.collections'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        collection_type = request.form.get('type') or collection.type
        privacy = request.form.get('privacy', 'public')
        is_public = (privacy == 'public')

        if not name:
            flash('Koleksiyon adı gerekli', 'error')
            return redirect(url_for('collections_ui.edit', collection_id=collection_id))

        try:
            repo = get_repository()
            success = repo.update_collection(
                collection_id,
                current_user.id,
                name=name,
                description=description,
                collection_type=collection_type,  # Firestore/SQLite use 'type' param name; we map below
                type=collection_type,
                is_public=is_public,
            )

            if not success:
                flash('Koleksiyon güncellenemedi', 'error')
                return redirect(url_for('collections_ui.edit', collection_id=collection_id))

            flash('Koleksiyon güncellendi', 'success')
            return redirect(url_for('profile.collections'))
        except Exception as e:
            print(f"[ERROR] Edit collection error: {e}")
            flash(f'Hata: {str(e)}', 'error')
            return redirect(url_for('collections_ui.edit', collection_id=collection_id))

    # GET
    return render_template('collections/edit.html', collection=collection)

@bp.route('/<collection_id>/add_product/<product_id>', methods=['POST'])
@login_required
def add_product(collection_id, product_id):
    """Koleksiyona ürün ekle"""
    try:
        collection = Collection.get_by_id(collection_id)
        if not collection or collection.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Koleksiyon bulunamadı'}), 404
            
        success = collection.add_product(product_id)
        if success:
            return jsonify({'success': True, 'message': 'Ürün koleksiyona eklendi'})
        else:
            return jsonify({'success': False, 'message': 'Ürün zaten koleksiyonda veya eklenemedi'})
            
    except Exception as e:
        print(f"[ERROR] Add to collection error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<collection_id>/remove_product/<product_id>', methods=['POST'])
@login_required
def remove_product(collection_id, product_id):
    """Koleksiyondan ürün çıkar"""
    try:
        collection = Collection.get_by_id(collection_id)
        if not collection or collection.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Koleksiyon bulunamadı'}), 404
            
        collection.remove_product(product_id)
        return jsonify({'success': True, 'message': 'Ürün koleksiyondan çıkarıldı'})
            
    except Exception as e:
        print(f"[ERROR] Remove from collection error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/<collection_id>/delete', methods=['POST'])
@login_required
def delete(collection_id):
    """Koleksiyonu sil"""
    try:
        collection = Collection.get_by_id(collection_id)
        if not collection or collection.user_id != current_user.id:
            flash('Koleksiyon bulunamadı', 'error')
            return redirect(url_for('profile.collections'))
            
        collection.delete()
        flash('Koleksiyon silindi', 'success')
        return redirect(url_for('profile.collections'))
            
    except Exception as e:
        print(f"[ERROR] Delete collection error: {e}")
        flash(f'Hata: {str(e)}', 'error')
        return redirect(url_for('profile.collections'))
