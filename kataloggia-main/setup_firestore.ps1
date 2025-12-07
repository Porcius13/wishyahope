# Firestore Kurulum Scripti
# Bu script .env dosyasını oluşturur ve gerekli ayarları yapar

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Firestore Kurulum Scripti" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Script'in bulunduğu dizin
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Service Account Key dosyasının yolu
$serviceAccountPath = Join-Path $scriptDir "miayis-service-account.json"

# Dosyanın varlığını kontrol et
if (-not (Test-Path $serviceAccountPath)) {
    Write-Host "❌ HATA: Service Account Key dosyası bulunamadı!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Lütfen önce Firebase Console'dan Service Account Key dosyasını indirin:" -ForegroundColor Yellow
    Write-Host "  1. https://console.firebase.google.com/ adresine gidin" -ForegroundColor White
    Write-Host "  2. Proje seçin: miayis" -ForegroundColor White
    Write-Host "  3. Project Settings → Service Accounts" -ForegroundColor White
    Write-Host "  4. 'Generate new private key' butonuna tıklayın" -ForegroundColor White
    Write-Host "  5. JSON dosyasını indirin ve şu konuma koyun:" -ForegroundColor White
    Write-Host "     $serviceAccountPath" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

Write-Host "✅ Service Account Key dosyası bulundu: $serviceAccountPath" -ForegroundColor Green
Write-Host ""

# .env dosyası oluştur
$envContent = @"
DB_BACKEND=firestore
FIREBASE_CREDENTIALS_PATH=$serviceAccountPath
FIREBASE_PROJECT_ID=miayis
"@

$envPath = Join-Path $scriptDir ".env"

# .env dosyası zaten varsa sor
if (Test-Path $envPath) {
    Write-Host "⚠️  .env dosyası zaten mevcut!" -ForegroundColor Yellow
    $overwrite = Read-Host "Üzerine yazmak istiyor musunuz? (E/H)"
    if ($overwrite -ne "E" -and $overwrite -ne "e") {
        Write-Host "İşlem iptal edildi." -ForegroundColor Yellow
        exit 0
    }
}

# .env dosyasını oluştur
$envContent | Out-File -FilePath $envPath -Encoding utf8 -NoNewline

Write-Host "✅ .env dosyası oluşturuldu: $envPath" -ForegroundColor Green
Write-Host ""
Write-Host "Oluşturulan ayarlar:" -ForegroundColor Cyan
Write-Host "  DB_BACKEND=firestore" -ForegroundColor White
Write-Host "  FIREBASE_CREDENTIALS_PATH=$serviceAccountPath" -ForegroundColor White
Write-Host "  FIREBASE_PROJECT_ID=miayis" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Artık uygulamayı başlatabilirsiniz:" -ForegroundColor Green
Write-Host "   python run.py" -ForegroundColor Cyan
Write-Host ""
