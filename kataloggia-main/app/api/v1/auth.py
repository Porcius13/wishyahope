"""
Authentication API endpoints
"""
from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.brute_force_protection import BruteForceProtection
from app.services.password_validator import PasswordValidator
from app.services.email_service import EmailService
from app.services.email_verification import EmailVerificationService
from app.utils.jwt_auth import JWTAuth, JWT_AVAILABLE
from app.middleware.security import SecurityMiddleware
from app.middleware.rate_limiter import rate_limit, get_remote_address

bp = Blueprint('auth', __name__)
auth_service = AuthService()

@bp.route('/login', methods=['GET'])
def login_page():
    """Login sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('login.html')

@bp.route('/login', methods=['POST'])
@rate_limit("5 per 15 minutes", key_func=lambda: f"login:{get_remote_address()}")
def login():
    """Login API with rate limiting and brute force protection"""
    try:
        # Debug: Check content type and get data
        content_type = request.content_type or ''
        print(f"[DEBUG] Content-Type: {content_type}")
        print(f"[DEBUG] Request method: {request.method}")
        print(f"[DEBUG] Request form: {dict(request.form)}")
        print(f"[DEBUG] Request JSON: {request.get_json(silent=True)}")
        
        # Check if this is a form submission (HTML form) or JSON request
        is_form_submission = request.form and not request.is_json
        
        # Try to get data from form first (for HTML forms), then JSON
        if request.form:
            data = request.form
        elif request.is_json:
            data = request.get_json()
        else:
            # Try to parse as form data
            data = request.form
        
        username = data.get('username')
        password = data.get('password')
        
        # Get client IP for brute force protection
        client_ip = get_remote_address()
        
        print(f"[DEBUG] Username: {username}, Password: {'*' * len(password) if password else 'None'}")
        print(f"[DEBUG] Is form submission: {is_form_submission}")
        
        if not username or not password:
            if is_form_submission:
                from flask import flash, redirect, url_for
                flash('Kullanıcı adı ve şifre gerekli', 'error')
                return redirect(url_for('auth.login_page'))
            return jsonify({
                'success': False,
                'error': 'Kullanıcı adı ve şifre gerekli'
            }), 400
        
        # Check brute force protection (before authentication)
        is_locked, lock_remaining = BruteForceProtection.is_locked(username=username, ip_address=client_ip)
        if is_locked:
            lock_minutes = lock_remaining // 60
            lock_seconds = lock_remaining % 60
            error_msg = f'Çok fazla başarısız giriş denemesi. Lütfen {lock_minutes} dakika {lock_seconds} saniye sonra tekrar deneyin.'
            
            if is_form_submission:
                from flask import flash, redirect, url_for
                flash(error_msg, 'error')
                return redirect(url_for('auth.login_page'))
            
            return jsonify({
                'success': False,
                'error': error_msg,
                'locked_until_seconds': lock_remaining
            }), 429
        
        user = auth_service.authenticate(username, password)
        print(f"[DEBUG] User found: {user is not None}")
        
        if user:
            # Clear failed attempts on successful login
            BruteForceProtection.clear_failed_attempts(username=username, ip_address=client_ip)
            
            remember = bool(data.get('remember', False)) or (data.get('remember') == '1')
            login_user(user, remember=remember)
            print(f"[DEBUG] User logged in: {user.username}")
            
            # Generate JWT token (optional, for API usage)
            jwt_token = None
            if JWT_AVAILABLE:
                jwt_token = JWTAuth.generate_token(user.id, user.username, user.email)
            
            # If it's a form submission (not AJAX), redirect to dashboard
            if is_form_submission:
                from flask import flash, redirect, url_for
                flash('Giriş başarılı!', 'success')
                return redirect(url_for('dashboard.index'))
            
            response_data = {
                'success': True,
                'message': 'Giriş başarılı',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }
            
            if jwt_token:
                response_data['token'] = jwt_token
            
            return jsonify(response_data), 200
        else:
            # Record failed attempt
            BruteForceProtection.record_failed_attempt(username=username, ip_address=client_ip)
            remaining_attempts = BruteForceProtection.get_remaining_attempts(username=username, ip_address=client_ip)
            
            print(f"[DEBUG] Authentication failed for username: {username}")
            
            error_msg = 'Kullanıcı adı veya şifre hatalı'
            if remaining_attempts < 3:
                error_msg += f'. Kalan deneme hakkı: {remaining_attempts}'
            
            # If it's a form submission, flash message and redirect
            if is_form_submission:
                from flask import flash, redirect, url_for
                flash(error_msg, 'error')
                return redirect(url_for('auth.login_page'))
            
            return jsonify({
                'success': False,
                'error': error_msg,
                'remaining_attempts': remaining_attempts
            }), 401
            
    except Exception as e:
        print(f"[ERROR] Login error: {e}")
        import traceback
        traceback.print_exc()
        
        # If it's a form submission, flash message and redirect
        is_form_submission = request.form and not request.is_json
        if is_form_submission:
            from flask import flash, redirect, url_for
            flash(f'Giriş hatası: {str(e)}', 'error')
            return redirect(url_for('auth.login_page'))
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/register', methods=['GET'])
def register_page():
    """Register sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('register.html')

