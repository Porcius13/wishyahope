# Service Account Key Nedir?

## ❌ Bu DEĞİL (Node.js kodu):
```javascript
var admin = require("firebase-admin");
var serviceAccount = require("path/to/serviceAccountKey.json");
```

## ✅ Bu (JSON dosyası içeriği):

Service Account Key, Firebase Console'dan indirdiğiniz bir **JSON dosyasıdır**. İçeriği şöyle görünür:

```json
{
  "type": "service_account",
  "project_id": "miayis",
  "private_key_id": "abc123def456...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@miayis.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40miayis.iam.gserviceaccount.com"
}
```

## 📥 Nasıl İndirilir?

1. **Firebase Console'a git**: https://console.firebase.google.com/
2. **Proje seç**: `miayis`
3. **⚙️ Project Settings** (sol altta dişli ikonu)
4. **Service Accounts** sekmesine tıkla
5. **"Generate new private key"** butonuna tıkla
6. **JSON dosyasını indir** (örn: `miayis-firebase-adminsdk-xxxxx-xxxxxxxxxx.json`)

## 📁 Dosyayı Nereye Koy?

Proje klasörüne koy (ama git'e commit etme!):

```
kataloggia-main/
├── miayis-service-account.json  ← Buraya koy
├── app/
├── models.py
└── ...
```

## 🔧 Python'da Nasıl Kullanılır?

Bizim kodumuz zaten hazır! Sadece environment variable ayarla:

```powershell
# Windows PowerShell
$env:FIREBASE_CREDENTIALS_PATH="D:\wishyachatgüzel taslak savepoint\kataloggia-main\kataloggia-main\miayis-service-account.json"
$env:DB_BACKEND="firestore"
```

## ⚠️ ÖNEMLİ: Güvenlik

1. **Bu JSON dosyasını ASLA git'e commit etme!**
2. **`.gitignore`'a ekle**: `*service-account*.json`
3. **Dosyayı kimseyle paylaşma!** (Tüm Firebase projenize erişim verir)

## ✅ Kontrol

Dosyayı indirdikten sonra:
- Dosya adı: `miayis-firebase-adminsdk-xxxxx-xxxxxxxxxx.json` gibi bir şey
- Dosya boyutu: ~2-3 KB
- İçinde `"project_id": "miayis"` yazıyor mu? → ✅
- İçinde `"private_key"` var mı? → ✅

## 🚀 Sonraki Adım

Dosyayı indirdikten sonra:
1. Dosyayı proje klasörüne koy
2. Environment variable ayarla (yukarıdaki gibi)
3. Uygulamayı başlat

