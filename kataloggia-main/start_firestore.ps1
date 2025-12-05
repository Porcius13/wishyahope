# Firestore ile Uygulama Başlatma Scripti (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Firestore ile Uygulama Başlatılıyor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ortam değişkenlerini ayarla
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:DB_BACKEND = "firestore"
$env:FIREBASE_CREDENTIALS_PATH = Join-Path $scriptDir "miayis-service-account.json"
$env:FIREBASE_PROJECT_ID = "miayis"
$env:PORT = "5000"
$env:HOST = "0.0.0.0"
$env:DEBUG = "True"

Write-Host "DB_BACKEND: $env:DB_BACKEND" -ForegroundColor Green
Write-Host "FIREBASE_PROJECT_ID: $env:FIREBASE_PROJECT_ID" -ForegroundColor Green
Write-Host "FIREBASE_CREDENTIALS_PATH: $env:FIREBASE_CREDENTIALS_PATH" -ForegroundColor Green
Write-Host ""
Write-Host "Uygulama başlatılıyor..." -ForegroundColor Yellow
Write-Host "URL: http://localhost:5000" -ForegroundColor Yellow
Write-Host ""

# Uygulamayı başlat
Set-Location $scriptDir
python run.py