@bp.route('/register', methods=['POST'])
@rate_limit("3 per hour", key_func=lambda: f"register:{get_remote_address()}")
def register():
    """Register API with rate limiting, password validation, and email verification"""
    try:
        # Debug: Check content type and get data
        content_type = request.content_type or ''
        print(f"[DEBUG] Register - Content-Type: {content_type}")
        print(f"[DEBUG] Register - Request form: {dict(request.form)}")
        print(f"[DEBUG] Register - Request JSON: {request.get_json(silent=True)}")
        
        # Try to get data from form first (for HTML forms), then JSON
        if request.form:
            data = request.form
        elif request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')  # For password confirmation
        
        is_form_submission = not request.is_json and content_type and 'application/json' not in content_type
        
        if not username or not email or not password:
            if is_form_submission:
                from flask import flash, redirect, url_for
                flash('Tüm alanlar gerekli', 'error')
                return redirect(url_for('auth.register_page'))
            
            return jsonify({
                'success': False,
                'error': 'Tüm alanlar gerekli'
            }), 400
        
        # Validate password confirmation (if provided)
        if confirm_password and not PasswordValidator.compare_passwords(password, confirm_password):
            if is_form_submission:
                from flask import flash, redirect, url_for
                flash('Şifreler eşleşmiyor', 'error')
                return redirect(url_for('auth.register_page'))
            
            return jsonify({
                'success': False,
                'error': 'Şifreler eşleşmiyor'
            }), 400
        
        # Validate email
        if not SecurityMiddleware.validate_email(email):
            if is_form_submission:
                from flask import flash, redirect, url_for
                flash('Geçersiz email formatı', 'error')
                return redirect(url_for('auth.register_page'))
            
            return jsonify({
                'success': False,
                'error': 'Geçersiz email formatı'
            }), 400
        
        # Validate password strength
        is_valid_password, password_errors = PasswordValidator.validate(password, username=username, email=email)
        if not is_valid_password:
            error_msg = 'Şifre gereksinimlerini karşılamıyor: ' + ', '.join(password_errors)
            if is_form_submission:
                from flask import flash, redirect, url_for
                flash(error_msg, 'error')
                return redirect(url_for('auth.register_page'))
            
            return jsonify({
                'success': False,
                'error': error_msg,
                'password_errors': password_errors
            }), 400
        
        # Sanitize inputs
        username = SecurityMiddleware.sanitize_input(username, max_length=50)
        email = SecurityMiddleware.sanitize_input(email, max_length=100)
        
        user = auth_service.register(username, email, password)
        
        if user:
            print(f"[DEBUG] User registered: {user.username}")
            
            # Auto-login after registration (email verification removed)
            remember = bool(data.get('remember', False)) or (data.get('remember') == '1')
            login_user(user, remember=remember)
            
            # Generate JWT token (optional, for API usage)
            jwt_token = None
            if JWT_AVAILABLE:
                jwt_token = JWTAuth.generate_token(user.id, user.username, user.email)
            
            if is_form_submission:
                from flask import redirect, url_for, flash
                flash('Kayıt başarılı! Hoş geldiniz.', 'success')
                return redirect(url_for('dashboard.index'))
            
            response_data = {
                'success': True,
                'message': 'Kayıt başarılı!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }
            
            if jwt_token:
                response_data['token'] = jwt_token
            
            return jsonify(response_data), 201
        else:
            if is_form_submission:
                from flask import flash, redirect, url_for
                flash('Kayıt başarısız. Kullanıcı adı veya email zaten kullanılıyor olabilir.', 'error')
                return redirect(url_for('auth.register_page'))
            
            return jsonify({
                'success': False,
                'error': 'Kayıt başarısız. Kullanıcı adı veya email zaten kullanılıyor olabilir.'
            }), 400
            
    except Exception as e:
        print(f"[ERROR] Register error: {e}")
        import traceback
        traceback.print_exc()
        
        is_form_submission = not request.is_json and content_type and 'application/json' not in content_type
        if is_form_submission:
            from flask import flash, redirect, url_for
            flash(f'Kayıt hatası: {str(e)}', 'error')
            return redirect(url_for('auth.register_page'))
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """Logout - hem API hem de basit link tıklaması için."""
    logout_user()

    # JSON bekleyen istekler için JSON cevap
    if request.is_json or request.method == 'POST':
        return jsonify({
            'success': True,
            'message': 'Çıkış başarılı'
        }), 200

    # Normal link tıklaması (GET) için dashboard / login sayfasına yönlendir
    from flask import redirect, url_for, flash
    flash('Çıkış yapıldı.', 'success')
    return redirect(url_for('main.index'))

@bp.route('/verify-email', methods=['GET'])
def verify_email():
    """Email verification endpoint"""
    try:
        token = request.args.get('token')
        
        if not token:
            return render_template('email_verification.html', 
                                 success=False, 
                                 message='Doğrulama tokenı bulunamadı')
        
        is_valid, user_id = EmailVerificationService.verify_token(token)
        
        if is_valid and user_id:
            return render_template('email_verification.html',
                                 success=True,
                                 message='Email adresiniz başarıyla doğrulandı! Artık giriş yapabilirsiniz.')
        else:
            return render_template('email_verification.html',
                                 success=False,
                                 message='Doğrulama tokenı geçersiz veya süresi dolmuş. Lütfen yeni bir doğrulama linki isteyin.')
            
    except Exception as e:
        print(f"[ERROR] Email verification error: {e}")
        return render_template('email_verification.html',
                             success=False,
                             message=f'Bir hata oluştu: {str(e)}')

@bp.route('/resend-verification', methods=['POST'])
@login_required
def resend_verification():
    """Resend email verification"""
    try:
        # Generate new token
        verification_token = EmailVerificationService.resend_verification_token(
            current_user.id, 
            current_user.email
        )
        
        # Send email
        base_url = request.url_root.rstrip('/')
        email_sent = EmailService.send_verification_email(
            current_user.email, 
            current_user.username, 
            verification_token, 
            base_url
        )
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': 'Doğrulama e-postası gönderildi'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'E-posta gönderilemedi'
            }), 500
            
    except Exception as e:
        print(f"[ERROR] Resend verification error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Mevcut kullanıcı bilgilerini getir"""
    return jsonify({
        'success': True,
        'data': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'email_verified': True  # Email verification disabled
        }
    }), 200
