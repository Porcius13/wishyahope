# Basit başlatma script'i
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Miayis Uygulaması Başlatılıyor..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ana dizine git
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$parentDir = Split-Path -Parent $scriptDir
Set-Location $parentDir

Write-Host "Çalışma dizini: $parentDir" -ForegroundColor Yellow
Write-Host ""

# .env dosyası kontrolü
$envPath = Join-Path $parentDir ".env"
if (Test-Path $envPath) {
    Write-Host "✅ .env dosyası bulundu" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env dosyası bulunamadı (opsiyonel)" -ForegroundColor Yellow
}

# Firestore için credentials kontrolü
if (-not $env:DB_BACKEND) {
    $env:DB_BACKEND = "firestore"
}

# Firestore Service Account Key kontrolü
$serviceAccountPath = Join-Path $scriptDir "miayis-service-account.json"
if (Test-Path $serviceAccountPath) {
    $env:FIREBASE_CREDENTIALS_PATH = $serviceAccountPath
    $env:FIREBASE_PROJECT_ID = "miayis"
    Write-Host "✅ Firestore Service Account Key bulundu" -ForegroundColor Green
    Write-Host "✅ Firestore database backend kullanılıyor" -ForegroundColor Green
} elseif ($env:FIREBASE_CREDENTIALS_PATH) {
    Write-Host "✅ Firestore credentials path ayarlanmış: $env:FIREBASE_CREDENTIALS_PATH" -ForegroundColor Green
    Write-Host "✅ Firestore database backend kullanılıyor" -ForegroundColor Green
} elseif ($env:FIREBASE_CREDENTIALS_JSON) {
    Write-Host "✅ Firestore credentials JSON ayarlanmış" -ForegroundColor Green
    Write-Host "✅ Firestore database backend kullanılıyor" -ForegroundColor Green
} else {
    Write-Host "⚠️  Firestore credentials bulunamadı!" -ForegroundColor Yellow
    Write-Host "   Lütfen şunlardan birini yapın:" -ForegroundColor Yellow
    Write-Host "   1. miayis-service-account.json dosyasını kataloggia-main klasörüne koyun" -ForegroundColor White
    Write-Host "   2. Ya da .env dosyasına FIREBASE_CREDENTIALS_PATH ekleyin" -ForegroundColor White
    Write-Host "   3. Ya da .env dosyasına FIREBASE_CREDENTIALS_JSON ekleyin" -ForegroundColor White
    Write-Host ""
    Write-Host "   Detaylar için: kataloggia-main\FIRESTORE_KURULUM.md" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Uygulama başlatılıyor..." -ForegroundColor Yellow
Write-Host "Tarayıcınızda şu adresi açın: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Durdurmak için: Ctrl+C" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Python'u çalıştır
Set-Location $scriptDir
python run.py
