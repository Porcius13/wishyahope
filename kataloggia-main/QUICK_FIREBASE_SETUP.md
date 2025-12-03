# Hızlı Firebase Kurulumu (Lokal Test)

## 1. Firebase Service Account Key İndir

1. Firebase Console'a git: https://console.firebase.google.com/
2. Proje seç: **miayis**
3. Project Settings → Service Accounts
4. "Generate new private key" butonuna tıkla
5. JSON dosyasını indir (örn: `miayis-service-account.json`)

## 2. JSON Dosyasını Proje Klasörüne Koy

```bash
# Örnek: kataloggia-main/miayis-service-account.json
```

## 3. Environment Variable Ayarla (Windows)

```powershell
# PowerShell'de:
$env:DB_BACKEND="firestore"
$env:FIREBASE_CREDENTIALS_PATH="D:\wishyachatgüzel taslak savepoint\kataloggia-main\kataloggia-main\miayis-service-account.json"
$env:FIREBASE_PROJECT_ID="miayis"
```

## 4. Uygulamayı Yeniden Başlat

```bash
python kataloggia-main/run_local.py --port 5000 --debug
```

## 5. Test Et

1. Tarayıcıdan `http://localhost:5000/register` sayfasına git
2. Yeni kullanıcı kaydet
3. Firebase Console → Firestore Database → `users` collection'ına bak
4. Yeni kullanıcıyı görmelisin!

## Alternatif: Application Default Credentials

Eğer Google Cloud SDK yüklüyse:

```bash
gcloud auth application-default login
```

Sonra sadece:
```bash
set DB_BACKEND=firestore
python kataloggia-main/run_local.py --port 5000 --debug
```

## Sorun Giderme

### "DefaultCredentialsError" hatası
→ `FIREBASE_CREDENTIALS_PATH` doğru ayarlanmamış veya dosya bulunamıyor

### "Permission denied" hatası
→ Service account key'in Firestore'a yazma izni yok. Firebase Console'dan IAM ayarlarını kontrol et.

### User oluşmuyor
→ Console loglarını kontrol et. `[HATA]` mesajlarına bak.

