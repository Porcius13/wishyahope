"""
Email Gönderim Durumu Kontrol Script'i
Kullanıcının email gönderim durumunu kontrol eder
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# .env yükle
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
dotenv_path = parent_dir / '.env'

if dotenv_path.exists():
    load_dotenv(dotenv_path)
    print("✅ .env dosyası yüklendi")
else:
    print("⚠️  .env dosyası bulunamadı")

print()
print("=" * 60)
print("📧 Email Gönderim Durumu")
print("=" * 60)
print()

# SMTP ayarları kontrolü
smtp_host = os.environ.get('SMTP_HOST')
smtp_port = os.environ.get('SMTP_PORT')
smtp_user = os.environ.get('SMTP_USER')
smtp_password = os.environ.get('SMTP_PASSWORD')
smtp_from = os.environ.get('SMTP_FROM')

print("SMTP Ayarları:")
print("-" * 60)
print(f"SMTP_HOST: {smtp_host or 'YOK ❌'}")
print(f"SMTP_PORT: {smtp_port or 'YOK ❌'}")
print(f"SMTP_USER: {smtp_user or 'YOK ❌'}")
print(f"SMTP_PASSWORD: {'*' * len(smtp_password) if smtp_password else 'YOK ❌'}")
print(f"SMTP_FROM: {smtp_from or 'YOK ❌'}")
print()

if not all([smtp_host, smtp_user, smtp_password]):
    print("❌ SMTP ayarları eksik!")
    print()
    print("🔧 Çözüm:")
    print("   .env dosyasına şunları ekleyin:")
    print("   SMTP_HOST=smtp.gmail.com")
    print("   SMTP_PORT=587")
    print("   SMTP_USER=tilsimsticker@gmail.com")
    print("   SMTP_PASSWORD=udqewccgzyhroqxe")
    print("   SMTP_FROM=Miayis App <tilsimsticker@gmail.com>")
    sys.exit(1)

print("✅ Tüm SMTP ayarları mevcut")
print()

# SMTP bağlantı testi
print("SMTP Bağlantı Testi:")
print("-" * 60)

try:
    import smtplib
    
    print(f"🔌 {smtp_host}:{smtp_port} bağlanılıyor...")
    server = smtplib.SMTP(smtp_host, int(smtp_port))
    print("✅ SMTP sunucusuna bağlanıldı")
    
    print("🔐 STARTTLS başlatılıyor...")
    server.starttls()
    print("✅ STARTTLS başarılı")
    
    print("🔑 Giriş yapılıyor...")
    server.login(smtp_user, smtp_password)
    print("✅ Giriş başarılı!")
    
    server.quit()
    print()
    print("✅ SMTP bağlantısı çalışıyor!")
    
except smtplib.SMTPAuthenticationError as e:
    print()
    print("❌ SMTP KİMLİK DOĞRULAMA HATASI!")
    print(f"   Hata: {e}")
    print()
    print("🔧 Kontrol edin:")
    print("   1. Gmail App Password doğru mu? (boşluksuz)")
    print("   2. 2 Adımlı Doğrulama açık mı?")
    print("   3. SMTP_USER doğru email adresi mi?")
    sys.exit(1)
    
except Exception as e:
    print()
    print(f"❌ SMTP BAĞLANTI HATASI: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("💡 Öneriler:")
print("=" * 60)
print("1. Uygulama console loglarını kontrol edin:")
print("   - '[EMAIL] Verification email sent to...' görünmeli")
print("   - Eğer '[EMAIL] Would send email...' görüyorsanız,")
print("     SMTP ayarları yüklenmemiş demektir")
print()
print("2. Gmail hesabınızı kontrol edin:")
print("   - Gelen kutusu")
print("   - Spam klasörü")
print()
print("3. Uygulamayı yeniden başlatın (.env yüklenmesi için)")
print()
print("4. Test email gönderin:")
print("   python kataloggia-main/test_email_sending.py")
print()
