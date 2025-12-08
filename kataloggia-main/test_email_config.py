"""
Email Configuration Test Script
.env dosyanızın doğru yapılandırıldığını kontrol eder
"""
import os
import sys
from pathlib import Path

# Project root'u bul
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
dotenv_path = parent_dir / '.env'

print("=" * 60)
print("Email Configuration Test")
print("=" * 60)
print()

# .env dosyası var mı kontrol et
if not dotenv_path.exists():
    print("❌ .env dosyası bulunamadı!")
    print(f"   Aranan konum: {dotenv_path}")
    print()
    print("💡 .env dosyası şu konumda olmalı:")
    print(f"   {parent_dir}\\.env")
    sys.exit(1)

print(f"✅ .env dosyası bulundu: {dotenv_path}")
print()

# python-dotenv yükle
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path)
    print("✅ .env dosyası yüklendi")
except ImportError:
    print("⚠️  python-dotenv yüklü değil")
    print("   pip install python-dotenv")
    sys.exit(1)

print()

# Değerleri kontrol et
checks = {
    'SMTP_HOST': os.environ.get('SMTP_HOST'),
    'SMTP_PORT': os.environ.get('SMTP_PORT'),
    'SMTP_USER': os.environ.get('SMTP_USER'),
    'SMTP_PASSWORD': os.environ.get('SMTP_PASSWORD'),
    'SMTP_FROM': os.environ.get('SMTP_FROM'),
}

print("📋 Environment Variables Kontrolü:")
print("-" * 60)

all_ok = True

for key, value in checks.items():
    if value:
        # Password gizle
        if 'PASSWORD' in key:
            display_value = '*' * len(value) if value else 'YOK'
        else:
            display_value = value
        
        print(f"✅ {key:20} = {display_value}")
        
        # Özel kontroller
        if key == 'SMTP_HOST' and 'gmail' not in value.lower():
            print(f"   ⚠️  Gmail için 'smtp.gmail.com' olmalı")
        
        if key == 'SMTP_PORT' and value != '587':
            print(f"   ⚠️  Gmail için port genellikle '587' (STARTTLS)")
        
        if key == 'SMTP_USER' and '@gmail.com' not in value:
            print(f"   ⚠️  Gmail adresi '@gmail.com' ile bitmeli")
        
        if key == 'SMTP_PASSWORD' and len(value) != 16:
            print(f"   ⚠️  App Password genellikle 16 karakter (boşluksuz)")
        
        if key == 'SMTP_FROM' and '<' not in value:
            print(f"   ⚠️  SMTP_FROM formatı: 'İsim <email@example.com>' olmalı")
            all_ok = False
        
    else:
        print(f"❌ {key:20} = YOK (Eksik!)")
        all_ok = False

print("-" * 60)
print()

# Öneriler
print("💡 Öneriler:")
if checks['SMTP_FROM'] and '<' not in checks['SMTP_FROM']:
    print("   SMTP_FROM düzeltmesi gerekiyor:")
    print(f"   Örnek: SMTP_FROM=Miayis App <{checks['SMTP_USER']}>")
    print()

# Test email gönderimi
if all_ok:
    print("🧪 Test Email Gönderimi:")
    print("-" * 60)
    
    try:
        from app.services.email_service import EmailService
        
        test_email = checks['SMTP_USER']  # Kendi email'inize test gönderin
        print(f"Test email gönderiliyor: {test_email}")
        print("(Sadece SMTP bağlantısı test ediliyor, gerçek email gönderilmeyecek)")
        print()
        
        # Basit SMTP bağlantı testi
        import smtplib
        
        try:
            server = smtplib.SMTP(checks['SMTP_HOST'], int(checks['SMTP_PORT']))
            server.starttls()
            server.login(checks['SMTP_USER'], checks['SMTP_PASSWORD'])
            print("✅ SMTP bağlantısı başarılı!")
            print("✅ Giriş doğrulaması başarılı!")
            server.quit()
            
            print()
            print("🎉 Email konfigürasyonu hazır!")
            print("   Artık uygulamadan email gönderebilirsiniz.")
            
        except smtplib.SMTPAuthenticationError:
            print("❌ SMTP kimlik doğrulama hatası!")
            print("   Kontrol edin:")
            print("   - App Password doğru mu? (boşluksuz)")
            print("   - 2 Adımlı Doğrulama açık mı?")
            print("   - SMTP_USER doğru email mi?")
            all_ok = False
            
        except smtplib.SMTPConnectError:
            print("❌ SMTP sunucusuna bağlanılamıyor!")
            print("   Kontrol edin:")
            print("   - SMTP_HOST doğru mu? (smtp.gmail.com)")
            print("   - SMTP_PORT doğru mu? (587)")
            print("   - İnternet bağlantınız var mı?")
            all_ok = False
            
        except Exception as e:
            print(f"❌ Hata: {e}")
            all_ok = False
            
    except ImportError:
        print("⚠️  Email service import edilemedi")
        print("   Uygulama yapısı kontrol edilmeli")
        all_ok = False

print()
print("=" * 60)

if all_ok:
    print("✅ Tüm kontroller başarılı!")
    sys.exit(0)
else:
    print("❌ Bazı sorunlar var, yukarıdaki önerilere bakın")
    sys.exit(1)
