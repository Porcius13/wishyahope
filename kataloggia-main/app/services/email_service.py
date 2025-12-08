"""
Email Service
Handles email sending for verification, password reset, etc.
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from flask import url_for, current_app

class EmailService:
    """Email sending service"""
    
    # Try to import external email libraries
    try:
        from flask_mail import Mail, Message
        MAIL_AVAILABLE = True
    except ImportError:
        MAIL_AVAILABLE = False
        print("[INFO] Flask-Mail yüklü değil, basit email gönderimi kullanılacak")
    
    @staticmethod
    def send_verification_email(user_email: str, username: str, verification_token: str, base_url: str = None) -> bool:
        """Send email verification email"""
        verification_url = f"{base_url or 'http://localhost:5000'}/auth/verify-email?token={verification_token}"
        
        subject = "Email Adresinizi Doğrulayın - miayis"
        body = f"""
Merhaba {username},

miayis'a hoş geldiniz! Hesabınızı aktifleştirmek için aşağıdaki bağlantıya tıklayın:

{verification_url}

Bu bağlantı 24 saat boyunca geçerlidir.

Eğer bu hesabı siz oluşturmadıysanız, bu e-postayı görmezden gelebilirsiniz.

İyi günler,
miayis Ekibi
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #000; color: #fff; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Email Adresinizi Doğrulayın</h2>
        <p>Merhaba {username},</p>
        <p>miayis'a hoş geldiniz! Hesabınızı aktifleştirmek için aşağıdaki butona tıklayın:</p>
        <a href="{verification_url}" class="button">Email'i Doğrula</a>
        <p>Ya da bu bağlantıyı tarayıcınıza kopyalayın:</p>
        <p style="word-break: break-all; color: #666; font-size: 12px;">{verification_url}</p>
        <p>Bu bağlantı 24 saat boyunca geçerlidir.</p>
        <p>Eğer bu hesabı siz oluşturmadıysanız, bu e-postayı görmezden gelebilirsiniz.</p>
        <div class="footer">
            <p>İyi günler,<br>miayis Ekibi</p>
        </div>
    </div>
</body>
</html>
        """
        
        return EmailService._send_email(user_email, subject, body, html_body)
    
    @staticmethod
    def send_password_reset_email(user_email: str, username: str, reset_token: str, base_url: str = None) -> bool:
        """Send password reset email"""
        reset_url = f"{base_url or 'http://localhost:5000'}/auth/reset-password?token={reset_token}"
        
        subject = "Şifre Sıfırlama - miayis"
        body = f"""
Merhaba {username},

Şifrenizi sıfırlamak için aşağıdaki bağlantıya tıklayın:

{reset_url}

Bu bağlantı 1 saat boyunca geçerlidir.

Eğer bu isteği siz yapmadıysanız, bu e-postayı görmezden gelebilirsiniz.

İyi günler,
miayis Ekibi
        """
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #000; color: #fff; text-decoration: none; border-radius: 4px; margin: 20px 0; }}
        .warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Şifre Sıfırlama</h2>
        <p>Merhaba {username},</p>
        <p>Şifrenizi sıfırlamak için aşağıdaki butona tıklayın:</p>
        <a href="{reset_url}" class="button">Şifreyi Sıfırla</a>
        <div class="warning">
            <strong>Önemli:</strong> Bu bağlantı 1 saat boyunca geçerlidir.
        </div>
        <p>Ya da bu bağlantıyı tarayıcınıza kopyalayın:</p>
        <p style="word-break: break-all; color: #666; font-size: 12px;">{reset_url}</p>
        <p>Eğer bu isteği siz yapmadıysanız, bu e-postayı görmezden gelebilirsiniz.</p>
        <div class="footer">
            <p>İyi günler,<br>miayis Ekibi</p>
        </div>
    </div>
</body>
</html>
        """
        
        return EmailService._send_email(user_email, subject, body, html_body)
    
    @staticmethod
    def _send_email(to_email: str, subject: str, text_body: str, html_body: Optional[str] = None) -> bool:
        """Send email using available method"""
        try:
            # Try Flask-Mail first
            if EmailService.MAIL_AVAILABLE:
                from flask import current_app
                from flask_mail import Mail, Message
                
                # This would need to be initialized in app factory
                # For now, fall back to simple SMTP
                pass
            
            # Try SMTP configuration
            smtp_host = os.environ.get('SMTP_HOST')
            smtp_port = int(os.environ.get('SMTP_PORT', '587'))
            smtp_user = os.environ.get('SMTP_USER')
            smtp_password = os.environ.get('SMTP_PASSWORD')
            smtp_from = os.environ.get('SMTP_FROM', smtp_user)
            
            if smtp_host and smtp_user and smtp_password:
                return EmailService._send_via_smtp(
                    to_email, subject, text_body, html_body,
                    smtp_host, smtp_port, smtp_user, smtp_password, smtp_from
                )
            
            # Fallback: Just log (for development)
            print(f"[EMAIL] ⚠️  SMTP ayarları bulunamadı - Email gönderilmeyecek!")
            print(f"[EMAIL] Alıcı: {to_email}")
            print(f"[EMAIL] Konu: {subject}")
            print(f"[EMAIL] Geliştirme modu: Email yerine sadece log basılıyor")
            print(f"[EMAIL] Email göndermek için .env dosyasına SMTP ayarlarını ekleyin")
            print(f"[EMAIL] Detaylar için: kataloggia-main/EMAIL_SETUP.md")
            return True  # Return True in development to not block registration
            
        except Exception as e:
            print(f"[ERROR] Email sending failed: {e}")
            return False
    
    @staticmethod
    def _send_via_smtp(to_email: str, subject: str, text_body: str, html_body: Optional[str],
                       smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str, smtp_from: str) -> bool:
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_from
            msg['To'] = to_email
            
            # Add text and HTML parts
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            msg.attach(part1)
            
            if html_body:
                part2 = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_from, [to_email], msg.as_string())
            
            print(f"[EMAIL] Verification email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"[ERROR] SMTP email sending failed: {e}")
            return False
