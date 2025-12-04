"""
Main routes (public pages)
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Ana sayfa"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('index.html')


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
