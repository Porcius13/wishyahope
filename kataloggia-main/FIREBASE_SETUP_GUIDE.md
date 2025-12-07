# 🔥 Firebase Firestore Kurulum Rehberi

## Hızlı Kurulum (3 Adım)

### 1️⃣ Service Account Key İndir

1. Firebase Console'a git: https://console.firebase.google.com/
2. Proje seç: **miayis**
3. ⚙️ **Project Settings** → **Service Accounts** sekmesi
4. **"Generate new private key"** butonuna tıkla
5. JSON dosyasını indir (örn: `miayis-service-account.json`)

### 2️⃣ JSON Dosyasını Proje Klasörüne Koy

JSON dosyasını `kataloggia-main` klasörüne kopyalayın:
```
kataloggia-main/
  └── miayis-service-account.json
```

### 3️⃣ Environment Variable Ayarla

**PowerShell'de:**
```powershell
cd "c:\Users\faxys\OneDrive\Desktop\wishyahope\kataloggia-main"
$env:FIREBASE_CREDENTIALS_PATH="c:\Users\faxys\OneDrive\Desktop\wishyahope\kataloggia-main\miayis-service-account.json"
$env:FIREBASE_PROJECT_ID="miayis"
```

**Veya kalıcı olarak `.env` dosyası oluştur:**
```powershell
# .env dosyası oluştur (kataloggia-main klasöründe)
@"
FIREBASE_CREDENTIALS_PATH=c:\Users\faxys\OneDrive\Desktop\wishyahope\kataloggia-main\miayis-service-account.json
FIREBASE_PROJECT_ID=miayis
DB_BACKEND=firestore
"@ | Out-File -FilePath ".env" -Encoding utf8
```

### 4️⃣ Uygulamayı Başlat

```powershell
python run.py
```

## ✅ Test Et

1. Tarayıcıdan `http://localhost:5000/register` sayfasına git
2. Yeni kullanıcı kaydet
3. Firebase Console → Firestore Database → `users` collection'ına bak
4. Yeni kullanıcıyı görmelisin!

## 🔧 Alternatif: Application Default Credentials

Eğer Google Cloud SDK yüklüyse:

```powershell
# Google Cloud SDK'yı yükle (eğer yoksa)
# https://cloud.google.com/sdk/docs/install

# Login ol
gcloud auth application-default login

# Proje seç
gcloud config set project miayis
```

Sonra sadece:
```powershell
python run.py
```

## ❌ Sorun Giderme

### "DefaultCredentialsError" hatası
→ `FIREBASE_CREDENTIALS_PATH` doğru ayarlanmamış veya dosya bulunamıyor
→ Dosya yolunu kontrol et: `Test-Path $env:FIREBASE_CREDENTIALS_PATH`

### "Permission denied" hatası
→ Service account key'in Firestore'a yazma izni yok
→ Firebase Console → IAM & Admin → Service Accounts → İzinleri kontrol et

### Dosya bulunamıyor
→ Mutlak yol kullan (örn: `C:\Users\...` yerine `c:\Users\...`)
→ Dosya adını kontrol et (büyük/küçük harf duyarlı olabilir)

## 📝 Notlar

- Service Account Key dosyasını **GİT'E EKLEMEYİN** (`.gitignore`'da olmalı)
- Dosya güvenli bir yerde saklanmalı
- Production'da Application Default Credentials kullanın

