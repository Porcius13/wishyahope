"""
Hızlı Email Gönderme Script'i
Email adresi ile kullanıcıyı bulur ve doğrulama email'i gönderir
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Path ve .env yükle
current_dir = Path(__file__).parent
parent_dir = current_dir.parent

# .env dosyasını farklı konumlarda ara
dotenv_paths = [
    parent_dir / '.env',  # wishyahope/.env
    current_dir / '.env',  # kataloggia-main/.env
    Path.cwd() / '.env',  # Mevcut çalışma dizini
]

dotenv_path = None
for path in dotenv_paths:
    if path.exists():
        dotenv_path = path
        break

if dotenv_path:
    load_dotenv(dotenv_path)
    print(f"✅ .env dosyası yüklendi: {dotenv_path}")
else:
    print("⚠️  .env dosyası bulunamadı")
    print(f"   Aranan konumlar:")
    for path in dotenv_paths:
        print(f"   - {path}")

sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(parent_dir))

# Email adresini argüman olarak al
email = sys.argv[1] if len(sys.argv) > 1 else None

if not email:
    print("=" * 60)
    print("📧 Hızlı Email Gönderme")
    print("=" * 60)
    print()
    email = input("Email adresi: ").strip()
    if not email:
        print("❌ Email adresi gerekli!")
        print()
        print("Kullanım: python send_email_now.py email@example.com")
        sys.exit(1)

print()
print("=" * 60)
print(f"📧 Email gönderiliyor: {email}")
print("=" * 60)
print()

try:
    from app.repositories import get_repository
    from app.services.email_service import EmailService
    from app.services.email_verification import EmailVerificationService
    
    # Kullanıcıyı email ile bul
    repo = get_repository()
    user_data = repo.get_user_by_email(email)
    
    if not user_data:
        print(f"❌ Kullanıcı bulunamadı: {email}")
        print()
        print("💡 Kontrol edin:")
        print("   - Email adresi doğru mu?")
        print("   - Kullanıcı kayıt oldu mu?")
        sys.exit(1)
    
    user_id = user_data.get('id')
    username = user_data.get('username')
    
    print(f"✅ Kullanıcı bulundu:")
    print(f"   Kullanıcı adı: {username}")
    print(f"   Email: {email}")
    print()
    
    # Token oluştur
    print("🔑 Token oluşturuluyor...")
    verification_token = EmailVerificationService.create_verification_token(user_id, email)
    print(f"✅ Token oluşturuldu")
    print()
    
    # SMTP ayarları kontrolü
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    
    if not all([smtp_host, smtp_user, smtp_password]):
        print("⚠️  SMTP ayarları eksik!")
        print("   Email gönderilemeyecek, sadece token oluşturuldu")
        print()
        print("🔧 Çözüm:")
        print("   1. .env dosyasını kontrol edin")
        print("   2. SMTP ayarlarını ekleyin")
        print("   3. Uygulamayı yeniden başlatın")
        print()
        print("🔗 Manuel doğrulama linki:")
        base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
        verification_url = f"{base_url}/auth/verify-email?token={verification_token}"
        print(f"   {verification_url}")
        print()
        print("💡 Bu linki tarayıcınıza kopyalayıp yapıştırarak email'i doğrulayabilirsiniz")
        sys.exit(0)
    
    # Email gönder
    print("📧 Email gönderiliyor...")
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    email_sent = EmailService.send_verification_email(email, username, verification_token, base_url)
    
    if email_sent:
        print()
        print("✅ EMAIL BAŞARIYLA GÖNDERİLDİ!")
        print()
        print("📬 Şimdi yapmanız gerekenler:")
        print("   1. Gmail hesabınızı açın: https://mail.google.com")
        print(f"   2. Gelen kutusunu kontrol edin ({email})")
        print("   3. Spam klasörünü de kontrol edin")
        print("   4. 'Email Adresinizi Doğrulayın - miayis' konulu email'i bulun")
        print()
        print("🔗 Manuel doğrulama linki (eğer email gelmezse):")
        verification_url = f"{base_url}/auth/verify-email?token={verification_token}"
        print(f"   {verification_url}")
    else:
        print()
        print("❌ EMAIL GÖNDERİLEMEDİ!")
        print()
        print("🔍 Kontrol edin:")
        print("   1. Console loglarını kontrol edin (yukarıdaki hata mesajları)")
        print("   2. .env dosyasında SMTP ayarları doğru mu?")
        print()
        print("🔗 Manuel doğrulama linki (email olmadan test için):")
        verification_url = f"{base_url}/auth/verify-email?token={verification_token}"
        print(f"   {verification_url}")
        print()
        print("💡 Bu linki tarayıcınıza kopyalayıp yapıştırarak email'i doğrulayabilirsiniz")
        
except Exception as e:
    print()
    print(f"❌ HATA: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
