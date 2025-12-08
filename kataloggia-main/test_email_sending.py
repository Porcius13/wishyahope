"""
Email Gönderim Test Scripti
Test kaydı oluşturur ve email gönderimini test eder
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import secrets

# Project root'u bul
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
dotenv_path = parent_dir / '.env'

# .env dosyasını yükle
try:
    from dotenv import load_dotenv
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
        print(f"✅ .env dosyası yüklendi")
    else:
        print(f"❌ .env dosyası bulunamadı: {dotenv_path}")
        sys.exit(1)
except ImportError:
    print("❌ python-dotenv yüklü değil. 'pip install python-dotenv' çalıştırın")
    sys.exit(1)

# Path'i ayarla
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(parent_dir))

print("=" * 60)
print("🧪 Email Gönderim Testi")
print("=" * 60)
print()

# SMTP ayarlarını kontrol et
smtp_host = os.environ.get('SMTP_HOST')
smtp_user = os.environ.get('SMTP_USER')
smtp_password = os.environ.get('SMTP_PASSWORD')

if not all([smtp_host, smtp_user, smtp_password]):
    print("❌ SMTP ayarları eksik!")
    print("   Lütfen .env dosyasında SMTP ayarlarını yapın")
    sys.exit(1)

print(f"📧 SMTP Ayarları:")
print(f"   Host: {smtp_host}")
print(f"   User: {smtp_user}")
print(f"   Password: {'*' * len(smtp_password)}")
print()

# Test email adresi
test_email = smtp_user  # Kendi email'inize test gönder
test_username = "test_user_" + secrets.token_hex(4)[:8]

print(f"📝 Test Bilgileri:")
print(f"   Test Email: {test_email}")
print(f"   Test Username: {test_username}")
print()

# Email service'i import et
try:
    from app.services.email_service import EmailService
    from app.services.email_verification import EmailVerificationService
    print("✅ Email servisleri yüklendi")
except Exception as e:
    print(f"❌ Email servisleri yüklenemedi: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("-" * 60)
print("TEST 1: Token Oluşturma")
print("-" * 60)

try:
    # Test için geçici bir user_id oluştur (gerçek DB'ye yazmadan)
    test_user_id = "test_" + secrets.token_hex(16)
    verification_token = EmailVerificationService.generate_verification_token()
    
    print(f"✅ Token oluşturuldu: {verification_token[:20]}...")
    print(f"   Token uzunluğu: {len(verification_token)} karakter")
except Exception as e:
    print(f"❌ Token oluşturma hatası: {e}")
    sys.exit(1)

print()
print("-" * 60)
print("TEST 2: Email Gönderimi")
print("-" * 60)

# Base URL
base_url = os.environ.get('BASE_URL', 'http://localhost:5000')

try:
    print(f"📧 Email gönderiliyor...")
    print(f"   Alıcı: {test_email}")
    print(f"   Base URL: {base_url}")
    
    success = EmailService.send_verification_email(
        user_email=test_email,
        username=test_username,
        verification_token=verification_token,
        base_url=base_url
    )
    
    if success:
        print()
        print("✅ EMAIL BAŞARIYLA GÖNDERİLDİ!")
        print()
        print("📬 Şimdi yapmanız gerekenler:")
        print("   1. Gmail hesabınızı açın: https://mail.google.com")
        print(f"   2. Gelen kutusunu kontrol edin ({test_email})")
        print("   3. Spam klasörünü de kontrol edin")
        print("   4. 'Email Adresinizi Doğrulayın - miayis' konulu email'i bulun")
        print("   5. Email'i açıp 'Email'i Doğrula' butonuna tıklayın")
        print()
        print("🔗 Doğrulama linki:")
        verification_url = f"{base_url}/auth/verify-email?token={verification_token}"
        print(f"   {verification_url}")
        print()
        print("💡 Bu linki tarayıcınıza kopyalayıp yapıştırarak da test edebilirsiniz")
    else:
        print()
        print("❌ EMAIL GÖNDERİLEMEDİ!")
        print()
        print("🔍 Kontrol edin:")
        print("   1. .env dosyasında SMTP ayarları doğru mu?")
        print("   2. Gmail App Password doğru mu?")
        print("   3. 2 Adımlı Doğrulama açık mı?")
        print("   4. İnternet bağlantınız var mı?")
        print()
        print("📋 Console loglarını kontrol edin (yukarıdaki hata mesajlarına bakın)")
        sys.exit(1)
        
except Exception as e:
    print()
    print(f"❌ EMAIL GÖNDERME HATASI: {e}")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("-" * 60)
print("TEST 3: SMTP Bağlantı Testi")
print("-" * 60)

try:
    import smtplib
    
    print("🔌 SMTP sunucusuna bağlanılıyor...")
    server = smtplib.SMTP(smtp_host, int(os.environ.get('SMTP_PORT', '587')))
    print("✅ SMTP sunucusuna bağlanıldı")
    
    print("🔐 STARTTLS başlatılıyor...")
    server.starttls()
    print("✅ STARTTLS başarılı")
    
    print("🔑 Giriş yapılıyor...")
    server.login(smtp_user, smtp_password)
    print("✅ Giriş başarılı!")
    
    server.quit()
    print()
    print("✅ Tüm SMTP testleri başarılı!")
    
except smtplib.SMTPAuthenticationError:
    print()
    print("❌ SMTP KİMLİK DOĞRULAMA HATASI!")
    print()
    print("🔧 Çözüm:")
    print("   1. Gmail App Password'ü doğru kopyaladınız mı? (boşluksuz)")
    print("   2. 2 Adımlı Doğrulama açık mı?")
    print("   3. SMTP_USER doğru email adresi mi?")
    print("   4. Yeni bir App Password oluşturmayı deneyin")
    sys.exit(1)
    
except smtplib.SMTPConnectError:
    print()
    print("❌ SMTP SUNUCUSUNA BAĞLANILAMADI!")
    print()
    print("🔧 Çözüm:")
    print("   1. SMTP_HOST doğru mu? (smtp.gmail.com)")
    print("   2. SMTP_PORT doğru mu? (587)")
    print("   3. İnternet bağlantınız var mı?")
    print("   4. Firewall SMTP portunu engelliyor mu?")
    sys.exit(1)
    
except Exception as e:
    print()
    print(f"❌ SMTP BAĞLANTI HATASI: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("🎉 TÜM TESTLER BAŞARILI!")
print("=" * 60)
print()
print("📧 Email'inizi kontrol edin ve doğrulama linkine tıklayın")
print()
print("✅ Email sistemi çalışıyor ve hazır!")
print()
