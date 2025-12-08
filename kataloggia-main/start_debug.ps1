# Debug modunda başlatma script'i
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Debug Modunda Başlatılıyor..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Script dizinine git
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$parentDir = Split-Path -Parent $scriptDir
Set-Location $scriptDir

Write-Host "Çalışma dizini: $scriptDir" -ForegroundColor Yellow
Write-Host ""

# Service Account kontrolü
$serviceAccountPath = Join-Path $scriptDir "miayis-service-account.json"
if (Test-Path $serviceAccountPath) {
    Write-Host "✅ Service Account Key bulundu: $serviceAccountPath" -ForegroundColor Green
    $env:DB_BACKEND = "firestore"
    $env:FIREBASE_CREDENTIALS_PATH = $serviceAccountPath
    $env:FIREBASE_PROJECT_ID = "miayis"
} else {
    Write-Host "❌ Service Account Key bulunamadı: $serviceAccountPath" -ForegroundColor Red
    Write-Host "   SQLite kullanılacak..." -ForegroundColor Yellow
    $env:DB_BACKEND = "sqlite"
}

# Python kontrolü
Write-Host ""
Write-Host "Python kontrolü..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python bulunamadı!" -ForegroundColor Red
    exit 1
}

# Environment variables
Write-Host ""
Write-Host "Environment Variables:" -ForegroundColor Cyan
Write-Host "  DB_BACKEND=$env:DB_BACKEND" -ForegroundColor White
Write-Host "  FIREBASE_PROJECT_ID=$env:FIREBASE_PROJECT_ID" -ForegroundColor White
if ($env:FIREBASE_CREDENTIALS_PATH) {
    Write-Host "  FIREBASE_CREDENTIALS_PATH=$env:FIREBASE_CREDENTIALS_PATH" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Uygulama başlatılıyor..." -ForegroundColor Yellow
Write-Host "URL: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Durdurmak için: Ctrl+C" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Uygulamayı başlat (hata çıktısını göster)
try {
    python run.py
} catch {
    Write-Host ""
    Write-Host "❌ HATA: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Detaylı hata için yukarıdaki çıktıyı kontrol edin." -ForegroundColor Yellow
    pause
}
