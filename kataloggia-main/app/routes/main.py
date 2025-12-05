"""
Main routes (public pages)
"""
from flask import Blueprint, render_template, redirect, url_for, abort
from flask_login import current_user
from models import Collection

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Ana sayfa"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('index.html')

@bp.route('/collection/<share_url>')
def public_collection(share_url):
    """Public koleksiyon görüntüleme (share_url ile)"""
    from models import User
    
    collection = Collection.get_by_share_url(share_url)
    
    if not collection:
        abort(404)
    
    # Sadece public koleksiyonlar görüntülenebilir
    if not collection.is_public:
        # Eğer kullanıcı koleksiyonun sahibiyse, yine de göster
        if not current_user.is_authenticated or collection.user_id != current_user.id:
            abort(404)
    
    # Get collection owner
    user = User.get_by_id(collection.user_id)
    
    # Get products in collection
    products = collection.get_products()
    
    # Format created_at for template
    collection_created_at_str = 'N/A'
    if collection.created_at:
        try:
            if hasattr(collection.created_at, 'strftime'):
                collection_created_at_str = collection.created_at.strftime('%d.%m.%Y')
            elif isinstance(collection.created_at, str):
                collection_created_at_str = collection.created_at[:10]
        except:
            collection_created_at_str = 'N/A'
    
    # Get like status and count
    is_liked = False
    likes_count = 0
    if current_user.is_authenticated:
        from app.repositories import get_repository
        repo = get_repository()
        is_liked = repo.is_collection_liked(current_user.id, collection.id)
        likes_count = repo.get_collection_likes_count(collection.id)
    else:
        from app.repositories import get_repository
        repo = get_repository()
        likes_count = repo.get_collection_likes_count(collection.id)
    
    return render_template('public_collection.html',
                         collection=collection,
                         products=products,
                         user=user,
                         collection_created_at_str=collection_created_at_str,
                         is_liked=is_liked,
                         likes_count=likes_count)


@bp.route('/proxy-image')
def proxy_image():
    """
    Mango gibi Referer kontrolü yapan siteler için resim proxy'si.
    Kullanım: /proxy-image?url=...
    """
    from flask import request, Response, stream_with_context
    import requests

    image_url = request.args.get('url')
    if not image_url:
        return "URL required", 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Mango için özel Referer
    if "mango.com" in image_url or "mngbcn.com" in image_url:
        headers["Referer"] = "https://shop.mango.com/"

    try:
        req = requests.get(image_url, headers=headers, stream=True, timeout=10)
        
        if req.status_code != 200:
            return f"Error fetching image: {req.status_code}", req.status_code

        return Response(
            stream_with_context(req.iter_content(chunk_size=1024)),
            content_type=req.headers.get('content-type', 'image/jpeg')
        )
    except Exception as e:
        return f"Proxy error: {str(e)}", 500
