# 📧 Gmail Email Ayarları - Çok Detaylı Kılavuz

## 🎯 Ne Yapacağız?

Gmail hesabınızı kullanarak uygulamanızdan email göndermek için:
1. Gmail'de 2 Adımlı Doğrulamayı açacağız
2. Bir "App Password" (Uygulama Şifresi) oluşturacağız
3. Bu şifreyi projeye ekleyeceğiz

---

## 📝 ADIM 1: Gmail Hesabınıza Giriş Yapın

1. Tarayıcınızda [https://myaccount.google.com/](https://myaccount.google.com/) adresine gidin
2. Gmail hesabınızla giriş yapın

---

## 🔐 ADIM 2: 2 Adımlı Doğrulamayı Aktifleştirin

### Zaten Aktifse Geçin
Eğer Gmail hesabınızda 2 Adımlı Doğrulama zaten açıksa, ADIM 3'e geçin.

### Aktif Değilse Açın:

1. **Sol menüden "Güvenlik"** sekmesine tıklayın
   - Eğer menü görünmüyorsa, sol üstteki hamburger menü (☰) simgesine tıklayın

2. **"Google'a giriş yapma"** bölümünü bulun
   - Sayfada aşağı kaydırın
   - "2 Adımlı Doğrulama" yazısını bulun

3. **"2 Adımlı Doğrulama"** üzerine tıklayın

4. **"Başlat"** butonuna tıklayın

5. Telefon numaranızı girin ve doğrulama yöntemi seçin:
   - **Metin mesajı (SMS)** - Önerilen
   - **Telefon araması**

6. Telefonunuza gelen kodu girin

7. **"Açık"** butonuna tıklayın

✅ Artık 2 Adımlı Doğrulama aktif!

---

## 🔑 ADIM 3: App Password (Uygulama Şifresi) Oluşturun

### 3.1: Uygulama Şifreleri Sayfasına Gidin

**Yöntem 1: Güvenlik Sayfasından**
1. Hala "Güvenlik" sayfasındasınız
2. "2 Adımlı Doğrulama" altında **"Uygulama şifreleri"** linkini bulun
3. Üzerine tıklayın

**Yöntem 2: Direkt Link**
- [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) adresine gidin

**⚠️ Eğer Link Görünmüyorsa:**
- 2 Adımlı Doğrulama aktif olmayabilir
- ADIM 2'ye geri dönün ve 2 Adımlı Doğrulamayı açın

### 3.2: Uygulama Şifresi Oluşturun

1. Sayfa açıldığında, üstte bir dropdown menü göreceksiniz: **"Uygulama seçin"**

2. **Dropdown'dan "Diğer (Özel ad)" seçin**
   - Liste açıldığında en alta kaydırın
   - "Diğer (Özel ad)" yazısını bulun ve seçin

3. Özel ad kutusuna bir isim yazın:
   - Örnekler:
     - `miayis-web-app`
     - `flask-email-service`
     - `my-project`
   - İstediğiniz bir isim yazabilirsiniz, sadece hatırlamak için

4. **"Oluştur"** butonuna tıklayın

5. **⚠️ ÖNEMLİ: ŞİFREYİ KOPYALAYIN!**
   - Google size 16 haneli bir şifre gösterecek
   - Format: `xxxx xxxx xxxx xxxx` (boşluklarla)
   - **Bu şifre sadece bir kez gösterilir!**
   - Şifreyi kopyalayıp güvenli bir yere kaydedin

6. **"Tamam"** butonuna tıklayın

✅ App Password oluşturuldu!

---

## 💾 ADIM 4: .env Dosyası Oluşturun

### 4.1: Dosya Konumunu Belirleyin

`.env` dosyası projenizin **ana dizininde** olmalı:

```
wishyahope/                    ← Ana dizin
  ├── .env                     ← BURAYA OLUŞTURACAĞIZ!
  ├── kataloggia-main/
  │   ├── app/
  │   ├── run.py
  │   └── ...
  ├── templates/
  └── static/
```

### 4.2: Windows'ta .env Dosyası Oluşturma

**Yöntem 1: VS Code ile (Önerilen)**
1. VS Code'u açın
2. Proje klasörünü açın (`wishyahope` klasörü)
3. Sol panelde ana klasöre sağ tıklayın
4. **"New File"** seçin
5. Dosya adını `.env` yazın (başındaki nokta önemli!)
6. Enter'a basın

**Yöntem 2: Notepad++ ile**
1. Notepad++'ı açın
2. Boş bir dosya oluşturun
3. **File > Save As**
4. Dosya adını `".env"` yazın (tırnak işaretleriyle birlikte!)
5. Kaydet tipi: **"All types (*.*)"**
6. Ana klasöre kaydedin

**Yöntem 3: Windows Explorer ile**
1. Windows Explorer'da ana klasöre gidin
2. Sağ tık > **Yeni > Metin Belgesi**
3. Dosya adını `env.txt` yapın
4. Enter'a basın
5. Dosyayı seçin ve F2 ile yeniden adlandırın
6. Adını `".env"` yapın (tırnak işaretleriyle!)
7. Windows uyarı verirse "Evet" deyin

### 4.3: Dosya Adını Kontrol Edin

✅ Doğru: `.env` (nokta ile başlayan, uzantısız)
❌ Yanlış: 
- `.env.txt`
- `env`
- `env.txt`
- `.env.`

---

## ✍️ ADIM 5: .env Dosyasına İçerik Yazın

### 5.1: .env Dosyasını Açın

VS Code, Notepad++ veya başka bir metin editörü ile açın.

### 5.2: İçeriği Yazın

Aşağıdaki şablonu kopyalayıp yapıştırın:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ornek@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM=Miayis <ornek@gmail.com>
```

### 5.3: Değerleri Değiştirin

**1. SMTP_USER:**
```env
SMTP_USER=ornek@gmail.com
```
↓ Kendi Gmail adresinizle değiştirin:
```env
SMTP_USER=ahmet.yilmaz@gmail.com
```

**2. SMTP_PASSWORD:**
```env
SMTP_PASSWORD=abcdefghijklmnop
```
↓ ADIM 3'te kopyaladığınız App Password'ü yazın:
- ⚠️ **BOŞLUKSUZ YAZIN!**
- Google'ın gösterdiği: `abcd efgh ijkl mnop`
- Yazmanız gereken: `abcdefghijklmnop`

Örnek:
```env
SMTP_PASSWORD=wxyz1234abcd5678
```

**3. SMTP_FROM (Opsiyonel):**
```env
SMTP_FROM=Miayis <ornek@gmail.com>
```
↓ İstediğiniz isim ve email ile değiştirin:
```env
SMTP_FROM=Miayis App <ahmet.yilmaz@gmail.com>
```

### 5.4: Tamamlanmış Örnek

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=ahmet.yilmaz@gmail.com
SMTP_PASSWORD=wxyz1234abcd5678
SMTP_FROM=Miayis <ahmet.yilmaz@gmail.com>
```

### 5.5: Dosyayı Kaydedin

Ctrl+S ile kaydedin.

---

## ✅ ADIM 6: Doğrulama

### 6.1: .env Dosyasının Varlığını Kontrol Edin

Windows Explorer'da:
- Dosya görünmüyorsa, "Gizli öğeleri göster" seçeneğini açın
- Klasör görünümü > Gizli öğeler (Checkbox)

VS Code'da:
- Dosya görünür olmalı

### 6.2: İçeriği Kontrol Edin

**.env dosyasında:**
- ✅ Her satır bir değişken tanımlamalı
- ✅ `=` işaretinin sağında değer olmalı
- ✅ Boş satır olabilir (sorun değil)
- ✅ `#` ile başlayan satırlar yorum (opsiyonel)
- ❌ Tırnak işareti kullanmayın: `"değer"` değil, `değer`
- ❌ Başında/sonunda boşluk olmamalı

**✅ Doğru:**
```env
SMTP_USER=email@gmail.com
SMTP_PASSWORD=abcd1234efgh5678
```

**❌ Yanlış:**
```env
SMTP_USER="email@gmail.com"     ← Tırnak yok
SMTP_PASSWORD= abcd 1234        ← Boşluk var
SMTP_USER = email@gmail.com     ← = öncesi boşluk var
```

---

## 🚀 ADIM 7: Uygulamayı Başlatın

### 7.1: Uygulamayı Kapatın

Eğer çalışıyorsa:
- Terminal'de Ctrl+C ile durdurun

### 7.2: Yeniden Başlatın

```bash
python kataloggia-main/run.py
```

### 7.3: Console Çıktısını Kontrol Edin

Şunu görmelisiniz:
```
[DEBUG] .env dosyası yüklendi: C:\Users\...\wishyahope\.env
```

Eğer görmüyorsanız:
- `.env` dosyası yanlış yerde olabilir
- Dosya adı yanlış olabilir (`.env.txt` gibi)

---

## 🧪 ADIM 8: Test Edin

### 8.1: Otomatik Test Script'i Çalıştırın

**En kolay yöntem: Test script'ini çalıştırın!**

```bash
python kataloggia-main/test_email_sending.py
```

Bu script:
- ✅ .env dosyasını kontrol eder
- ✅ SMTP bağlantısını test eder
- ✅ Token oluşturur
- ✅ Gerçek email gönderir
- ✅ Tüm adımları otomatik yapar

**Script çıktısı:**
```
✅ EMAIL BAŞARIYLA GÖNDERİLDİ!
📬 Şimdi yapmanız gerekenler:
   1. Gmail hesabınızı açın
   2. Gelen kutusunu kontrol edin
   3. Spam klasörünü de kontrol edin
   4. Email'i açıp doğrulama linkine tıklayın
```

### 8.2: Manuel Test (Alternatif)

Eğer script çalışmazsa, manuel olarak test edin:

1. Tarayıcıda uygulamanıza gidin: `http://localhost:5000`
2. Kayıt ol sayfasına gidin: `/register`
3. Yeni bir kullanıcı kaydedin
4. Kendi Gmail adresinizi kullanın (test için)

### 8.3: Console Loglarını Kontrol Edin

**Başarılı email gönderimi:**
```
[EMAIL] Verification email sent to tilsimsticker@gmail.com
```

**Hata varsa:**
```
[ERROR] SMTP email sending failed: ...
```

### 8.4: Email Kutusunu Kontrol Edin

1. Gmail hesabınızı açın: [https://mail.google.com](https://mail.google.com)
2. **Gelen kutusunu** kontrol edin
3. **Spam klasörünü** de kontrol edin
4. "Email Adresinizi Doğrulayın - miayis" konulu email'i bulun

### 8.5: Email Linkini Test Edin

1. Email'i açın
2. "Email'i Doğrula" butonuna tıklayın
3. Ya da doğrulama linkini tarayıcıya kopyalayın
4. Tarayıcıda doğrulama sayfası açılmalı
5. "Email adresiniz başarıyla doğrulandı!" mesajını görmelisiniz

---

## 🛠️ Sorun Giderme

### Problem: "Authentication failed" hatası

**Çözüm:**
1. App Password'ü doğru kopyaladınız mı? (boşluksuz)
2. 2 Adımlı Doğrulama aktif mi?
3. SMTP_USER doğru mu? (tam email adresi)

### Problem: ".env dosyası yüklenmiyor"

**Çözüm:**
1. Dosya adı tam olarak `.env` mi? (`.env.txt` değil)
2. Dosya `wishyahope/` klasöründe mi? (`kataloggia-main/` içinde değil)
3. Uygulamayı yeniden başlattınız mı?

### Problem: "Email gelmiyor"

**Çözüm:**
1. Spam klasörünü kontrol edin
2. Console'da hata var mı?
3. Gmail hesabı doğru mu?
4. App Password doğru mu?

### Problem: "Connection refused"

**Çözüm:**
1. SMTP_HOST: `smtp.gmail.com`
2. SMTP_PORT: `587`
3. İnternet bağlantınız var mı?
4. Firewall SMTP portunu engelliyor mu?

---

## 📋 Hızlı Kontrol Listesi

- [ ] 2 Adımlı Doğrulama açık
- [ ] App Password oluşturuldu
- [ ] App Password kopyalandı (16 haneli)
- [ ] `.env` dosyası oluşturuldu (doğru yerde)
- [ ] SMTP_USER = Gmail adresiniz
- [ ] SMTP_PASSWORD = App Password (boşluksuz)
- [ ] Dosya kaydedildi
- [ ] Uygulama yeniden başlatıldı
- [ ] Test kayıt oluşturuldu
- [ ] Email geldi

---

## 🎉 Başarılı!

Artık email gönderim sistemi çalışıyor! Kullanıcılar kayıt olduğunda email doğrulama mesajları otomatik olarak gönderilecek.
