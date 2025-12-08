"""
Email Doğrulama Linkini Yeniden Gönder
Kayıt olmuş kullanıcıya email doğrulama linki gönderir
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Path ve .env yükle
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
dotenv_path = parent_dir / '.env'

if dotenv_path.exists():
    load_dotenv(dotenv_path)
    print("✅ .env dosyası yüklendi")
else:
    print("⚠️  .env dosyası bulunamadı")

sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(parent_dir))

print("=" * 60)
print("📧 Email Doğrulama Linki Gönderme")
print("=" * 60)
print()

# Kullanıcı bilgilerini al
print("Lütfen aşağıdaki bilgileri girin:")
print("(Kullanıcı adı VEYA email adresi yeterli)")
input_str = input("Kullanıcı adı veya email: ").strip()

if not input_str:
    print("❌ Kullanıcı adı veya email gerekli!")
    sys.exit(1)

# Email mi yoksa kullanıcı adı mı olduğunu kontrol et
if '@' in input_str:
    # Email gibi görünüyor
    email = input_str
    username = None
else:
    # Kullanıcı adı gibi görünüyor
    username = input_str
    email = None

print()

print()
print("-" * 60)

try:
    from app.repositories import get_repository
    from app.services.email_service import EmailService
    from app.services.email_verification import EmailVerificationService
    
    # Kullanıcıyı bul (önce email ile, sonra kullanıcı adı ile)
    repo = get_repository()
    user_data = None
    
    # Email ile ara (daha kesin)
    if email:
        user_data = repo.get_user_by_email(email)
        if user_data:
            print(f"📧 Email ile kullanıcı bulundu: {email}")
    
    # Eğer bulunamazsa kullanıcı adı ile dene
    if not user_data and username:
        user_data = repo.get_user_by_username(username)
        if user_data:
            print(f"👤 Kullanıcı adı ile kullanıcı bulundu: {username}")
    
    if not user_data:
        print(f"❌ Kullanıcı bulunamadı!")
        if username:
            print(f"   Aranan kullanıcı adı: {username}")
        if email:
            print(f"   Aranan email: {email}")
        print()
        print("💡 Kontrol edin:")
        print("   - Kullanıcı adı veya email doğru mu?")
        print("   - Kayıt işlemi başarılı oldu mu?")
        sys.exit(1)
    
    user_id = user_data.get('id')
    db_username = user_data.get('username')
    db_email = user_data.get('email')
    
    # Kullanıcı adı veya email eşleşmesini kontrol et
    if username and db_username.lower() != username.lower():
        if email.lower() != db_email.lower():
            print(f"⚠️  Uyarı: Kullanıcı adı eşleşmedi, email ile bulundu")
    
    if email and db_email.lower() != email.lower():
        print(f"❌ Email adresi eşleşmiyor!")
        print(f"   Veritabanı: {db_email}")
        print(f"   Girilen: {email}")
        sys.exit(1)
    
    print(f"✅ Kullanıcı bulundu!")
    print(f"   Kullanıcı adı: {db_username}")
    print(f"   Email: {db_email}")
    print()
    
    # Token oluştur
    print("🔑 Token oluşturuluyor...")
    verification_token = EmailVerificationService.create_verification_token(user_id, email)
    print(f"✅ Token oluşturuldu: {verification_token[:20]}...")
    print()
    
    # Email gönder
    print("📧 Email gönderiliyor...")
    base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
    email_sent = EmailService.send_verification_email(db_email, db_username, verification_token, base_url)
    
    if email_sent:
        print()
        print("✅ EMAIL BAŞARIYLA GÖNDERİLDİ!")
        print()
        print("📬 Yapmanız gerekenler:")
        print("   1. Gmail hesabınızı açın: https://mail.google.com")
        print(f"   2. Gelen kutusunu kontrol edin ({db_email})")
        print("   3. Spam klasörünü de kontrol edin")
        print("   4. 'Email Adresinizi Doğrulayın - miayis' konulu email'i bulun")
        print()
        print("🔗 Doğrulama linki (manuel test için):")
        verification_url = f"{base_url}/auth/verify-email?token={verification_token}"
        print(f"   {verification_url}")
        print()
        print("💡 Bu linki tarayıcınıza kopyalayıp yapıştırarak email'i doğrulayabilirsiniz")
    else:
        print()
        print("❌ EMAIL GÖNDERİLEMEDİ!")
        print()
        print("🔍 Kontrol edin:")
        print("   1. .env dosyasında SMTP ayarları var mı?")
        print("   2. Uygulamayı yeniden başlattınız mı? (.env yüklenmesi için)")
        print("   3. Console loglarını kontrol edin")
        
except Exception as e:
    print()
    print(f"❌ HATA: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
