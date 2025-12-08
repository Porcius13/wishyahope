# 📧 Email Gönderim Yapılandırması

## Genel Bakış

Email gönderim sistemi 3 modda çalışır:
1. **SMTP ile gerçek email gönderimi** (Production için önerilen)
2. **Development modu** (SMTP ayarları yoksa sadece log basar)
3. **Flask-Mail entegrasyonu** (gelecekte eklenebilir)

## 🔧 Yapılandırma

### Environment Variables

Email gönderimi için aşağıdaki environment variable'ları ayarlayın:

```bash
# SMTP Sunucu Ayarları
SMTP_HOST=smtp.gmail.com          # SMTP sunucu adresi
SMTP_PORT=587                     # SMTP port (genellikle 587 veya 465)
SMTP_USER=your-email@gmail.com    # SMTP kullanıcı adı (email)
SMTP_PASSWORD=your-app-password   # SMTP şifresi veya app password
SMTP_FROM=noreply@miayis.com      # Gönderen email (opsiyonel, SMTP_USER kullanılır)
```

### Gmail ile Yapılandırma - Adım Adım Kılavuz

#### ADIM 1: Gmail Hesabınıza Giriş Yapın
1. [Google Hesabım](https://myaccount.google.com/) sayfasına gidin
2. Gmail hesabınızla giriş yapın

#### ADIM 2: 2 Adımlı Doğrulamayı Aktifleştirin

**Eğer zaten aktifse ADIM 3'e geçin!**

1. Sol menüden **"Güvenlik"** sekmesine tıklayın
2. **"Google'a giriş yapma"** bölümünde **"2 Adımlı Doğrulama"** öğesini bulun
3. **"2 Adımlı Doğrulama"** üzerine tıklayın
4. Eğer açık değilse, **"Başlat"** butonuna tıklayın
5. Telefon numaranızı doğrulayın (SMS veya telefon araması)
6. Doğrulama kodunu girip işlemi tamamlayın

**⚠️ ÖNEMLİ:** App Password oluşturmak için 2 Adımlı Doğrulama **MUTLAKA** aktif olmalı!

#### ADIM 3: App Password (Uygulama Şifresi) Oluşturun

1. Hala **"Güvenlik"** sayfasındasınız
2. **"2 Adımlı Doğrulama"** altında **"Uygulama şifreleri"** linkini bulun
   - Link bulunamazsa: [Uygulama şifreleri](https://myaccount.google.com/apppasswords) sayfasına direkt gidin
3. **"Uygulama şifreleri"** üzerine tıklayın
4. Gerekirse tekrar şifrenizi girin
5. **"Uygulama seçin"** dropdown menüsünden **"Diğer (Özel ad)"** seçin
6. Özel ad kutusuna bir isim yazın, örneğin:
   - `miayis-app`
   - `flask-email`
   - `web-app`
7. **"Oluştur"** butonuna tıklayın
8. Google size **16 haneli bir şifre** gösterecek (4 haneli gruplar halinde)
   - Örnek: `abcd efgh ijkl mnop`
   - ⚠️ **BU ŞİFREYİ HEMEN KOPYALAYIN!** Sadece bir kez gösterilir!
9. Şifreyi güvenli bir yere kaydedin

#### ADIM 4: .env Dosyası Oluşturun

Projenizin ana dizininde (kataloggia-main klasörünün bir üst dizini) `.env` dosyası oluşturun.

**Windows için:**
1. Proje klasörünüze gidin (örn: `C:\Users\faxys\OneDrive\Desktop\wishyahope`)
2. Yeni bir metin belgesi oluşturun
3. Adını `.env` yapın (başındaki nokta önemli!)
   - Windows Explorer'da dosya adını değiştirirken `".env"` (tırnak işaretleriyle birlikte) yazın
   - Ya da Notepad++ veya VS Code kullanarak `.env` dosyası oluşturun

**VS Code ile:**
1. VS Code'da projeyi açın
2. Sol üstteki **"Explorer"** panelinden ana klasöre sağ tıklayın
3. **"New File"** seçin
4. Dosya adını `.env` yazın

#### ADIM 5: .env Dosyasına Değerleri Yazın

`.env` dosyasını açın ve aşağıdaki satırları ekleyin:

```env
# Gmail SMTP Ayarları
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ornek@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM=Miayis App <ornek@gmail.com>
```

**Değerleri Değiştirin:**
- `SMTP_USER`: Gmail adresinizi yazın (örn: `ahmet@gmail.com`)
- `SMTP_PASSWORD`: ADIM 3'te kopyaladığınız 16 haneli app password'ü yazın
  - ⚠️ **Boşluksuz yazın!** 
  - Örnek: `abcd efgh ijkl mnop` yerine `abcdefghijklmnop` yazın
- `SMTP_FROM`: İstediğiniz gönderen ismi (opsiyonel, genelde SMTP_USER ile aynı)

**Örnek Tamamlanmış .env Dosyası:**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ahmet.yilmaz@gmail.com
SMTP_PASSWORD=abcd1234efgh5678
SMTP_FROM=Miayis <ahmet.yilmaz@gmail.com>
```

#### ADIM 6: .env Dosyasının Konumunu Kontrol Edin

`.env` dosyası şu konumda olmalı:
```
wishyahope/
  └── .env          ← BURADA!
  └── kataloggia-main/
  └── templates/
  └── static/
```

**Kontrol için:** `run.py` dosyası `.env` dosyasını otomatik olarak yükler:
```python
dotenv_path = os.path.join(project_root, '.env')  # wishyahope/.env
```

#### ADIM 7: Değerleri Doğrulayın

**⚠️ ÖNEMLİ KONTROLLER:**

1. **SMTP_PASSWORD'de boşluk var mı?**
   - ❌ Yanlış: `abcd efgh ijkl mnop`
   - ✅ Doğru: `abcdefghijklmnop`

2. **SMTP_USER doğru mu?**
   - Gmail adresinizin tamamını yazın: `email@gmail.com`

3. **Dosya adı `.env` mi?**
   - ❌ Yanlış: `.env.txt` veya `env`
   - ✅ Doğru: `.env` (nokta ile başlayan, uzantısız)

#### ADIM 8: Uygulamayı Yeniden Başlatın

1. Uygulamayı kapatın (Ctrl+C)
2. Yeniden başlatın:
   ```bash
   python kataloggia-main/run.py
   ```

3. Console'da şunu görmelisiniz:
   ```
   [DEBUG] .env dosyası yüklendi: C:\Users\...\wishyahope\.env
   ```

#### ADIM 9: Test Edin

Bir kullanıcı kayıt olduğunda:
- Console'da `[EMAIL] Verification email sent to ...` mesajını görmelisiniz
- Email hesabınızın gelen kutusunu kontrol edin
- Spam klasörünü de kontrol edin

**Test için:**
```python
# Python console'da test edin
import os
from dotenv import load_dotenv
load_dotenv()

print("SMTP_HOST:", os.environ.get('SMTP_HOST'))
print("SMTP_USER:", os.environ.get('SMTP_USER'))
print("SMTP_PASSWORD:", "***" if os.environ.get('SMTP_PASSWORD') else "YOK")
```

---

### 🔧 Alternatif: Environment Variables (Windows PowerShell)

Eğer `.env` dosyası kullanmak istemiyorsanız, PowerShell'de direkt ayarlayabilirsiniz:

```powershell
# PowerShell'i yönetici olarak açın
$env:SMTP_HOST="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_USER="ornek@gmail.com"
$env:SMTP_PASSWORD="abcdefghijklmnop"
$env:SMTP_FROM="Miayis <ornek@gmail.com>"

# Uygulamayı çalıştırın
python kataloggia-main/run.py
```

**⚠️ NOT:** Bu ayarlar sadece o PowerShell oturumunda geçerlidir. Kapatıp açarsanız tekrar ayarlamanız gerekir.

### Outlook/Hotmail ile Yapılandırma

```bash
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=your-email@outlook.com
SMTP_PASSWORD=your-password
```

### SendGrid ile Yapılandırma

```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM=noreply@yourdomain.com
```

### Mailgun ile Yapılandırma

```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@yourdomain.mailgun.org
SMTP_PASSWORD=your-mailgun-smtp-password
SMTP_FROM=noreply@yourdomain.com
```

### Amazon SES ile Yapılandırma

```bash
SMTP_HOST=email-smtp.region.amazonaws.com  # Örn: email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-ses-smtp-username
SMTP_PASSWORD=your-ses-smtp-password
SMTP_FROM=noreply@yourdomain.com
```

## 🚀 Kullanım

### Development Modu (SMTP Ayarları Yoksa)

Eğer SMTP ayarları yapılmazsa, sistem development modunda çalışır:
- Email gönderilmez
- Console'a log basılır
- Kayıt işlemi engellenmez (geliştirme için)

**Console Çıktısı:**
```
[EMAIL] Would send email to user@example.com
[EMAIL] Subject: Email Adresinizi Doğrulayın - miayis
[EMAIL] Body: Merhaba username,...
```

### Production Modu (SMTP Ayarlarıyla)

SMTP ayarları yapıldığında:
- Gerçek email gönderilir
- HTML ve plain text formatında gönderilir
- Başarı/hata logları tutulur

## 📝 Email Tipleri

### 1. Email Doğrulama Emaili

**Ne zaman gönderilir:**
- Kullanıcı kayıt olduğunda
- Kullanıcı "Email'i Yeniden Gönder" butonuna tıkladığında

**İçerik:**
- Hoş geldin mesajı
- Email doğrulama linki
- 24 saatlik geçerlilik süresi bilgisi

**Endpoint:** `POST /register` veya `POST /auth/resend-verification`

### 2. Şifre Sıfırlama Emaili

**Ne zaman gönderilir:**
- Kullanıcı şifre sıfırlama talebi gönderdiğinde (gelecekte eklenecek)

**İçerik:**
- Şifre sıfırlama linki
- 1 saatlik geçerlilik süresi bilgisi
- Güvenlik uyarısı

## 🔍 Test Etme

### Otomatik Test (Önerilen)

**Test script'ini çalıştırın:**

```bash
python kataloggia-main/test_email_sending.py
```

Bu script:
- ✅ Tüm SMTP ayarlarını kontrol eder
- ✅ Bağlantıyı test eder
- ✅ Gerçek email gönderir
- ✅ Detaylı rapor verir

### Manuel Test

### 1. Environment Variables Kontrolü

```bash
python kataloggia-main/test_email_config.py
```

Ya da Python'da:
```python
import os
from dotenv import load_dotenv
load_dotenv()

print("SMTP_HOST:", os.environ.get('SMTP_HOST'))
print("SMTP_PORT:", os.environ.get('SMTP_PORT'))
print("SMTP_USER:", os.environ.get('SMTP_USER'))
print("SMTP_PASSWORD:", "***" if os.environ.get('SMTP_PASSWORD') else "YOK")
```

### 2. Email Gönderimini Test Edin

**Otomatik test script'i kullanın:**
```bash
python kataloggia-main/test_email_sending.py
```

**Ya da manuel olarak:**
```python
from app.services.email_service import EmailService

# Test email gönderimi
success = EmailService.send_verification_email(
    user_email="your-email@gmail.com",
    username="TestUser",
    verification_token="test-token-123",
    base_url="http://localhost:5000"
)

if success:
    print("Email başarıyla gönderildi!")
else:
    print("Email gönderimi başarısız!")
```

### 3. Log Kontrolü

Email gönderimi sırasında logları kontrol edin:
- `[EMAIL] Verification email sent to ...` - Başarılı
- `[ERROR] SMTP email sending failed: ...` - Hata

## 🛠️ Sorun Giderme

### Problem: "Authentication failed"

**Çözüm:**
- Gmail kullanıyorsanız App Password kullanın (normal şifre değil!)
- 2 Adımlı Doğrulama aktif olmalı
- SMTP_USER email adresiniz olmalı

### Problem: "Connection refused"

**Çözüm:**
- SMTP_HOST ve SMTP_PORT'u kontrol edin
- Firewall/port engellemesi olabilir
- SSL/TLS ayarlarını kontrol edin (port 587 genellikle STARTTLS kullanır)

### Problem: "Email gönderilmiyor ama hata yok"

**Çözüm:**
- Spam klasörünü kontrol edin
- SMTP ayarlarının doğru olduğundan emin olun
- Logları kontrol edin

### Problem: "Development modunda çalışıyor"

**Çözüm:**
- Environment variable'ların ayarlandığından emin olun
- Uygulama restart edin
- `.env` dosyası kullanıyorsanız yüklendiğinden emin olun

## 📦 Render/Heroku gibi Platformlarda Kullanım

### Render

1. Render Dashboard > Environment Variables
2. Aşağıdaki değişkenleri ekleyin:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SMTP_FROM=noreply@miayis.com
   ```

### Heroku

```bash
heroku config:set SMTP_HOST=smtp.gmail.com
heroku config:set SMTP_PORT=587
heroku config:set SMTP_USER=your-email@gmail.com
heroku config:set SMTP_PASSWORD=your-app-password
heroku config:set SMTP_FROM=noreply@miayis.com
```

### .env Dosyası Kullanımı

`kataloggia-main/.env` dosyası oluşturun:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@miayis.com
```

Python'da yüklemek için `python-dotenv` kullanın:

```python
from dotenv import load_dotenv
load_dotenv()
```

## 🔐 Güvenlik Notları

1. **App Password Kullanın:** Gmail için normal şifre yerine App Password kullanın
2. **Environment Variables:** Şifreleri asla kodda hardcode etmeyin
3. **HTTPS:** Production'da mutlaka HTTPS kullanın
4. **Rate Limiting:** Email gönderimi için rate limiting aktif (3 kayıt/saat)
5. **Token Güvenliği:** Email token'ları 24 saat sonra expire olur

## 📚 İleri Seviye

### Async Email Gönderimi

Gelecekte Celery ile async email gönderimi eklenebilir:

```python
from app.tasks.email_tasks import send_verification_email_async

# Async olarak gönder
send_verification_email_async.delay(user_email, username, token)
```

### Email Queue

Çok fazla email gönderilecekse queue sistemi kullanılabilir:
- Redis + Celery
- AWS SQS
- RabbitMQ

### Email Tracking

Email açılma ve tıklama takibi için:
- Pixel tracking eklenebilir
- Link tracking eklenebilir
- Database'de event logging yapılabilir

## ✅ Checklist

- [ ] SMTP ayarları yapılandırıldı
- [ ] Test email gönderildi
- [ ] Email spam klasöründe değil
- [ ] Email doğrulama linki çalışıyor
- [ ] Production ortamında test edildi
- [ ] Error logging çalışıyor
