# Firestore ile Uygulama Başlatma Scripti
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Firestore ile Uygulama Başlatılıyor" -ForegroundColor Cyan
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
    Write-Host "   Beklenen konum: $serviceAccountPath" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Lütfen Firebase Console'dan Service Account Key dosyasını indirin:" -ForegroundColor Yellow
    Write-Host "  1. https://console.firebase.google.com/ adresine gidin" -ForegroundColor White
    Write-Host "  2. Proje seçin: miayis" -ForegroundColor White
    Write-Host "  3. Project Settings → Service Accounts" -ForegroundColor White
    Write-Host "  4. 'Generate new private key' butonuna tıklayın" -ForegroundColor White
    Write-Host "  5. JSON dosyasını indirin ve şu konuma koyun:" -ForegroundColor White
    Write-Host "     $serviceAccountPath" -ForegroundColor Cyan
    Write-Host ""
    pause
    exit 1
}

Write-Host "✅ Service Account Key dosyası bulundu" -ForegroundColor Green
Write-Host "   Konum: $serviceAccountPath" -ForegroundColor Gray
Write-Host ""

# Environment variables ayarla
$env:DB_BACKEND = "firestore"
$env:FIREBASE_CREDENTIALS_PATH = $serviceAccountPath
$env:FIREBASE_PROJECT_ID = "miayis"
$env:PYTHONUNBUFFERED = "1"
$env:FLASK_ENV = "development"

Write-Host "Environment Variables:" -ForegroundColor Cyan
Write-Host "  DB_BACKEND=$env:DB_BACKEND" -ForegroundColor White
Write-Host "  FIREBASE_CREDENTIALS_PATH=$env:FIREBASE_CREDENTIALS_PATH" -ForegroundColor White
Write-Host "  FIREBASE_PROJECT_ID=$env:FIREBASE_PROJECT_ID" -ForegroundColor White
Write-Host ""

Write-Host "🚀 Uygulama başlatılıyor..." -ForegroundColor Yellow
Write-Host "URL: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Durdurmak için Ctrl+C tuşlarına basın" -ForegroundColor Gray
Write-Host ""
Write-Host "----------------------------------------" -ForegroundColor Gray
Write-Host ""

# Uygulamayı başlat
try {
    python run.py
} catch {
    Write-Host ""
    Write-Host "❌ HATA: Uygulama başlatılamadı!" -ForegroundColor Red
    Write-Host "Hata detayları:" -ForegroundColor Yellow
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    pause
}
