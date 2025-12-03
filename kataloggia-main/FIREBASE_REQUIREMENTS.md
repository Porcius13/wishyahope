# Firebase Firestore İçin Gereken Bilgiler

## 🔑 Zorunlu Bilgiler

### 1. Firebase Project ID
- **Değer**: `miayis` (zaten ayarlı)
- **Nerede**: `app/config.py` → `FIREBASE_PROJECT_ID = 'miayis'`
- **Değiştirmek için**: Environment variable: `FIREBASE_PROJECT_ID=miayis`

### 2. Firebase Authentication (İki Seçenek)

#### Seçenek A: Service Account Key (Önerilen - Lokal Test İçin)

**Gereken:**
- Service Account Key JSON dosyası

**Nasıl Alınır:**
1. Firebase Console: https://console.firebase.google.com/
2. Proje seç: **miayis**
3. ⚙️ Project Settings → Service Accounts
4. "Generate new private key" butonuna tıkla
5. JSON dosyasını indir (örn: `miayis-service-account.json`)

**JSON Dosyası İçeriği:**
```json
{
  "type": "service_account",
  "project_id": "miayis",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...@miayis.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

**Environment Variable:**
```bash
# Windows PowerShell
$env:FIREBASE_CREDENTIALS_PATH="C:\path\to\miayis-service-account.json"

# Windows CMD
set FIREBASE_CREDENTIALS_PATH=C:\path\to\miayis-service-account.json

# Linux/Mac
export FIREBASE_CREDENTIALS_PATH=/path/to/miayis-service-account.json
```

#### Seçenek B: Application Default Credentials (Production İçin)

**Gereken:**
- Google Cloud SDK yüklü olmalı
- `gcloud auth application-default login` komutu çalıştırılmış olmalı

**Kurulum:**
```bash
# Google Cloud SDK'yı yükle (eğer yoksa)
# https://cloud.google.com/sdk/docs/install

# Login ol
gcloud auth application-default login

# Proje seç
gcloud config set project miayis
```

**Not:** Bu durumda `FIREBASE_CREDENTIALS_PATH` ayarlamaya gerek yok.

## 📋 Özet: Minimum Gereksinimler

### Lokal Test İçin:
1. ✅ Firebase Project ID: `miayis` (zaten var)
2. ✅ Service Account Key JSON dosyası (indir)
3. ✅ `FIREBASE_CREDENTIALS_PATH` environment variable (ayarla)
4. ✅ `DB_BACKEND=firestore` environment variable (ayarla)

### Production İçin:
1. ✅ Firebase Project ID: `miayis` (zaten var)
2. ✅ Application Default Credentials (gcloud auth)
3. ✅ `DB_BACKEND=firestore` environment variable (ayarla)

## 🔧 Environment Variables Listesi

```bash
# Zorunlu
DB_BACKEND=firestore

# Firebase Project ID (varsayılan: miayis)
FIREBASE_PROJECT_ID=miayis

# Service Account Key Path (Seçenek A için)
FIREBASE_CREDENTIALS_PATH=C:\path\to\service-account-key.json
```

## 📝 Örnek Kurulum (Windows PowerShell)

```powershell
# 1. Service Account Key'i indir ve proje klasörüne koy
# Örnek: D:\wishyachatgüzel taslak savepoint\kataloggia-main\kataloggia-main\miayis-service-account.json

# 2. Environment variables ayarla
$env:DB_BACKEND="firestore"
$env:FIREBASE_PROJECT_ID="miayis"
$env:FIREBASE_CREDENTIALS_PATH="D:\wishyachatgüzel taslak savepoint\kataloggia-main\kataloggia-main\miayis-service-account.json"

# 3. Uygulamayı başlat
cd kataloggia-main
python run_local.py --port 5000 --debug
```

## ✅ Kontrol Listesi

- [ ] Firebase Console'a erişim var mı? (https://console.firebase.google.com/)
- [ ] `miayis` projesi seçili mi?
- [ ] Service Account Key JSON dosyası indirildi mi?
- [ ] JSON dosyası güvenli bir yerde mi? (git'e commit etme!)
- [ ] `FIREBASE_CREDENTIALS_PATH` doğru dosya yolunu gösteriyor mu?
- [ ] `DB_BACKEND=firestore` ayarlandı mı?
- [ ] Firestore Database aktif mi? (Firebase Console → Firestore Database)

## 🚨 Güvenlik Uyarıları

1. **Service Account Key'i asla git'e commit etme!**
   - `.gitignore`'a ekle: `*service-account*.json`
   - Environment variable kullan

2. **Key dosyasını paylaşma!**
   - Sadece güvenilir kişilerle paylaş
   - Production'da Application Default Credentials kullan

3. **Firestore Security Rules ayarla!**
   - Firebase Console → Firestore Database → Rules
   - Sadece yetkili kullanıcılar yazabilsin

## 🔍 Test Etme

1. Uygulamayı başlat
2. `http://localhost:5000/register` sayfasına git
3. Yeni kullanıcı kaydet
4. Firebase Console → Firestore Database → `users` collection'ına bak
5. Yeni kullanıcıyı görmelisin!

## 📞 Sorun Giderme

### "DefaultCredentialsError"
→ `FIREBASE_CREDENTIALS_PATH` yanlış veya dosya bulunamıyor

### "Permission denied"
→ Service Account'un Firestore'a yazma izni yok. Firebase Console → IAM & Admin → Service Accounts

### "Project not found"
→ `FIREBASE_PROJECT_ID` yanlış veya proje mevcut değil

### User oluşmuyor
→ Console loglarını kontrol et. `[HATA]` mesajlarına bak.

