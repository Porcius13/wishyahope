"""
Dashboard routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.product import Product
from app.services.scraping_service import ScrapingService
from app.services.product_service import ProductService

bp = Blueprint('dashboard', __name__)
scraping_service = ScrapingService()
product_service = ProductService()

@bp.route('/dashboard')
@login_required
def index():
    """Dashboard ana sayfa"""
    products = Product.get_by_user_id(current_user.id)
    return render_template('dashboard.html', products=products)

@bp.route('/add_product', methods=['POST'])
@login_required
def add_product():
    """Ürün ekle (URL'den scrape ederek)"""
    try:
        from models import ProductImportIssue
        # Debug: Check what we're receiving
        print(f"[DEBUG] Request method: {request.method}")
        print(f"[DEBUG] Content-Type: {request.content_type}")
        print(f"[DEBUG] Request form: {dict(request.form)}")
        print(f"[DEBUG] Request JSON: {request.get_json(silent=True)}")
        print(f"[DEBUG] Request args: {dict(request.args)}")
        
        # Try multiple ways to get the URL
        product_url = None
        
        # Try form data first
        if request.form:
            product_url = request.form.get('product_url') or request.form.get('url')
        
        # Try JSON
        if not product_url and request.is_json:
            json_data = request.get_json(silent=True)
            if json_data:
                product_url = json_data.get('product_url') or json_data.get('url')
        
        # Try args (query parameters)
        if not product_url:
            product_url = request.args.get('product_url') or request.args.get('url')
        
        print(f"[DEBUG] Extracted product_url: {product_url}")
        
        if not product_url:
            error_msg = 'URL gerekli'
            # Kayıt altına al
            ProductImportIssue.create(
                user_id=current_user.id,
                url=product_url or '',
                status='failed',
                reason=error_msg
            )
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 400
            flash(error_msg, 'error')
            return redirect(url_for('dashboard.index'))
        
        # Hibrit yaklaşım: Önce DB'den kontrol et
        from models import Product
        from datetime import datetime, timedelta
        
        existing_product = Product.get_by_url(product_url)
        scraped_data = None
        should_scrape = True
        
        if existing_product:
            # Timestamp kontrolü - 24 saat içindeyse DB'den kullan
            created_at_dt = existing_product.created_at
            
            # Firestore Timestamp'i datetime'a çevir
            if hasattr(created_at_dt, 'timestamp'):
                # Firestore Timestamp object
                created_at_dt = created_at_dt.to_datetime() if hasattr(created_at_dt, 'to_datetime') else datetime.fromtimestamp(created_at_dt.timestamp())
            elif isinstance(created_at_dt, str):
                try:
                    created_at_dt = datetime.strptime(created_at_dt, '%Y-%m-%d %H:%M:%S.%f')
                except ValueError:
                    try:
                        created_at_dt = datetime.strptime(created_at_dt, '%Y-%m-%d %H:%M:%S')
                    except:
                        created_at_dt = datetime.now()
            
            if not isinstance(created_at_dt, datetime):
                created_at_dt = datetime.now()
            
            time_diff = datetime.now() - created_at_dt
            
            if time_diff < timedelta(hours=24):
                # DB'den kullan - 24 saat içinde
                print(f"[DEBUG] Using existing product from DB (age: {time_diff})")
                scraped_data = {
                    'name': existing_product.name,
                    'price': existing_product.price,
                    'image': existing_product.image,
                    'brand': existing_product.brand,
                    'url': existing_product.url,
                    'old_price': existing_product.old_price,
                    'current_price': existing_product.current_price,
                    'discount_percentage': existing_product.discount_percentage,
                    'images': existing_product.images,
                    'discount_message': existing_product.discount_info
                }
                should_scrape = False
            else:
                # 24 saatten eski, yeniden scrape et
                print(f"[DEBUG] Existing product is too old (age: {time_diff}), re-scraping...")
        
        # Eğer DB'de yoksa veya eskiyse scrape et
        if should_scrape:
            print(f"[DEBUG] Scraping URL: {product_url}")
            scraped_data = scraping_service.scrape_product(product_url)
            print(f"[DEBUG] Scraped data: {scraped_data}")
        
        if not scraped_data:
            # Buraya genelde fiyat veya GÖRSEL bulunamadığında düşüyoruz
            error_msg = (
                'Ürün bilgileri çekilemedi. Çoğu zaman ürün görseli veya fiyat bulunamadığında '
                'bu hata oluşur. Lütfen geçerli bir ürün linki girin.'
            )
            print(f"[ERROR] Scraping failed for URL (missing image/price/title?): {product_url}")
            ProductImportIssue.create(
                user_id=current_user.id,
                url=product_url,
                status='failed',
                reason=error_msg
            )
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 404
            flash(error_msg, 'error')
            return redirect(url_for('dashboard.index'))
        
        # Kritik alan kontrolleri - sadece bunlar hata kaydı oluşturur
        if not scraped_data.get('name'):
            error_msg = 'Ürün adı bulunamadı. Lütfen geçerli bir ürün URL\'si girin.'
            print(f"[ERROR] Product name not found in scraped data: {scraped_data}")
            ProductImportIssue.create(
                user_id=current_user.id,
                url=product_url,
                status='failed',
                reason=error_msg,
                raw_data=scraped_data
            )
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 404
            flash(error_msg, 'error')
            return redirect(url_for('dashboard.index'))
        
        if not scraped_data.get('price'):
            error_msg = 'Ürün fiyatı bulunamadı. Lütfen geçerli bir ürün URL\'si girin.'
            print(f"[ERROR] Product price not found in scraped data: {scraped_data}")
            ProductImportIssue.create(
                user_id=current_user.id,
                url=product_url,
                status='failed',
                reason=error_msg,
                raw_data=scraped_data
            )
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 404
            flash(error_msg, 'error')
            return redirect(url_for('dashboard.index'))
        
        if not scraped_data.get('image'):
            error_msg = 'Ürün görseli bulunamadı. Lütfen geçerli bir ürün URL\'si girin.'
            print(f"[ERROR] Product image not found in scraped data: {scraped_data}")
            ProductImportIssue.create(
                user_id=current_user.id,
                url=product_url,
                status='failed',
                reason=error_msg,
                raw_data=scraped_data
            )
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 404
            flash(error_msg, 'error')
            return redirect(url_for('dashboard.index'))
        
        # Marka kontrolü - UNKNOWN ise hata kaydı oluştur
        brand = scraped_data.get('brand', '').strip().upper()
        if not brand or brand == 'UNKNOWN':
            error_msg = 'Ürün markası bulunamadı veya UNKNOWN olarak listelendi.'
            print(f"[ERROR] Product brand is UNKNOWN or missing: {scraped_data.get('brand')}")
            ProductImportIssue.create(
                user_id=current_user.id,
                url=product_url,
                status='failed',
                reason=error_msg,
                raw_data=scraped_data
            )
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 404
            flash(error_msg, 'error')
            return redirect(url_for('dashboard.index'))

        # Ürünü oluştur
        product = product_service.create_product(
            user_id=current_user.id,
            name=scraped_data.get('name', 'Bilinmeyen Ürün'),
            price=scraped_data.get('price', '0'),
            image=scraped_data.get('image'),
            brand=scraped_data.get('brand', 'Bilinmeyen'),
            url=product_url,
            old_price=scraped_data.get('old_price'),
            current_price=scraped_data.get('price'),
            discount_percentage=scraped_data.get('discount_percentage'),
            images=scraped_data.get('images')
        )
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Ürün başarıyla eklendi',
                'data': product.to_dict() if hasattr(product, 'to_dict') else None
            }), 201
        
        flash('Ürün başarıyla eklendi!', 'success')
        return redirect(url_for('dashboard.index') + '?added=1')
        
    except Exception as e:
        print(f"[ERROR] Add product error: {e}")
        import traceback
        traceback.print_exc()

        # Beklenmeyen tüm hataları da problemli ürünler tablosuna yaz
        try:
            from models import ProductImportIssue
            ProductImportIssue.create(
                user_id=current_user.id if current_user and getattr(current_user, "id", None) else None,
                url=product_url or '',
                status='error',
                reason=str(e)[:500],
                raw_data=None
            )
        except Exception as log_err:
            print(f"[ERROR] Failed to create import issue for unexpected error: {log_err}")

        if request.is_json:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

        flash(f'Ürün eklenirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

@bp.route('/delete_product/<product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    """Ürün sil"""
    try:
        success = product_service.delete_product(product_id, current_user.id)
        
        if request.is_json:
            if success:
                return jsonify({'success': True, 'message': 'Ürün başarıyla silindi'}), 200
            else:
                return jsonify({'success': False, 'error': 'Ürün bulunamadı veya silinemedi'}), 404
        
        if success:
            flash('Ürün başarıyla silindi', 'success')
        else:
            flash('Ürün silinirken hata oluştu veya ürün bulunamadı', 'error')
            
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        print(f"[ERROR] Delete product error: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
            
        flash(f'Ürün silinirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

