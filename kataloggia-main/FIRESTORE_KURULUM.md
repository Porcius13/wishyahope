# 🔥 Firestore Kurulum Rehberi (Sadece Firestore Kullanımı)

## 📋 Adım 1: Firebase Service Account Key İndir

1. **Firebase Console'a git**: https://console.firebase.google.com/
2. **Proje seç**: `miayis`
3. **⚙️ Project Settings** (sol altta dişli ikonu) → **Service Accounts** sekmesi
4. **"Generate new private key"** butonuna tıkla
5. **JSON dosyasını indir** (örn: `miayis-firebase-adminsdk-xxxxx-xxxxxxxxxx.json`)

## 📁 Adım 2: JSON Dosyasını Proje Klasörüne Koy

İndirdiğiniz JSON dosyasını `kataloggia-main` klasörüne kopyalayın ve adını `miayis-service-account.json` olarak değiştirin:

```
kataloggia-main/
  ├── miayis-service-account.json  ← Buraya koy
  ├── app/
  ├── run.py
  └── ...
```

## ⚙️ Adım 3: Environment Variables Ayarla

### Seçenek A: PowerShell ile (Geçici - Sadece bu oturum için)

```powershell
cd "c:\Users\faxys\OneDrive\Desktop\wishyahope\kataloggia-main"
$env:DB_BACKEND = "firestore"
$env:FIREBASE_CREDENTIALS_PATH = "c:\Users\faxys\OneDrive\Desktop\wishyahope\kataloggia-main\miayis-service-account.json"
$env:FIREBASE_PROJECT_ID = "miayis"
```

### Seçenek B: .env Dosyası Oluştur (Kalıcı - Önerilen)

`kataloggia-main` klasöründe `.env` dosyası oluşturun:

```powershell
cd "c:\Users\faxys\OneDrive\Desktop\wishyahope\kataloggia-main"

@"
DB_BACKEND=firestore
FIREBASE_CREDENTIALS_PATH=c:\Users\faxys\OneDrive\Desktop\wishyahope\kataloggia-main\miayis-service-account.json
FIREBASE_PROJECT_ID=miayis
"@ | Out-File -FilePath ".env" -Encoding utf8
```

### Seçenek C: Hazır Script Kullan

```powershell
cd "c:\Users\faxys\OneDrive\Desktop\wishyahope\kataloggia-main"
.\start_firestore.ps1
```

## 🚀 Adım 4: Uygulamayı Başlat

```powershell
python run.py
```

## ✅ Test Et

1. Tarayıcıdan `http://localhost:5000/register` sayfasına git
2. Yeni kullanıcı kaydet
3. Firebase Console → Firestore Database → `users` collection'ına bak
4. Yeni kullanıcıyı görmelisin!

## ❌ Sorun Giderme

### "DefaultCredentialsError" hatası
- **Çözüm**: `FIREBASE_CREDENTIALS_PATH` doğru ayarlanmamış veya dosya bulunamıyor
- **Kontrol**: `Test-Path $env:FIREBASE_CREDENTIALS_PATH` komutu ile dosya yolunu kontrol et

### "Permission denied" hatası
- **Çözüm**: Service account key'in Firestore'a yazma izni yok
- **Kontrol**: Firebase Console → IAM & Admin → Service Accounts → İzinleri kontrol et

### Dosya bulunamıyor
- **Çözüm**: Mutlak yol kullan (örn: `C:\Users\...` yerine `c:\Users\...`)
- **Kontrol**: Dosya adını kontrol et (büyük/küçük harf duyarlı olabilir)

## 🔒 Güvenlik Notları

- ⚠️ **Service Account Key dosyasını ASLA git'e commit etmeyin!**
- ✅ Dosya zaten `.gitignore`'da (`*service-account*.json`)
- 🔐 Dosyayı güvenli bir yerde saklayın
- 🚀 Production'da Application Default Credentials kullanın

## 📝 Notlar

- `DB_BACKEND=firestore` ayarı ile sadece Firestore kullanılır
- SQLite devre dışı kalır
- Tüm veriler Firebase Firestore'da saklanır
